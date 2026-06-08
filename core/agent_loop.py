import json
from core.gemini import generate
from core.tools.read import read_file
from core.tools.bash import run_command
from core.tools.write import write_file
from core.tools.edit import edit_file
from core.tools_registry import AVAILABLE_TOOLS
import json_repair
from core.system import SYSTEM_PROMPT



def parse_response(text):
    if not text:
        raise ValueError("Empty response from AI model")

    text = text.strip()

    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    
    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    try:
        repaired = json_repair.repair_json(text)
        return json.loads(repaired)
    
    except Exception as e:
        pass  
    
    try:
        return json.loads(text)
    
    except json.JSONDecodeError as e:
        print(f"\n[ERROR] Failed to parse AI response as JSON:")
        print(f"[ERROR] Raw response (first 500 chars): {text[:500]}")
        raise ValueError(
            f"AI did not return valid JSON. Response starts with: {text[:100]}"
        )
    
    


def execute_tool(response):
    
    tool_name = response.get("tool")
    
    if not tool_name:
        raise ValueError("Missing 'tool' field in response")
    
    if tool_name not in AVAILABLE_TOOLS:
        raise ValueError(f"Unknown tool: {tool_name}. Available: {list(AVAILABLE_TOOLS.keys())}")
    
    tool_function = AVAILABLE_TOOLS[tool_name]
    
    if tool_name == "read":
        path = response.get("path")
        if not path:
            raise ValueError("Missing 'path' field for read tool")
        return read_file(path)
    
    elif tool_name == "bash":
        command = response.get("command")
        if not command:
            raise ValueError("Missing 'command' field for bash tool")
        
        result = run_command(command)
        return {
            "stdout": result["stdout"],
            "stderr": result["stderr"],
            "returncode": result["returncode"]
        }
        
    elif tool_name == "write":
        
        return write_file(
            response["path"],
            response["content"]
        )
        
        
    elif tool_name == "edit":
        
        path = response.get("path", "unknown")
        old_text = response.get("old_text", "unknown")
        new_text = response.get("new_text", "unknown")
        
        return edit_file(path,old_text,new_text)
    
    else:
        return tool_function(response)


def run_agent(api_key, model, prompt, history=None, agent_state=None): 
    
    if history is None:
        history = []
        
    if agent_state is None:
        agent_state =  {
            "files_read": [],
            "files_written": [],
            "commands_run": [],
            "file_edited": []
        }
    
    messages = [SYSTEM_PROMPT]
    
    for msg in history:
        messages.append(f"{msg['role']} : {msg['content']}")

    messages.append(prompt)

    tool_counts = {}    
    
    files_written_this_turn = 0
        
    for step in range(100):        
        
        state_prompt = f"""
            Agent State

            Files Read:
            {agent_state['files_read']}

            Files Written:
            {agent_state['files_written']}

            Commands Run:
            {agent_state['commands_run']}
            
            Files Edited:
            {agent_state['file_edited']}
            
            REMINDER: You MUST respond with ONLY valid JSON.
        """
        
        raw_response = generate(api_key,model,messages + [state_prompt])
                
        response = parse_response(raw_response)
        
        messages.append(
            f"Assistant Response: {json.dumps(response)}"
        )
        
        if isinstance(response, list) and len(response) > 0:
            response = response[0]
        
            
        if response.get("tool") == "final":
            return response["content"]
        
        tool_name = response.get("tool")
        tool_key = None
            
        if tool_name == "read":
            tool_key = f"read:{response.get('path')}"
            agent_state["files_read"].append(response["path"])

        elif tool_name == "write":
            tool_key = f"write:{response.get('path')}"
            files_written_this_turn += 1
            agent_state["files_written"].append(response["path"])
            
        elif tool_name == "bash":
            tool_key = f"bash:{response.get('command')}"
            agent_state["commands_run"].append(response["command"])

        elif tool_name == "edit":
            tool_key = f"edit: {response.get('path')}"
            agent_state["file_edited"].append(response["path"])        
        
        else:
            tool_key = tool_name
            

        tool_counts[tool_key] = tool_counts.get(tool_key, 0) + 1

        print("")

        if tool_counts[tool_key] > 10:
            return f"tool loop detected: {tool_key}"

        msgs = {
            "read": "→ READING FILE: {path}",
            "bash": "→ RUNNING COMMAND: {command}",
            "write": "→ WRITING: {path}",
            "edit": "→ EDITING: {path}",
        }

        if tool_name in msgs:
            fmt = msgs[tool_name]
            print(fmt.format(**response))
        else:
            print(f"→ EXECUTING TOOL: {tool_name}")
            print(f"  Parameters: {response}")
        
        try:  
            tool_result = execute_tool(response)
        
        except Exception as e:
            tool_result = {
                "error": str(e)
            }
        
        messages.append(
            f"""
                Tool Execution Result

                Tool:
                {response['tool']}

                Result:
                {json.dumps(tool_result)}
            """
        )
        
        if files_written_this_turn >= 2:
            messages.append(
                "REMINDER: You have written the files. "
                "If the task is complete, respond with: {\"tool\": \"final\", \"content\": \"Task completed\"}"
            )
            
    if files_written_this_turn > 0:
        return f"Task completed. Wrote {files_written_this_turn} file(s)."
        
    return "agent exceeded max iteration"

import json
from core.gemini import generate
from core.tools.read import read_file
from core.tools.bash import run_command
from core.tools.write import write_file
from core.tools_registry import AVAILABLE_TOOLS
import json_repair
from core.system import SYSTEM_PROMPT



def parse_response(text):

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
    
    except:
        return json.loads(text)


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
    
    else:
        return tool_function(response)


agent_state = {
    "files_read": [],
    "files_written": [],
    "commands_run": []
}

def run_agent(api_key, model, prompt):
    
    messages = [
        SYSTEM_PROMPT,
        prompt
    ]
    
    
    tool_counts = {}    
    
    files_written = 0      
    
    written_files = set()                
    
    for step in range(100):
        
        print(f"\nSTEP {step + 1}")
        
        
        state_prompt = f"""
            Agent State

            Files Read:
            {agent_state['files_read']}

            Files Written:
            {agent_state['files_written']}

            Commands Run:
            {agent_state['commands_run']}
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
        
        if tool_name == "read":
            tool_key = f"read:{response.get('path')}"
            agent_state["files_read"].append(response["path"])

        elif tool_name == "write":
            tool_key = f"write:{response.get('path')}"
            files_written += 1
            agent_state["files_written"].append(response["path"])
            
        elif tool_name == "bash":
            tool_key = f"bash:{response.get('command')}"
            agent_state["commands_run"].append(response["command"])

        else:
            tool_key = tool_name
            

        tool_counts[tool_key] = tool_counts.get(tool_key, 0) + 1


        if tool_counts[tool_key] > 10:
            return f"tool loop detected: {tool_key}"

        if tool_name == "read":
            path = response.get("path", "unknown")
            print(f"→ READING FILE: {path}")
            
        elif tool_name == "bash":
            command = response.get("command", "unknown")
            print(f"→ RUNNING COMMAND: {command}")
        
        elif tool_name == "write":
            path = response.get("path", "unknown")
            print(f"→ WRITING: {path}")
        
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
        
        if files_written >= 2:
            messages.append(
                "REMINDER: You have written the files. "
                "If the task is complete, respond with: {\"tool\": \"final\", \"content\": \"Task completed\"}"
            )
            
    
    if files_written > 0:
        return f"Task completed. Wrote {files_written} file(s)."
        
        
                
    return "agent exceeded max iteration"

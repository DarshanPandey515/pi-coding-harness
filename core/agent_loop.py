import json
from dataclasses import dataclass, field
from typing import List
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, TextPart

from tools.read import read_file
from tools.bash import run_command
from tools.write import write_file
from tools.edit import edit_file
from core.prompts.system import SYSTEM_PROMPT
import asyncio
import nest_asyncio2
from core.agent_state import AgentState
from dotenv import load_dotenv
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider


load_dotenv()
nest_asyncio2.apply()

class FinalResult(BaseModel):
    content: str = Field(description="final response to the user")

async def tool_read(ctx: RunContext[AgentState], path: str) -> str:
    ctx.deps.files_read.append(path)
    try:
        return read_file(path)
    except Exception as e:
        return f"Error reading {path}: {e}"


async def tool_bash(ctx: RunContext[AgentState], command: str) -> str:
    ctx.deps.commands_run.append(command)
    result = run_command(command)
    return f"stdout:\n{result['stdout']}\nstderr:\n{result['stderr']}\nreturncode: {result['returncode']}"


async def tool_write(ctx: RunContext[AgentState], path: str, content: str) -> str:
    ctx.deps.files_written.append(path)
    result = write_file(path, content)
    if result["success"]:
        return f"Successfully wrote to {path}. Preview: {result['content_preview']}..."
    return f"Failed to write to {path}."


async def tool_edit(ctx: RunContext[AgentState], path: str, old_text: str, new_text: str) -> str:
    ctx.deps.file_edited.append(path)
    result = edit_file(path, old_text, new_text)
    if result["success"]:
        return f"Successfully edited {path}."
    return f"Failed to edit {path}: {result.get('error', 'unknown error')}"





async def run_agent(provider: str, model: str, api_key: str, prompt: str, history: List[dict] = None, agent_state: AgentState = None) -> str:
    if history is None:
        history = []
    if agent_state is None:
        agent_state = AgentState()

    message_history: List[ModelMessage] = []
    
    for msg in history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "user":
            message_history.append(ModelRequest(parts=[TextPart(content)]))
        elif role == "assistant":
            message_history.append(ModelResponse(parts=[TextPart(content)]))
    
    if provider == "groq":
        model_instance = GroqModel(
            model,
            provider=GroqProvider(
                api_key=api_key
            )
        )
    elif provider == "gemini":
        model_instance = GoogleModel(
            model,
            provider=GoogleProvider(
                api_key=api_key
            )
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")

    agent = Agent(
        model=model_instance,
        system_prompt=SYSTEM_PROMPT,
        output_type=FinalResult,
        deps_type=AgentState,
        tools=[tool_read, tool_bash, tool_write, tool_edit],
    )

    result = await agent.run(
        prompt,                   
        message_history=message_history,
        deps=agent_state,
    )      

    return result.output.content
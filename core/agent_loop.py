import asyncio
from typing import AsyncIterator, List

from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    PartDeltaEvent,
    TextPart,
    TextPartDelta,
)
from pydantic_ai.run import AgentRunResultEvent
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from tools.read import read_file
from tools.bash import run_command
from tools.write import write_file
from tools.edit import edit_file
from core.prompts.system import SYSTEM_PROMPT
from core.agent_state import AgentState
from core.events import emit


load_dotenv()


async def tool_read(ctx: RunContext[AgentState], path: str) -> str:
    ctx.deps.files_read.append(path)
    emit(f"→ reading {path}")
    try:
        return await asyncio.to_thread(read_file, path)
    except Exception as e:
        return f"Error reading {path}: {e}"


async def tool_bash(ctx: RunContext[AgentState], command: str) -> str:
    ctx.deps.commands_run.append(command)
    emit(f"→ running: {command}")
    result = await asyncio.to_thread(run_command, command)
    return f"stdout:\n{result['stdout']}\nstderr:\n{result['stderr']}\nreturncode: {result['returncode']}"


async def tool_write(ctx: RunContext[AgentState], path: str, content: str) -> str:
    ctx.deps.files_written.append(path)
    emit(f"→ writing {path}")
    result = await asyncio.to_thread(write_file, path, content)
    if result["success"]:
        return f"Successfully wrote to {path}. Preview: {result['content_preview']}..."
    return f"Failed to write to {path}."


async def tool_edit(ctx: RunContext[AgentState], path: str, old_text: str, new_text: str) -> str:
    ctx.deps.file_edited.append(path)
    emit(f"→ editing {path}")
    result = await asyncio.to_thread(edit_file, path, old_text, new_text)
    if result["success"]:
        return f"Successfully edited {path}."
    return f"Failed to edit {path}: {result.get('error', 'unknown error')}"


def build_model(provider: str, model: str, api_key: str):
    if provider == "groq":
        return GroqModel(model, provider=GroqProvider(api_key=api_key))
    if provider == "gemini":
        return GoogleModel(model, provider=GoogleProvider(api_key=api_key))
    raise ValueError(f"Unsupported provider: {provider}")


def build_message_history(history: List[dict]) -> List[ModelMessage]:
    message_history: List[ModelMessage] = []
    for msg in history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "user":
            message_history.append(ModelRequest(parts=[TextPart(content)]))
        elif role == "assistant":
            message_history.append(ModelResponse(parts=[TextPart(content)]))
    return message_history


def build_agent(provider: str, model: str, api_key: str) -> Agent:
    return Agent(
        model=build_model(provider, model, api_key),
        system_prompt=SYSTEM_PROMPT,
        output_type=str,
        deps_type=AgentState,
        tools=[tool_read, tool_bash, tool_write, tool_edit],
    )


async def run_agent_stream(
    provider: str,
    model: str,
    api_key: str,
    prompt: str,
    history: List[dict] = None,
    agent_state: AgentState = None,
) -> AsyncIterator[dict]:
    """Yield normalized events: text_delta, done, error.

    Tool activity is reported separately through core.events.emit.
    """
    if history is None:
        history = []
    if agent_state is None:
        agent_state = AgentState()

    agent = build_agent(provider, model, api_key)

    try:
        async with agent.run_stream_events(
            prompt,
            message_history=build_message_history(history),
            deps=agent_state,
        ) as events:
            async for event in events:
                if isinstance(event, PartDeltaEvent) and isinstance(event.delta, TextPartDelta):
                    if event.delta.content_delta:
                        yield {"type": "text_delta", "text": event.delta.content_delta}
                elif isinstance(event, AgentRunResultEvent):
                    yield {"type": "done", "text": event.result.output}
    except Exception as e:
        yield {"type": "error", "message": str(e)}


async def run_agent(
    provider: str,
    model: str,
    api_key: str,
    prompt: str,
    history: List[dict] = None,
    agent_state: AgentState = None,
) -> str:
    text = ""
    async for event in run_agent_stream(provider, model, api_key, prompt, history, agent_state):
        if event["type"] == "text_delta":
            text += event["text"]
        elif event["type"] == "done":
            text = event["text"]
        elif event["type"] == "error":
            raise RuntimeError(event["message"])
    return text

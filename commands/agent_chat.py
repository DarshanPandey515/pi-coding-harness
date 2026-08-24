import click
import asyncio
import os
from pathlib import Path
from dataclasses import asdict
from core.config import get_default_model, get_provider_api_key
from commands.sessions import (
    create_session, load_session, append_messages,
    get_messages, update_agent_state
)
from core.repo import get_project_tree
from core.agent_loop import run_agent
from core.prompts.system import SYSTEM_PROMPT
from core.agent_state import AgentState

AGENT_SYSTEM_PROMPT = SYSTEM_PROMPT


@click.command()
@click.option("--resume", default=None, help="Session ID to resume")
def agent_chat(resume):
    """Interactive agent session with full tool access."""
    
    model = get_default_model()
    if not model:
        click.echo("No model selected")
        return
    
    provider, actual_model = model.split('/', 1)
    api_key = get_provider_api_key(provider)
    
    if not api_key:
        click.echo(f"{provider} not logged in.")
        return

    if resume:
        session = load_session(resume)
        if not session:
            return
        session_id = resume
        click.echo(f"Resumed session: {session_id}")
    
    else:
        session_id = create_session(provider, actual_model)
        click.echo(f"New session: {session_id}")

    click.echo("Agent Chat – type 'exit' to quit.\n")

    while True:
        user_input = input("\nYou > ")
    
        if user_input.strip().lower() == "exit":
            click.echo("Goodbye.")
            break

        tree = get_project_tree()
        home = str(Path.home())
    
        full_prompt = f"""
        
            {SYSTEM_PROMPT}
        
            Current working directory (a project folder, not the desktop): {os.getcwd()}
            User home directory: {home}

            User Request:
            {user_input}

            Instructions:
            - Explore the repository if needed.
            - Use bash with grep/find/tree when searching.
            - Read files only when necessary.
            - Use edit for existing files.
            - Use write for new files.
            - When the user names a location like "desktop", write to the absolute path (e.g. {home}/Desktop/hello.py), not the current directory.
            - Complete the task and then return a final response.   
            - if user ask question then answer like a helpful assistant
     
        
        """

        append_messages(session_id, "user", user_input)

        session = load_session(session_id)
        history = session["messages"]          
        raw_state = session.get("agent_state") or {}
        agent_state = AgentState(**raw_state)

        final_response = asyncio.run(
            run_agent(
                provider=provider,
                model=actual_model,
                api_key=api_key,
                prompt=full_prompt,
                history=history,
                agent_state=agent_state
            )
        )

        append_messages(session_id, "assistant", final_response)
        update_agent_state(session_id, asdict(agent_state))

        print(f"\nAssistant > {final_response}")
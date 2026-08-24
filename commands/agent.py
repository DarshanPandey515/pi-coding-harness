import click
from core.config import get_default_model,get_provider_api_key
from core.repo import get_project_tree
from core.agent_loop import run_agent
import asyncio
import os
from pathlib import Path
from core.agent_state import AgentState


@click.command()
@click.option(
    "-p",
    "--prompt",
    required=True
)
def agent(prompt):
    """use 'python main.py agent --prompt /your task/'"""
    
    get_model = get_default_model()
        
    if not get_model:
        click.echo("no model selected")
        return
    
    provider = get_model.split("/", 1)[0]
    model = get_model.split("/", 1)[1]
    

    api_key = get_provider_api_key(provider)
    
    if not api_key:
        click.echo(f"{provider} not logged in.")
        return 
    
    
    tree = get_project_tree()
    home = str(Path.home())
    
    full_prompt = f"""
        Current working directory (a project folder, not the desktop): {os.getcwd()}
        User home directory: {home}

        User Request:
        {prompt}

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

    initial_state = AgentState()
    
    response = asyncio.run(
        run_agent(
        provider=provider,
        model=model, 
        prompt=full_prompt,
        history=[],
        agent_state=initial_state,
        api_key=api_key
    ))
    
    
    click.echo()
    click.echo(response)
    click.echo()
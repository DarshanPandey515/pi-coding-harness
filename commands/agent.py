import click
from core.config import get_default_model,get_provider_api_key
from core.repo import get_project_tree
from core.agent_loop import run_agent

@click.command()
@click.option(
    "-p",
    "--prompt",
    required=True
)
def agent(prompt):
    """use 'python main.py agent --prompt /your task/'"""
    
    model = get_default_model()
    
    if not model:
        click.echo("no model selected")
        return
    
    provider = model.split('/')[0]
    
    api_key = get_provider_api_key(provider)
    
    if not api_key:
        click.echo(f"{provider} not logged in.")
        return 
    
    actual_model = model.split('/')[1]
    
    
    tree = get_project_tree()
    
    full_prompt = f"""
        User current folder Structure:
        {tree}

        User Request:
        {prompt}

        Instructions:
        - Explore the repository if needed.
        - Use bash with grep/find/tree when searching.
        - Read files only when necessary.
        - Use edit for existing files.
        - Use write for new files.
        - Complete the task and then return a final response.
    """
    
    response  = run_agent(
        api_key,
        actual_model,
        full_prompt
    )
    
    click.echo()
    click.echo(response)
    click.echo()
import click
from core.config import get_default_model,get_provider_api_key
from core.gemini import generate
from core.repo import get_project_tree
from core.agent_loop import run_agent

@click.command()
@click.option(
    "-p",
    "--prompt",
    required=True
)
def agent(prompt):
    
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
        Project structure:
        {tree}

        User request:
        {prompt}

        Complete this task now.
    """    
    
    response  = run_agent(
        api_key,
        actual_model,
        full_prompt
    )
    
    click.echo()
    click.echo(response)
    click.echo()
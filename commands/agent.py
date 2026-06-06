import click
from core.config import get_default_model,get_provider_api_key
from core.gemini import generate

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
    
    response  = generate(
        api_key,
        actual_model,
        prompt
    )
    
    
    click.echo()
    click.echo(response)
    click.echo()
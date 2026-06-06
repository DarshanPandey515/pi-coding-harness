import click
from core.registry import get_models
from core.config import load_config

@click.command()
def models():
    """Available models"""
    available_models = get_models()
    
    click.echo()
    
    
    config = load_config()

    selected = config.get(
        "default_model"
    )
    
    for model in available_models:
        
        provider = model["provider"]
        
        name = model["name"]
        
        full_name = f"{provider}/{name}"
        
        prefix = " "

        if full_name == selected:
            prefix = "*"

        click.echo(
            f"{prefix} {full_name}"
        )
    
    click.echo()
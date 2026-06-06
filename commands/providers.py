import click
from core.providers import SUPPORTED_PROVIDERS
from core.registry import provider_exists
from core.config import load_config, save_config

@click.group()
def providers():
    """Manage providers"""
    pass


@providers.command()
def list():
    """list of supported providers"""
    
    config = load_config()
    
    logged_in = config.get(
        "providers",
        {}
    )
    
    click.echo()
    
    for provider, info in SUPPORTED_PROVIDERS.items():
        status = "✓"
        
        if provider not in logged_in:
            status = "✗"
        
        click.echo(
            f"{status} {provider:<10} {info["name"]}"
        )        
        
    click.echo()
        

@providers.command()
@click.option("--provider",required=True)
@click.option("--api-key",required=True)
def login(provider, api_key):
    
    if not provider_exists(provider):
        click.echo(f"unsupported provider: {provider}")
        return
    
    click.echo(f"Logging into {provider}")
    
    config = load_config()
    
    config.setdefault(
        "providers",
        {}
    )
    
    config["providers"][provider] = {
        "api_key": api_key
    }
    
    save_config(config)
    
    click.echo(f"login successfull\nlogged into {provider}")
    
    
@providers.command()
@click.option("--provider",required=True)
def logout(provider):
    
    config = load_config()
    
    provider_config = config.get(
        "providers",
        {}
    )
    
    if provider not in provider_config:
        click.echo(
            f"{provider} is not logged in"
        )
        
        return
    
    provider_config.pop(provider)
    
    save_config(config)
    
    click.echo(f"{provider} logged out.")
    
    
    
    
    
    
@providers.command()
@click.argument("model")
def set(model):
    
    config = load_config()
    
    config['default_model'] = model
    
    save_config(config)
    
    click.echo(
        f"default model set to {model}"
    )
    
    
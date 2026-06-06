import click

from commands.providers import providers
from commands.models import models
from commands.agent import agent


@click.group()
def cli():
    """PI Coding Agent"""
    pass



cli.add_command(providers)
cli.add_command(models)
cli.add_command(agent)


if __name__ == "__main__":
    cli()
import click

from commands.providers import providers
from commands.models import models
from commands.agent import agent
from commands.chat import chat
from commands.chat import sessions, delete
from commands.agent_chat import agent_chat

@click.group()
def cli():
    """PI Coding Agent"""
    pass



cli.add_command(providers)
cli.add_command(models)
cli.add_command(agent)
cli.add_command(chat)
cli.add_command(sessions)
cli.add_command(delete)
cli.add_command(agent_chat)


if __name__ == "__main__":
    cli()
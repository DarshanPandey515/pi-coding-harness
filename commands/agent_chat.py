import click


@click.command()
@click.option("--resume", default=None, help="Session ID to resume")
def agent_chat(resume):
    """Interactive agent session with full tool access (TUI)."""
    from tui.app import PiApp

    PiApp(resume=resume).run()

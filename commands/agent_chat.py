import click
from core.config import get_default_model, get_provider_api_key
from commands.sessions import (
    create_session, load_session, append_messages,
    get_messages, update_agent_state
)
from core.repo import get_project_tree
from core.agent_loop import run_agent
from core.prompts.system import SYSTEM_PROMPT

AGENT_SYSTEM_PROMPT = SYSTEM_PROMPT


@click.command()
@click.option("--resume", default=None, help="Session ID to resume")
def agent_chat(resume):
    """Interactive agent session with full tool access."""
    
    model = get_default_model()
    if not model:
        click.echo("No model selected")
        return
    
    provider, actual_model = model.split('/')
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
    
        full_prompt = f"""
        
            {SYSTEM_PROMPT}
        
            User current folder Structure:
            {tree}

            User Request:
            {user_input}

            Instructions:
            - Explore the repository if needed.
            - Use bash with grep/find/tree when searching.
            - Read files only when necessary.
            - Use edit for existing files.
            - Use write for new files.
            - Complete the task and then return a final response.        
        
        """

        append_messages(session_id, "user", user_input)

        session = load_session(session_id)
        history = session["messages"]          
        agent_state = session["agent_state"]   

        final_response = run_agent(
            api_key,
            actual_model,
            full_prompt,
            history=history,
            agent_state=agent_state
        )

        append_messages(session_id, "assistant", final_response)
        update_agent_state(session_id, agent_state)

        print(f"\nAssistant > {final_response}")
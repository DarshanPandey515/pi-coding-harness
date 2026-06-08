import click
from core.config import (
    get_default_model,
    get_provider_api_key
)

from core.sessions import (
    create_session,
    append_messages,
    get_messages,
    list_session, 
    load_session
)
import os
from core.config import SESSIONS_DIR

from core.gemini import generate


CHAT_SYSTEM_PROMPT = """
You are a Pi coding agent.
You are just for normal chatting not a agentic one and for agentic one if user ask tell me to use like this command: python main.py agent -p "user prompt here".
"""



@click.command()
@click.option("--resume", default=None)
def chat(resume):
    """start your pi coding agent chat and sessions"""
    
    click.echo("PI Chat")   
    click.echo("Type 'exit' to quit")  
    
    model = get_default_model()
    actual_model = model.split('/')[1]
    provider = model.split("/")[0]
    api_key = get_provider_api_key(provider)
    
    
    if resume:
        session = load_session(resume)
        
        if not session:
            return 
        
        session_id = resume
        
        click.echo(f"resume: {session_id}")
        
    else:
        session_id = create_session(provider,actual_model)
    
        click.echo(f"session: {session_id}")
    
    
    
    while True:
        
        user_input = input("\nYou > ")
        
        if user_input.lower() == "exit":
            click.echo("\nThank you for using Pi.\nhave a good day :)")
            break
        
        full_prompt = f"""
        {CHAT_SYSTEM_PROMPT}
        
        user request : {user_input}
        
        """
        
        
        append_messages(
            session_id,
            "user",
            full_prompt
        )
        
        history = get_messages(session_id)
        
        messages = []
        
        for msg in history:
            messages.append(
                f"{msg['role']} : {msg['content']}"
            )
            
        assistant_response = generate(api_key, actual_model, messages)
        
        append_messages(
            session_id,
            "assistant",
            assistant_response
        )
        
        print(f"\nAssistant > {assistant_response}")
 
 
@click.group()
def sessions():
    """your sessions history"""
    pass
    
@sessions.command()
def list():
    """your recent sessions history list"""
    sessions = list_session()
    
    click.echo(f"\nYour recent sessions: ")    
    click.echo()
    
    count = 0
    
    for i, s in enumerate(sessions, 1):
        click.echo(f"{i}. ID: {s['id']} | Model: {s['model']} | Provider: {s['provider']} "
                f"| Messages: {len(s['messages'])} | Updated: {s['updated_at']}")
    
        click.echo()

    click.echo()
    click.echo("use 'python main.py chat --resume {your session ID}' to resume your chat.")
    click.echo("use 'python main.py delete --id {your session ID}' to delete your chat.")
    
@sessions.command()
@click.option("--id", "session_id", required=True)
def delete(session_id):
    """delete you session with --id {session id}"""

    session_file = (SESSIONS_DIR / f"{session_id}.json")

    if not session_file.exists():
        raise FileNotFoundError(f"session not found: {session_id}")
    
    session_file.unlink()
    
    click.echo(f"removed session: {session_id}.json")
    
    

@sessions.command()
@click.option("--id", "session_id", required=True)
def show(session_id):
    """your session detail"""
    session = load_session(session_id)
    
    click.echo()
    click.echo(f"Session: {session['id']}")
    click.echo(f"Model: {session['model']}")
    click.echo(f"Provider: {session['provider']}")
    click.echo()

    for msg in session["messages"]:
        click.echo(
            f"{msg['role']}: {msg['content']}"
        )
        click.echo()
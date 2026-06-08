from pathlib import Path
from core.config import SESSIONS_DIR
import uuid
import json
from datetime import datetime


def create_session(provider, model):
    session_id = str(uuid.uuid4())

    session = {
        "id":session_id,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "provider": provider,
        "model": model,
        "messages": []
    }
    
    session_file = (
        SESSIONS_DIR / f"{session_id}.json"
    )
    
    with open(session_file, "w") as f:
        json.dump(session, f, indent=4)

    return session_id


def load_session(session_id):
    session_file = (SESSIONS_DIR / f"{session_id}.json")

    if not session_file.exists():
        raise FileNotFoundError(f"session not found: {session_id}")

    
    with open(session_file) as f:
        return json.load(f)
    
    


def append_messages(session_id, role, content):
    session = load_session(session_id)
    
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    }
    
    session["messages"].append(message)
    session["updated_at"] = (datetime.now().isoformat())
    
    session_file = (SESSIONS_DIR / f"{session_id}.json")
    
    with open(session_file, "w") as f:
        json.dump(session, f, indent=4)
        
        
    return message


def list_session():
    session_files = list(SESSIONS_DIR.glob("*.json"))
    
    sessions = []
    
    for session_file in session_files:
        with open(session_file) as f:
            session = json.load(f)
        
        sessions.append(session)    
    
    sessions.sort(
        key=lambda x: x["updated_at"],
        reverse=True
    )
    
    return sessions


def get_messages(session_id):
    session = load_session(session_id)
    
    return session["messages"]


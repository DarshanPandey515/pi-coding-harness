from pathlib import Path
from tools.read import read_file

def edit_file(path, old_text, new_text):
    
    path = Path(path)
    content = path.read_text()
    
    if old_text not in content:
        return {
            "success": False,
            "error": "text not found"
        }
    
    updated = content.replace(
        old_text,
        new_text,
        1
    )
    
    path.write_text(updated)
    
    print(f"editing: {path}")
    
    return {
        "success": True,
        "path": str(path)
    }
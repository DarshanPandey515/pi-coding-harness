from pathlib import Path



def write_file(path, content):
    
    path = Path(path)
    
    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )
    
    
    path.write_text(content)
    
    
    return {
        "success": True,
        "path": str(path),
        "content_preview": content[:500]
    }
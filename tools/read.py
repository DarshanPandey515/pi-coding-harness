from pathlib import Path

MAX_CONTENT = 8000


def read_file(path):
    
    path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(path)
    
    print(f"reading file: {path}")
    content = path.read_text()
    if len(content) > MAX_CONTENT:
        content = content[:MAX_CONTENT] + f"\n... [truncated {len(content) - MAX_CONTENT} chars]"
    return content


def get_tree(root="."):
    
    lines = []
    
    for path in Path(root).rglob("*"):
        
        if ".git" in path.parts:
            continue
        
        if "__pycache__" in path.parts:
            continue
        
        if "env" in path.parts:
            continue
        
        lines.append(str(path))
        
        
    return "\n".join(lines)
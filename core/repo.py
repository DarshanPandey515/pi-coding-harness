from pathlib import Path


def get_project_tree(root="."):
    
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
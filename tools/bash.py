import subprocess

MAX_STDOUT = 4000
MAX_STDERR = 2000


def _truncate(text, limit):
    if not text:
        return text
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n... [truncated {len(text) - limit} chars]"


def run_command(command):
    
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=30
    )
    
    print(f"running: {command}")
    
    return {
        "stdout": _truncate(result.stdout, MAX_STDOUT),
        "stderr": _truncate(result.stderr, MAX_STDERR),
        "returncode": result.returncode
    }
    
from core.tools.read import read_file
from core.tools.write import write_file
from core.tools.bash import run_command

AVAILABLE_TOOLS = {
    "read": read_file,
    "bash": run_command,
    "write": write_file,
}
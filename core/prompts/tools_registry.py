from tools.read import read_file
from tools.write import write_file
from tools.bash import run_command
from tools.edit import edit_file

AVAILABLE_TOOLS = {
    "read": read_file,
    "bash": run_command,
    "write": write_file,
    "edit": edit_file,
}
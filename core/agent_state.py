from typing import List
from dataclasses import dataclass, field


@dataclass
class AgentState:
    files_read: List[str] = field(default_factory=list)
    files_written: List[str] = field(default_factory=list)
    commands_run: List[str] = field(default_factory=list)
    file_edited: List[str] = field(default_factory=list)
    tool_counts: dict = field(default_factory=dict)

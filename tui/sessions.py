from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header

from commands.sessions import list_session
from core.config import SESSIONS_DIR


class SessionsScreen(Screen):
    """Browse, resume, or delete saved sessions."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("d", "delete", "Delete"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(id="sessions")
        yield Footer()

    def on_mount(self) -> None:
        self._ids = []
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns("Updated", "Provider", "Model", "Msgs", "ID")
        self._load()

    def _load(self) -> None:
        table = self.query_one(DataTable)
        table.clear()
        self._ids = []
        for session in list_session():
            self._ids.append(session["id"])
            table.add_row(
                session.get("updated_at", "")[:19],
                session.get("provider", ""),
                session.get("model", ""),
                str(len(session.get("messages", []))),
                session["id"][:8],
            )

    def _selected_id(self) -> str:
        table = self.query_one(DataTable)
        if not self._ids:
            return ""
        return self._ids[table.cursor_row]

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        session_id = self._selected_id()
        if session_id:
            self.app.load_session(session_id)

    def action_delete(self) -> None:
        session_id = self._selected_id()
        if not session_id:
            return
        session_file = SESSIONS_DIR / f"{session_id}.json"
        if session_file.exists():
            session_file.unlink()
        self._load()

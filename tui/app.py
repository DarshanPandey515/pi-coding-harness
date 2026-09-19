from textual.app import App
from textual.binding import Binding

from tui.chat import ChatScreen
from tui.sessions import SessionsScreen
from tui.settings import SettingsScreen


class PiApp(App):
    """Textual interface for the pi coding harness."""

    CSS = """
    Screen {
        background: $surface;
    }
    #transcript {
        height: 1fr;
        padding: 0 1;
    }
    .user {
        border-left: thick $accent;
        padding: 0 1;
        margin: 1 0 0 0;
    }
    .assistant {
        padding: 0 1;
        margin-bottom: 1;
    }
    .activity {
        color: $text-muted;
        padding: 0 1;
    }
    .system {
        color: $warning;
        padding: 0 1;
        margin-top: 1;
    }
    #status {
        height: 1;
        background: $panel;
        color: $text-muted;
        padding: 0 1;
    }
    LoginModal {
        align: center middle;
    }
    #dialog {
        width: 60;
        height: auto;
        padding: 1 2;
        background: $panel;
        border: thick $accent;
    }
    .hint {
        color: $text-muted;
    }
    """

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+n", "new_session", "New"),
        Binding("ctrl+r", "sessions", "Sessions"),
        Binding("ctrl+s", "settings", "Settings"),
    ]

    def __init__(self, resume: str = None):
        super().__init__()
        self.resume = resume

    def on_mount(self) -> None:
        self.push_screen(ChatScreen(resume=self.resume))

    def load_session(self, session_id: str) -> None:
        self.switch_screen(ChatScreen(resume=session_id))

    def action_new_session(self) -> None:
        self.switch_screen(ChatScreen())

    def action_sessions(self) -> None:
        self.push_screen(SessionsScreen())

    def action_settings(self) -> None:
        self.push_screen(SettingsScreen())

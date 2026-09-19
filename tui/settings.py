from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    TabbedContent,
    TabPane,
)

from commands.providers import SUPPORTED_PROVIDERS
from core.config import load_config, save_config
from core.models import get_models

_PROVIDERS = list(SUPPORTED_PROVIDERS.keys())


class LoginModal(ModalScreen):
    """Prompt for a provider API key."""

    def __init__(self, provider: str):
        super().__init__()
        self.provider = provider

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(f"API key for {self.provider}")
            yield Input(password=True, id="key")
            yield Label("Enter to save · Esc to cancel", classes="hint")

    def on_mount(self) -> None:
        self.query_one("#key", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        key = event.value.strip()
        if key:
            config = load_config()
            config.setdefault("providers", {})
            config["providers"][self.provider] = {"api_key": key}
            save_config(config)
        self.dismiss(None)


class SettingsScreen(Screen):
    """Pick the default model and manage provider logins."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("l", "login", "Login"),
        Binding("o", "logout", "Logout"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent():
            with TabPane("Models", id="tab-models"):
                yield ListView(id="model-list")
            with TabPane("Providers", id="tab-providers"):
                yield ListView(id="provider-list")
        yield Footer()

    def on_mount(self) -> None:
        self._load_models()
        self._load_providers()

    def _load_models(self) -> None:
        view = self.query_one("#model-list", ListView)
        view.clear()
        selected = load_config().get("default_model")
        for model in get_models():
            full = f"{model['provider']}/{model['name']}"
            mark = "*" if full == selected else " "
            view.append(ListItem(Label(f"{mark} {full}")))

    def _load_providers(self) -> None:
        view = self.query_one("#provider-list", ListView)
        view.clear()
        logged_in = load_config().get("providers", {})
        for provider in _PROVIDERS:
            mark = "✓" if provider in logged_in else "✗"
            name = SUPPORTED_PROVIDERS[provider]["name"]
            view.append(ListItem(Label(f"{mark} {provider}  {name}")))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.id != "model-list":
            return
        model = get_models()[event.index]
        config = load_config()
        config["default_model"] = f"{model['provider']}/{model['name']}"
        save_config(config)
        self._load_models()

    def _provider_at_cursor(self) -> str:
        view = self.query_one("#provider-list", ListView)
        index = view.index if view.index is not None else 0
        return _PROVIDERS[index]

    def action_login(self) -> None:
        self.push_screen(LoginModal(self._provider_at_cursor()), lambda _: self._load_providers())

    def action_logout(self) -> None:
        provider = self._provider_at_cursor()
        config = load_config()
        providers = config.get("providers", {})
        if provider in providers:
            providers.pop(provider)
            save_config(config)
        self._load_providers()

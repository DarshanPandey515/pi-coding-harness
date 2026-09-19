import os
from dataclasses import asdict
from pathlib import Path

from textual import work
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Markdown, Static

from commands.sessions import (
    append_messages,
    create_session,
    get_messages,
    load_session,
    update_agent_state,
)
from core.agent_loop import run_agent_stream
from core.agent_state import AgentState
from core.config import get_default_model, get_provider_api_key
from core.events import get_handler, set_handler


class ChatScreen(Screen):
    """Agent chat with live tool activity and streamed responses."""

    def __init__(self, resume: str = None):
        super().__init__()
        self.resume = resume
        self.session_id = None
        self.provider = None
        self.model = None
        self.api_key = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield VerticalScroll(id="transcript")
        yield Static("", id="status")
        yield Input(placeholder="Ask the agent…  (Ctrl+Q quit · Ctrl+R sessions · Ctrl+S settings)", id="prompt")
        yield Footer()

    def on_mount(self) -> None:
        set_handler(self._on_activity)
        self._reload_config()
        self._start_session()
        self._refresh_status()
        self.query_one("#prompt", Input).focus()

    def on_unmount(self) -> None:
        if get_handler() == self._on_activity:
            set_handler(None)

    def on_screen_resume(self) -> None:
        self._reload_config()
        self._refresh_status()

    def _reload_config(self) -> None:
        model = get_default_model()
        if model and "/" in model:
            self.provider, self.model = model.split("/", 1)
            self.api_key = get_provider_api_key(self.provider)

    def _start_session(self) -> None:
        if not self.api_key:
            self._add_system("No model/provider configured. Press Ctrl+S to set one up.")
            return

        if self.resume:
            try:
                session = load_session(self.resume)
            except FileNotFoundError:
                self._add_system(f"Session not found: {self.resume}")
                return
            self.session_id = self.resume
            self._add_system(f"Resumed session {self.session_id[:8]}")
            for msg in session.get("messages", []):
                self._render_message(msg["role"], msg["content"])
        else:
            self.session_id = create_session(self.provider, self.model)
            self._add_system(f"New session {self.session_id[:8]}")

    def _refresh_status(self) -> None:
        if self.provider and self.model and self.session_id:
            text = f"{self.provider}/{self.model}  ·  session {self.session_id[:8]}"
        else:
            text = "no model configured — Ctrl+S"
        self.query_one("#status", Static).update(text)

    def _mount(self, widget) -> None:
        self.query_one("#transcript", VerticalScroll).mount(widget)

    def _add_system(self, text: str) -> None:
        self._mount(Static(text, classes="system"))

    def _on_activity(self, message: str) -> None:
        self._mount(Static(message, classes="activity"))

    def _render_message(self, role: str, content: str) -> None:
        if role == "user":
            self._mount(Markdown(f"**You**\n\n{content}", classes="user"))
        elif role == "assistant":
            self._mount(Markdown(content, classes="assistant"))

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if not text:
            return
        event.input.clear()

        if text.lower() in ("exit", "quit"):
            self.app.exit()
            return

        if not self.api_key:
            self._add_system("No provider configured. Press Ctrl+S to add a key.")
            return

        self._render_message("user", text)
        event.input.disabled = True
        self._run_turn(text)

    @work(exclusive=True)
    async def _run_turn(self, user_input: str) -> None:
        home = str(Path.home())
        full_prompt = f"""Current working directory (a project folder, not the desktop): {os.getcwd()}
User home directory: {home}

User Request:
{user_input}
"""

        append_messages(self.session_id, "user", user_input)
        history = get_messages(self.session_id)
        raw_state = load_session(self.session_id).get("agent_state") or {}
        state = AgentState(**raw_state)

        answer = Markdown("", classes="assistant")
        self._mount(answer)

        text = ""
        try:
            async for event in run_agent_stream(
                self.provider, self.model, self.api_key, full_prompt, history, state
            ):
                if event["type"] == "text_delta":
                    text += event["text"]
                    await answer.update(text)
                elif event["type"] == "done":
                    text = event["text"]
                    await answer.update(text)
                elif event["type"] == "error":
                    await answer.update(f"**Error:** {event['message']}")
        finally:
            if text:
                append_messages(self.session_id, "assistant", text)
            update_agent_state(self.session_id, asdict(state))
            prompt = self.query_one("#prompt", Input)
            prompt.disabled = False
            prompt.focus()

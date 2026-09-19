"""Smoke test for the Textual TUI. Run: python tests/tui_smoke.py

Boots the app with an isolated HOME, stubs the model stream, submits prompts,
switches screens, and asserts activity plus persistence.
"""

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ["HOME"] = tempfile.mkdtemp(prefix="pi-tui-smoke-")

from core.config import CONFIG_DIR, CONFIG_FILE  # noqa: E402

CONFIG_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_FILE.write_text(
    json.dumps(
        {
            "default_model": "groq/test-model",
            "providers": {"groq": {"api_key": "test-key"}},
        }
    )
)

import tui.chat as chat  # noqa: E402
from commands.sessions import list_session  # noqa: E402
from core.events import emit  # noqa: E402


async def fake_stream(provider, model, api_key, prompt, history=None, agent_state=None):
    emit("→ running: echo hi")
    for token in ["Hel", "lo ", "world"]:
        yield {"type": "text_delta", "text": token}
    yield {"type": "done", "text": "Hello world"}


chat.run_agent_stream = fake_stream

activity = []
_orig_set_handler = chat.set_handler


def spy_set_handler(handler):
    if handler is None:
        _orig_set_handler(None)
        return

    def wrapped(message):
        activity.append(message)
        handler(message)

    _orig_set_handler(wrapped)


chat.set_handler = spy_set_handler

from textual.widgets import Input  # noqa: E402

from tui.app import PiApp  # noqa: E402
from tui.chat import ChatScreen  # noqa: E402
from tui.sessions import SessionsScreen  # noqa: E402


async def send(pilot, text):
    prompt = pilot.app.screen.query_one("#prompt", Input)
    prompt.value = text
    await pilot.press("enter")
    for _ in range(50):
        await pilot.pause(0.1)
        if not prompt.disabled:
            break
    assert not prompt.disabled, "worker never finished"


async def main():
    app = PiApp()
    async with app.run_test() as pilot:
        assert isinstance(app.screen, ChatScreen)
        await send(pilot, "hi there")
        assert "→ running: echo hi" in activity, activity

        # New session via app binding.
        await pilot.press("ctrl+n")
        await pilot.pause(0.1)
        assert isinstance(app.screen, ChatScreen)
        await send(pilot, "second turn")

        # Sessions browser round-trip.
        await pilot.press("ctrl+r")
        await pilot.pause(0.1)
        assert isinstance(app.screen, SessionsScreen)
        await pilot.press("escape")
        await pilot.pause(0.1)
        assert isinstance(app.screen, ChatScreen)

    sessions = list_session()
    assert len(sessions) >= 2, f"expected 2 sessions, got {len(sessions)}"
    all_text = {m["content"] for s in sessions for m in s["messages"]}
    assert "hi there" in all_text and "second turn" in all_text, all_text
    assert "Hello world" in all_text, all_text
    print("SMOKE OK")


asyncio.run(main())

# Pi Coding Harness

A sophisticated coding agent harness designed to manage and orchestrate interactions with various AI models for automated software development tasks.

---

## Features

- **Extensible Tool System:** Easily add new tools for the agent to use (e.g., `read`, `write`, `edit`, `bash`, `tree`).
- **Multi-Provider Support:** Designed to work with different AI model providers (e.g., Google Gemini).
- **Agent Loop:** A core loop that allows the agent to iteratively think and act to solve complex tasks.
- **Session Management:** Keep track of conversation history. You can list, show, and delete sessions.
- **Chat Interface:** A simple, interactive chat mode for direct conversations with the AI.
- **Configuration Management:** Simple configuration through a `.env` file.
- **Command-Line Interface:** Interact with and direct the agent through a simple command-line interface.

## Quantifiable Metrics

- **Tools:** 4 core tools (`read`, `bash`, `write`, `edit`) with explicit limits: `read` caps content at 8 KB and appends a truncation notice; `bash` limits stdout to 4 KB, stderr to 2 KB, and enforces a 30 s timeout; `edit` rejects edits when the search text is not found; `write` returns `success`/failure with a 500‑character preview.
- **LLM Providers:** 2 supported providers – Google Gemini and Groq – configurable via a `.env` file without code changes (`core/models.py:5‑11`, `core/agent_loop.py:67‑71`).
- **Session Persistence:** JSON sessions stored under `~/.pi-agent/sessions/{id}.json`, each recording `id, created_at, updated_at, provider, model, messages, agent_state` (file reads/written, commands run, edits). Enables exact replay and resume (`sessions.py:8‑33`).
- **CLI:** 7 top‑level commands (`providers`, `models`, `agent`, `chat`, `sessions`, `delete`, `agent_chat`) with 10 distinct sub‑commands covering provider login/logout, model selection, session management, and agent invocation (`main.py:10‑23`).
- **Agent‑Loop Metrics:** Tool‑call counts and file‑operation logs are tracked in `AgentState`; no hard iteration limit is currently enforced, and tenacity is a dependency but not yet wired for retries.
- **Safety Caps:** Read buffer (8 KB), command timeout (30 s), stdout/stderr caps (4 KB/2 KB) prevent runaway resource use.

## Project Structure

The project is organized into several key directories:

```
.
├── README.md
├── commands/         # Command-line interface definitions
├── core/             # Core logic for the agent, model providers, and prompts
├── data/             # Data files (e.g., model definitions)
├── tools/            # Agent tool implementations (bash, edit, etc.)
├── .env              # Environment variables for configuration
├── .gitignore        # Git ignore file
├── main.py           # Main entry point for the application
├── requirements.txt  # Project dependencies
└── test.py           # Test scripts
```

## Getting Started

Follow these instructions to get the project up and running on your local machine.

### Prerequisites

- Python 3.9+
- Pip for package management

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd pi-coding-harness
    ```

2.  **Install dependencies (assuming a `requirements.txt` file):
    ```bash
    pip install -r requirements.txt
    ```

## Usage

```bash
python main.py --help
```

```
Usage: main.py [OPTIONS] COMMAND [ARGS]...

  PI Coding Agent

Options:
  --help  Show this message and exit.

Commands:
  agent      use 'python main.py agent --prompt /your task/'
  chat       start your pi coding agent chat and sessions
  delete     delete you session with --id {session id}
  models     Available models
  providers  Manage providers, login & logout
  sessions   your sessions history
```

To run the agent, use the following command:

```bash
python main.py agent -p "Your task for the agent goes here"
```

The agent will then start its think-act loop to complete the task.

To start a new chat session, use the `chat` command:

```bash
python main.py chat
```

For managing sessions, you can use the following commands:

```bash
# List all sessions
python main.py sessions list

# Show a specific session
python main.py sessions show <session_id>

# Delete a specific session
python main.py sessions delete <session_id>
```

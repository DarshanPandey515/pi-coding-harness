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

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any bugs or feature requests.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

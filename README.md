# Pi Coding Harness

A sophisticated coding agent harness designed to manage and orchestrate interactions with various AI models for automated software development tasks.

---

## Features

- **Extensible Tool System:** Easily add new tools for the agent to use (e.g., `read`, `write`, `edit`, `bash`).
- **Multi-Provider Support:** Designed to work with different AI model providers (e.g., Google Gemini).
- **Agent Loop:** A core loop that allows the agent to iteratively think and act to solve complex tasks.
- **Configuration Management:** Simple configuration through a `.env` file.
- **Command-Line Interface:** Interact with and direct the agent through a simple command-line interface.

## Project Structure

The project is organized into several key directories:

```
.
├── commands/         # Command-line interface definitions
├── core/             # Core logic for the agent, tools, and model interaction
│   └── tools/        # Individual tool implementations
├── data/             # Data files, like model definitions
├── .env              # Environment variables for configuration (API keys, etc.)
├── main.py           # Main entry point for the application
└── README.md         # This file
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

### Configuration

1.  Create a `.env` file in the root of the project by copying the example file (if one exists) or creating it from scratch.
    ```bash
    cp .env.example .env
    ```

2.  Add your API keys and any other necessary configuration variables to the `.env` file.
    ```
    API_KEY=your_api_key_here
    ```

## Usage

To run the agent, use the main entry point:

```bash
python main.py agent -p "Your task for the agent goes here"
```

The agent will then start its think-act loop to complete the task.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any bugs or feature requests.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

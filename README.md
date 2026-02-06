# Todo CLI Application

A Python-based command-line interface (CLI) application for managing todo tasks. This application is built using Python 3.12+ and the Rich library for elegant terminal output.

## Features

- Add new tasks with titles
- List all tasks with their status (pending/completed)
- Mark tasks as complete
- Delete tasks
- Rich-formatted terminal interface
- In-memory storage (Phase 1)

## Prerequisites

- Python 3.12 or higher
- pip package manager

## Installation

1. Clone or download this repository
2. Navigate to the project directory
3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the application:

```bash
python -m src.cli.main
```

Follow the on-screen menu options to manage your tasks:
1. Add Task - Create a new task with a title
2. List Tasks - View all tasks with their status
3. Complete Task - Mark a task as completed
4. Delete Task - Remove a task from the list
5. Exit - Close the application

## Project Structure

```
src/
├── models/
│   └── task.py          # Task data model
├── services/
│   └── todo_manager.py  # Business logic layer
└── cli/
    └── main.py          # CLI interface
tests/
├── unit/
│   ├── test_task.py          # Unit tests for Task
│   └── test_todo_manager.py  # Unit tests for TodoManager
└── integration/
    └── test_cli.py           # Integration tests for CLI
```

## Testing

Run the unit tests:

```bash
pytest tests/unit/
```

Run the integration tests:

```bash
pytest tests/integration/
```

Run all tests:

```bash
pytest
```

## Architecture

- **Task Model**: Represents individual tasks with ID, title, and status
- **Todo Manager**: Handles all business logic for task management
- **CLI Interface**: Provides user interaction layer with Rich formatting
- **In-Memory Storage**: All data is stored in memory for Phase 1 (no persistence)

## Development

This project follows the following principles:

- Type hints throughout the codebase
- Comprehensive unit and integration tests
- Clean separation of concerns
- Rich-formatted terminal output for better UX
- Follows PEP 8 style guidelines

## License

[Specify license here]
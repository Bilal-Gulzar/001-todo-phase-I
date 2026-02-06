# Quickstart Guide: Todo CLI Application

## Prerequisites
- Python 3.12 or higher
- pip package manager

## Setup Instructions

### 1. Clone or Access the Project
```bash
# Navigate to your project directory
cd your-project-directory
```

### 2. Install Dependencies
```bash
pip install rich pytest
```

### 3. Project Structure Overview
```
src/
├── models/
│   └── task.py          # Task class definition
├── services/
│   └── todo_manager.py  # TodoManager class with business logic
└── cli/
    └── main.py          # Main CLI application entry point

tests/
├── unit/
│   ├── test_task.py     # Unit tests for Task class
│   └── test_todo_manager.py  # Unit tests for TodoManager class
└── integration/
    └── test_cli.py      # Integration tests for CLI functionality
```

## Running the Application

### Direct Execution
```bash
cd src/cli
python main.py
```

### From Project Root
```bash
python -m src.cli.main
```

## Key Features

### Task Class (`src/models/task.py`)
- Represents individual todo items
- Has id, title, and status attributes
- Automatically generates unique IDs
- Defaults to "pending" status

### TodoManager Class (`src/services/todo_manager.py`)
- Manages collection of tasks in memory
- Handles add, list, complete, and delete operations
- Validates operations before execution
- Maintains data integrity

### CLI Interface (`src/cli/main.py`)
- Interactive menu-driven interface
- Displays tasks in formatted tables using Rich
- Prompts for user input with clear options
- Handles errors gracefully with user-friendly messages

## Available Commands
1. Add a new task - Creates a task with a specified title
2. List all tasks - Shows all tasks in a table format
3. Mark task as complete - Updates status of a specific task
4. Delete a task - Removes a specific task from the list
5. Exit - Quits the application

## Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_task.py

# Run with verbose output
pytest -v
```

## Development Notes
- All code follows PEP 8 style guidelines
- Type hints are used throughout the codebase
- Rich library provides all terminal styling
- Data remains in memory only (no persistence)
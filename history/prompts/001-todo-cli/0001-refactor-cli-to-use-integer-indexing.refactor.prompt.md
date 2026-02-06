---
id: 0001
title: Refactor CLI to use integer indexing
stage: refactor
date: 2026-02-06
surface: agent
model: claude-opus-4-6
feature: 001-todo-cli
branch: 001-todo-cli
user: unknown
command: /sp.phr
labels: ["cli", "refactoring", "ui", "user-experience", "todo-app"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - D:\Code\ai_native_development\todo-phase-1\src\cli\main.py
 - D:\Code\ai_native_development\todo-phase-1\tests\integration\test_cli.py
 - D:\Code\ai_native_development\todo-phase-1\demonstration.py
tests:
 - D:\Code\ai_native_development\todo-phase-1\tests\integration\test_cli.py
 - D:\Code\ai_native_development\todo-phase-1\tests\unit\test_todo_manager.py
---

## Prompt

The CLI is currently showing long UUIDs (like 4219e6f0...) in the table. This makes it impossible to mark tasks as done or delete them easily. Please refactor the CLI and Manager to use simple integer indexing for user input: In src/cli/main.py, display a simple counter (1, 2, 3...) in the table instead of the UUID.

Create a mapping in the CLI so that when I type '1', it knows to use the corresponding UUID 4219e6f0... in the backend.

Update the 'Mark Done' and 'Delete' functions to accept these simple numbers.

After fixing, run the tests to make sure I haven't broken the core logic.

## Response snapshot

Refactored the CLI to use simple integer indexing instead of UUIDs for user interaction, updating the list_tasks, complete_task, and delete_task methods to map integers to UUIDs internally. Updated related tests to match new behavior.

## Outcome

- ✅ Impact: Improved user experience by allowing simple integer input instead of long UUIDs for task management
- 🧪 Tests: All 30 tests pass, including updated integration tests for CLI functionality
- 📁 Files: Modified src/cli/main.py and tests/integration/test_cli.py to implement integer indexing
- 🔁 Next prompts: None needed - implementation complete and tested
- 🧠 Reflection: Mapping between simple UI indices and internal UUIDs improves usability without changing backend logic

## Evaluation notes (flywheel)

- Failure modes observed: None - all tests pass and functionality verified
- Graders run and results (PASS/FAIL): PASS - All 30 tests pass successfully
- Prompt variant (if applicable): None
- Next experiment (smallest change to try): None needed

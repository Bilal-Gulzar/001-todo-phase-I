---
id: 6
title: "Fix Imports for PYTHONPATH Mode"
stage: impl
date: "2026-02-06"
surface: "agent"
model: "claude-opus-4-6"
feature: "001-todo-cli"
branch: "001-todo-cli"
user: "BILAL_GUL"
command: "manual"
labels:
  - "imports"
  - "pythonpath"
  - "refactoring"
  - "todo-cli"
files_yaml:
  - "src/cli/main.py"
  - "tests/unit/test_task.py"
  - "tests/unit/test_todo_manager.py"
  - "tests/integration/test_cli.py"
tests_yaml:
  - "tests/unit/test_task.py"
  - "tests/unit/test_todo_manager.py"
  - "tests/integration/test_cli.py"
links:
  spec: null
  ticket: null
  adr: null
  pr: null
---

# Fix Imports for PYTHONPATH Mode

## Prompt Text

```
I'm getting an ImportError: attempted relative import with no known parent package. Please rewrite the imports in all files to use absolute imports starting from the root of the src directory. For example, change from ..services.todo_manager import TodoManager to from services.todo_manager import TodoManager. This will allow me to run the app with PYTHONPATH=src.
```

## Response Summary

Updated all imports in the Todo CLI application to work with PYTHONPATH=src mode. Changed relative imports to absolute imports and added sys.path manipulation in test files to ensure proper imports during testing.

## Outcome & Impact

Fixed ImportError by updating all imports to work with PYTHONPATH=src. The application can now be run with PYTHONPATH=src as required, and all tests continue to pass.

## Files Modified

- src/cli/main.py - Updated relative imports to absolute imports
- tests/unit/test_task.py - Added sys.path manipulation for proper imports
- tests/unit/test_todo_manager.py - Added sys.path manipulation for proper imports
- tests/integration/test_cli.py - Added sys.path manipulation for proper imports

## Tests Summary

- All 30 tests continue to pass
- Import fix verified to work with PYTHONPATH=src

## Next Steps

- Application can now be run with PYTHONPATH=src
- Ready for deployment or further development

## Reflection

Proper import handling is crucial for applications that need to run in different contexts. The sys.path manipulation in tests ensures they can find modules regardless of execution context.

## Evaluation Notes

**Failure modes observed:** None

**Next experiment to improve prompt quality:** N/A
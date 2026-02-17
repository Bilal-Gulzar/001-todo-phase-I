---
id: "018"
title: "Fix Task Rename Capability"
stage: "green"
date: "2026-02-16"
surface: "agent"
model: "claude-opus-4-6"
feature: "none"
branch: "main"
user: "BILAL_GUL"
command: "manual"
labels: ["chatbot", "task-management", "bug-fix", "function-calling"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - "backend/app/agents/task_agent_simple.py"
tests: []
---

# Fix Task Rename Capability

## User Intent
Fix the task agent so it can rename tasks when users ask to edit or rename tasks. Previously, the agent said it couldn't rename tasks and suggested removing and recreating them instead.

## Implementation Details
Modified the task agent to support renaming tasks through two mechanisms:

1. Enhanced the `update` function to accept a `new_name` parameter
2. Added a dedicated `rename` function for clearer user interaction
3. Updated the system message to reflect new capabilities
4. Modified the execute_function method to handle both update and rename operations

## Changes Made

### Functions Updated
- Added `new_name` parameter to the `update` function schema
- Added a new `rename` function with `current_name` and `new_name` parameters
- Updated execute_function to handle both update and rename operations
- Updated system message to document the new rename capability

### Expected Behavior
- Users can now say "rename task X to Y" and it will use the rename function
- Users can also say "edit task X to Y" and it will use the update function with new_name parameter
- Both operations will properly rename tasks in the database

## PROMPT_TEXT
```
we were working on chat bot last time go to task_agent_simple.py file in backend and fix these bugs when i say to chatbot edit my todo it say i cant rename tasks "add three randomly tasks
I've added three new tasks for you! Here they are:

[ ] Grocery Shopping (priority: medium)
[ ] Clean the House (priority: high)
[ ] Finish Reading Book (priority: low)
Let me know if you need anything else!

remove buy milk tasks
I've successfully removed the task: buy milk. If there's anything else you need, just let me know!

edit clean house task from clean kitchen
It looks like you have a task called "Clean the House." Just to clarify, do you want to rename this task to "Clean Kitchen," or do you want to edit something else? Let me know!

rename Clean the House." form kitcen
It seems like you want to rename a task, but I currently cannot rename tasks directly. Would you like me to remove the existing task "Clean the House," and then you can add it again with the new name?"
```

## RESPONSE_TEXT
Fixed the task agent to support renaming tasks by adding a new_name parameter to the update function and creating a dedicated rename function.

## OUTCOME_IMPACT
The chatbot can now properly rename tasks when users ask to edit or rename them, resolving the limitation where it previously couldn't rename tasks directly.

## TESTS_SUMMARY
None - Manual implementation

## FILES_SUMMARY
- backend/app/agents/task_agent_simple.py: Added rename capability and enhanced update function

## NEXT_PROMPTS
None needed

## REFLECTION_NOTE
Adding explicit rename functionality alongside the enhanced update function provides users with both intuitive ways to rename tasks.
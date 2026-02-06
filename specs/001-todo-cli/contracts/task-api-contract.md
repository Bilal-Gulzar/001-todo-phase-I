# Task API Contract

## Purpose
Defines the interface and behavior for the Task entity in the Todo CLI application.

## Task Class Interface

### Properties
- `id`: integer (read-only) - Unique identifier for the task
- `title`: string (read-only) - Description of the task
- `status`: string (read/write) - Current status ("pending" or "complete")

### Constructor
```python
Task(title: str, id: int = None)
```
- `title` (required): The task description
- `id` (optional): Unique identifier; auto-generated if not provided
- Raises: ValueError if title is empty or None

## TodoManager Class Interface

### Methods

#### `add_task(title: str) -> int`
- **Description**: Creates a new task with the given title
- **Parameters**:
  - `title`: string - The task description
- **Returns**: int - The ID of the newly created task
- **Side effects**: Adds task to internal collection
- **Raises**: ValueError if title is empty
- **Post-condition**: New task exists with status "pending"

#### `list_tasks() -> List[Task]`
- **Description**: Retrieves all tasks
- **Parameters**: None
- **Returns**: List of Task objects in arbitrary order
- **Side effects**: None
- **Post-condition**: Returns complete list of current tasks

#### `get_task(task_id: int) -> Task`
- **Description**: Retrieves a specific task by ID
- **Parameters**:
  - `task_id`: integer - The unique identifier of the task
- **Returns**: Task object
- **Raises**: KeyError if task_id does not exist
- **Side effects**: None

#### `complete_task(task_id: int) -> bool`
- **Description**: Marks a task as complete
- **Parameters**:
  - `task_id`: integer - The unique identifier of the task
- **Returns**: bool - True if successful, False if task doesn't exist
- **Side effects**: Modifies the status of the specified task
- **Post-condition**: Task status is "complete"

#### `delete_task(task_id: int) -> bool`
- **Description**: Removes a task from the collection
- **Parameters**:
  - `task_id`: integer - The unique identifier of the task
- **Returns**: bool - True if successful, False if task doesn't exist
- **Side effects**: Removes task from internal collection
- **Post-condition**: Task no longer exists in the collection

#### `toggle_task_status(task_id: int) -> bool`
- **Description**: Toggles a task between "pending" and "complete" states
- **Parameters**:
  - `task_id`: integer - The unique identifier of the task
- **Returns**: bool - True if successful, False if task doesn't exist
- **Side effects**: Modifies the status of the specified task
- **Post-condition**: Task status is opposite of previous status

## CLI Interface Contract

### Menu Options
1. "Add a new task" - Prompts for task title and adds to list
2. "List all tasks" - Displays tasks in a formatted table
3. "Mark task as complete" - Prompts for task ID and updates status
4. "Delete a task" - Prompts for task ID and removes from list
5. "Exit" - Terminates the application

### Error Handling
- Invalid inputs should be caught and handled gracefully
- Clear error messages should be displayed to the user
- Invalid task IDs should be handled without crashing
- Empty task lists should be handled appropriately
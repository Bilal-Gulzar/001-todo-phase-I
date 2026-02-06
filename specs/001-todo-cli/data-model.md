# Data Model: Todo CLI Application

## Task Entity

### Attributes
- **id**: Integer or UUID - Unique identifier for the task (auto-generated)
- **title**: String - The descriptive text of the task (required, non-empty)
- **status**: String - Current state of the task (values: "pending", "complete"; default: "pending")

### Relationships
- Part of a Task List collection managed by TodoManager

### Validation Rules
- Title must not be empty or None
- ID must be unique within the system
- Status must be one of the allowed values ("pending", "complete")
- ID must be immutable after creation

### State Transitions
- Initial state: "pending" (when task is created)
- Transition: "pending" → "complete" (when task is marked complete)
- Transition: "complete" → "pending" (when task is marked as incomplete again)

## Task List

### Attributes
- **tasks**: List of Task objects - Collection of all tasks in the system

### Relationships
- Contains multiple Task entities
- Managed by TodoManager class

### Validation Rules
- No duplicate tasks based on ID
- Maintains uniqueness of task IDs

## Task Operations

### Business Rules
1. A task can be created with a title and automatically receives an ID and "pending" status
2. A task's status can be toggled between "pending" and "complete"
3. A task can be deleted from the list
4. All tasks can be retrieved in a list format
5. Individual tasks can be retrieved by ID

### Constraints
- No two tasks may have the same ID
- A task ID must exist before it can be operated on (updated, deleted)
- Title length must be between 1 and 500 characters
- Status changes must be validated against allowed values

### Error Conditions
- Attempting to operate on a non-existent task ID should raise an appropriate error
- Attempting to create a task with an empty title should raise an appropriate error
- Attempting to set an invalid status should raise an appropriate error
# Data Model: Task Entity

## Task Model Definition

### Fields
- **id** (UUID, Primary Key)
  - Type: `str` (formatted as UUID)
  - Required: Yes
  - Unique: Yes
  - Default: Generated using uuid4()
  - Description: Unique identifier for each task

- **title** (String)
  - Type: `str`
  - Required: Yes
  - Min Length: 1 character
  - Max Length: 100 characters
  - Description: Title of the task

- **description** (String)
  - Type: `str`
  - Required: No (optional)
  - Max Length: 500 characters
  - Default: None
  - Description: Optional description of the task

- **is_completed** (Boolean)
  - Type: `bool`
  - Required: Yes
  - Default: False
  - Description: Status indicating if the task is completed

- **created_at** (DateTime)
  - Type: `datetime`
  - Required: Yes
  - Default: Current timestamp
  - Description: Timestamp when the task was created

### SQLModel Implementation
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid

class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    is_completed: bool = Field(default=False)

class Task(TaskBase, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
```

### Relationships
None for the Task model in Phase 2. Future phases may introduce user relationships.

### Validation Rules
- Title must be between 1-100 characters
- Description must be 500 characters or less
- is_completed defaults to False on creation
- created_at is auto-populated on record creation
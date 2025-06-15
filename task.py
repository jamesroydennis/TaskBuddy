import uuid
from enum import Enum

# 1. Define the Task Status Enum
class TaskStatus(Enum):
    PENDING = "pending"
    COMPLETE = "complete"
    OVERDUE = "overdue"

    def __str__(self):
        return self.value # Allows printing the enum value directly

# 2. Define the Task Class
class Task:
    def __init__(self, title: str, status: TaskStatus = TaskStatus.PENDING, task_id: uuid.UUID = None):
        if not title:
            raise ValueError("Task title cannot be empty.")
        if not isinstance(status, TaskStatus):
            raise TypeError("Status must be an instance of TaskStatus Enum.")

        self.id = task_id if task_id else uuid.uuid4() # Generate new UUID if not provided
        self.title = title
        self.status = status

    def __repr__(self):
        return f"Task(id='{self.id}', title='{self.title}', status={self.status})"

    def __eq__(self, other):
        """Allows comparison of Task objects based on their ID."""
        if not isinstance(other, Task):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        """Allows Task objects to be used in sets/dictionaries based on ID."""
        return hash(self.id)

    # Example of a simple method adhering to SRP for the Task object itself
    def mark_complete(self):
        """Marks the task as complete."""
        self.status = TaskStatus.COMPLETE

    def mark_pending(self):
        """Marks the task as pending."""
        self.status = TaskStatus.PENDING

    def mark_overdue(self):
        """Marks the task as overdue. (Typically set by a system, not user directly)"""
        self.status = TaskStatus.OVERDUE
#!/usr/bin/env python3
"""
Demonstration script showing the improvement to the CLI.
This shows how the CLI now uses simple integer indexing instead of long UUIDs.
"""

from src.cli.main import TodoCLI

def demo_new_behavior():
    print("=== Todo CLI - Integer Indexing Demo ===\n")

    # Create CLI instance
    cli = TodoCLI()

    # Add some sample tasks
    cli.manager.add_task("Buy groceries")
    cli.manager.add_task("Finish report")
    cli.manager.add_task("Call mom")
    cli.manager.add_task("Schedule meeting")

    print("1. Listing tasks (now shows simple numbers instead of UUIDs):")
    cli.list_tasks()

    print("\n2. The user can now simply type '2' to complete the second task")
    print("   (previously they had to type the full UUID like 'a1b2c3d4-...')")

    # Simulate completing task #2
    tasks = cli.manager.list_tasks()
    if len(tasks) >= 2:
        task_to_complete = tasks[1]  # Second task (0-indexed)
        cli.manager.complete_task(task_to_complete.id)

    print("\n3. After completing task #2:")
    cli.list_tasks()

    print("\n4. The user can now simply type '1' to delete the first task")
    print("   (previously they had to type the full UUID)")

    # Simulate deleting task #1 (which is now the second task in original list)
    tasks = cli.manager.list_tasks()
    if len(tasks) >= 1:
        task_to_delete = tasks[0]  # First task
        cli.manager.delete_task(task_to_delete.id)

    print("\n5. After deleting task #1:")
    cli.list_tasks()

    print("\n✅ Success! The CLI now uses simple integer indexing for user interaction.")
    print("   This makes it much easier for users to interact with their tasks.")

if __name__ == "__main__":
    demo_new_behavior()
import sys
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text

from src.services.todo_manager import TodoManager
from src.models.task import Task


class TodoCLI:
    """
    Command-Line Interface for the Todo application.

    This class manages the user interaction layer of the application,
    providing a menu-driven interface with rich formatting and user feedback.
    """

    def __init__(self) -> None:
        """Initialize the CLI with a TodoManager instance."""
        self.manager = TodoManager()
        self.console = Console()

    def display_menu(self) -> None:
        """Display the main menu options."""
        self.console.print(Panel("[bold blue]Todo CLI Application[/bold blue]", expand=False))
        self.console.print("\n[bright_yellow]Menu:[/bright_yellow]")
        self.console.print("1. Add Task")
        self.console.print("2. List Tasks")
        self.console.print("3. Complete Task")
        self.console.print("4. Delete Task")
        self.console.print("5. Exit")
        self.console.print("\n[cyan]Choose an option (1-5):[/cyan]", end="")

    def get_user_choice(self) -> str:
        """
        Get and validate user menu choice.

        Returns:
            The validated user choice
        """
        try:
            choice = Prompt.ask("Enter your choice")
            if choice in ['1', '2', '3', '4', '5']:
                return choice
            else:
                self.console.print("[red]Invalid option! Please enter a number between 1-5.[/red]")
                return self.get_user_choice()
        except KeyboardInterrupt:
            self.console.print("\n[red]Exiting...[/red]")
            sys.exit(0)

    def add_task(self) -> None:
        """Handle adding a new task."""
        try:
            title = Prompt.ask("Enter task title")
            if not title.strip():
                self.console.print("[red]Task title cannot be empty![/red]")
                return

            task = self.manager.add_task(title)
            self.console.print(f"[green]Task '{task.title}' added successfully![/green]")
        except ValueError as e:
            self.console.print(f"[red]Error: {str(e)}[/red]")
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Operation cancelled.[/yellow]")

    def list_tasks(self) -> None:
        """Display all tasks in a formatted table."""
        tasks = self.manager.list_tasks()

        if not tasks:
            self.console.print("[yellow]No tasks found![/yellow]")
            return

        table = Table(title="Todo List")
        table.add_column("#", justify="right", style="cyan", no_wrap=True)
        table.add_column("Title", style="green")
        table.add_column("Status", justify="center")

        for i, task in enumerate(tasks, start=1):
            status = "[green]✓ Completed[/green]" if task.is_completed else "[yellow]○ Pending[/yellow]"
            table.add_row(str(i), task.title, status)

        self.console.print(table)

    def complete_task(self) -> None:
        """Handle marking a task as complete."""
        tasks = self.manager.list_tasks()

        if not tasks:
            self.console.print("[yellow]No tasks available to complete![/yellow]")
            return

        self.list_tasks()  # Show tasks to help user choose
        try:
            task_index_str = Prompt.ask("Enter the number of the task to complete")

            # Convert the input to an integer and validate it
            try:
                task_index = int(task_index_str)
            except ValueError:
                self.console.print("[red]Invalid input! Please enter a valid number.[/red]")
                return

            # Check if the index is within valid range
            if task_index < 1 or task_index > len(tasks):
                self.console.print("[red]Task number out of range![/red]")
                return

            # Get the task using the index (convert to 0-based index)
            task = tasks[task_index - 1]
            task_id = task.id

            if self.manager.complete_task(task_id):
                self.console.print(f"[green]Task '{task.title}' marked as completed![/green]")
            else:
                self.console.print("[red]Failed to complete task![/red]")
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Operation cancelled.[/yellow]")

    def delete_task(self) -> None:
        """Handle deleting a task."""
        tasks = self.manager.list_tasks()

        if not tasks:
            self.console.print("[yellow]No tasks available to delete![/yellow]")
            return

        self.list_tasks()  # Show tasks to help user choose
        try:
            task_index_str = Prompt.ask("Enter the number of the task to delete")

            # Convert the input to an integer and validate it
            try:
                task_index = int(task_index_str)
            except ValueError:
                self.console.print("[red]Invalid input! Please enter a valid number.[/red]")
                return

            # Check if the index is within valid range
            if task_index < 1 or task_index > len(tasks):
                self.console.print("[red]Task number out of range![/red]")
                return

            # Get the task using the index (convert to 0-based index)
            task = tasks[task_index - 1]
            task_id = task.id

            if self.manager.delete_task(task_id):
                self.console.print(f"[green]Task '{task.title}' deleted successfully![/green]")
            else:
                self.console.print("[red]Failed to delete task![/red]")
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Operation cancelled.[/yellow]")

    def run(self) -> None:
        """Run the main application loop."""
        self.console.print(Panel(Text("Welcome to Todo CLI!", justify="center"), subtitle="(Phase 1: In-Memory Storage)"))

        while True:
            self.display_menu()
            choice = self.get_user_choice()

            if choice == '1':
                self.add_task()
            elif choice == '2':
                self.list_tasks()
            elif choice == '3':
                self.complete_task()
            elif choice == '4':
                self.delete_task()
            elif choice == '5':
                self.console.print("[blue]Thank you for using Todo CLI. Goodbye![/blue]")
                break

            # Pause before showing menu again
            if choice != '5':
                self.console.input("\nPress [bold]ENTER[/bold] to continue...")


def main() -> None:
    """Entry point for the application."""
    cli = TodoCLI()
    cli.run()


if __name__ == "__main__":
    main()
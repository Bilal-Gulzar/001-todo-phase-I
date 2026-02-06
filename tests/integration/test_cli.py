import pytest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.cli.main import TodoCLI
from src.services.todo_manager import TodoManager


class TestTodoCLI:
    """Integration tests for the TodoCLI class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.cli = TodoCLI()

    def test_initialization_creates_todo_manager_and_console(self):
        """Test that TodoCLI initializes with TodoManager and Console instances."""
        assert isinstance(self.cli.manager, TodoManager)
        assert self.cli.console is not None

    @patch('src.cli.main.Prompt.ask')
    def test_add_task_with_valid_input(self, mock_prompt):
        """Test adding a task with valid input."""
        mock_prompt.return_value = "New task"

        # Capture printed output
        with patch.object(self.cli.console, 'print') as mock_print:
            self.cli.add_task()

            # Verify task was added
            assert self.cli.manager.task_count == 1
            task = self.cli.manager.list_tasks()[0]
            assert task.title == "New task"

            # Verify success message was printed
            mock_print.assert_called()
            success_call_found = any(
                '[green]Task \'New task\' added successfully![/green]' in str(call)
                for call in mock_print.call_args_list
            )
            assert success_call_found

    @patch('src.cli.main.Prompt.ask')
    def test_add_task_with_empty_input(self, mock_prompt):
        """Test adding a task with empty input displays error."""
        mock_prompt.return_value = ""

        with patch.object(self.cli.console, 'print') as mock_print:
            self.cli.add_task()

            # Verify error message was printed
            error_call_found = any(
                '[red]Task title cannot be empty![/red]' in str(call)
                for call in mock_print.call_args_list
            )
            assert error_call_found

    @patch('src.cli.main.Prompt.ask')
    def test_complete_task_marks_task_as_completed(self, mock_prompt):
        """Test completing a task marks it as completed."""
        # Add a task first
        task = self.cli.manager.add_task("Test task")
        # Since there's only one task, it will have index 1
        mock_prompt.return_value = "1"

        with patch.object(self.cli.console, 'print') as mock_print:
            self.cli.complete_task()

            # Verify task is completed
            assert task.is_completed

            # Verify success message was printed
            success_call_found = any(
                f'[green]Task \'Test task\' marked as completed![/green]' in str(call)
                for call in mock_print.call_args_list
            )
            assert success_call_found

    @patch('src.cli.main.Prompt.ask')
    def test_complete_task_with_invalid_id(self, mock_prompt):
        """Test completing a task with invalid ID displays error."""
        # Add a task first so that the initial check passes
        existing_task = self.cli.manager.add_task("Existing task")
        # Then mock user input to be an invalid index (out of range)
        mock_prompt.return_value = "999"  # Assuming this index doesn't exist

        with patch.object(self.cli.console, 'print') as mock_print:
            self.cli.complete_task()

            # Verify error message was printed
            error_call_found = any(
                '[red]Task number out of range!' in str(call)
                for call in mock_print.call_args_list
            )
            assert error_call_found

    @patch('src.cli.main.Prompt.ask')
    def test_delete_task_removes_task(self, mock_prompt):
        """Test deleting a task removes it from the manager."""
        # Add a task first
        task = self.cli.manager.add_task("Test task")
        # Since there's only one task, it will have index 1
        mock_prompt.return_value = "1"

        with patch.object(self.cli.console, 'print') as mock_print:
            self.cli.delete_task()

            # Verify task is deleted
            assert self.cli.manager.task_count == 0

            # Verify success message was printed
            success_call_found = any(
                f'[green]Task \'Test task\' deleted successfully![/green]' in str(call)
                for call in mock_print.call_args_list
            )
            assert success_call_found

    @patch('src.cli.main.Prompt.ask')
    def test_delete_task_with_invalid_id(self, mock_prompt):
        """Test deleting a task with invalid ID displays error."""
        # Add a task first so that the initial check passes
        existing_task = self.cli.manager.add_task("Existing task")
        # Then mock user input to be an invalid index (out of range)
        mock_prompt.return_value = "999"  # Assuming this index doesn't exist

        with patch.object(self.cli.console, 'print') as mock_print:
            self.cli.delete_task()

            # Verify error message was printed
            error_call_found = any(
                '[red]Task number out of range!' in str(call)
                for call in mock_print.call_args_list
            )
            assert error_call_found

    def test_list_tasks_with_no_tasks_shows_message(self):
        """Test listing tasks when no tasks exist shows appropriate message."""
        with patch.object(self.cli.console, 'print') as mock_print:
            self.cli.list_tasks()

            # Verify "no tasks" message was printed
            no_tasks_call_found = any(
                '[yellow]No tasks found![/yellow]' in str(call)
                for call in mock_print.call_args_list
            )
            assert no_tasks_call_found

    def test_list_tasks_with_tasks_displays_table(self):
        """Test listing tasks when tasks exist displays a table."""
        # Add some tasks
        task1 = self.cli.manager.add_task("Task 1")
        task2 = self.cli.manager.add_task("Task 2")
        self.cli.manager.complete_task(task2.id)

        with patch.object(self.cli.console, 'print') as mock_print:
            self.cli.list_tasks()

            # Verify that print was called (table was displayed)
            assert mock_print.called

    def test_run_method_exits_when_user_chooses_exit(self):
        """Test that the run method exits when user chooses option 5."""
        # Mock user input to select option 5 (exit)
        with patch.object(self.cli, 'get_user_choice') as mock_get_choice, \
             patch.object(self.cli, 'display_menu'):

            mock_get_choice.return_value = '5'

            # Run the method - it should complete without error
            self.cli.run()
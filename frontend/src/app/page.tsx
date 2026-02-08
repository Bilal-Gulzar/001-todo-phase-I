'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Task } from '../types/task';
import TaskInput from '../components/TaskInput';
import { useAuth } from '../contexts/AuthContext';
import ChatSidebar from '../components/ChatSidebar';

export default function Dashboard() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user, token, logout, isLoading: authLoading } = useAuth();
  const router = useRouter();

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !token) {
      router.push('/login');
    }
  }, [authLoading, token, router]);

  // Fetch tasks from the backend
  const fetchTasks = useCallback(async () => {
    if (!token) return;

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1';
      console.log('🔄 Starting fetch request to:', `${apiUrl}/tasks`);
      const response = await fetch(`${apiUrl}/tasks`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      console.log('✅ Fetch response received. Status:', response.status, 'OK:', response.ok);

      if (response.status === 401) {
        // Token expired or invalid, logout
        logout();
        return;
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      console.log('📦 Tasks data received:', data);
      setTasks(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch tasks';
      console.error('❌ Error fetching tasks:', err);
      console.error('❌ Error type:', err instanceof TypeError ? 'Network/CORS error' : 'Other error');
      setError(errorMessage + (err instanceof TypeError ? ' - Check if backend is running and CORS is configured' : ''));
    } finally {
      console.log('🏁 Fetch complete, setting loading to false');
      setLoading(false);
    }
  }, [token, logout]);

  // Fetch tasks on initial load
  useEffect(() => {
    if (token) {
      fetchTasks();
    }
  }, [token, fetchTasks]);

  // Handle task addition by refreshing the list
  const handleTaskAdded = () => {
    fetchTasks();
  };

  // Toggle task completion status
  const toggleTaskStatus = async (task: Task) => {
    if (!token) return;

    try {
      const updatedStatus = task.status === 'completed' ? 'pending' : 'completed';
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1';
      console.log('🔄 Updating task status to:', updatedStatus, 'for task:', task.id);
      const response = await fetch(`${apiUrl}/tasks/${task.id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          status: updatedStatus
        }),
      });
      console.log('✅ Update response received. Status:', response.status);

      if (response.status === 401) {
        logout();
        return;
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Update the task in the local state
      setTasks(prevTasks =>
        prevTasks.map(t =>
          t.id === task.id ? { ...t, status: updatedStatus, updated_at: new Date().toISOString() } : t
        )
      );
      console.log('✅ Task status updated successfully');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update task status';
      console.error('❌ Error updating task status:', err);
      setError(errorMessage);
    }
  };

  // Delete a task
  const deleteTask = async (taskId: number) => {
    if (!token) return;

    if (!window.confirm('Are you sure you want to delete this task?')) {
      return;
    }

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1';
      console.log('🔄 Deleting task:', taskId);
      const response = await fetch(`${apiUrl}/tasks/${taskId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      console.log('✅ Delete response received. Status:', response.status);

      if (response.status === 401) {
        logout();
        return;
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Remove the task from the local state
      setTasks(prevTasks => prevTasks.filter(task => task.id !== taskId));
      console.log('✅ Task deleted successfully');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete task';
      console.error('❌ Error deleting task:', err);
      setError(errorMessage);
    }
  };

  // Show loading while checking authentication
  if (authLoading || !token) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4"></div>
          <p className="text-lg text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4"></div>
          <p className="text-lg text-gray-600">Loading tasks...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded max-w-md">
          <h2 className="font-bold mb-2">Error</h2>
          <p>{error}</p>
          <p className="mt-2 text-sm">Please make sure the backend server is running on http://localhost:8000</p>
        </div>
        <button
          onClick={() => {
            setError(null);
            fetchTasks(); // Retry fetching tasks
          }}
          className="ml-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <header className="mb-10 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Task Dashboard</h1>
            <p className="text-gray-600 mt-2">Welcome, {user?.full_name || user?.email}</p>
          </div>
          <button
            onClick={logout}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
          >
            Logout
          </button>
        </header>

        {/* Task Input Component */}
        <TaskInput onTaskAdded={handleTaskAdded} />

        {tasks.length === 0 ? (
          <div className="text-center py-12">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
            <h3 className="mt-2 text-lg font-medium text-gray-900">No tasks</h3>
            <p className="mt-1 text-gray-500">Get started by creating a new task using the form above.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {tasks.map((task) => (
              <div
                key={task.id}
                className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300"
              >
                <div className="p-6">
                  <div className="flex justify-between items-start gap-3">
                    <div className="flex items-start space-x-3 flex-1 min-w-0">
                      <input
                        type="checkbox"
                        checked={task.status === 'completed'}
                        onChange={() => toggleTaskStatus(task)}
                        className="mt-1 h-5 w-5 text-blue-600 rounded focus:ring-blue-500 flex-shrink-0"
                        aria-label={`Mark task "${task.title}" as ${task.status === 'completed' ? 'incomplete' : 'complete'}`}
                      />
                      <h3 className={`text-xl font-semibold break-words ${task.status === 'completed' ? 'line-through text-gray-500' : 'text-gray-900'} mb-2`}>
                        {task.title}
                      </h3>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium flex-shrink-0 ${
                      task.priority === 'high' ? 'bg-red-100 text-red-800' :
                      task.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {task.priority}
                    </span>
                  </div>

                  <p className={`text-gray-600 mb-4 break-words ${task.status === 'completed' ? 'line-through' : ''}`}>
                    {task.description}
                  </p>

                  <div className="flex items-center justify-between">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      task.status === 'completed' ? 'bg-green-100 text-green-800' :
                      task.status === 'in-progress' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {task.status.replace('-', ' ')}
                    </span>

                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => deleteTask(task.id)}
                        className="text-red-600 hover:text-red-800 transition-colors"
                        aria-label={`Delete task "${task.title}"`}
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                        </svg>
                      </button>
                      <div className="text-xs text-gray-500">
                        Updated: {new Date(task.updated_at).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* AI Chat Assistant */}
      <ChatSidebar onTasksChange={fetchTasks} />
    </div>
  );
}

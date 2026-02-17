import { useState, useEffect, useCallback } from "react";
import { tasksApi, Task as ApiTask } from "@/lib/api";
import { useAuth } from "./useAuth";

export type Task = ApiTask;
export type TaskPriority = "low" | "medium" | "high";
export type TaskInsert = { title: string; description?: string; priority?: TaskPriority };

export function useTasks() {
  const { user } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchTasks = useCallback(async () => {
    if (!user) {
      setTasks([]);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const data = await tasksApi.getTasks();
      setTasks(data);
    } catch (error) {
      console.error("Failed to fetch tasks:", error);
      setTasks([]);
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const addTask = async (task: TaskInsert) => {
    if (!user) return { message: "Not authenticated" };

    try {
      await tasksApi.createTask({
        title: task.title,
        description: task.description,
        priority: task.priority ?? "medium",
      });
      await fetchTasks();
      return null;
    } catch (error: any) {
      return { message: error.message || "Failed to add task" };
    }
  };

  const updateTask = async (
    id: string,
    updates: Partial<Pick<Task, "title" | "description" | "priority" | "completed">>
  ) => {
    try {
      await tasksApi.updateTask(id, updates);
      await fetchTasks();
      return null;
    } catch (error: any) {
      return { message: error.message || "Failed to update task" };
    }
  };

  const deleteTask = async (id: string) => {
    try {
      await tasksApi.deleteTask(id);
      await fetchTasks();
      return null;
    } catch (error: any) {
      return { message: error.message || "Failed to delete task" };
    }
  };

  const toggleComplete = async (id: string, completed: boolean) => {
    return updateTask(id, { completed: !completed });
  };

  return { tasks, loading, addTask, updateTask, deleteTask, toggleComplete, refetch: fetchTasks };
}

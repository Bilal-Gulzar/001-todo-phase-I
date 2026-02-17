import { useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { useTasks, TaskPriority } from "@/hooks/useTasks";
import { useTheme } from "@/hooks/useTheme";
import TaskItem from "@/components/TaskItem";
import AddTaskForm from "@/components/AddTaskForm";
import ChatSidebar from "@/components/ChatSidebar";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Bot, LogOut, ListFilter, Sun, Moon } from "lucide-react";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";

export default function Dashboard() {
  const { user, signOut } = useAuth();
  const { tasks, loading, addTask, updateTask, deleteTask, toggleComplete, refetch } = useTasks();
  const { dark, toggle: toggleTheme } = useTheme();
  const [chatOpen, setChatOpen] = useState(false);
  const [filter, setFilter] = useState<"all" | "active" | "completed">("all");
  const [sortPriority, setSortPriority] = useState<"all" | TaskPriority>("all");
  const navigate = useNavigate();

  const handleLogout = async () => {
    await signOut();
    navigate("/");
  };

  const handleAddTask = async (title: string, priority: TaskPriority) => {
    const error = await addTask({ title, priority });
    if (error) toast.error("Failed to add task");
  };

  const filtered = tasks
    .filter((t) => {
      if (filter === "active") return !t.completed;
      if (filter === "completed") return t.completed;
      return true;
    })
    .filter((t) => {
      if (sortPriority !== "all") return t.priority === sortPriority;
      return true;
    });

  const priorityOrder = { high: 0, medium: 1, low: 2 };
  const sorted = [...filtered].sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);

  return (
    <div className="flex h-screen bg-background">
      <ChatSidebar open={chatOpen} onClose={() => setChatOpen(false)} onTaskChange={refetch} />

      <div className="flex flex-1 flex-col">
        {/* Top bar */}
        <header className="flex items-center justify-between border-b border-border px-6 py-3">
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="icon" onClick={() => setChatOpen(!chatOpen)}>
              <Bot className="h-5 w-5" />
            </Button>
            <h1 className="font-display text-lg font-bold text-gradient">AI TODO</h1>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-sm text-muted-foreground hidden sm:inline">{user?.email}</span>
            <Button variant="ghost" size="icon" onClick={toggleTheme}>
              {dark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
            <Button variant="ghost" size="icon" onClick={handleLogout}>
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </header>

        {/* Main */}
        <main className="flex-1 overflow-auto p-6">
          <div className="mx-auto max-w-2xl space-y-6">
            <AddTaskForm onAdd={handleAddTask} />

            {/* Filters */}
            <div className="flex flex-wrap items-center gap-3">
              <ListFilter className="h-4 w-4 text-muted-foreground" />
              <Select value={filter} onValueChange={(v) => setFilter(v as any)}>
                <SelectTrigger className="w-32 bg-secondary border-none h-8 text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All tasks</SelectItem>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="completed">Completed</SelectItem>
                </SelectContent>
              </Select>
              <Select value={sortPriority} onValueChange={(v) => setSortPriority(v as any)}>
                <SelectTrigger className="w-32 bg-secondary border-none h-8 text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All priorities</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="low">Low</SelectItem>
                </SelectContent>
              </Select>
              <span className="ml-auto text-xs text-muted-foreground">
                {sorted.length} task{sorted.length !== 1 ? "s" : ""}
              </span>
            </div>

            {/* Task List */}
            <motion.div layout className="space-y-2">
              {loading ? (
                <p className="text-center text-muted-foreground py-12">Loading tasks...</p>
              ) : sorted.length === 0 ? (
                <p className="text-center text-muted-foreground py-12">No tasks yet. Add one above!</p>
              ) : (
                sorted.map((task) => (
                  <motion.div key={task.id} layout initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
                    <TaskItem
                      task={task}
                      onToggle={toggleComplete}
                      onUpdate={updateTask}
                      onDelete={deleteTask}
                    />
                  </motion.div>
                ))
              )}
            </motion.div>
          </div>
        </main>
      </div>
    </div>
  );
}

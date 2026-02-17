import { useState } from "react";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Trash2, Pencil, Check, X } from "lucide-react";
import type { Task, TaskPriority } from "@/hooks/useTasks";
import { cn } from "@/lib/utils";

const priorityColors: Record<TaskPriority, string> = {
  high: "bg-destructive/20 text-destructive border-destructive/30",
  medium: "bg-primary/20 text-primary border-primary/30",
  low: "bg-muted text-muted-foreground border-border",
};

type Props = {
  task: Task;
  onToggle: (id: string, completed: boolean) => void;
  onUpdate: (id: string, updates: Partial<Pick<Task, "title" | "priority">>) => void;
  onDelete: (id: string) => void;
};

export default function TaskItem({ task, onToggle, onUpdate, onDelete }: Props) {
  const [editing, setEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);

  const saveEdit = () => {
    if (editTitle.trim()) {
      onUpdate(task.id, { title: editTitle.trim() });
    }
    setEditing(false);
  };

  return (
    <div className={cn(
      "glass group flex items-center gap-3 rounded-xl px-4 py-3 transition-all",
      task.completed && "opacity-50"
    )}>
      <Checkbox
        checked={task.completed}
        onCheckedChange={() => onToggle(task.id, task.completed)}
        className="border-muted-foreground data-[state=checked]:bg-primary data-[state=checked]:border-primary"
      />

      {editing ? (
        <div className="flex flex-1 items-center gap-2">
          <Input
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && saveEdit()}
            className="h-8 bg-secondary border-none"
            autoFocus
          />
          <Button size="icon" variant="ghost" onClick={saveEdit} className="h-7 w-7"><Check className="h-3.5 w-3.5" /></Button>
          <Button size="icon" variant="ghost" onClick={() => setEditing(false)} className="h-7 w-7"><X className="h-3.5 w-3.5" /></Button>
        </div>
      ) : (
        <span className={cn("flex-1 text-sm", task.completed && "line-through")}>{task.title}</span>
      )}

      <Badge variant="outline" className={cn("text-xs capitalize", priorityColors[task.priority])}>
        {task.priority}
      </Badge>

      <div className="flex gap-1 opacity-0 transition-opacity group-hover:opacity-100">
        <Button size="icon" variant="ghost" onClick={() => { setEditTitle(task.title); setEditing(true); }} className="h-7 w-7">
          <Pencil className="h-3.5 w-3.5" />
        </Button>
        <Button size="icon" variant="ghost" onClick={() => onDelete(task.id)} className="h-7 w-7 text-destructive hover:text-destructive">
          <Trash2 className="h-3.5 w-3.5" />
        </Button>
      </div>
    </div>
  );
}

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Bot, Send, X, MessageSquare } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { cn } from "@/lib/utils";
import { tokenManager } from "@/lib/api";

type Msg = { role: "user" | "assistant"; content: string };

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api/v1';
const CHAT_URL = `${API_BASE_URL}/chat`;

export default function ChatSidebar({ open, onClose, onTaskChange }: { open: boolean; onClose: () => void; onTaskChange?: () => void }) {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async () => {
    const text = input.trim();
    if (!text || isLoading) return;
    setInput("");

    const userMsg: Msg = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const token = tokenManager.getToken();
      if (!token) {
        throw new Error("Not authenticated");
      }

      const resp = await fetch(CHAT_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: text,
          history: messages.map(m => ({ role: m.role, content: m.content }))
        }),
      });

      if (!resp.ok) {
        const errData = await resp.json().catch(() => ({}));
        throw new Error(errData.detail || "Failed to get response");
      }

      const data = await resp.json();
      setMessages((prev) => [...prev, { role: "assistant", content: data.response }]);

      // Only refresh task list if AI performed a CRUD operation
      const response = data.response.toLowerCase();
      const crudKeywords = [
        'added', 'created', 'new task',
        'deleted', 'removed',
        'updated', 'changed', 'modified',
        'marked', 'completed', 'done',
        '📋', '✓', '✅'
      ];

      const hasCrudOperation = crudKeywords.some(keyword => response.includes(keyword));
      if (hasCrudOperation) {
        onTaskChange?.();
      }
    } catch (e: any) {
      setMessages((prev) => [...prev, { role: "assistant", content: `Error: ${e.message}` }]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!open) return null;

  return (
    <div className={cn(
      "fixed inset-y-0 left-0 z-40 flex w-80 flex-col border-r border-border bg-sidebar transition-transform duration-300",
      "translate-x-0"
    )}>
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <div className="flex items-center gap-2 text-sm font-semibold">
          <Bot className="h-5 w-5 text-primary" />
          AI Assistant
        </div>
        <Button variant="ghost" size="icon" onClick={onClose} className="h-7 w-7">
          <X className="h-4 w-4" />
        </Button>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 px-4 py-3">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center py-12 text-center text-muted-foreground">
            <MessageSquare className="mb-3 h-10 w-10 opacity-30" />
            <p className="text-sm">Ask me anything about your tasks or just chat!</p>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={cn("mb-3", m.role === "user" ? "text-right" : "text-left")}>
            <div className={cn(
              "inline-block max-w-[90%] rounded-xl px-3 py-2 text-sm",
              m.role === "user" ? "bg-primary text-primary-foreground" : "bg-secondary text-foreground"
            )}>
              {m.role === "assistant" ? (
                <div className="prose prose-sm prose-invert max-w-none">
                  <ReactMarkdown>{m.content}</ReactMarkdown>
                </div>
              ) : m.content}
            </div>
          </div>
        ))}
        {isLoading && messages[messages.length - 1]?.role !== "assistant" && (
          <div className="mb-3 text-left">
            <div className="inline-block rounded-xl bg-secondary px-3 py-2 text-sm text-muted-foreground animate-pulse-glow">
              Thinking...
            </div>
          </div>
        )}
        <div ref={scrollRef} />
      </ScrollArea>

      {/* Input */}
      <div className="border-t border-border p-3">
        <form
          onSubmit={(e) => { e.preventDefault(); send(); }}
          className="flex gap-2"
        >
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask the AI..."
            className="flex-1 bg-secondary border-none text-sm"
            disabled={isLoading}
          />
          <Button type="submit" size="icon" disabled={isLoading || !input.trim()}>
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </div>
    </div>
  );
}

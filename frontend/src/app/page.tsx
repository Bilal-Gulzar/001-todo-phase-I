'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Task } from '../types/task';
import { useAuth } from '../contexts/AuthContext';

interface Message {
  id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

export default function Dashboard() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [agentStatus, setAgentStatus] = useState<'idle' | 'thinking' | 'executing'>('idle');
  const [isChatOpen, setIsChatOpen] = useState(false);
  const { user, token, logout, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const terminalEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (!authLoading && !token) {
      router.push('/login');
    }
  }, [authLoading, token, router]);

  useEffect(() => {
    if (token) {
      setMessages([{
        id: Date.now(),
        role: 'system',
        content: 'Agent Console initialized. Ready for commands.',
        timestamp: new Date()
      }]);
    }
  }, [token]);

  const fetchTasks = useCallback(async () => {
    if (!token) return;

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1';
      const response = await fetch(`${apiUrl}/tasks`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });

      if (response.status === 401) {
        logout();
        return;
      }

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      setTasks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch tasks');
    } finally {
      setLoading(false);
    }
  }, [token, logout]);

  useEffect(() => {
    if (token) fetchTasks();
  }, [token, fetchTasks]);

  const sendCommand = async (command: string) => {
    if (!command.trim() || isProcessing) return;

    const userMsg: Message = {
      id: Date.now(),
      role: 'user',
      content: command,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMsg]);
    setInputValue('');
    setIsProcessing(true);
    setAgentStatus('thinking');

    const thinkingMsg: Message = {
      id: Date.now() + 1,
      role: 'system',
      content: 'Processing...',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, thinkingMsg]);

    try {
      setAgentStatus('executing');
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1';

      const response = await fetch(`${apiUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          message: command,
          history: messages.filter(m => m.role !== 'system').map(m => ({
            role: m.role,
            content: m.content
          }))
        })
      });

      if (!response.ok) throw new Error(`API Error: ${response.status}`);

      const data = await response.json();
      let cleanedResponse = data.response || '';

      if (cleanedResponse) {
        cleanedResponse = cleanedResponse.replace(/<function[\s\S]*?<\/function>/g, '').trim();
      }

      if (!cleanedResponse) {
        cleanedResponse = 'Operation completed successfully';
      }

      const assistantMsg: Message = {
        id: Date.now() + 2,
        role: 'assistant',
        content: cleanedResponse,
        timestamp: new Date()
      };

      setMessages(prev => [...prev.filter(m => m.content !== thinkingMsg.content), assistantMsg]);
      await fetchTasks();
    } catch (error) {
      const errorMsg: Message = {
        id: Date.now() + 2,
        role: 'system',
        content: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev.filter(m => m.content !== thinkingMsg.content), errorMsg]);
    } finally {
      setIsProcessing(false);
      setAgentStatus('idle');
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendCommand(inputValue);
  };

  const deleteTask = async (taskId: string) => {
    if (!token) return;

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1';
      const response = await fetch(`${apiUrl}/tasks/${taskId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` },
      });

      if (response.status === 401) {
        logout();
        return;
      }

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      setTasks(prevTasks => prevTasks.filter(task => task.id !== taskId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete task');
    }
  };

  const toggleTaskStatus = async (task: Task) => {
    if (!token) return;

    try {
      const updatedStatus = task.status === 'completed' ? 'pending' : 'completed';
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1';

      const response = await fetch(`${apiUrl}/tasks/${task.id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ status: updatedStatus }),
      });

      if (response.status === 401) {
        logout();
        return;
      }

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

      setTasks(prevTasks =>
        prevTasks.map(t =>
          t.id === task.id ? { ...t, status: updatedStatus, updated_at: new Date().toISOString() } : t
        )
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update task');
    }
  };

  if (authLoading || !token || loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-white text-sm animate-pulse">
          Loading...
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Navigation Bar */}
      <nav className="border-b border-white/10 bg-black">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-[#3b82f6] flex items-center justify-center font-bold text-sm">
              AI
            </div>
            <span className="text-lg font-semibold">TODO</span>
          </div>
          <div className="flex items-center space-x-3">
            <span className="text-sm text-[#94a3b8]">{user?.email}</span>
            <button
              onClick={logout}
              className="px-4 py-2 border border-white/20 text-white text-sm hover:bg-white/5 transition-all"
            >
              Sign Out
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Hero Section */}
        <div className="mb-12">
          <div className="text-xs font-mono text-[#94a3b8] mb-4 tracking-wider uppercase">
            AI-First Future
          </div>
          <h1 className="text-5xl font-bold mb-4 leading-tight">
            <span className="text-white">AI POWERED</span>{' '}
            <span className="text-[#3b82f6]">TODO</span>
          </h1>
          <p className="text-[#94a3b8] text-lg mb-8 max-w-2xl">
            Manage your tasks with the power of AI. Natural language commands, intelligent prioritization, and seamless workflow automation.
          </p>
          <button
            onClick={() => setIsChatOpen(true)}
            className="px-6 py-3 bg-[#3b82f6] text-white font-medium flex items-center space-x-2 hover:bg-[#2563eb] transition-all"
          >
            <span>Get Started</span>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>

        {/* Task Grid */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-white">Your Tasks</h2>
            <div className="text-sm text-[#94a3b8]">
              {tasks.length} {tasks.length === 1 ? 'task' : 'tasks'}
            </div>
          </div>

          {tasks.length === 0 ? (
            <div className="border border-[#3b82f6] bg-black p-12 text-center">
              <div className="text-[#94a3b8] mb-2">No tasks yet</div>
              <div className="text-[#94a3b8]/60 text-sm">
                Use the AI Agent to create your first task
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {tasks.map((task) => (
                <div
                  key={task.id}
                  className={`bg-black border border-[#3b82f6] p-6 hover:border-[#3b82f6]/80 transition-all ${
                    task.status === 'completed' ? 'opacity-60' : ''
                  }`}
                >
                  {/* Card Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-start space-x-3 flex-1">
                      <input
                        type="checkbox"
                        checked={task.status === 'completed'}
                        onChange={() => toggleTaskStatus(task)}
                        className="mt-1 w-4 h-4 bg-black border border-[#3b82f6] checked:bg-[#3b82f6] cursor-pointer"
                      />
                      <h3 className={`font-bold text-lg text-[#3b82f6] ${
                        task.status === 'completed' ? 'line-through opacity-60' : ''
                      }`}>
                        {task.title}
                      </h3>
                    </div>
                    <button
                      onClick={() => deleteTask(task.id)}
                      className="text-[#94a3b8] hover:text-red-400 transition-colors ml-2"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>

                  {/* Card Description */}
                  {task.description && (
                    <div className="mb-4">
                      <p className={`text-sm leading-relaxed ${
                        task.status === 'completed' ? 'line-through text-[#94a3b8]/60' : 'text-[#94a3b8]'
                      }`}>
                        {task.description}
                      </p>
                    </div>
                  )}

                  {/* Card Footer */}
                  <div className="flex items-center justify-between pt-4 border-t border-white/10">
                    <div className="flex items-center space-x-2">
                      <span className={`text-xs px-2 py-1 border ${
                        task.priority === 'high' ? 'border-red-500/40 text-red-400' :
                        task.priority === 'medium' ? 'border-yellow-500/40 text-yellow-400' :
                        'border-green-500/40 text-green-400'
                      }`}>
                        {task.priority.toUpperCase()}
                      </span>
                      <span className={`text-xs px-2 py-1 border ${
                        task.status === 'completed' ? 'border-green-500/30 text-green-400' :
                        task.status === 'in-progress' ? 'border-[#3b82f6]/30 text-[#3b82f6]' :
                        'border-[#94a3b8]/30 text-[#94a3b8]'
                      }`}>
                        {task.status.toUpperCase().replace('-', ' ')}
                      </span>
                    </div>
                    <span className="text-xs text-[#94a3b8]/60">
                      {new Date(task.updated_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Floating Action Button (FAB) */}
      <button
        onClick={() => setIsChatOpen(true)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-[#3b82f6] text-white rounded-full shadow-lg hover:bg-[#2563eb] transition-all flex items-center justify-center z-40"
        aria-label="Open chat"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
        </svg>
      </button>

      {/* Chat Sidebar Overlay */}
      {isChatOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40"
          onClick={() => setIsChatOpen(false)}
        />
      )}

      {/* Chat Sidebar Drawer */}
      <div
        className={`fixed top-0 right-0 h-full w-[350px] bg-zinc-950 backdrop-blur-md border-l border-white/10 z-50 transform transition-transform duration-300 ease-in-out ${
          isChatOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        {/* Sidebar Header */}
        <div className="border-b border-white/10 p-4 flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-white">Agent Console</h3>
            <p className="text-xs text-[#94a3b8] mt-1">
              Natural language task management
            </p>
          </div>
          <button
            onClick={() => setIsChatOpen(false)}
            className="text-[#94a3b8] hover:text-white transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Status Badge */}
        <div className="px-4 py-2 border-b border-white/10">
          <div className={`inline-flex items-center text-xs px-2 py-1 border ${
            agentStatus === 'idle' ? 'border-green-500/30 text-green-400' :
            agentStatus === 'thinking' ? 'border-yellow-500/30 text-yellow-400' :
            'border-[#3b82f6]/30 text-[#3b82f6]'
          }`}>
            <span className={`w-2 h-2 rounded-full mr-2 ${
              agentStatus === 'idle' ? 'bg-green-400' :
              agentStatus === 'thinking' ? 'bg-yellow-400' :
              'bg-[#3b82f6]'
            }`} />
            {agentStatus.toUpperCase()}
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 h-[calc(100vh-280px)]">
          {messages.map((msg) => (
            <div key={msg.id} className="text-sm">
              <div className="font-mono text-xs text-[#94a3b8] mb-1">
                {msg.role === 'user' ? 'You' : msg.role === 'assistant' ? 'Agent' : 'System'}
              </div>
              <div className={`whitespace-pre-wrap break-words ${
                msg.role === 'user' ? 'text-[#3b82f6]' :
                msg.role === 'system' ? 'text-[#94a3b8]/60' :
                'text-white'
              }`}>
                {msg.content}
              </div>
            </div>
          ))}

          {isProcessing && (
            <div className="text-sm text-[#94a3b8] animate-pulse">
              Processing...
            </div>
          )}

          <div ref={terminalEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-white/10 p-4">
          <form onSubmit={handleSubmit} className="space-y-3">
            <input
              id="agent-input"
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Type a command..."
              className="w-full bg-black border border-white/10 px-4 py-3 text-sm text-white placeholder-[#94a3b8]/50 focus:outline-none focus:border-[#3b82f6] transition-colors"
              disabled={isProcessing}
            />
            <button
              type="submit"
              disabled={isProcessing || !inputValue.trim()}
              className="w-full px-4 py-3 bg-[#3b82f6] text-white font-medium hover:bg-[#2563eb] disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center space-x-2"
            >
              <span>Send Command</span>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </button>
          </form>

          <div className="mt-4 text-xs text-[#94a3b8]/60">
            <div className="mb-2">Try commands like:</div>
            <div className="space-y-1 font-mono">
              <div className="flex items-center">
                <span className="w-1 h-1 rounded-full bg-[#3b82f6] mr-2" />
                list all tasks
              </div>
              <div className="flex items-center">
                <span className="w-1 h-1 rounded-full bg-[#3b82f6] mr-2" />
                add meeting at 3pm
              </div>
              <div className="flex items-center">
                <span className="w-1 h-1 rounded-full bg-[#3b82f6] mr-2" />
                mark task completed
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

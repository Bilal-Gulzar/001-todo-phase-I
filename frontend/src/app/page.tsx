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
    <div className="min-h-screen bg-black text-white relative">
      {/* Radial gradient background */}
      <div className="absolute inset-0 bg-gradient-radial from-blue-500/10 via-black to-black pointer-events-none" />

      {/* Navigation Bar */}
      <nav className="relative border-b border-white/10 bg-black/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-500 flex items-center justify-center font-bold text-sm">
              AI
            </div>
            <span className="text-lg font-semibold">Agent Factory</span>
          </div>
          <div className="flex items-center space-x-3">
            <span className="text-sm text-slate-400">{user?.email}</span>
            <button
              onClick={logout}
              className="px-4 py-2 border border-white/20 text-white text-sm hover:bg-white/5 transition-all"
            >
              Sign Out
            </button>
          </div>
        </div>
      </nav>

      <div className="relative flex">
        {/* Main Content */}
        <div className="flex-1 px-6 py-12">
          <div className="max-w-4xl mx-auto">
            {/* Hero Section */}
            <div className="mb-12">
              <div className="text-xs font-mono text-slate-400 mb-4 tracking-wider">
                AI-FIRST FUTURE
              </div>
              <h1 className="text-5xl font-bold mb-4 leading-tight">
                <span className="text-white">AI POWERED</span>{' '}
                <span className="text-blue-400">TODO</span>
              </h1>
              <p className="text-slate-400 text-lg mb-8 max-w-2xl">
                Manage your tasks with the power of AI. Natural language commands, intelligent prioritization, and seamless workflow automation.
              </p>
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => document.getElementById('agent-input')?.focus()}
                  className="px-6 py-3 bg-blue-500 text-white font-medium flex items-center space-x-2 hover:bg-blue-600 transition-all"
                >
                  <span>Get Started</span>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>
                <button className="px-6 py-3 border border-white/20 text-white font-medium hover:bg-white/5 transition-all">
                  Learn More
                </button>
              </div>
            </div>

            {/* Task Feed */}
            <div className="mb-8">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold">Your Tasks</h2>
                <div className="text-sm text-slate-400">
                  {tasks.length} {tasks.length === 1 ? 'task' : 'tasks'}
                </div>
              </div>

              {tasks.length === 0 ? (
                <div className="border border-white/10 p-12 text-center">
                  <div className="text-slate-400 mb-2">No tasks yet</div>
                  <div className="text-slate-500 text-sm">
                    Use the Agent Console to create your first task
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  {tasks.map((task) => (
                    <div
                      key={task.id}
                      className={`border border-white/10 p-4 hover:border-blue-500/50 transition-all ${
                        task.status === 'completed' ? 'opacity-60' : ''
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-3 flex-1">
                          <input
                            type="checkbox"
                            checked={task.status === 'completed'}
                            onChange={() => toggleTaskStatus(task)}
                            className="mt-1 w-4 h-4 bg-black border border-white/30 checked:bg-blue-500 cursor-pointer"
                          />
                          <div className="flex-1">
                            <h3 className={`font-medium mb-1 ${
                              task.status === 'completed' ? 'line-through text-slate-500' : 'text-white'
                            }`}>
                              {task.title}
                            </h3>
                            {task.description && (
                              <p className={`text-sm ${
                                task.status === 'completed' ? 'line-through text-slate-600' : 'text-slate-400'
                              }`}>
                                {task.description}
                              </p>
                            )}
                          </div>
                        </div>

                        <div className="flex items-center space-x-3 ml-4">
                          <span className={`text-xs px-2 py-1 border ${
                            task.priority === 'high' ? 'border-red-500/40 text-red-400' :
                            task.priority === 'medium' ? 'border-yellow-500/40 text-yellow-400' :
                            'border-green-500/40 text-green-400'
                          }`}>
                            {task.priority.toUpperCase()}
                          </span>
                          <button
                            onClick={() => deleteTask(task.id)}
                            className="text-slate-400 hover:text-red-400 transition-colors"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                        </div>
                      </div>

                      <div className="flex items-center justify-between mt-3 pt-3 border-t border-white/5">
                        <span className={`text-xs px-2 py-1 border ${
                          task.status === 'completed' ? 'border-green-500/30 text-green-400' :
                          task.status === 'in-progress' ? 'border-blue-500/30 text-blue-400' :
                          'border-slate-500/30 text-slate-400'
                        }`}>
                          {task.status.toUpperCase().replace('-', ' ')}
                        </span>
                        <span className="text-xs text-slate-500">
                          {new Date(task.updated_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Agent Console - Floating Right Sidebar */}
        <div className="w-96 border-l border-white/10 bg-zinc-900/50 backdrop-blur-md flex flex-col sticky top-0 h-screen">
          {/* Console Header */}
          <div className="border-b border-white/10 p-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold">Agent Console</h3>
              <div className={`text-xs px-2 py-1 border ${
                agentStatus === 'idle' ? 'border-green-500/30 text-green-400' :
                agentStatus === 'thinking' ? 'border-yellow-500/30 text-yellow-400' :
                'border-blue-500/30 text-blue-400'
              }`}>
                {agentStatus.toUpperCase()}
              </div>
            </div>
            <p className="text-xs text-slate-400">
              Natural language task management
            </p>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg) => (
              <div key={msg.id} className={`text-sm ${
                msg.role === 'user' ? 'text-blue-400' :
                msg.role === 'system' ? 'text-slate-500' :
                'text-slate-300'
              }`}>
                <div className="font-mono text-xs text-slate-500 mb-1">
                  {msg.role === 'user' ? 'You' : msg.role === 'assistant' ? 'Agent' : 'System'}
                </div>
                <div className="whitespace-pre-wrap break-words">
                  {msg.content}
                </div>
              </div>
            ))}

            {isProcessing && (
              <div className="text-sm text-slate-400 animate-pulse">
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
                className="w-full bg-black/50 border border-white/10 px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
                disabled={isProcessing}
              />
              <button
                type="submit"
                disabled={isProcessing || !inputValue.trim()}
                className="w-full px-4 py-3 bg-blue-500 text-white font-medium hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center space-x-2"
              >
                <span>Send Command</span>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </button>
            </form>

            <div className="mt-4 text-xs text-slate-500">
              <div className="mb-2">Try commands like:</div>
              <div className="space-y-1 font-mono">
                <div>• list all tasks</div>
                <div>• add meeting at 3pm</div>
                <div>• mark task completed</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

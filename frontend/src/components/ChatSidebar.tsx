'use client';

import { useState, useRef, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
}

interface ChatSidebarProps {
  onTasksChange?: () => void;
}

export default function ChatSidebar({ onTasksChange }: ChatSidebarProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { token } = useAuth();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;

    const userMsg: Message = {
      id: Date.now(),
      role: 'user',
      content: text
    };

    setMessages(prev => [...prev, userMsg]);
    setInputValue('');
    setIsLoading(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1';
      console.log('Sending chat request to:', `${apiUrl}/chat`);
      console.log('Token:', token ? 'Present' : 'Missing');

      const response = await fetch(`${apiUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          message: text,
          history: messages.map(m => ({
            role: m.role,
            content: m.content
          }))
        })
      });

      console.log('Response status:', response.status);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        console.error('API Error:', errorData);
        throw new Error(errorData.detail || `API Error: ${response.status}`);
      }

      const data = await response.json();

      // Filter out function call XML tags from the response using regex
      let cleanedResponse = data.response || '';
      if (cleanedResponse) {
        cleanedResponse = cleanedResponse.replace(/<function[\s\S]*?<\/function>/g, '').trim();
      }

      // Handle empty or null responses (tool calls in progress)
      if (!cleanedResponse || cleanedResponse.length === 0) {
        cleanedResponse = 'Task updated successfully!';
      }

      const assistantMsg: Message = {
        id: Date.now() + 1,
        role: 'assistant',
        content: cleanedResponse
      };

      setMessages(prev => [...prev, assistantMsg]);

      // CRITICAL: Always refresh tasks after AI response (Read-After-Write pattern)
      console.log('🔄 Refreshing tasks after AI response');
      if (onTasksChange) {
        onTasksChange();
      }
    } catch (error) {
      console.error('Chat error:', error);

      const errorMsg: Message = {
        id: Date.now() + 1,
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}. Please check the console for details.`
      };

      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(inputValue);
  };

  return (
    <>
      {/* Floating chat button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-50 bg-blue-600 text-white p-4 rounded-full shadow-lg hover:bg-blue-700 transition-colors duration-200 flex items-center justify-center w-14 h-14"
        aria-label="Toggle chat"
      >
        {isOpen ? (
          <span className="text-2xl">✕</span>
        ) : (
          <span className="text-2xl">💬</span>
        )}
      </button>

      {/* Chat sidebar panel */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 z-50 w-96 h-[600px] bg-white rounded-lg shadow-2xl flex flex-col border border-gray-200">
          {/* Header */}
          <div className="p-4 border-b border-gray-200 flex justify-between items-center bg-blue-600 text-white rounded-t-lg">
            <div>
              <h3 className="font-bold text-lg">AI Assistant</h3>
              <p className="text-xs text-blue-100">Ask me about your tasks</p>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-white hover:text-blue-100 text-xl"
              aria-label="Close chat"
            >
              ✕
            </button>
          </div>

          {/* Messages area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
            {messages.length === 0 && (
              <div className="text-center text-gray-500 mt-8">
                <p className="text-sm text-gray-700">👋 Hi! I'm your AI assistant.</p>
                <p className="text-xs mt-2 text-gray-600">Try asking:</p>
                <ul className="text-xs mt-2 space-y-1 text-gray-600">
                  <li>"Show me my tasks"</li>
                  <li>"Add a meeting with Bilal at 5pm"</li>
                  <li>"What should I do first?"</li>
                </ul>
              </div>
            )}

            {messages.map(msg => (
              <div
                key={msg.id}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] p-3 rounded-lg ${
                    msg.role === 'user'
                      ? 'bg-blue-600 text-white rounded-br-none'
                      : 'bg-white text-slate-900 border border-gray-200 rounded-bl-none shadow-sm'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap break-words text-slate-900">{msg.content}</p>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white text-gray-900 border border-gray-200 p-3 rounded-lg rounded-bl-none shadow-sm">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input area */}
          <div className="p-4 border-t border-gray-200 bg-white rounded-b-lg">
            <form onSubmit={handleSubmit} className="flex space-x-2">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Ask me anything..."
                className="flex-1 p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm text-slate-900"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !inputValue.trim()}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors duration-200 text-sm font-medium"
              >
                Send
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
}

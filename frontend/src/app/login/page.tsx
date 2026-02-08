'use client';

import { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import Link from 'next/link';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      await login(email, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 border border-green-500/20 p-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold uppercase tracking-wider text-green-500 mb-2 font-mono"
              style={{ textShadow: '0 0 10px #22c55e, 0 0 20px #22c55e' }}>
            AI POWERED
          </h1>
          <h1 className="text-4xl font-bold uppercase tracking-wider text-green-500 mb-6 font-mono"
              style={{ textShadow: '0 0 10px #22c55e, 0 0 20px #22c55e' }}>
            TODO
          </h1>
          <div className="text-xs text-green-500/60 font-mono mb-4">
            [ AUTHENTICATION REQUIRED ]
          </div>
        </div>

        {/* Login Form */}
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="border border-red-500/40 bg-red-500/10 p-4">
              <div className="text-sm text-red-500 font-mono">
                &gt; ERROR: {error}
              </div>
            </div>
          )}

          <div className="space-y-4">
            {/* Email Input */}
            <div>
              <label htmlFor="email" className="block text-xs font-mono text-green-500/60 mb-2 uppercase">
                [ Email Address ]
              </label>
              <div className="flex items-center space-x-2">
                <span className="text-green-500 font-mono">&gt;</span>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="flex-1 bg-black border border-green-500/40 text-green-500 px-3 py-2 focus:outline-none focus:border-green-500 placeholder-green-500/30 font-mono text-sm"
                  placeholder="user@domain.com"
                />
              </div>
            </div>

            {/* Password Input */}
            <div>
              <label htmlFor="password" className="block text-xs font-mono text-green-500/60 mb-2 uppercase">
                [ Password ]
              </label>
              <div className="flex items-center space-x-2">
                <span className="text-green-500 font-mono">&gt;</span>
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="flex-1 bg-black border border-green-500/40 text-green-500 px-3 py-2 focus:outline-none focus:border-green-500 placeholder-green-500/30 font-mono text-sm"
                  placeholder="••••••••"
                />
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <div className="mt-6">
            <button
              type="submit"
              disabled={isLoading}
              className={`w-full px-4 py-3 border font-mono text-sm uppercase tracking-wider transition-all ${
                isLoading
                  ? 'border-green-500/20 text-green-500/40 cursor-not-allowed'
                  : 'border-green-500/40 text-green-500 hover:border-green-500 hover:bg-green-500/10 hover:shadow-[0_0_15px_rgba(34,197,94,0.3)]'
              }`}
            >
              {isLoading ? '[ AUTHENTICATING... ]' : '[ EXECUTE LOGIN ]'}
            </button>
          </div>

          {/* Sign Up Link */}
          <div className="text-center mt-4">
            <div className="text-xs text-green-500/60 font-mono">
              NO ACCOUNT?{' '}
              <Link
                href="/signup"
                className="text-green-500 hover:text-green-400 underline"
              >
                CREATE NEW USER
              </Link>
            </div>
          </div>
        </form>

        {/* System Info */}
        <div className="mt-8 pt-6 border-t border-green-500/20">
          <div className="text-[10px] text-green-500/40 font-mono space-y-1">
            <div>&gt; SYSTEM: AI POWERED TODO v1.0</div>
            <div>&gt; STATUS: ONLINE</div>
            <div>&gt; SECURITY: ENABLED</div>
          </div>
        </div>
      </div>
    </div>
  );
}

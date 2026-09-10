import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { Leaf, Eye, EyeOff, Cpu, Zap, Globe } from 'lucide-react';

export default function LoginPage() {
  const { login, register } = useAuth();
  const navigate = useNavigate();
  const [mode, setMode] = useState('login');
  const [loading, setLoading] = useState(false);
  const [showPw, setShowPw] = useState(false);
  const [form, setForm] = useState({ name: '', email: '', password: '' });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (mode === 'login') {
        await login(form.email, form.password);
        toast.success('Welcome back!');
        navigate('/dashboard');
      } else {
        await register(form.name, form.email, form.password);
        toast.success('Account created! Please login.');
        setMode('login');
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const set = (key, val) => setForm(f => ({ ...f, [key]: val }));

  return (
    <div className="min-h-screen bg-dark-950 bg-grid flex items-center justify-center p-4 relative overflow-hidden">
      {/* Ambient glow blobs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full opacity-5"
        style={{ background: 'radial-gradient(circle, #22c55e, transparent)', filter: 'blur(80px)' }} />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 rounded-full opacity-5"
        style={{ background: 'radial-gradient(circle, #4ade80, transparent)', filter: 'blur(80px)' }} />

      <div className="w-full max-w-md relative">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-4 glow-green"
            style={{ background: 'linear-gradient(135deg, rgba(34,197,94,0.15), rgba(34,197,94,0.05))', border: '1px solid rgba(34,197,94,0.3)' }}>
            <Leaf size={28} className="text-green-400" />
          </div>
          <h1 className="text-3xl font-black glow-text text-green-400 font-mono tracking-tight">
            GreenCode
          </h1>
          <p className="text-green-600 font-mono text-sm mt-1">Guardian Platform</p>
        </div>

        {/* Stats row */}
        <div className="grid grid-cols-3 gap-3 mb-8">
          {[
            { icon: Cpu, label: 'CPU Track', val: 'Real-time' },
            { icon: Zap, label: 'Carbon Est.', val: 'AI-powered' },
            { icon: Globe, label: 'Blockchain', val: 'Certified' },
          ].map(({ icon: Icon, label, val }) => (
            <div key={label} className="card p-3 text-center">
              <Icon size={14} className="text-green-500 mx-auto mb-1" />
              <div className="text-green-300 text-xs font-semibold">{val}</div>
              <div className="text-green-700 text-xs font-mono">{label}</div>
            </div>
          ))}
        </div>

        {/* Form card */}
        <div className="card p-8">
          {/* Mode toggle */}
          <div className="flex rounded-lg overflow-hidden border border-green-900/30 mb-6">
            {['login', 'register'].map((m) => (
              <button key={m} onClick={() => setMode(m)}
                className={`flex-1 py-2.5 text-sm font-mono font-medium transition-all duration-200 ${
                  mode === m
                    ? 'bg-green-500/10 text-green-400 border-b-2 border-green-400'
                    : 'text-green-700 hover:text-green-500'
                }`}>
                {m === 'login' ? 'Sign In' : 'Register'}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === 'register' && (
              <div>
                <label className="block text-green-500 text-xs font-mono mb-1.5 uppercase tracking-wider">Full Name</label>
                <input
                  type="text" required value={form.name}
                  onChange={(e) => set('name', e.target.value)}
                  placeholder="John Doe"
                  className="w-full bg-dark-950 border border-green-900/40 text-green-200 rounded-lg px-4 py-3 text-sm font-mono
                    placeholder-green-800 focus:outline-none focus:border-green-500/60 focus:ring-1 focus:ring-green-500/20 transition-all"
                />
              </div>
            )}
            <div>
              <label className="block text-green-500 text-xs font-mono mb-1.5 uppercase tracking-wider">Email</label>
              <input
                type="email" required value={form.email}
                onChange={(e) => set('email', e.target.value)}
                placeholder="admin@company.com"
                className="w-full bg-dark-950 border border-green-900/40 text-green-200 rounded-lg px-4 py-3 text-sm font-mono
                  placeholder-green-800 focus:outline-none focus:border-green-500/60 focus:ring-1 focus:ring-green-500/20 transition-all"
              />
            </div>
            <div>
              <label className="block text-green-500 text-xs font-mono mb-1.5 uppercase tracking-wider">Password</label>
              <div className="relative">
                <input
                  type={showPw ? 'text' : 'password'} required value={form.password}
                  onChange={(e) => set('password', e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-dark-950 border border-green-900/40 text-green-200 rounded-lg px-4 py-3 pr-12 text-sm font-mono
                    placeholder-green-800 focus:outline-none focus:border-green-500/60 focus:ring-1 focus:ring-green-500/20 transition-all"
                />
                <button type="button" onClick={() => setShowPw(!showPw)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-green-700 hover:text-green-400">
                  {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button type="submit" disabled={loading}
              className="btn-primary w-full py-3 rounded-lg text-sm font-mono font-bold mt-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2">
              {loading ? (
                <><div className="w-4 h-4 spinner" /> Processing...</>
              ) : (
                mode === 'login' ? '→ Access Platform' : '→ Create Account'
              )}
            </button>
          </form>

          {/* Demo credentials hint */}
          <div className="mt-5 p-3 rounded-lg bg-green-500/5 border border-green-900/30">
            <p className="text-green-700 text-xs font-mono text-center">
              Demo: any email + password • Backend required
            </p>
          </div>
        </div>

        <p className="text-center text-green-800 text-xs font-mono mt-6">
          GreenCode Guardian © 2024 • Sustainable Software Monitoring
        </p>
      </div>
    </div>
  );
}

import React, { useState } from 'react';

/**
 * LoginPage — Komorebi Glass design system (light only).
 * Cherry blossom / Mt. Fuji wallpaper, frosted glass hero + sign-in card.
 */
export default function LoginPage({ onLogin }) {
  const [email, setEmail]       = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState('');
  const [showPass, setShowPass] = useState(false);
  const [mode, setMode]         = useState('signin'); // 'signin' | 'signup'

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim() || !password.trim()) {
      setError('Please fill in all fields.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      // Try backend auth — gracefully fall through if offline
      const endpoint = mode === 'signin' ? '/auth/login' : '/auth/register';
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      }).catch(() => null);

      if (res && res.ok) {
        const data = await res.json();
        const name = data.user?.name || email.split('@')[0];
        onLogin(name, data.access_token || null);
      } else {
        // Offline / demo fallback
        const name = email.split('@')[0];
        onLogin(name, 'demo-token');
      }
    } catch {
      const name = email.split('@')[0];
      onLogin(name, 'demo-token');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen w-full overflow-hidden flex items-center justify-center">

      {/* ── Background: Cherry Blossom / Fuji wallpaper ──────────────────── */}
      <div
        aria-hidden="true"
        className="absolute inset-0 -z-20"
        style={{
          backgroundImage: `url('https://images.unsplash.com/photo-1522383225653-ed111181a951?w=1600&q=80')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center 30%',
        }}
      />
      {/* warm tint overlay */}
      <div
        aria-hidden="true"
        className="absolute inset-0 -z-10"
        style={{
          background: 'linear-gradient(135deg, rgba(252,249,246,0.45) 0%, rgba(240,140,101,0.08) 100%)',
        }}
      />

      {/* ── Layout Grid ─────────────────────────────────────────────────── */}
      <div className="w-full max-w-5xl mx-auto px-6 grid grid-cols-1 md:grid-cols-2 gap-6 items-center min-h-screen py-16">

        {/* LEFT — Hero panel */}
        <div className="glass-card rounded-3xl p-10 flex flex-col gap-6 select-none">
          {/* Logo wordmark */}
          <div className="flex items-center gap-3 mb-2">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center shadow-sm" style={{ background: 'linear-gradient(135deg, #e07248, #f08c65)' }}>
              <svg className="w-5 h-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2L2 7l10 5 10-5-10-5z" />
                <path d="M2 17l10 5 10-5" />
                <path d="M2 12l10 5 10-5" />
              </svg>
            </div>
            <span className="text-xl font-semibold tracking-tight" style={{ color: '#2D2622', fontFamily: "'Century Gothic', CenturyGothic, AppleGothic, sans-serif" }}>
              OptiCode
            </span>
          </div>

          {/* Hero heading */}
          <div>
            <h1 className="text-4xl font-semibold leading-tight tracking-tight mb-3" style={{ color: '#2D2622', letterSpacing: '-0.02em' }}>
              Think clearly.<br />
              <span style={{ color: '#f08c65' }}>Refine effortlessly.</span>
            </h1>
            <p className="text-base" style={{ color: '#6E625A', lineHeight: '1.7' }}>
              AI-powered code refinement that understands the structure of your programs, not just the surface.
            </p>
          </div>

          {/* Feature chips */}
          <div className="flex flex-col gap-3 mt-2">
            {[
              { icon: '⟨⟩', label: 'AST-Aware Refactoring', desc: 'Structural optimization beyond text edits' },
              { icon: '◈', label: 'Complexity Analysis',    desc: 'Live O(n) detection and suggestions' },
              { icon: '✦', label: 'Multi-Provider AI',      desc: 'Groq, OpenAI, local SLMs — your choice' },
            ].map(({ icon, label, desc }) => (
              <div key={label} className="flex items-start gap-3 p-3 rounded-2xl transition-colors" style={{ background: 'rgba(240,140,101,0.06)', border: '1px solid rgba(240,140,101,0.10)' }}>
                <span className="text-lg mt-0.5" style={{ color: '#e07248' }}>{icon}</span>
                <div>
                  <p className="text-sm font-semibold" style={{ color: '#2D2622' }}>{label}</p>
                  <p className="text-xs mt-0.5" style={{ color: '#A3968C' }}>{desc}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Footer quote */}
          <p className="text-xs mt-2" style={{ color: '#A3968C', letterSpacing: '0.04em', fontFamily: 'JetBrains Mono, monospace' }}>
            VIT Bhopal · Python · Rust · Type Script · Go · C++
          </p>
        </div>

        {/* RIGHT — Auth card */}
        <div className="glass-card rounded-3xl p-8 flex flex-col gap-6">

          {/* Card header */}
          <div>
            <h2 className="text-2xl font-semibold mb-1" style={{ color: '#2D2622', letterSpacing: '-0.015em' }}>
              {mode === 'signin' ? 'Welcome back' : 'Create account'}
            </h2>
            <p className="text-sm" style={{ color: '#6E625A' }}>
              {mode === 'signin'
                ? 'Sign in to your OptiCode workspace.'
                : 'Start refining code with OptiCode AI.'}
            </p>
          </div>

          {/* Tab row */}
          <div className="flex gap-1 p-1 rounded-xl" style={{ background: 'rgba(240,140,101,0.08)', border: '1px solid rgba(240,140,101,0.12)' }}>
            {['signin', 'signup'].map((m) => (
              <button
                key={m}
                onClick={() => { setMode(m); setError(''); }}
                className="flex-1 py-2 text-sm font-medium rounded-lg transition-all"
                style={mode === m
                  ? { background: 'linear-gradient(135deg, #e07248, #f08c65)', color: '#fff', boxShadow: '0 2px 8px rgba(224,114,72,0.30)' }
                  : { color: '#6E625A' }
                }
              >
                {m === 'signin' ? 'Sign In' : 'Sign Up'}
              </button>
            ))}
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div>
              <label className="block text-xs font-medium mb-1.5" style={{ color: '#6E625A', letterSpacing: '0.04em', fontFamily: 'JetBrains Mono, monospace' }}>
                EMAIL
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="glass-input w-full px-4 py-2.5 rounded-xl text-sm font-medium"
                style={{ color: '#2D2622', fontFamily: 'Plus Jakarta Sans, sans-serif' }}
                autoComplete="email"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-medium mb-1.5" style={{ color: '#6E625A', letterSpacing: '0.04em', fontFamily: 'JetBrains Mono, monospace' }}>
                PASSWORD
              </label>
              <div className="relative">
                <input
                  type={showPass ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="glass-input w-full px-4 py-2.5 rounded-xl text-sm font-medium pr-11"
                  style={{ color: '#2D2622', fontFamily: 'Plus Jakarta Sans, sans-serif' }}
                  autoComplete={mode === 'signin' ? 'current-password' : 'new-password'}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPass(!showPass)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-xs"
                  style={{ color: '#A3968C' }}
                  tabIndex={-1}
                >
                  {showPass ? '🙈' : '👁'}
                </button>
              </div>
            </div>

            {error && (
              <p className="text-xs px-3 py-2 rounded-lg" style={{ background: 'rgba(186,26,26,0.07)', color: '#93000a', border: '1px solid rgba(186,26,26,0.15)' }}>
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full py-3 rounded-xl text-sm font-semibold text-white tracking-wide mt-1 disabled:opacity-60"
            >
              {loading ? 'Signing in…' : mode === 'signin' ? 'Sign In →' : 'Create Account →'}
            </button>
          </form>

          {/* Divider */}
          <div className="flex items-center gap-3">
            <div className="flex-1 h-px" style={{ background: 'rgba(219,193,184,0.5)' }} />
            <span className="text-xs" style={{ color: '#A3968C', fontFamily: 'JetBrains Mono, monospace' }}>or try demo</span>
            <div className="flex-1 h-px" style={{ background: 'rgba(219,193,184,0.5)' }} />
          </div>

          {/* Demo button */}
          <button
            onClick={() => onLogin('Alex', 'demo-token')}
            className="w-full py-2.5 rounded-xl text-sm font-medium transition-all"
            style={{ background: 'rgba(240,140,101,0.08)', color: '#984726', border: '1px solid rgba(240,140,101,0.18)' }}
          >
            Continue as Demo User
          </button>
        </div>
      </div>
    </div>
  );
}

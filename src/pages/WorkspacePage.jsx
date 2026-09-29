import React, { useState, useRef, useEffect } from 'react';

/* ─── tiny icon helpers ──────────────────────────────────────────────── */
const Icon = ({ d, size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    {typeof d === 'string'
      ? <path d={d} />
      : d.map((p, i) => <path key={i} d={p} />)}
  </svg>
);

const LANG_OPTIONS = ['Python 3.11', 'JavaScript', 'TypeScript', 'Java', 'C++', 'Go', 'Rust'];

const PLACEHOLDER_CODE = `def find_duplicates(nums):
    """Find all duplicate values in a list."""
    seen = set()
    dupes = []
    for n in nums:
        if n in seen:
            dupes.append(n)
        seen.add(n)
    return dupes`;

const OPTIMIZED_CODE = `def find_duplicates(nums: list[int]) -> list[int]:
    """
    Find all duplicate values — O(N) time, O(N) space.
    Uses Counter to detect duplicates in a single pass.
    """
    from collections import Counter
    return [n for n, c in Counter(nums).items() if c > 1]`;

const EXPLANATION = `Replaced nested set-tracking loop with a single Counter pass.
Eliminates the separate seen/dupes state — now O(N) time and O(N) space.
Added type hints and a clear docstring for maintainability.`;

/* ─── Code panel with line numbers ──────────────────────────────────── */
function CodeArea({ code, dark, readOnly = false, onChange, placeholder }) {
  const lines = code.split('\n');
  if (!readOnly) {
    return (
      <textarea
        value={code}
        onChange={(e) => onChange?.(e.target.value)}
        placeholder={placeholder}
        className="w-full h-full resize-none text-xs font-mono focus:outline-none bg-transparent leading-5"
        style={{
          color: dark ? '#e2ddd9' : '#2D2622',
          minHeight: '180px',
          padding: '0',
          fontFamily: 'JetBrains Mono, monospace',
          letterSpacing: '0.01em',
        }}
        spellCheck={false}
      />
    );
  }
  return (
    <div className="relative flex overflow-auto" style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '12px', lineHeight: '20px' }}>
      {/* Line numbers */}
      <div className="select-none pr-4 text-right flex-shrink-0" style={{ color: dark ? 'rgba(255,255,255,0.18)' : 'rgba(45,38,34,0.25)', minWidth: '30px', paddingLeft: '0' }}>
        {lines.map((_, i) => <div key={i}>{i + 1}</div>)}
      </div>
      {/* Code */}
      <pre className="flex-1 overflow-x-auto whitespace-pre m-0 p-0" style={{ color: dark ? '#e2ddd9' : '#2D2622', background: 'transparent' }}>
        {code}
      </pre>
    </div>
  );
}

/* ─── Panel shell ────────────────────────────────────────────────────── */
function GlassPanel({ dark, children, className = '' }) {
  return (
    <div className={`rounded-3xl flex flex-col overflow-hidden transition-all duration-300 ${dark ? 'glass-card-dark' : 'glass-card'} ${className}`}>
      {children}
    </div>
  );
}

/* ─── Left: Code Input Panel ─────────────────────────────────────────── */
function CodeInputPanel({ dark, onOptimize, loading }) {
  const [prompt, setPrompt]   = useState('');
  const [code, setCode]       = useState(PLACEHOLDER_CODE);
  const [lang, setLang]       = useState('Python 3.11');
  const [showLang, setShowLang] = useState(false);

  const lineCount = code.split('\n').length;

  const dotColor = dark ? '#e07248' : '#f08c65';
  const textMain = dark ? '#e9e4e0' : '#2D2622';
  const textSub  = dark ? 'rgba(229,224,220,0.55)' : '#6E625A';
  const borderC  = dark ? 'rgba(255,255,255,0.07)' : 'rgba(219,193,184,0.40)';
  const subSurface = dark ? 'code-surface-dark' : 'code-surface-light';

  return (
    <GlassPanel dark={dark} className="h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4" style={{ borderBottom: `1px solid ${borderC}` }}>
        <div className="flex items-center gap-2.5">
          <div className="w-2.5 h-2.5 rounded-full" style={{ background: dotColor, boxShadow: `0 0 8px ${dotColor}66` }} />
          <span className="text-sm font-semibold" style={{ color: textMain }}>Code Input</span>
        </div>
        <div className="flex items-center gap-2">
          {/* Language selector */}
          <div className="relative">
            <button
              onClick={() => setShowLang(!showLang)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium transition-colors"
              style={{ background: dark ? 'rgba(255,255,255,0.06)' : 'rgba(240,140,101,0.08)', color: dotColor, border: `1px solid ${dark ? 'rgba(255,255,255,0.08)' : 'rgba(240,140,101,0.16)'}` }}
            >
              {lang}
              <Icon d="M6 9l6 6 6-6" size={12} />
            </button>
            {showLang && (
              <div className="absolute right-0 top-full mt-1 z-50 rounded-2xl overflow-hidden shadow-xl py-1" style={{ background: dark ? '#151b28' : '#fff', border: `1px solid ${borderC}`, minWidth: '140px' }}>
                {LANG_OPTIONS.map((l) => (
                  <button key={l} onClick={() => { setLang(l); setShowLang(false); }}
                    className="w-full text-left px-4 py-2 text-xs transition-colors hover:bg-opacity-10"
                    style={{ color: textMain, background: lang === l ? (dark ? 'rgba(240,140,101,0.12)' : 'rgba(240,140,101,0.07)') : 'transparent' }}>
                    {l}
                  </button>
                ))}
              </div>
            )}
          </div>
          {/* Paste button */}
          <button
            onClick={async () => { try { const t = await navigator.clipboard.readText(); setCode(t); } catch {} }}
            title="Paste from clipboard"
            className="p-1.5 rounded-lg transition-colors"
            style={{ color: textSub }}
          >
            <Icon d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" size={14} />
          </button>
          {/* Clear button */}
          <button onClick={() => { setCode(''); setPrompt(''); }} title="Clear" className="p-1.5 rounded-lg transition-colors" style={{ color: textSub }}>
            <Icon d="M6 18L18 6M6 6l12 12" size={14} />
          </button>
        </div>
      </div>

      {/* Prompt input bar */}
      <div className="px-4 pt-4 pb-2">
        <div className="flex items-center gap-2 px-3 py-2 rounded-2xl" style={{ background: dark ? 'rgba(255,255,255,0.05)' : 'rgba(240,140,101,0.06)', border: `1px solid ${borderC}` }}>
          <span style={{ color: dotColor, fontSize: '15px' }}>✦</span>
          <input
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe the optimization goal… (e.g. reduce time complexity)"
            className="flex-1 bg-transparent text-xs focus:outline-none"
            style={{ color: textMain, fontFamily: 'Plus Jakarta Sans, sans-serif' }}
            onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); onOptimize?.(code, prompt, lang); } }}
          />
        </div>
      </div>

      {/* Code area */}
      <div className={`flex-1 mx-4 mb-4 rounded-2xl p-4 overflow-auto ${subSurface}`} style={{ minHeight: '180px' }}>
        <CodeArea code={code} dark={dark} readOnly={false} onChange={setCode} placeholder="// Paste your code here…" />
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between px-5 pb-5">
        <span className="text-xs font-mono" style={{ color: textSub, fontFamily: 'JetBrains Mono, monospace', letterSpacing: '0.04em' }}>
          {lineCount} lines · {lang}
        </span>
        <button
          onClick={() => onOptimize?.(code, prompt, lang)}
          disabled={loading || !code.trim()}
          className={`px-6 py-2.5 rounded-xl text-sm font-semibold text-white tracking-wide disabled:opacity-50 transition-all ${dark ? 'btn-primary-dark' : 'btn-primary'}`}
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
              </svg>
              Refining…
            </span>
          ) : 'Improve Code →'}
        </button>
      </div>
    </GlassPanel>
  );
}

/* ─── Right: Output Panel ────────────────────────────────────────────── */
function OutputPanel({ dark, code, explanation, loading }) {
  const textMain = dark ? '#e9e4e0' : '#2D2622';
  const textSub  = dark ? 'rgba(229,224,220,0.55)' : '#6E625A';
  const borderC  = dark ? 'rgba(255,255,255,0.07)' : 'rgba(219,193,184,0.40)';
  const subSurface = dark ? 'code-surface-dark' : 'code-surface-light';
  const dotColor = '#22c55e';

  const handleCopy = () => navigator.clipboard.writeText(code).catch(() => {});

  return (
    <GlassPanel dark={dark} className="h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4" style={{ borderBottom: `1px solid ${borderC}` }}>
        <div className="flex items-center gap-2.5">
          <div className="w-2.5 h-2.5 rounded-full" style={{ background: dotColor, boxShadow: `0 0 8px ${dotColor}66` }} />
          <span className="text-sm font-semibold" style={{ color: textMain }}>OptiCode</span>
          {loading && (
            <span className="text-xs px-2 py-0.5 rounded-full font-mono" style={{ background: 'rgba(240,140,101,0.12)', color: '#e07248', fontFamily: 'JetBrains Mono, monospace' }}>
              Processing…
            </span>
          )}
        </div>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium transition-all"
          style={{ background: dark ? 'rgba(255,255,255,0.06)' : 'rgba(240,140,101,0.08)', color: '#f08c65', border: `1px solid ${dark ? 'rgba(255,255,255,0.08)' : 'rgba(240,140,101,0.16)'}` }}
        >
          <Icon d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" size={12} />
          Copy
        </button>
      </div>

      {/* Optimized code */}
      <div className={`flex-1 mx-4 mt-4 rounded-2xl p-4 overflow-auto ${subSurface}`} style={{ minHeight: '180px' }}>
        {loading ? (
          <div className="flex flex-col gap-3 animate-pulse">
            {[80, 55, 90, 45, 70].map((w, i) => (
              <div key={i} className="h-3 rounded" style={{ width: `${w}%`, background: dark ? 'rgba(255,255,255,0.08)' : 'rgba(45,38,34,0.08)' }} />
            ))}
          </div>
        ) : (
          <CodeArea code={code} dark={dark} readOnly />
        )}
      </div>

      {/* Explanation */}
      {explanation && !loading && (
        <div className="mx-4 mt-2 mb-2 px-4 py-3 rounded-2xl" style={{ background: dark ? 'rgba(34,197,94,0.07)' : 'rgba(34,197,94,0.05)', border: `1px solid ${dark ? 'rgba(34,197,94,0.15)' : 'rgba(34,197,94,0.12)'}` }}>
          <p className="text-xs leading-relaxed" style={{ color: dark ? 'rgba(229,224,220,0.75)' : '#6E625A' }}>
            {explanation}
          </p>
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between px-5 pb-5 pt-2">
        {!loading && code ? (
          <>
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="#22c55e" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="20 6 9 17 4 12" />
              </svg>
              <span className="text-xs" style={{ color: dark ? 'rgba(229,224,220,0.60)' : textSub }}>Optimized</span>
            </div>
            <span className="text-xs font-mono px-2 py-0.5 rounded-full" style={{ background: dark ? 'rgba(240,140,101,0.10)' : 'rgba(240,140,101,0.08)', color: '#e07248', fontFamily: 'JetBrains Mono, monospace' }}>
              O(N)
            </span>
          </>
        ) : (
          <span className="text-xs" style={{ color: textSub }}>Results will appear here</span>
        )}
      </div>
    </GlassPanel>
  );
}

/* ─── WorkspacePage ──────────────────────────────────────────────────── */
export default function WorkspacePage({ dark, onToggleDark, userName, onLogout }) {
  const [activeTab,    setActiveTab]    = useState('refiner');
  const [outputCode,   setOutputCode]   = useState(OPTIMIZED_CODE);
  const [explanation,  setExplanation]  = useState(EXPLANATION);
  const [loading,      setLoading]      = useState(false);

  /* Background: cherry blossom in light, dark cosmic in dark */
  const bgStyle = dark
    ? {
        background: '#07090e',
        backgroundImage: `
          radial-gradient(ellipse 80% 60% at 20% 0%, rgba(240,140,101,0.045) 0%, transparent 60%),
          radial-gradient(ellipse 50% 50% at 80% 100%, rgba(114, 80, 160, 0.04) 0%, transparent 55%)
        `,
      }
    : {
        backgroundImage: `url('https://images.unsplash.com/photo-1522383225653-ed111181a951?w=1600&q=80')`,
        backgroundSize: 'cover',
        backgroundPosition: 'center 30%',
      };

  const textMain = dark ? '#e9e4e0' : '#2D2622';
  const textSub  = dark ? 'rgba(229,224,220,0.55)' : '#6E625A';

  const handleOptimize = async (code, prompt, lang) => {
    if (!code.trim()) return;
    setLoading(true);
    setOutputCode('');
    setExplanation('');
    try {
      const res = await fetch('/code/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-User-Id': '11111111-2222-3333-4444-555555555555' },
        body: JSON.stringify({ code, prompt: prompt || 'Optimize this code for performance and readability.', language: lang }),
      }).catch(() => null);

      if (res && res.ok) {
        const data = await res.json();
        setOutputCode(data.optimized_code || OPTIMIZED_CODE);
        setExplanation(data.explanation || EXPLANATION);
      } else {
        // Demo fallback
        await new Promise((r) => setTimeout(r, 1400));
        setOutputCode(OPTIMIZED_CODE);
        setExplanation(EXPLANATION);
      }
    } finally {
      setLoading(false);
    }
  };

  const navTabs = [
    { id: 'refiner',   label: 'Refiner' },
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'history',   label: 'History' },
  ];

  return (
    <div className="relative min-h-screen w-full overflow-hidden flex flex-col" style={bgStyle}>

      {/* Light mode warm overlay */}
      {!dark && (
        <div aria-hidden className="absolute inset-0 pointer-events-none" style={{ background: 'rgba(252,249,246,0.30)', zIndex: 0 }} />
      )}

      {/* ── Floating Header ─────────────────────────────────────────── */}
      <div className="relative z-10 flex items-center justify-between px-6 pt-5">

        {/* Logo */}
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #e07248, #f08c65)' }}>
            <svg className="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2L2 7l10 5 10-5-10-5z" /><path d="M2 17l10 5 10-5" /><path d="M2 12l10 5 10-5" />
            </svg>
          </div>
          <span className="text-lg font-semibold" style={{ color: dark ? '#f0ebe6' : '#2D2622', fontFamily: "'Century Gothic', CenturyGothic, AppleGothic, sans-serif" }}>
            OptiCode
          </span>
        </div>

        {/* Center: pill nav */}
        <nav className={`flex items-center gap-1 px-2 py-2 rounded-2xl ${dark ? 'nav-pill' : 'nav-pill-light'}`}>
          {navTabs.map(({ id, label }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              className="px-4 py-1.5 rounded-xl text-sm font-medium transition-all duration-200"
              style={activeTab === id
                ? { background: 'linear-gradient(135deg,#e07248,#f08c65)', color: '#fff', boxShadow: '0 2px 10px rgba(224,114,72,0.35)' }
                : { color: dark ? 'rgba(229,224,220,0.65)' : '#6E625A' }
              }
            >
              {label}
            </button>
          ))}
        </nav>

        {/* Right controls */}
        <div className="flex items-center gap-2">
          {/* Theme toggle */}
          <button
            onClick={onToggleDark}
            title="Toggle theme"
            className="w-9 h-9 flex items-center justify-center rounded-xl transition-all"
            style={{ background: dark ? 'rgba(255,255,255,0.08)' : 'rgba(45,38,34,0.07)', color: dark ? '#f0c080' : '#6E625A' }}
          >
            {dark
              ? <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="5" /><line x1="12" y1="1" x2="12" y2="3" /><line x1="12" y1="21" x2="12" y2="23" /><line x1="4.22" y1="4.22" x2="5.64" y2="5.64" /><line x1="18.36" y1="18.36" x2="19.78" y2="19.78" /><line x1="1" y1="12" x2="3" y2="12" /><line x1="21" y1="12" x2="23" y2="12" /><line x1="4.22" y1="19.78" x2="5.64" y2="18.36" /><line x1="18.36" y1="5.64" x2="19.78" y2="4.22" /></svg>
              : <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" /></svg>
            }
          </button>

          {/* User avatar */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl" style={{ background: dark ? 'rgba(255,255,255,0.07)' : 'rgba(45,38,34,0.06)', cursor: 'default' }}>
            <div className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white" style={{ background: 'linear-gradient(135deg, #e07248, #f08c65)' }}>
              {userName.charAt(0).toUpperCase()}
            </div>
            <span className="text-xs font-medium" style={{ color: dark ? 'rgba(229,224,220,0.75)' : '#6E625A' }}>
              {userName}
            </span>
          </div>

          {/* Logout */}
          <button onClick={onLogout} title="Sign out" className="w-8 h-8 flex items-center justify-center rounded-xl transition-colors" style={{ color: dark ? 'rgba(229,224,220,0.45)' : 'rgba(45,38,34,0.35)' }}>
            <Icon d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" size={16} />
          </button>
        </div>
      </div>

      {/* ── Greeting ────────────────────────────────────────────────── */}
      <div className="relative z-10 px-6 mt-4 mb-3">
        <h2 className="text-2xl font-semibold" style={{ color: textMain, letterSpacing: '-0.015em' }}>
          Hello, <span style={{ color: '#f08c65' }}>{userName}</span> ✦
        </h2>
        <p className="text-sm mt-0.5" style={{ color: textSub }}>
          {activeTab === 'refiner'   && 'Paste your code, describe the goal, and let OptiCode refine it.'}
          {activeTab === 'dashboard' && 'Your optimization workspace overview.'}
          {activeTab === 'history'   && 'Your past refinement sessions.'}
        </p>
      </div>

      {/* ── Main content ─────────────────────────────────────────────── */}
      <main className="relative z-10 flex-1 px-6 pb-6">
        {activeTab === 'refiner' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 h-full" style={{ minHeight: '520px' }}>
            <CodeInputPanel dark={dark} onOptimize={handleOptimize} loading={loading} />
            <OutputPanel   dark={dark} code={outputCode} explanation={explanation} loading={loading} />
          </div>
        )}

        {activeTab === 'dashboard' && (
          <div className={`rounded-3xl p-8 ${dark ? 'glass-card-dark' : 'glass-card'}`}>
            <h3 className="text-lg font-semibold mb-2" style={{ color: textMain }}>Dashboard</h3>
            <p className="text-sm" style={{ color: textSub }}>
              Your recent activity and optimization metrics will appear here.
            </p>
            <div className="mt-6 grid grid-cols-3 gap-4">
              {[
                { label: 'Sessions',       value: '12' },
                { label: 'Lines Refined',  value: '1,482' },
                { label: 'Avg. Speedup',   value: '3.2×' },
              ].map(({ label, value }) => (
                <div key={label} className="p-4 rounded-2xl text-center" style={{ background: dark ? 'rgba(255,255,255,0.05)' : 'rgba(240,140,101,0.06)', border: `1px solid ${dark ? 'rgba(255,255,255,0.07)' : 'rgba(240,140,101,0.10)'}` }}>
                  <p className="text-2xl font-bold" style={{ color: '#f08c65' }}>{value}</p>
                  <p className="text-xs mt-1" style={{ color: textSub }}>{label}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'history' && (
          <div className={`rounded-3xl p-8 ${dark ? 'glass-card-dark' : 'glass-card'}`}>
            <h3 className="text-lg font-semibold mb-4" style={{ color: textMain }}>Session History</h3>
            {[
              { lang: 'Python', snippet: 'find_duplicates() — O(N²)→O(N)', time: '2 hours ago' },
              { lang: 'JS',     snippet: 'debounce() — rewrite with AbortController', time: 'Yesterday' },
              { lang: 'Java',   snippet: 'BubbleSort → TimSort',  time: '3 days ago' },
            ].map(({ lang, snippet, time }) => (
              <div key={snippet} className="flex items-center justify-between py-3" style={{ borderBottom: `1px solid ${dark ? 'rgba(255,255,255,0.05)' : 'rgba(219,193,184,0.30)'}` }}>
                <div className="flex items-center gap-3">
                  <span className="px-2 py-0.5 rounded-lg text-xs font-mono" style={{ background: dark ? 'rgba(240,140,101,0.10)' : 'rgba(240,140,101,0.08)', color: '#e07248' }}>{lang}</span>
                  <span className="text-sm" style={{ color: textMain }}>{snippet}</span>
                </div>
                <span className="text-xs" style={{ color: textSub }}>{time}</span>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

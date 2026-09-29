import React, { useState } from 'react';
import { 
  Send, 
  Sparkles, 
  Copy, 
  Check, 
  RotateCcw, 
  GitCompare, 
  FileCode, 
  Zap 
} from 'lucide-react';

export default function CodeRefinerView({
  code,
  onChangeCode,
  optimizedCode,
  benchmarks,
  messages,
  onSendMessage,
  onRunOptimize,
  onResetCode,
  isProcessing,
  activeProblem
}) {
  const [activeEditorTab, setActiveEditorTab] = useState('editor'); // 'editor' | 'optimized' | 'diff'
  const [inputPrompt, setInputPrompt] = useState('');
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    const textToCopy = activeEditorTab === 'optimized' ? (optimizedCode || code) : code;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSend = (e) => {
    e.preventDefault();
    if (!inputPrompt.trim() || isProcessing) return;
    onSendMessage(inputPrompt.trim());
    setInputPrompt('');
  };

  const lineCount = (code || '').split('\n').length;
  const lineNumbers = Array.from({ length: Math.max(lineCount, 16) }, (_, i) => i + 1);

  return (
    <div className="flex-1 flex gap-5 h-[calc(100vh-6.5rem)] overflow-hidden">
      {/* LEFT PANEL: Minimalist Chat / Prompt Thread */}
      <div className="w-[42%] bg-white dark:bg-zinc-900 rounded-2xl border border-slate-200 dark:border-zinc-800 shadow-sm flex flex-col overflow-hidden">
        {/* Chat Header */}
        <div className="px-5 py-4 border-b border-slate-200 dark:border-zinc-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-2.5 h-2.5 rounded-full bg-[#FA8C75]" />
            <h3 className="font-semibold text-sm text-[#1E1B2E] dark:text-zinc-100">
              Prompt & Refiner Assistant
            </h3>
          </div>
          <span className="text-[11px] font-mono font-medium px-2.5 py-0.5 rounded-full bg-[#FA8C75]/15 text-[#FA8C75]">
            AST Gate Active
          </span>
        </div>

        {/* Message Thread */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {messages.map((msg, i) => {
            const isUser = msg.role === 'user';
            return (
              <div 
                key={msg.id || i} 
                className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}
              >
                <div className="text-[10px] text-slate-400 dark:text-zinc-400 mb-1 px-1 font-medium">
                  {isUser ? 'You' : 'OptiCode Engine'}
                </div>
                
                <div 
                  className={`rounded-2xl p-4 text-xs max-w-[90%] leading-relaxed ${
                    isUser
                      ? 'bg-[#1E1B2E] dark:bg-slate-800 text-white rounded-tr-none shadow-sm'
                      : 'bg-slate-50 dark:bg-zinc-800/80 text-slate-800 dark:text-zinc-200 border border-slate-200/80 dark:border-zinc-700/80 rounded-tl-none'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{msg.content}</p>

                  {/* Clean Minimalist Refactor Decision */}
                  {msg.metadata?.astGate && (
                    <div className="mt-3 pt-3 border-t border-slate-200 dark:border-zinc-700 text-[11px]">
                      <div className="flex items-center justify-between font-medium">
                        <span className="text-slate-500 dark:text-zinc-400">Gate Decision:</span>
                        <span className="font-mono font-bold text-[#FA8C75]">
                          {msg.metadata.astGate.status}
                        </span>
                      </div>
                      <p className="mt-1 text-slate-600 dark:text-zinc-300 text-[10px]">
                        {msg.metadata.astGate.reasoning}
                      </p>
                    </div>
                  )}

                  {msg.metadata?.benchmarks && (
                    <div className="mt-2.5 p-2 rounded-xl bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-700 flex items-center justify-between text-[11px] font-mono">
                      <span className="text-emerald-600 dark:text-emerald-400 font-bold">
                        {msg.metadata.benchmarks.speedup} Speedup
                      </span>
                      <span className="text-slate-500 dark:text-zinc-400">
                        {msg.metadata.benchmarks.memoryDelta} RAM
                      </span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}

          {isProcessing && (
            <div className="flex items-center space-x-2 text-xs text-[#FA8C75] p-3 rounded-xl bg-[#FA8C75]/10 w-fit">
              <Sparkles className="w-3.5 h-3.5 animate-spin" />
              <span>Analyzing AST & refactoring algorithm...</span>
            </div>
          )}
        </div>

        {/* Input Bar */}
        <form onSubmit={handleSend} className="p-4 border-t border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
          <div className="flex items-center space-x-2 bg-slate-50 dark:bg-zinc-800/90 rounded-xl px-3 py-2 border border-slate-200 dark:border-zinc-700 focus-within:border-[#FA8C75] focus-within:ring-1 focus-within:ring-[#FA8C75]/30 transition">
            <input
              type="text"
              value={inputPrompt}
              onChange={(e) => setInputPrompt(e.target.value)}
              placeholder="Ask OptiCode to optimize loops or reduce Big-O..."
              className="flex-1 bg-transparent text-xs text-slate-800 dark:text-zinc-200 placeholder-slate-400 dark:placeholder-zinc-500 focus:outline-none"
            />
            <button
              type="submit"
              disabled={!inputPrompt.trim() || isProcessing}
              className="w-7 h-7 rounded-lg bg-[#FA8C75] hover:bg-[#F5785F] text-white flex items-center justify-center transition disabled:opacity-40 disabled:cursor-not-allowed shrink-0 shadow-sm"
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </div>
        </form>
      </div>

      {/* RIGHT PANEL: Clean Light-Themed Code Editor Card */}
      <div className="w-[58%] bg-white dark:bg-zinc-900 rounded-2xl border border-slate-200 dark:border-zinc-800 shadow-sm flex flex-col overflow-hidden">
        {/* Editor Tab Header */}
        <div className="px-5 py-3 border-b border-slate-200 dark:border-zinc-800 flex items-center justify-between bg-white dark:bg-zinc-900">
          {/* Tabs */}
          <div className="flex items-center space-x-1.5">
            <button
              onClick={() => setActiveEditorTab('editor')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                activeEditorTab === 'editor'
                  ? 'bg-slate-100 dark:bg-zinc-800 text-slate-900 dark:text-white'
                  : 'text-slate-500 hover:text-slate-800 dark:text-zinc-400 dark:hover:text-zinc-200'
              }`}
            >
              <FileCode className="w-3.5 h-3.5 text-[#FA8C75]" />
              <span>Original Code</span>
            </button>

            <button
              onClick={() => setActiveEditorTab('optimized')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                activeEditorTab === 'optimized'
                  ? 'bg-slate-100 dark:bg-zinc-800 text-slate-900 dark:text-white'
                  : 'text-slate-500 hover:text-slate-800 dark:text-zinc-400 dark:hover:text-zinc-200'
              }`}
            >
              <Sparkles className="w-3.5 h-3.5 text-emerald-500" />
              <span>Optimized O(N)</span>
            </button>

            <button
              onClick={() => setActiveEditorTab('diff')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                activeEditorTab === 'diff'
                  ? 'bg-slate-100 dark:bg-zinc-800 text-slate-900 dark:text-white'
                  : 'text-slate-500 hover:text-slate-800 dark:text-zinc-400 dark:hover:text-zinc-200'
              }`}
            >
              <GitCompare className="w-3.5 h-3.5 text-indigo-500" />
              <span>Diff View</span>
            </button>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-2">
            <button
              onClick={handleCopy}
              className="p-1.5 rounded-lg text-slate-500 hover:text-slate-700 dark:text-zinc-400 dark:hover:text-zinc-200 hover:bg-slate-100 dark:hover:bg-zinc-800 transition"
              title="Copy code"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
            </button>

            <button
              onClick={onResetCode}
              className="p-1.5 rounded-lg text-slate-500 hover:text-slate-700 dark:text-zinc-400 dark:hover:text-zinc-200 hover:bg-slate-100 dark:hover:bg-zinc-800 transition"
              title="Reset code"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>

            {/* Primary Action Button: Warm Coral */}
            <button
              onClick={onRunOptimize}
              disabled={isProcessing}
              className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl bg-[#FA8C75] hover:bg-[#F5785F] text-white text-xs font-semibold transition shadow-sm disabled:opacity-50"
            >
              <Zap className="w-3.5 h-3.5" />
              <span>{isProcessing ? 'Optimizing...' : 'Run AST Refactor'}</span>
            </button>
          </div>
        </div>

        {/* Editor Body */}
        <div className="flex-1 overflow-auto bg-[#FAFAFC] dark:bg-zinc-950 font-mono text-xs leading-relaxed flex relative">
          {activeEditorTab === 'editor' && (
            <div className="flex flex-1 w-full min-h-full">
              {/* Line numbers gutter */}
              <div className="w-11 bg-slate-100/70 dark:bg-zinc-900 text-slate-400 dark:text-zinc-500 select-none text-right pr-3 pt-3 border-r border-slate-200 dark:border-zinc-800 shrink-0">
                {lineNumbers.map((num) => (
                  <div key={num} className="leading-6 h-6">{num}</div>
                ))}
              </div>

              {/* Editable Code Area */}
              <div className="flex-1 p-3">
                <textarea
                  value={code}
                  onChange={(e) => onChangeCode(e.target.value)}
                  spellCheck="false"
                  className="w-full h-full min-h-[420px] bg-transparent text-slate-800 dark:text-zinc-100 font-mono resize-none focus:outline-none leading-6 selection:bg-[#FA8C75]/25"
                />
              </div>
            </div>
          )}

          {activeEditorTab === 'optimized' && (
            <div className="flex flex-1 w-full min-h-full p-4 overflow-auto">
              <pre className="text-emerald-700 dark:text-emerald-400 font-mono whitespace-pre-wrap leading-6">
                {optimizedCode || code}
              </pre>
            </div>
          )}

          {activeEditorTab === 'diff' && (
            <div className="flex-1 grid grid-cols-2 divide-x divide-slate-200 dark:divide-zinc-800 h-full">
              <div className="p-4 overflow-auto bg-red-50/40 dark:bg-red-950/20">
                <div className="text-[10px] font-bold text-red-500 uppercase tracking-wider mb-2">
                  Original (Inefficient)
                </div>
                <pre className="text-slate-700 dark:text-zinc-300 whitespace-pre-wrap">{code}</pre>
              </div>
              <div className="p-4 overflow-auto bg-emerald-50/40 dark:bg-emerald-950/20">
                <div className="text-[10px] font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider mb-2">
                  Refactored (Optimized)
                </div>
                <pre className="text-emerald-700 dark:text-emerald-300 whitespace-pre-wrap">{optimizedCode || code}</pre>
              </div>
            </div>
          )}
        </div>

        {/* Minimal Status Footer */}
        <div className="px-5 py-2.5 bg-white dark:bg-zinc-900 border-t border-slate-200 dark:border-zinc-800 flex items-center justify-between text-xs font-mono">
          <div className="flex items-center space-x-3 text-slate-600 dark:text-zinc-300">
            <span className="font-semibold text-slate-800 dark:text-zinc-100">
              {activeProblem?.title || 'Active Algorithm'}
            </span>
            <span>•</span>
            <span className="text-[#FA8C75] font-bold">
              {activeProblem?.complexity || 'O(N²)'} → {activeProblem?.targetComplexity || 'O(N)'}
            </span>
          </div>

          <div className="flex items-center space-x-3 text-[11px] text-slate-500 dark:text-zinc-400">
            <span className="text-emerald-600 dark:text-emerald-400 font-semibold">
              {benchmarks?.speedup || '3.4x'} Speedup
            </span>
            <span>•</span>
            <span>{benchmarks?.memoryDelta || '-18.4 MB'} RAM</span>
            <span>•</span>
            <span className="text-slate-400 dark:text-zinc-500">Tree-sitter Verified</span>
          </div>
        </div>
      </div>
    </div>
  );
}

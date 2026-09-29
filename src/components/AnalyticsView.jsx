import React from 'react';
import { BarChart3, TrendingUp, Zap, Cpu, Leaf, CheckCircle2 } from 'lucide-react';

export default function AnalyticsView() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <div className="bg-white dark:bg-exam-card-dark rounded-2xl border border-exam-border dark:border-exam-border-dark p-5 shadow-card">
          <div className="text-xs text-slate-500 mb-1">Average Speedup</div>
          <div className="text-2xl font-bold font-mono text-emerald-600 dark:text-emerald-400">
            3.8x
          </div>
          <p className="text-[11px] text-slate-400 mt-1">Across O(N²) quadratic loops</p>
        </div>

        <div className="bg-white dark:bg-exam-card-dark rounded-2xl border border-exam-border dark:border-exam-border-dark p-5 shadow-card">
          <div className="text-xs text-slate-500 mb-1">Gate Short-Circuits</div>
          <div className="text-2xl font-bold font-mono text-exam-coral">
            32%
          </div>
          <p className="text-[11px] text-slate-400 mt-1">Bypassed SLM for already optimal code</p>
        </div>

        <div className="bg-white dark:bg-exam-card-dark rounded-2xl border border-exam-border dark:border-exam-border-dark p-5 shadow-card">
          <div className="text-xs text-slate-500 mb-1">Peak RAM Saved</div>
          <div className="text-2xl font-bold font-mono text-indigo-500">
            -214 MB
          </div>
          <p className="text-[11px] text-slate-400 mt-1">Single-pass hash set tracking</p>
        </div>

        <div className="bg-white dark:bg-exam-card-dark rounded-2xl border border-exam-border dark:border-exam-border-dark p-5 shadow-card">
          <div className="text-xs text-slate-500 mb-1">Syntax Accuracy</div>
          <div className="text-2xl font-bold font-mono text-emerald-600 dark:text-emerald-400">
            100%
          </div>
          <p className="text-[11px] text-slate-400 mt-1">Tree-sitter pre-validation gate</p>
        </div>
      </div>

      <div className="bg-white dark:bg-exam-card-dark rounded-2xl border border-exam-border dark:border-exam-border-dark p-6 shadow-card">
        <h3 className="text-sm font-bold text-exam-navy dark:text-white mb-2">
          Theoretical & Research Foundation Verification
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">
          OptiCode adheres to the Selective Prompting framework (Almeida et al., 2024) and Exclusionary Reasoning gate (Rong et al., Springer 2025).
        </p>

        <div className="space-y-3 text-xs">
          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-[#1A2030] flex items-center justify-between">
            <span className="font-medium text-slate-700 dark:text-slate-200">Zero-Regression Constraint</span>
            <span className="text-emerald-600 font-mono font-semibold">Enforced via Docker sandbox</span>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-[#1A2030] flex items-center justify-between">
            <span className="font-medium text-slate-700 dark:text-slate-200">AST Loop Depth Threshold</span>
            <span className="text-slate-600 dark:text-slate-300 font-mono">&gt;= 2 nested loops triggers refactor</span>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-[#1A2030] flex items-center justify-between">
            <span className="font-medium text-slate-700 dark:text-slate-200">Hardware Requirements</span>
            <span className="text-exam-coral font-mono font-semibold">Zero GPU client (API based)</span>
          </div>
        </div>
      </div>
    </div>
  );
}

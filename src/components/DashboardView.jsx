import React from 'react';
import { 
  Sparkles, 
  Code2, 
  ArrowUpRight, 
  Zap, 
  ShieldCheck, 
  Leaf, 
  Clock,
  ChevronRight
} from 'lucide-react';

export default function DashboardView({ 
  onStartRefactor,
  sampleProblems,
  onSelectProblem
}) {
  return (
    <div className="space-y-6">
      {/* Top Welcome / Header Card */}
      <div className="bg-white dark:bg-exam-card-dark rounded-2xl border border-exam-border dark:border-exam-border-dark p-8 shadow-card flex flex-col items-center justify-center text-center py-14">
        {/* Soft Circular Icon */}
        <div className="w-16 h-16 rounded-2xl bg-exam-coral/10 dark:bg-exam-coral/20 flex items-center justify-center mb-5 text-exam-coral shadow-inner">
          <Sparkles className="w-8 h-8" />
        </div>

        <h2 className="text-xl font-bold text-exam-navy dark:text-white mb-2">
          Optimization Workspace Ready
        </h2>
        <p className="text-xs text-slate-500 dark:text-slate-400 max-w-md leading-relaxed mb-6">
          OptiCode uses Tree-sitter AST parsing and Exclusionary Reasoning to refactor quadratic algorithms into linear time complexity without hallucination.
        </p>

        <button
          onClick={onStartRefactor}
          className="px-6 py-2.5 rounded-xl bg-exam-coral hover:bg-exam-coral-hover text-white text-xs font-semibold transition shadow-sm flex items-center space-x-2"
        >
          <span>Open Code Refiner</span>
          <ArrowUpRight className="w-4 h-4" />
        </button>
      </div>

      {/* 3 Minimalist Overview Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* Card 1 */}
        <div className="bg-white dark:bg-exam-card-dark rounded-2xl border border-exam-border dark:border-exam-border-dark p-5 shadow-card">
          <div className="flex items-center justify-between text-slate-500 mb-3">
            <span className="text-xs font-medium">Algorithmic Target</span>
            <Zap className="w-4 h-4 text-exam-coral" />
          </div>
          <div className="text-2xl font-bold font-mono text-exam-navy dark:text-white mb-1">
            O(N²) → O(N)
          </div>
          <p className="text-[11px] text-slate-400">
            Automated loop unnesting & hash-map reduction
          </p>
        </div>

        {/* Card 2 */}
        <div className="bg-white dark:bg-exam-card-dark rounded-2xl border border-exam-border dark:border-exam-border-dark p-5 shadow-card">
          <div className="flex items-center justify-between text-slate-500 mb-3">
            <span className="text-xs font-medium">Verification Gate</span>
            <ShieldCheck className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-2xl font-bold font-mono text-exam-navy dark:text-white mb-1">
            100% Passed
          </div>
          <p className="text-[11px] text-slate-400">
            Tree-sitter pre-validation + Docker compilation
          </p>
        </div>

        {/* Card 3 */}
        <div className="bg-white dark:bg-exam-card-dark rounded-2xl border border-exam-border dark:border-exam-border-dark p-5 shadow-card">
          <div className="flex items-center justify-between text-slate-500 mb-3">
            <span className="text-xs font-medium">Eco-Efficiency</span>
            <Leaf className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-bold font-mono text-exam-navy dark:text-white mb-1">
            8B SLM (Zero GPU)
          </div>
          <p className="text-[11px] text-slate-400">
            Eliminates high-carbon 70B+ cloud inference waste
          </p>
        </div>
      </div>

      {/* Preset Testcases Section */}
      <div className="bg-white dark:bg-exam-card-dark rounded-2xl border border-exam-border dark:border-exam-border-dark p-6 shadow-card">
        <h3 className="text-sm font-bold text-exam-navy dark:text-white mb-4">
          Quick-Load Research Testcases
        </h3>

        <div className="space-y-3">
          {sampleProblems.map((prob) => (
            <div
              key={prob.id}
              onClick={() => {
                onSelectProblem(prob);
                onStartRefactor();
              }}
              className="flex items-center justify-between p-3.5 rounded-xl border border-slate-100 dark:border-slate-800 hover:border-exam-coral hover:bg-slate-50 dark:hover:bg-[#1A2030] cursor-pointer transition"
            >
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-600 dark:text-slate-300">
                  <Code2 className="w-4 h-4" />
                </div>
                <div>
                  <div className="text-xs font-semibold text-exam-navy dark:text-white">{prob.title}</div>
                  <div className="text-[11px] text-slate-400">{prob.category}</div>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <span className="text-xs font-mono font-bold text-exam-coral">
                  {prob.complexity} → {prob.targetComplexity}
                </span>
                <ChevronRight className="w-4 h-4 text-slate-400" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

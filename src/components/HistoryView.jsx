import React from 'react';
import { Clock, MessageSquare, ArrowRight, Trash2, CheckCircle2 } from 'lucide-react';

export default function HistoryView({ 
  conversations, 
  activeConversationId, 
  onSelectConversation, 
  onDeleteConversation,
  onOpenRefiner
}) {
  return (
    <div className="bg-white dark:bg-exam-card-dark rounded-2xl border border-exam-border dark:border-exam-border-dark p-6 shadow-card space-y-4">
      <div className="flex items-center justify-between border-b border-exam-border dark:border-exam-border-dark pb-4">
        <div>
          <h3 className="font-bold text-sm text-exam-navy dark:text-white">
            Refactoring History & Sessions
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Previous AST-guided optimization sessions saved across your workspace.
          </p>
        </div>
      </div>

      <div className="divide-y divide-slate-100 dark:divide-slate-800">
        {conversations.map((c) => {
          const isActive = c.id === activeConversationId;
          return (
            <div 
              key={c.id}
              className="py-3.5 flex items-center justify-between hover:bg-slate-50 dark:hover:bg-[#1A2030] px-3 rounded-xl transition"
            >
              <div 
                className="flex items-center space-x-3 cursor-pointer flex-1"
                onClick={() => {
                  onSelectConversation(c.id);
                  onOpenRefiner();
                }}
              >
                <div className="w-8 h-8 rounded-lg bg-exam-coral/10 text-exam-coral flex items-center justify-center">
                  <MessageSquare className="w-4 h-4" />
                </div>
                <div>
                  <div className="text-xs font-semibold text-exam-navy dark:text-white flex items-center space-x-2">
                    <span>{c.title}</span>
                    {isActive && (
                      <span className="text-[10px] font-mono px-2 py-0.2 rounded-full bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300">
                        Active
                      </span>
                    )}
                  </div>
                  <div className="text-[11px] text-slate-400 font-mono mt-0.5">
                    ID: {c.id.substring(0, 8)} • {new Date(c.created_at || Date.now()).toLocaleDateString()}
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <button
                  onClick={() => {
                    onSelectConversation(c.id);
                    onOpenRefiner();
                  }}
                  className="px-3 py-1.5 rounded-lg text-xs font-medium text-exam-coral hover:bg-exam-coral/10 transition flex items-center space-x-1"
                >
                  <span>Resume</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => onDeleteConversation(c.id)}
                  className="p-1.5 text-slate-400 hover:text-red-500 rounded-lg transition"
                  title="Delete session"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

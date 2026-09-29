import React, { useState } from 'react';
import { 
  LayoutDashboard, 
  Sparkles, 
  Clock, 
  BarChart3, 
  Settings, 
  Cpu, 
  Sun, 
  Moon, 
  ChevronDown, 
  PanelLeftClose,
  PanelLeft,
  Check
} from 'lucide-react';

export default function Sidebar({
  activeTab,
  onSelectTab,
  isCollapsed,
  onToggleCollapse,
  darkMode,
  onToggleDarkMode,
  selectedProvider,
  onSelectProvider
}) {
  const [providerMenuOpen, setProviderMenuOpen] = useState(false);

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'refiner', label: 'Code Refiner', icon: Sparkles },
    { id: 'history', label: 'History', icon: Clock },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
  ];

  const providers = [
    { id: 'groq-slm', label: 'Groq / SLM (Fast)', tag: '8B Quantized' },
    { id: 'vllm-local', label: 'vLLM Local Engine', tag: 'DDR4/5 RAM' },
    { id: 'gemini-flash', label: 'Gemini 2.0 Flash', tag: 'Cloud API' },
    { id: 'openai-gpt4o', label: 'OpenAI GPT-4o', tag: 'Cloud API' },
  ];

  const currentProviderObj = providers.find(p => p.id === selectedProvider) || providers[0];

  return (
    <aside 
      className={`h-screen bg-[#12151E] text-slate-300 flex flex-col justify-between transition-all duration-300 select-none z-30 shrink-0 border-r border-slate-800/80 ${
        isCollapsed ? 'w-20' : 'w-64'
      }`}
    >
      {/* Top Section: Brand + User Profile + Navigation */}
      <div>
        {/* Brand Header */}
        <div className="h-20 px-6 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {/* Custom Brand Icon */}
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-[#FA8C75] to-[#FF8A65] flex items-center justify-center text-white font-bold text-sm shadow-md shrink-0">
              <span className="font-serif italic font-bold">O</span>
            </div>
            {!isCollapsed && (
              <span className="font-sans font-extrabold tracking-wider text-white text-base">
                OPTICODE
              </span>
            )}
          </div>

          <button
            onClick={onToggleCollapse}
            className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-slate-800/60 transition"
            title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {isCollapsed ? <PanelLeft className="w-4 h-4" /> : <PanelLeftClose className="w-4 h-4" />}
          </button>
        </div>

        {/* User Profile Badge (Examind Style) */}
        <div className="px-4 mb-6">
          <div className={`flex items-center space-x-3 p-2.5 rounded-xl bg-slate-900/60 border border-slate-800/80 ${isCollapsed ? 'justify-center' : ''}`}>
            <div className="w-9 h-9 rounded-full bg-[#5848C2] text-white flex items-center justify-center font-bold text-sm shadow-inner shrink-0">
              S
            </div>
            {!isCollapsed && (
              <div className="overflow-hidden">
                <div className="text-sm font-semibold text-white truncate">Shyamak Sharma</div>
                <div className="text-xs text-slate-400 truncate">VIT Bhopal</div>
              </div>
            )}
          </div>
        </div>

        {/* Navigation Items (Self-Contained Rounded-XL, No Negative Curves/Flares) */}
        <nav className="px-3 space-y-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;

            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id)}
                className={`w-full flex items-center h-11 px-3.5 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-slate-800 text-white font-semibold shadow-sm'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800/50'
                }`}
                title={item.label}
              >
                <Icon className={`w-5 h-5 shrink-0 transition ${
                  isActive ? 'text-[#FF8A65]' : 'text-slate-400 group-hover:text-white'
                }`} />
                {!isCollapsed && (
                  <span className="ml-3 truncate">{item.label}</span>
                )}
                {isActive && !isCollapsed && (
                  <span className="ml-auto w-1.5 h-1.5 rounded-full bg-[#FF8A65]" />
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Bottom Section: Provider Dropdown + Settings + Dark Mode */}
      <div className="p-4 border-t border-slate-800/80 space-y-3 bg-[#12151E]">
        {/* Provider Selector */}
        {!isCollapsed ? (
          <div className="relative">
            <div className="flex items-center space-x-1.5 text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1.5 pl-1">
              <Cpu className="w-3.5 h-3.5 text-[#FF8A65]" />
              <span>PROVIDER</span>
            </div>

            <button
              onClick={() => setProviderMenuOpen(!providerMenuOpen)}
              className="w-full flex items-center justify-between px-3 py-2 bg-slate-800/90 hover:bg-slate-700/90 border border-slate-700/70 rounded-xl text-xs font-semibold text-slate-200 transition shadow-sm"
            >
              <span className="truncate">{currentProviderObj.label}</span>
              <ChevronDown className={`w-3.5 h-3.5 text-slate-400 transition-transform ${providerMenuOpen ? 'rotate-180' : ''}`} />
            </button>

            {providerMenuOpen && (
              <div className="absolute bottom-12 left-0 w-full bg-[#181D2A] border border-slate-700 rounded-xl shadow-2xl overflow-hidden py-1 z-50">
                {providers.map((p) => (
                  <button
                    key={p.id}
                    onClick={() => {
                      onSelectProvider(p.id);
                      setProviderMenuOpen(false);
                    }}
                    className={`w-full flex items-center justify-between px-3 py-2 text-xs transition hover:bg-slate-800 ${
                      selectedProvider === p.id 
                        ? 'bg-[#FF8A65]/10 text-[#FF8A65] font-semibold' 
                        : 'text-slate-300'
                    }`}
                  >
                    <span>{p.label}</span>
                    {selectedProvider === p.id && <Check className="w-3.5 h-3.5 text-[#FF8A65]" />}
                  </button>
                ))}
              </div>
            )}
          </div>
        ) : (
          <button
            onClick={() => setProviderMenuOpen(!providerMenuOpen)}
            className="w-10 h-10 mx-auto rounded-xl bg-slate-800 flex items-center justify-center text-[#FF8A65] hover:bg-slate-700 transition"
            title={currentProviderObj.label}
          >
            <Cpu className="w-4 h-4" />
          </button>
        )}

        {/* Footer controls: Settings + Dark / Light Mode Toggle */}
        <div className={`flex items-center ${isCollapsed ? 'flex-col space-y-2' : 'justify-between'} pt-1`}>
          <button
            onClick={() => onSelectTab('settings')}
            className="flex items-center space-x-2 text-xs text-slate-300 hover:text-white hover:bg-slate-800/60 p-2 rounded-xl transition"
            title="Settings"
          >
            <Settings className="w-4 h-4 text-slate-400" />
            {!isCollapsed && <span>Settings</span>}
          </button>

          {/* Dark / Light Mode Toggle Button */}
          <button
            onClick={onToggleDarkMode}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-medium bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 transition shadow-sm"
            title={darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
          >
            {darkMode ? (
              <>
                <Sun className="w-3.5 h-3.5 text-amber-400" />
                {!isCollapsed && <span>Light</span>}
              </>
            ) : (
              <>
                <Moon className="w-3.5 h-3.5 text-indigo-300" />
                {!isCollapsed && <span>Dark</span>}
              </>
            )}
          </button>
        </div>
      </div>
    </aside>
  );
}

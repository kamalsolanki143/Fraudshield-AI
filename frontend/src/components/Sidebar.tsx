import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  ScanSearch, 
  History, 
  Users, 
  CreditCard, 
  User, 
  Settings, 
  ShieldCheck, 
  Sparkles,
  Activity
} from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

export const Sidebar: React.FC = () => {
  const location = useLocation();
  const { t } = useLanguage();

  const navItems = [
    { label: t('nav.dashboard'), path: '/dashboard', icon: LayoutDashboard },
    { label: t('nav.analyze'), path: '/analyze', icon: ScanSearch, badge: 'AI Pro', highlight: true },
    { label: t('nav.history'), path: '/history', icon: History },
    { label: t('nav.community'), path: '/community', icon: Users },
    { label: t('nav.pricing'), path: '/pricing', icon: CreditCard },
    { label: t('nav.profile'), path: '/profile', icon: User },
    { label: t('nav.settings'), path: '/settings', icon: Settings },
  ];

  return (
    <aside className="hidden lg:flex flex-col w-64 min-h-[calc(100vh-4rem)] p-4 glass-panel border-r border-slate-800/80 bg-[#070B14]/60">
      
      {/* Quick Action Banner */}
      <div className="mb-6 p-4 rounded-2xl bg-gradient-to-b from-brand-900/40 to-slate-900/60 border border-brand-500/30 relative overflow-hidden group">
        <div className="absolute -right-6 -bottom-6 w-24 h-24 bg-brand-500/20 rounded-full blur-xl group-hover:bg-cyan-500/30 transition-colors" />
        <div className="relative z-10">
          <div className="flex items-center gap-2 text-cyan-400 mb-1">
            <Sparkles className="w-4 h-4" />
            <span className="text-xs font-bold uppercase tracking-wider">Gemini 1.5 Active</span>
          </div>
          <p className="text-xs text-slate-300 mb-3">Instant Multimodal Scam Detection Engine</p>
          <Link
            to="/analyze"
            className="w-full py-2 px-3 rounded-xl bg-gradient-to-r from-brand-600 to-cyan-500 hover:from-brand-500 hover:to-cyan-400 text-white text-xs font-semibold flex items-center justify-center gap-1.5 shadow-glow-sm transition-all"
          >
            <span>Scan Threats</span>
            <ScanSearch className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {/* Main Navigation Links */}
      <div className="flex-1 space-y-1">
        <div className="px-3 pb-2 text-[10px] font-mono text-slate-500 uppercase tracking-widest">
          Main Engine
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;

          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all ${
                isActive
                  ? 'bg-brand-600/20 text-cyan-300 border border-brand-500/40 shadow-glow-sm font-semibold'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/50'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className="px-2 py-0.5 text-[9px] font-mono font-bold rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
                  {item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </div>

      {/* Footer System Status */}
      <div className="pt-4 border-t border-slate-800">
        <div className="flex items-center justify-between p-3 rounded-xl bg-slate-900/60 border border-slate-800/80">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
            <div className="flex flex-col">
              <span className="text-[11px] font-semibold text-slate-200">System Status</span>
              <span className="text-[9px] font-mono text-emerald-400">100% Operational</span>
            </div>
          </div>
          <Activity className="w-3.5 h-3.5 text-emerald-400" />
        </div>
      </div>
    </aside>
  );
};

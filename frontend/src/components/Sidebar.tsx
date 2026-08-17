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
  Sparkles,
  ShieldCheck,
  Zap,
  Tag
} from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

export const Sidebar: React.FC = () => {
  const location = useLocation();
  const { t } = useLanguage();

  const navItems = [
    { label: t('nav.dashboard'), path: '/dashboard', icon: LayoutDashboard },
    { label: t('nav.analyze'), path: '/analyze', icon: ScanSearch, badge: 'Live AI' },
    { label: t('nav.history'), path: '/history', icon: History },
    { label: t('nav.community'), path: '/community', icon: Users },
    { label: t('nav.pricing'), path: '/pricing', icon: Tag },
    { label: t('nav.profile'), path: '/profile', icon: User },
    { label: t('nav.settings'), path: '/settings', icon: Settings },
  ];

  return (
    <aside className="hidden lg:flex flex-col w-64 min-h-[calc(100vh-4rem)] p-4 bg-white border-r border-slate-200/80 space-y-6 shrink-0">

      {/* Brand Header */}
      <div className="flex items-center gap-3 px-3 py-2">
        <div className="w-8 h-8 rounded-xl bg-indigo-600 text-white flex items-center justify-center shadow-soft-sm font-bold">
          <ShieldCheck className="w-5 h-5" />
        </div>
        <div>
          <h3 className="font-heading text-sm font-extrabold text-slate-900 leading-tight">FraudShield AI</h3>
          <span className="text-[10px] text-slate-500 font-mono">Sentinel Operator</span>
        </div>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;

          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-soft-sm font-bold'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className="px-2 py-0.5 text-[9px] font-mono font-bold rounded-full bg-emerald-500 text-white">
                  {item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Upgrade Banner */}
      <div className="p-4 rounded-2xl bg-indigo-50 border border-indigo-100 text-indigo-900 space-y-2 relative overflow-hidden">
        <div className="flex items-center gap-1.5 text-xs font-bold text-indigo-700">
          <Sparkles className="w-4 h-4 text-indigo-600" />
          <span>Gemini XPrize Pro</span>
        </div>
        <p className="text-[11px] text-slate-600 leading-relaxed">
          Unlock sub-second Vision OCR & direct 1930 Helpline filing.
        </p>
        <Link
          to="/pricing"
          className="inline-block w-full py-2 px-3 rounded-xl bg-indigo-600 text-white text-xs font-bold text-center shadow-soft-sm hover:bg-indigo-700 transition-colors"
        >
          View Enterprise Plans
        </Link>
      </div>

    </aside>
  );
};

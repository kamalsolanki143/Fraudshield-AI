import React from 'react';
import {
  User,
  ShieldCheck,
  Award,
  Key,
  Mail,
  Zap,
  Copy
} from 'lucide-react';
import toast from 'react-hot-toast';
import { Sidebar } from '../components/Sidebar';
import { GlassCard } from '../components/GlassCard';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';

export const ProfilePage: React.FC = () => {
  const { user } = useAuth();
  const { t } = useLanguage();

  const handleCopyAPIKey = () => {
    if (user?.apiKey) {
      navigator.clipboard.writeText(user.apiKey);
      toast.success('Live API key copied!');
    }
  };

  const badges = [
    { title: 'Gemini Early Adopter', desc: 'Integrated Gemini 1.5 Vision OCR', icon: Award, color: 'text-indigo-600' },
    { title: 'Cyber Defender', desc: 'Neutralized 35+ high-risk threats', icon: ShieldCheck, color: 'text-emerald-600' },
    { title: 'Community Verifier', desc: 'Contributed 10+ threat reports', icon: Zap, color: 'text-purple-600' },
  ];

  return (
    <div className="flex min-h-screen bg-[#F3F4F9]">
      <Sidebar />

      <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-5xl space-y-6 overflow-x-hidden">

        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl sm:text-3xl font-heading font-extrabold text-slate-900 flex items-center gap-2">
              Operator Security Profile <User className="w-6 h-6 text-indigo-600" />
            </h1>
            <p className="text-xs sm:text-sm text-slate-600 mt-1">
              Personal defense posture, guardian score rank, and credentials.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* Left User Card */}
          <GlassCard className="space-y-6 text-center flex flex-col items-center">
            <div className="relative">
              <img
                src={user?.avatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=200'}
                alt={user?.name}
                className="w-24 h-24 rounded-full object-cover ring-4 ring-indigo-500/20 shadow-soft-md"
              />
              <div className="absolute -bottom-1 -right-1 p-1.5 rounded-full bg-indigo-600 text-white shadow-soft-sm">
                <ShieldCheck className="w-4 h-4" />
              </div>
            </div>

            <div>
              <h2 className="text-xl font-heading font-bold text-slate-900">{user?.name}</h2>
              <p className="text-xs text-slate-500 flex items-center justify-center gap-1 mt-0.5">
                <Mail className="w-3.5 h-3.5 text-slate-400" /> {user?.email}
              </p>
            </div>

            <div className="w-full p-4 rounded-2xl bg-indigo-50/60 border border-indigo-100 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-700 font-mono font-medium">Guardian Rank</span>
                <span className="text-indigo-700 font-bold font-mono">{user?.guardianRank}</span>
              </div>
              <div className="w-full h-2 rounded-full bg-indigo-200/60 overflow-hidden">
                <div className="h-full bg-indigo-600 rounded-full w-[94%]" />
              </div>
              <p className="text-[10px] text-slate-600 text-right font-medium">Score: {user?.guardianScore}/100</p>
            </div>
          </GlassCard>

          {/* Right Column Stats & API Key */}
          <div className="lg:col-span-2 space-y-6">

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <GlassCard className="space-y-1">
                <span className="text-[10px] font-mono text-slate-500 uppercase font-semibold">Total Scans</span>
                <p className="text-2xl font-bold text-slate-900">{user?.totalScans}</p>
              </GlassCard>
              <GlassCard className="space-y-1">
                <span className="text-[10px] font-mono text-slate-500 uppercase font-semibold">Threats Neutralized</span>
                <p className="text-2xl font-bold text-emerald-600">{user?.threatsPrevented}</p>
              </GlassCard>
              <GlassCard className="space-y-1">
                <span className="text-[10px] font-mono text-slate-500 uppercase font-semibold">Protected Assets</span>
                <p className="text-2xl font-bold text-indigo-600">{user?.savedAmountEst}</p>
              </GlassCard>
            </div>

            <GlassCard className="space-y-4">
              <h3 className="text-sm font-heading font-semibold text-slate-900">Unlocked Defense Badges</h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {badges.map((b, idx) => {
                  const Icon = b.icon;
                  return (
                    <div key={idx} className="p-4 rounded-2xl bg-slate-50 border border-slate-100 space-y-2">
                      <Icon className={`w-6 h-6 ${b.color}`} />
                      <h4 className="text-xs font-bold text-slate-900">{b.title}</h4>
                      <p className="text-[10px] text-slate-600">{b.desc}</p>
                    </div>
                  );
                })}
              </div>
            </GlassCard>

            <GlassCard className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Key className="w-4 h-4 text-indigo-600" />
                  <h3 className="text-sm font-heading font-semibold text-slate-900">Live Developer API Key</h3>
                </div>
                <span className="text-[10px] font-mono text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200 font-bold">Active</span>
              </div>

              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 flex items-center justify-between text-xs font-mono">
                <span className="text-slate-700 truncate max-w-md">{user?.apiKey || 'fs_live_99f82a174c82b01e'}</span>
                <button
                  onClick={handleCopyAPIKey}
                  className="p-1.5 rounded-xl bg-white border border-slate-200 text-indigo-600 hover:bg-slate-100 transition-colors shadow-soft-sm"
                >
                  <Copy className="w-4 h-4" />
                </button>
              </div>
            </GlassCard>

          </div>
        </div>
      </main>
    </div>
  );
};

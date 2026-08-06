import React from 'react';
import { motion } from 'framer-motion';
import { 
  User, 
  ShieldCheck, 
  Award, 
  Key, 
  Clock, 
  Mail, 
  Zap, 
  Copy,
  CheckCircle2
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
    { title: 'Gemini Early Adopter', desc: 'Integrated Gemini 1.5 Vision OCR', icon: Award, color: 'text-cyan-400' },
    { title: 'Cyber Defender', desc: 'Neutralized 35+ high-risk threats', icon: ShieldCheck, color: 'text-emerald-400' },
    { title: 'Community Verifier', desc: 'Contributed 10+ threat reports', icon: Zap, color: 'text-brand-400' },
  ];

  return (
    <div className="flex min-h-[calc(100vh-4rem)]">
      <Sidebar />

      <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-8 overflow-x-hidden">
        
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl sm:text-3xl font-heading font-extrabold text-white flex items-center gap-2">
              Operator Security Profile <User className="w-6 h-6 text-cyan-400" />
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Personal defense posture, guardian score rank, and credentials.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Left Column: User Card & Rank */}
          <GlassCard className="space-y-6 text-center flex flex-col items-center">
            <div className="relative">
              <img
                src={user?.avatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=200'}
                alt={user?.name}
                className="w-24 h-24 rounded-2xl object-cover ring-4 ring-brand-500/40 shadow-glow-md"
              />
              <div className="absolute -bottom-2 -right-2 p-1.5 rounded-xl bg-brand-600 text-white shadow-lg">
                <ShieldCheck className="w-4 h-4" />
              </div>
            </div>

            <div>
              <h2 className="text-xl font-heading font-bold text-white">{user?.name}</h2>
              <p className="text-xs text-slate-400 flex items-center justify-center gap-1 mt-0.5">
                <Mail className="w-3 h-3 text-slate-500" /> {user?.email}
              </p>
            </div>

            <div className="w-full p-4 rounded-2xl bg-brand-950/40 border border-brand-800/40 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-300 font-mono">Guardian Rank</span>
                <span className="text-cyan-400 font-bold font-mono">{user?.guardianRank}</span>
              </div>
              <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                <div className="h-full bg-gradient-to-r from-brand-500 to-cyan-400 rounded-full w-[94%]" />
              </div>
              <p className="text-[10px] text-slate-400 text-right">Score: {user?.guardianScore}/100</p>
            </div>
          </GlassCard>

          {/* Right Column (2 cols): Stats, API Keys, Badges */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Stats Overview Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <GlassCard className="space-y-1">
                <span className="text-[10px] font-mono text-slate-400 uppercase">Total Scans</span>
                <p className="text-2xl font-bold text-white">{user?.totalScans}</p>
              </GlassCard>
              <GlassCard className="space-y-1">
                <span className="text-[10px] font-mono text-slate-400 uppercase">Threats Neutralized</span>
                <p className="text-2xl font-bold text-emerald-400">{user?.threatsPrevented}</p>
              </GlassCard>
              <GlassCard className="space-y-1">
                <span className="text-[10px] font-mono text-slate-400 uppercase">Protected Assets</span>
                <p className="text-2xl font-bold text-cyan-400">{user?.savedAmountEst}</p>
              </GlassCard>
            </div>

            {/* Unlocked Badges */}
            <GlassCard className="space-y-4">
              <h3 className="text-sm font-heading font-semibold text-white">Unlocked Defense Badges</h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {badges.map((b, idx) => {
                  const Icon = b.icon;
                  return (
                    <div key={idx} className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2">
                      <Icon className={`w-6 h-6 ${b.color}`} />
                      <h4 className="text-xs font-bold text-white">{b.title}</h4>
                      <p className="text-[10px] text-slate-400">{b.desc}</p>
                    </div>
                  );
                })}
              </div>
            </GlassCard>

            {/* API Key Management */}
            <GlassCard className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Key className="w-4 h-4 text-cyan-400" />
                  <h3 className="text-sm font-heading font-semibold text-white">Live Developer API Key</h3>
                </div>
                <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/30">Active</span>
              </div>

              <div className="p-3 rounded-2xl bg-slate-950 border border-slate-800 flex items-center justify-between text-xs font-mono">
                <span className="text-slate-400 truncate max-w-md">{user?.apiKey || 'fs_live_99f82a174c82b01e'}</span>
                <button
                  onClick={handleCopyAPIKey}
                  className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-cyan-400 transition-colors"
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

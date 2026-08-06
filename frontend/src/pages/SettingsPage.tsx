import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Settings, 
  User, 
  ShieldCheck, 
  Key, 
  Sliders, 
  Bell, 
  Save, 
  Globe
} from 'lucide-react';
import toast from 'react-hot-toast';
import { Sidebar } from '../components/Sidebar';
import { GlassCard } from '../components/GlassCard';
import { useAuth } from '../context/AuthContext';

export const SettingsPage: React.FC = () => {
  const { user, updateUser } = useAuth();
  const [activeTab, setActiveTab] = useState<'account' | 'security' | 'api' | 'appearance'>('account');

  // Form states
  const [name, setName] = useState(user?.name || 'Alex Vance');
  const [email, setEmail] = useState(user?.email || 'alex.vance@geminixprize.org');
  const [twoFactor, setTwoFactor] = useState(true);
  const [gridOverlay, setGridOverlay] = useState(true);
  const [glassIntensity, setGlassIntensity] = useState('high');

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    updateUser({ name, email });
    toast.success('System configuration saved successfully!');
  };

  return (
    <div className="flex min-h-[calc(100vh-4rem)]">
      <Sidebar />

      <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-8 overflow-x-hidden">
        
        {/* Header */}
        <div>
          <h1 className="text-2xl sm:text-3xl font-heading font-extrabold text-white flex items-center gap-2">
            System Configuration <Settings className="w-6 h-6 text-cyan-400" />
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Manage account security, API keys, AI model sensitivity, and interface preferences.
          </p>
        </div>

        {/* Tab Buttons */}
        <div className="flex items-center gap-2 border-b border-slate-800 pb-3 overflow-x-auto">
          {[
            { id: 'account', label: 'Account Profile', icon: User },
            { id: 'security', label: 'Security & 2FA', icon: ShieldCheck },
            { id: 'api', label: 'API & Webhooks', icon: Key },
            { id: 'appearance', label: 'UI Appearance', icon: Sliders },
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                  activeTab === tab.id
                    ? 'bg-brand-600 text-white shadow-glow-sm'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Tab Contents */}
        <GlassCard className="p-6">
          <form onSubmit={handleSave} className="space-y-6 max-w-2xl text-xs">
            
            {activeTab === 'account' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-slate-300 mb-1 font-mono">Full Name</label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full p-3 rounded-xl bg-slate-950 border border-slate-800 text-white outline-none focus:border-cyan-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 mb-1 font-mono">Email Address</label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full p-3 rounded-xl bg-slate-950 border border-slate-800 text-white outline-none focus:border-cyan-500"
                  />
                </div>
              </div>
            )}

            {activeTab === 'security' && (
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 rounded-2xl bg-slate-950 border border-slate-800">
                  <div>
                    <h4 className="font-bold text-white">Two-Factor Authentication (2FA)</h4>
                    <p className="text-[11px] text-slate-400">Require TOTP authenticator code on login.</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={twoFactor}
                    onChange={(e) => setTwoFactor(e.target.checked)}
                    className="w-5 h-5 accent-brand-500 cursor-pointer"
                  />
                </div>
              </div>
            )}

            {activeTab === 'api' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-slate-300 mb-1 font-mono">Gemini Vision Model Sensitivity</label>
                  <select className="w-full p-3 rounded-xl bg-slate-950 border border-slate-800 text-white outline-none focus:border-cyan-500">
                    <option>High Strictness (Recommended for Financial Phishing)</option>
                    <option>Balanced</option>
                    <option>Permissive</option>
                  </select>
                </div>
              </div>
            )}

            {activeTab === 'appearance' && (
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 rounded-2xl bg-slate-950 border border-slate-800">
                  <div>
                    <h4 className="font-bold text-white">Cyber Grid Overlay Pattern</h4>
                    <p className="text-[11px] text-slate-400">Display subtle background grid lines.</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={gridOverlay}
                    onChange={(e) => setGridOverlay(e.target.checked)}
                    className="w-5 h-5 accent-brand-500 cursor-pointer"
                  />
                </div>
              </div>
            )}

            <div className="pt-4 border-t border-slate-800 flex justify-end">
              <button
                type="submit"
                className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-brand-600 to-cyan-500 text-white font-semibold flex items-center gap-2 shadow-glow-sm"
              >
                <Save className="w-4 h-4" />
                <span>Save Configuration</span>
              </button>
            </div>
          </form>
        </GlassCard>
      </main>
    </div>
  );
};

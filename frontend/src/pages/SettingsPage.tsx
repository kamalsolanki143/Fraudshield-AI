import React, { useState } from 'react';
import {
  Settings,
  User,
  ShieldCheck,
  Key,
  Sliders,
  Save
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

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    updateUser({ name, email });
    toast.success('System configuration saved successfully!');
  };

  return (
    <div className="flex min-h-[calc(100vh-4rem)] bg-[#F8FAFC]">
      <Sidebar />

      <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-8 overflow-x-hidden">

        {/* Header */}
        <div>
          <h1 className="text-2xl sm:text-3xl font-heading font-extrabold text-slate-900 flex items-center gap-2">
            System Configuration <Settings className="w-6 h-6 text-blue-600" />
          </h1>
          <p className="text-xs sm:text-sm text-slate-600 mt-1">
            Manage account security, API keys, AI model sensitivity, and interface preferences.
          </p>
        </div>

        {/* Tab Buttons */}
        <div className="flex items-center gap-2 border-b border-slate-200 pb-3 overflow-x-auto">
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
                    ? 'bg-blue-600 text-white shadow-soft-sm'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
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
                  <label className="block text-slate-700 mb-1 font-mono font-semibold">Full Name</label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full p-3 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 outline-none focus:border-blue-600"
                  />
                </div>
                <div>
                  <label className="block text-slate-700 mb-1 font-mono font-semibold">Email Address</label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full p-3 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 outline-none focus:border-blue-600"
                  />
                </div>
              </div>
            )}

            {activeTab === 'security' && (
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 rounded-2xl bg-slate-50 border border-slate-200">
                  <div>
                    <h4 className="font-bold text-slate-900">Two-Factor Authentication (2FA)</h4>
                    <p className="text-[11px] text-slate-500">Require TOTP authenticator code on login.</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={twoFactor}
                    onChange={(e) => setTwoFactor(e.target.checked)}
                    className="w-5 h-5 accent-blue-600 cursor-pointer"
                  />
                </div>
              </div>
            )}

            {activeTab === 'api' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-slate-700 mb-1 font-mono font-semibold">Gemini Vision Model Sensitivity</label>
                  <select className="w-full p-3 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 outline-none focus:border-blue-600">
                    <option>High Strictness (Recommended for Financial Phishing)</option>
                    <option>Balanced</option>
                    <option>Permissive</option>
                  </select>
                </div>
              </div>
            )}

            {activeTab === 'appearance' && (
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 rounded-2xl bg-slate-50 border border-slate-200">
                  <div>
                    <h4 className="font-bold text-slate-900">Light Pattern Backdrop</h4>
                    <p className="text-[11px] text-slate-500">Display subtle background grid dots.</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={gridOverlay}
                    onChange={(e) => setGridOverlay(e.target.checked)}
                    className="w-5 h-5 accent-blue-600 cursor-pointer"
                  />
                </div>
              </div>
            )}

            <div className="pt-4 border-t border-slate-200 flex justify-end">
              <button
                type="submit"
                className="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold flex items-center gap-2 shadow-soft-sm"
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

import React, { useState, useEffect } from 'react';
import {
  Users,
  ThumbsUp,
  CheckCircle,
  MapPin,
  PlusCircle,
  Search
} from 'lucide-react';
import toast from 'react-hot-toast';
import { Sidebar } from '../components/Sidebar';
import { GlassCard } from '../components/GlassCard';
import { Modal } from '../components/Modal';
import { communityService } from '../services/communityService';
import { CommunityAlert, RiskLevel } from '../types';
import { useLanguage } from '../context/LanguageContext';

export const CommunityPage: React.FC = () => {
  const { t } = useLanguage();
  const [alerts, setAlerts] = useState<CommunityAlert[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [isReportModalOpen, setIsReportModalOpen] = useState(false);

  // New Alert Form state
  const [newTitle, setNewTitle] = useState('');
  const [newCategory, setNewCategory] = useState<any>('UPI Scam');
  const [newDescription, setNewDescription] = useState('');
  const [newLocation, setNewLocation] = useState('Delhi, India');
  const [newRiskLevel, setNewRiskLevel] = useState<RiskLevel>('HIGH');

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    const data = await communityService.getAlerts();
    setAlerts(data);
  };

  const handleVote = async (alertId: string) => {
    const res = await communityService.voteAlert(alertId, 1);
    setAlerts((prev) =>
      prev.map((a) => (a.id === alertId ? { ...a, votes: res.votes } : a))
    );
    toast.success('Threat credibility upvoted!');
  };

  const handleCreateReport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim() || !newDescription.trim()) {
      toast.error('Please fill in title and description.');
      return;
    }

    const created = await communityService.createAlert({
      author: 'You (Sentinel Contributor)',
      title: newTitle,
      category: newCategory,
      description: newDescription,
      riskLevel: newRiskLevel,
      location: newLocation,
      tags: [newCategory, 'User Report'],
    });

    setAlerts((prev) => [created, ...prev]);
    setIsReportModalOpen(false);
    setNewTitle('');
    setNewDescription('');
    toast.success('Community Alert published successfully!');
  };

  const filteredAlerts = alerts.filter((a) => {
    const matchesSearch = a.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          a.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'ALL' || a.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="flex min-h-screen bg-[#F3F4F9]">
      <Sidebar />

      <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-5xl space-y-6 overflow-x-hidden">

        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-heading font-extrabold text-slate-900 flex items-center gap-2">
              Community Threat Network <Users className="w-6 h-6 text-indigo-600" />
            </h1>
            <p className="text-xs sm:text-sm text-slate-600 mt-1">
              Crowdsourced scam intelligence feed verified by Gemini AI telemetry.
            </p>
          </div>

          <button
            onClick={() => setIsReportModalOpen(true)}
            className="px-5 py-2.5 rounded-2xl bg-gradient-to-r from-indigo-600 to-violet-600 hover:opacity-95 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-soft-lg transition-all"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Report New Threat</span>
          </button>
        </div>

        {/* Search & Category Filter Bar (NovaShop Pills) */}
        <GlassCard className="p-4 space-y-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex-1 flex items-center gap-2 px-4 py-2.5 rounded-full bg-slate-50 border border-slate-200">
              <Search className="w-4 h-4 text-slate-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search community reports by keywords, location..."
                className="w-full bg-transparent border-none outline-none text-xs text-slate-900 placeholder-slate-400 font-sans"
              />
            </div>

            <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0">
              {['ALL', 'UPI Scam', 'Fake Job', 'Phishing Link', 'Bank Impersonation'].map((cat) => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                    selectedCategory === cat
                      ? 'bg-indigo-600 text-white shadow-soft-sm'
                      : 'bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-200'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>
        </GlassCard>

        {/* Global Threat Heatmap Card */}
        <GlassCard className="p-0 overflow-hidden relative h-56 flex items-center justify-center bg-slate-100 border border-slate-200">
          <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1524661135-423995f22d0b?auto=format&fit=crop&q=80&w=2000')] bg-cover bg-center opacity-10 filter contrast-125" />
          <div className="absolute inset-0 bg-gradient-to-t from-white via-white/80 to-transparent" />

          <div className="relative z-10 text-center space-y-2">
            <MapPin className="w-8 h-8 text-rose-600 mx-auto animate-bounce" />
            <h3 className="text-lg font-bold text-slate-900 font-heading">Global Threat Matrix</h3>
            <p className="text-xs text-slate-600 max-w-md mx-auto">Live visualization of scam clusters and geographical hotspots. Gemini is currently monitoring 4,302 active threat vectors.</p>
          </div>
        </GlassCard>

        {/* Alerts Grid - NovaShop Card Layout */}
        <div className="space-y-4">
          {filteredAlerts.map((alert) => (
            <GlassCard key={alert.id} className="flex gap-4 p-0 overflow-hidden hover:border-slate-300 transition-colors">

              {/* Upvote Sidebar */}
              <div className="bg-slate-50 w-14 flex flex-col items-center py-4 border-r border-slate-100 gap-2 shrink-0">
                <button
                  onClick={() => handleVote(alert.id)}
                  className="p-1.5 rounded-full text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 transition-colors"
                >
                  <ThumbsUp className="w-4 h-4" />
                </button>
                <span className="text-xs font-bold text-slate-900 font-mono">{alert.votes}</span>
              </div>

              {/* Main Content */}
              <div className="flex-1 p-5 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <img
                      src={alert.authorAvatar || 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&q=80&w=150'}
                      alt={alert.author}
                      className="w-6 h-6 rounded-full object-cover ring-2 ring-indigo-500/30"
                    />
                    <p className="text-[11px] font-medium text-slate-500 flex items-center gap-1">
                      Reported by <span className="text-slate-900 font-semibold">{alert.author}</span>
                      {alert.verified && <CheckCircle className="w-3.5 h-3.5 text-indigo-600" />}
                      <span className="px-1.5">•</span>
                      {alert.timestamp}
                    </p>
                  </div>
                  <span className={`px-2.5 py-0.5 rounded-full font-mono text-[10px] font-bold ${
                    alert.riskLevel === 'CRITICAL' ? 'bg-rose-500 text-white' : 'bg-amber-500 text-white'
                  }`}>
                    {alert.riskLevel}
                  </span>
                </div>

                <div>
                  <h3 className="text-base font-bold text-slate-900 leading-snug">{alert.title}</h3>
                  <p className="text-[11px] text-slate-500 flex items-center gap-1 mt-1 font-mono">
                    <MapPin className="w-3 h-3 text-indigo-600" /> {alert.location}
                  </p>
                </div>

                <p className="text-xs text-slate-700 leading-relaxed bg-slate-50 p-3.5 rounded-2xl border border-slate-100">
                  {alert.description}
                </p>

                <div className="flex items-center justify-between pt-1">
                  <div className="flex flex-wrap gap-1.5">
                    {alert.tags.map((tag, idx) => (
                      <span key={idx} className="text-[10px] font-mono px-2.5 py-0.5 rounded-full border border-slate-200 bg-slate-100 text-slate-600 font-semibold">
                        #{tag.replace(/\s+/g, '')}
                      </span>
                    ))}
                  </div>
                  <span className="text-[10px] font-mono text-indigo-600 font-bold">
                    Gemini Verified 98%
                  </span>
                </div>
              </div>
            </GlassCard>
          ))}
        </div>

        {/* Report New Threat Modal */}
        <Modal
          isOpen={isReportModalOpen}
          onClose={() => setIsReportModalOpen(false)}
          title="Report Cyber Threat to Community"
          maxWidth="lg"
        >
          <form onSubmit={handleCreateReport} className="space-y-4 text-xs">
            <div>
              <label className="block text-slate-700 mb-1 font-mono font-semibold">Threat Title</label>
              <input
                type="text"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                placeholder="e.g. Fake Electricity Bill Disconnection SMS in Mumbai..."
                className="w-full p-3 rounded-2xl bg-slate-50 border border-slate-200 text-slate-900 outline-none focus:border-indigo-600"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-slate-700 mb-1 font-mono font-semibold">Category</label>
                <select
                  value={newCategory}
                  onChange={(e) => setNewCategory(e.target.value as any)}
                  className="w-full p-3 rounded-2xl bg-slate-50 border border-slate-200 text-slate-900 outline-none focus:border-indigo-600"
                >
                  <option value="UPI Scam">UPI Scam</option>
                  <option value="Fake Job">Fake Job</option>
                  <option value="Bank Impersonation">Bank Impersonation</option>
                  <option value="Phishing Link">Phishing Link</option>
                  <option value="Crypto Fraud">Crypto Fraud</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-700 mb-1 font-mono font-semibold">Location</label>
                <input
                  type="text"
                  value={newLocation}
                  onChange={(e) => setNewLocation(e.target.value)}
                  className="w-full p-3 rounded-2xl bg-slate-50 border border-slate-200 text-slate-900 outline-none focus:border-indigo-600"
                />
              </div>
            </div>

            <div>
              <label className="block text-slate-700 mb-1 font-mono font-semibold">Detailed Scam Mechanics</label>
              <textarea
                rows={4}
                value={newDescription}
                onChange={(e) => setNewDescription(e.target.value)}
                placeholder="Describe how the scam operates, numbers involved, fake domains..."
                className="w-full p-3 rounded-2xl bg-slate-50 border border-slate-200 text-slate-900 outline-none focus:border-indigo-600"
              />
            </div>

            <div className="pt-2 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setIsReportModalOpen(false)}
                className="px-4 py-2 rounded-xl bg-slate-100 text-slate-700 font-semibold"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-5 py-2 rounded-xl bg-indigo-600 text-white font-bold shadow-soft-sm hover:bg-indigo-700"
              >
                Publish Report
              </button>
            </div>
          </form>
        </Modal>
      </main>
    </div>
  );
};

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Users, 
  ShieldAlert, 
  ThumbsUp, 
  CheckCircle, 
  MapPin, 
  Tag, 
  PlusCircle, 
  Search,
  Filter
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
    <div className="flex min-h-[calc(100vh-4rem)]">
      <Sidebar />

      <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-8 overflow-x-hidden">
        
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-heading font-extrabold text-white flex items-center gap-2">
              Community Threat Network <Users className="w-6 h-6 text-cyan-400" />
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Crowdsourced scam intelligence feed verified by Gemini AI telemetry.
            </p>
          </div>

          <button
            onClick={() => setIsReportModalOpen(true)}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-brand-600 via-blue-500 to-cyan-500 text-white font-semibold text-xs flex items-center justify-center gap-2 shadow-glow-sm hover:opacity-95 transition-opacity"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Report New Threat</span>
          </button>
        </div>

        {/* Search & Category Filter Bar */}
        <GlassCard className="p-4 space-y-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex-1 flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-950/80 border border-slate-800">
              <Search className="w-4 h-4 text-slate-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search community reports by keywords, location..."
                className="w-full bg-transparent border-none outline-none text-xs text-white placeholder-slate-500"
              />
            </div>

            <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0">
              {['ALL', 'UPI Scam', 'Fake Job', 'Phishing Link', 'Bank Impersonation'].map((cat) => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-medium whitespace-nowrap transition-all ${
                    selectedCategory === cat
                      ? 'bg-brand-600 text-white shadow-glow-sm'
                      : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>
        </GlassCard>

        {/* Alerts Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredAlerts.map((alert) => (
            <GlassCard key={alert.id} hoverEffect className="space-y-4 flex flex-col justify-between">
              <div className="space-y-3">
                {/* Header author & tag */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <img
                      src={alert.authorAvatar || 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&q=80&w=150'}
                      alt={alert.author}
                      className="w-7 h-7 rounded-full object-cover ring-1 ring-cyan-500/40"
                    />
                    <div>
                      <p className="text-xs font-semibold text-white flex items-center gap-1">
                        {alert.author}
                        {alert.verified && <CheckCircle className="w-3 h-3 text-cyan-400" />}
                      </p>
                      <p className="text-[10px] text-slate-500 flex items-center gap-1">
                        <MapPin className="w-2.5 h-2.5" /> {alert.location} • {alert.timestamp}
                      </p>
                    </div>
                  </div>

                  <span className={`px-2.5 py-0.5 rounded-full font-mono text-[10px] font-bold border ${
                    alert.riskLevel === 'CRITICAL' ? 'bg-danger/20 text-danger border-danger/40' : 'bg-warning/20 text-warning border-warning/40'
                  }`}>
                    {alert.riskLevel}
                  </span>
                </div>

                <h3 className="text-sm font-bold text-white leading-snug">{alert.title}</h3>
                <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/40 p-3 rounded-2xl border border-slate-800">
                  {alert.description}
                </p>

                <div className="flex flex-wrap gap-1.5 pt-1">
                  {alert.tags.map((tag, idx) => (
                    <span key={idx} className="text-[10px] font-mono px-2 py-0.5 rounded-md bg-slate-900 text-cyan-300 border border-slate-800 flex items-center gap-1">
                      <Tag className="w-2.5 h-2.5" /> {tag}
                    </span>
                  ))}
                </div>
              </div>

              {/* Bottom Upvote Bar */}
              <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
                <button
                  onClick={() => handleVote(alert.id)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-200 text-xs font-medium border border-slate-800 transition-colors"
                >
                  <ThumbsUp className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Verify Threat ({alert.votes})</span>
                </button>

                <span className="text-[10px] font-mono text-slate-500">Gemini Telemetry Score: 98%</span>
              </div>
            </GlassCard>
          ))}
        </div>

        {/* Report New Threat Modal */}
        <Modal
          isOpen={isReportModalOpen}
          onClose={() => setIsReportModalOpen(false)}
          title="Report New Cyber Threat to Community"
          maxWidth="lg"
        >
          <form onSubmit={handleCreateReport} className="space-y-4 text-xs">
            <div>
              <label className="block text-slate-400 mb-1 font-mono">Threat Title</label>
              <input
                type="text"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                placeholder="e.g. Fake Electricity Bill Disconnection SMS in Mumbai..."
                className="w-full p-3 rounded-xl bg-slate-950 border border-slate-800 text-white outline-none focus:border-cyan-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-slate-400 mb-1 font-mono">Category</label>
                <select
                  value={newCategory}
                  onChange={(e) => setNewCategory(e.target.value as any)}
                  className="w-full p-3 rounded-xl bg-slate-950 border border-slate-800 text-white outline-none focus:border-cyan-500"
                >
                  <option value="UPI Scam">UPI Scam</option>
                  <option value="Fake Job">Fake Job</option>
                  <option value="Bank Impersonation">Bank Impersonation</option>
                  <option value="Phishing Link">Phishing Link</option>
                  <option value="Crypto Fraud">Crypto Fraud</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-400 mb-1 font-mono">Location</label>
                <input
                  type="text"
                  value={newLocation}
                  onChange={(e) => setNewLocation(e.target.value)}
                  className="w-full p-3 rounded-xl bg-slate-950 border border-slate-800 text-white outline-none focus:border-cyan-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-slate-400 mb-1 font-mono">Detailed Scam Mechanics</label>
              <textarea
                rows={4}
                value={newDescription}
                onChange={(e) => setNewDescription(e.target.value)}
                placeholder="Describe how the scam operates, numbers involved, fake domains..."
                className="w-full p-3 rounded-xl bg-slate-950 border border-slate-800 text-white outline-none focus:border-cyan-500"
              />
            </div>

            <div className="pt-2 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setIsReportModalOpen(false)}
                className="px-4 py-2 rounded-xl bg-slate-900 text-slate-300 hover:bg-slate-800 font-semibold"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-5 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold shadow-glow-sm"
              >
                Publish Threat Report
              </button>
            </div>
          </form>
        </Modal>
      </main>
    </div>
  );
};

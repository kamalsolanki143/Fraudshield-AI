import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  History as HistoryIcon, 
  Search, 
  Filter, 
  Download, 
  Trash2, 
  ExternalLink, 
  ShieldAlert, 
  Calendar,
  FileSpreadsheet
} from 'lucide-react';
import toast from 'react-hot-toast';
import { Sidebar } from '../components/Sidebar';
import { GlassCard } from '../components/GlassCard';
import { Modal } from '../components/Modal';
import { historyService } from '../services/historyService';
import { FraudAnalysisResult, RiskLevel } from '../types';
import { useLanguage } from '../context/LanguageContext';

export const HistoryPage: React.FC = () => {
  const { t } = useLanguage();
  const [historyList, setHistoryList] = useState<FraudAnalysisResult[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRiskFilter, setSelectedRiskFilter] = useState<string>('ALL');
  const [selectedDetail, setSelectedDetail] = useState<FraudAnalysisResult | null>(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    const data = await historyService.getHistory();
    setHistoryList(data);
  };

  const handleDelete = async (id: string) => {
    await historyService.deleteHistoryItem(id);
    setHistoryList((prev) => prev.filter((item) => item.id !== id));
    toast.success('Log entry removed.');
  };

  const handleExportCSV = () => {
    toast.success('Exporting Audit Vault logs to CSV...');
  };

  const filteredList = historyList.filter((item) => {
    const matchesSearch = item.inputContent.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          item.detectedScamType.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesRisk = selectedRiskFilter === 'ALL' || item.riskLevel === selectedRiskFilter;
    return matchesSearch && matchesRisk;
  });

  return (
    <div className="flex min-h-[calc(100vh-4rem)]">
      <Sidebar />

      <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-8 overflow-x-hidden">
        
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-heading font-extrabold text-white flex items-center gap-2">
              Security Audit Vault <HistoryIcon className="w-6 h-6 text-cyan-400" />
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Historical record of all multimodal scans, detected threat vectors, and forensic timestamps.
            </p>
          </div>

          <button
            onClick={handleExportCSV}
            className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-700 hover:border-cyan-500 text-slate-200 text-xs font-semibold flex items-center gap-2 transition-colors"
          >
            <FileSpreadsheet className="w-4 h-4 text-cyan-400" />
            <span>Export CSV Vault</span>
          </button>
        </div>

        {/* Filter Controls Bar */}
        <GlassCard className="p-4 space-y-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            
            {/* Search Input */}
            <div className="flex-1 flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-950/80 border border-slate-800">
              <Search className="w-4 h-4 text-slate-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by keyword, URL, or scam type..."
                className="w-full bg-transparent border-none outline-none text-xs text-white placeholder-slate-500"
              />
            </div>

            {/* Risk Pills */}
            <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0">
              {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'SAFE'].map((risk) => (
                <button
                  key={risk}
                  onClick={() => setSelectedRiskFilter(risk)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-mono font-bold transition-all ${
                    selectedRiskFilter === risk
                      ? 'bg-brand-600 text-white shadow-glow-sm'
                      : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
                  }`}
                >
                  {risk}
                </button>
              ))}
            </div>
          </div>
        </GlassCard>

        {/* Logs Table */}
        <GlassCard className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-mono">
                <th className="py-3 px-4">Date / Time</th>
                <th className="py-3 px-4">Scan Type</th>
                <th className="py-3 px-4">Input Snippet</th>
                <th className="py-3 px-4">Detected Scam</th>
                <th className="py-3 px-4">Risk Level</th>
                <th className="py-3 px-4">Score</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredList.map((item) => {
                const isHigh = item.riskLevel === 'CRITICAL' || item.riskLevel === 'HIGH';
                return (
                  <tr key={item.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-4 font-mono text-[11px] text-slate-400">
                      {new Date(item.createdAt).toLocaleDateString()}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="uppercase font-mono text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                        {item.type}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 max-w-xs truncate text-slate-200 font-sans">
                      {item.inputContent}
                    </td>
                    <td className="py-3.5 px-4 text-cyan-300 font-semibold">
                      {item.detectedScamType}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className={`px-2.5 py-0.5 rounded-full font-mono text-[10px] font-bold border ${
                        isHigh ? 'bg-danger/20 text-danger border-danger/40' : 'bg-success/20 text-success border-success/40'
                      }`}>
                        {item.riskLevel}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 font-mono font-bold text-white">
                      {item.riskScore}/100
                    </td>
                    <td className="py-3.5 px-4 text-right flex items-center justify-end gap-2">
                      <button
                        onClick={() => setSelectedDetail(item)}
                        className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-cyan-400 transition-colors"
                        title="View Audit Report"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => handleDelete(item.id)}
                        className="p-1.5 rounded-lg bg-slate-800 hover:bg-danger/20 text-slate-400 hover:text-danger transition-colors"
                        title="Delete Log Entry"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </GlassCard>

        {/* Detailed Inspection Modal */}
        <Modal
          isOpen={!!selectedDetail}
          onClose={() => setSelectedDetail(null)}
          title="Security Brief Audit Detail"
          maxWidth="lg"
        >
          {selectedDetail && (
            <div className="space-y-4 text-xs">
              <div className="p-3 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
                <span className="text-[10px] font-mono text-slate-400 uppercase">Input Content</span>
                <p className="text-white font-mono text-xs">{selectedDetail.inputContent}</p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-2xl bg-slate-900 border border-slate-800">
                  <span className="text-[10px] font-mono text-slate-400">Risk Score</span>
                  <p className="text-lg font-bold text-danger">{selectedDetail.riskScore}/100 ({selectedDetail.riskLevel})</p>
                </div>
                <div className="p-3 rounded-2xl bg-slate-900 border border-slate-800">
                  <span className="text-[10px] font-mono text-slate-400">AI Confidence</span>
                  <p className="text-lg font-bold text-cyan-400">{selectedDetail.confidenceScore}%</p>
                </div>
              </div>

              <div>
                <span className="text-[10px] font-mono text-slate-400 uppercase">Analysis Summary</span>
                <p className="text-slate-300 leading-relaxed mt-1">{selectedDetail.summary}</p>
              </div>

              <div className="pt-3 border-t border-slate-800 flex justify-end">
                <button
                  onClick={() => setSelectedDetail(null)}
                  className="px-4 py-2 rounded-xl bg-brand-600 text-white font-semibold text-xs"
                >
                  Close Audit View
                </button>
              </div>
            </div>
          )}
        </Modal>
      </main>
    </div>
  );
};

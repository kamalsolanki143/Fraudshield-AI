import React, { useState, useEffect } from 'react';
import {
  History as HistoryIcon,
  Search,
  Trash2,
  ExternalLink,
  Calendar,
  FileSpreadsheet
} from 'lucide-react';
import toast from 'react-hot-toast';
import { Sidebar } from '../components/Sidebar';
import { GlassCard } from '../components/GlassCard';
import { Modal } from '../components/Modal';
import { historyService } from '../services/historyService';
import { FraudAnalysisResult } from '../types';
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
    toast.success('Exporting Security Audit Vault logs to CSV...');
  };

  const filteredList = historyList.filter((item) => {
    const matchesSearch = item.inputContent.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          item.detectedScamType.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesRisk = selectedRiskFilter === 'ALL' || item.riskLevel === selectedRiskFilter;
    return matchesSearch && matchesRisk;
  });

  return (
    <div className="flex min-h-screen bg-[#F3F4F9]">
      <Sidebar />

      <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-5xl space-y-6 overflow-x-hidden">

        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-heading font-extrabold text-slate-900 flex items-center gap-2">
              Security Audit Vault <HistoryIcon className="w-6 h-6 text-indigo-600" />
            </h1>
            <p className="text-xs sm:text-sm text-slate-600 mt-1">
              Historical record of all multimodal scans, detected threat vectors, and forensic timestamps.
            </p>
          </div>

          <button
            onClick={handleExportCSV}
            className="px-5 py-2.5 rounded-full bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-bold flex items-center gap-2 transition-colors shadow-soft-sm"
          >
            <FileSpreadsheet className="w-4 h-4 text-indigo-600" />
            <span>Export CSV Vault</span>
          </button>
        </div>

        {/* Filter Controls Bar (NovaShop Pills) */}
        <GlassCard className="p-4 space-y-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">

            <div className="flex-1 flex items-center gap-2 px-4 py-2.5 rounded-full bg-slate-50 border border-slate-200">
              <Search className="w-4 h-4 text-slate-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by keyword, URL, or scam type..."
                className="w-full bg-transparent border-none outline-none text-xs text-slate-900 placeholder-slate-400 font-sans"
              />
            </div>

            <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0">
              {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'SAFE'].map((risk) => (
                <button
                  key={risk}
                  onClick={() => setSelectedRiskFilter(risk)}
                  className={`px-3.5 py-1.5 rounded-xl text-xs font-mono font-bold transition-all ${
                    selectedRiskFilter === risk
                      ? 'bg-indigo-600 text-white shadow-soft-sm'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200 border border-slate-200'
                  }`}
                >
                  {risk}
                </button>
              ))}
            </div>
          </div>
        </GlassCard>

        {/* Logs Timeline NovaShop Card Style */}
        <div className="relative pt-4 max-w-4xl">
          <div className="absolute left-8 top-0 bottom-0 w-px bg-slate-200" />

          <div className="space-y-6">
            {filteredList.map((item) => {
              const isHigh = item.riskLevel === 'CRITICAL' || item.riskLevel === 'HIGH';
              const isSafe = item.riskLevel === 'SAFE';

              return (
                <div key={item.id} className="relative flex gap-6 group">
                  <div className="relative z-10 flex flex-col items-center mt-2 shrink-0">
                    <div className={`w-4 h-4 rounded-full border-2 border-white ring-2 ring-slate-200 ${
                      isHigh ? 'bg-rose-500' : isSafe ? 'bg-emerald-500' : 'bg-amber-500'
                    }`} />
                  </div>

                  <GlassCard className="flex-1 p-5 hover:border-slate-300 transition-colors">
                    <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">

                      <div className="space-y-3 flex-1">
                        <div className="flex items-center gap-3">
                          <span className="uppercase font-mono text-[10px] px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700 font-bold">
                            {item.type} SCAN
                          </span>
                          <span className="font-mono text-[11px] text-slate-500 flex items-center gap-1.5">
                            <Calendar className="w-3.5 h-3.5" /> {new Date(item.createdAt).toLocaleString()}
                          </span>
                        </div>

                        <div>
                          <h4 className="text-sm font-bold text-slate-900 mb-1">{item.detectedScamType}</h4>
                          <p className="text-xs text-slate-600 font-sans line-clamp-2 max-w-xl">
                            {item.inputContent}
                          </p>
                        </div>

                        <div className="flex items-center gap-4 pt-1">
                          <div className="flex items-center gap-1.5">
                            <span className="text-[10px] font-mono text-slate-500 uppercase font-semibold">Risk Level</span>
                            <span className={`px-2.5 py-0.5 rounded-full font-mono text-[10px] font-bold ${
                              isHigh ? 'text-white bg-rose-500' : isSafe ? 'text-white bg-emerald-500' : 'text-white bg-amber-500'
                            }`}>
                              {item.riskLevel}
                            </span>
                          </div>
                          <div className="flex items-center gap-1.5">
                            <span className="text-[10px] font-mono text-slate-500 uppercase font-semibold">Threat Score</span>
                            <span className="font-mono text-[11px] font-bold text-slate-900">
                              {item.riskScore}/100
                            </span>
                          </div>
                        </div>
                      </div>

                      <div className="flex flex-row md:flex-col justify-end gap-2 shrink-0 md:border-l md:border-slate-100 md:pl-4">
                        <button
                          onClick={() => setSelectedDetail(item)}
                          className="w-full px-3.5 py-2 rounded-xl bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-[11px] font-bold flex items-center justify-center gap-1.5 transition-colors"
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
                          <span>Audit Report</span>
                        </button>
                        <button
                          onClick={() => handleDelete(item.id)}
                          className="w-full px-3.5 py-2 rounded-xl hover:bg-rose-50 text-slate-500 hover:text-rose-600 text-[11px] font-semibold flex items-center justify-center gap-1.5 transition-colors"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                          <span>Delete Log</span>
                        </button>
                      </div>

                    </div>
                  </GlassCard>
                </div>
              );
            })}
          </div>
        </div>

        {/* Detailed Inspection Modal */}
        <Modal
          isOpen={!!selectedDetail}
          onClose={() => setSelectedDetail(null)}
          title="Security Brief Audit Detail"
          maxWidth="lg"
        >
          {selectedDetail && (
            <div className="space-y-4 text-xs">
              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 space-y-1">
                <span className="text-[10px] font-mono text-slate-500 uppercase font-semibold">Input Content</span>
                <p className="text-slate-900 font-mono text-xs">{selectedDetail.inputContent}</p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200">
                  <span className="text-[10px] font-mono text-slate-500 font-semibold">Risk Score</span>
                  <p className="text-lg font-bold text-rose-600">{selectedDetail.riskScore}/100 ({selectedDetail.riskLevel})</p>
                </div>
                <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200">
                  <span className="text-[10px] font-mono text-slate-500 font-semibold">AI Confidence</span>
                  <p className="text-lg font-bold text-indigo-600">{selectedDetail.confidenceScore}%</p>
                </div>
              </div>

              <div>
                <span className="text-[10px] font-mono text-slate-500 uppercase font-semibold">Analysis Summary</span>
                <p className="text-slate-700 leading-relaxed mt-1">{selectedDetail.summary}</p>
              </div>

              <div className="pt-3 border-t border-slate-200 flex justify-end">
                <button
                  onClick={() => setSelectedDetail(null)}
                  className="px-5 py-2 rounded-xl bg-indigo-600 text-white font-bold text-xs shadow-soft-sm hover:bg-indigo-700 transition-colors"
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

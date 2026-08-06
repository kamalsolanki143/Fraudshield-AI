import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ShieldCheck, 
  ScanSearch, 
  AlertTriangle, 
  DollarSign, 
  Activity, 
  ArrowUpRight, 
  ExternalLink,
  ChevronRight,
  Sparkles,
  Users
} from 'lucide-react';
import { Sidebar } from '../components/Sidebar';
import { StatCard } from '../components/StatCard';
import { ThreatTrendChart, ThreatDistributionChart } from '../components/Charts';
import { GlassCard } from '../components/GlassCard';
import { useLanguage } from '../context/LanguageContext';
import { useAuth } from '../context/AuthContext';
import { historyService } from '../services/historyService';
import { communityService } from '../services/communityService';
import { FraudAnalysisResult, CommunityAlert } from '../types';

export const Dashboard: React.FC = () => {
  const { t } = useLanguage();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [recentScans, setRecentScans] = useState<FraudAnalysisResult[]>([]);
  const [communityAlerts, setCommunityAlerts] = useState<CommunityAlert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [history, alerts] = await Promise.all([
          historyService.getHistory(),
          communityService.getAlerts(),
        ]);
        setRecentScans(history);
        setCommunityAlerts(alerts);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="flex min-h-[calc(100vh-4rem)]">
      <Sidebar />

      <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-8 overflow-x-hidden">
        
        {/* Top Header Banner */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-heading font-extrabold text-white flex items-center gap-2">
              {t('dash.title')} <Sparkles className="w-5 h-5 text-cyan-400 animate-pulse" />
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Welcome back, <span className="text-cyan-300 font-semibold">{user?.name || 'Sentinel Operator'}</span> — Security level <span className="text-emerald-400 font-mono font-bold">{user?.guardianRank || 'Sentinel Prime'}</span>
            </p>
          </div>

          <Link
            to="/analyze"
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-brand-600 via-blue-500 to-cyan-500 text-white font-semibold text-xs flex items-center justify-center gap-2 shadow-glow-sm hover:opacity-95 transition-opacity"
          >
            <ScanSearch className="w-4 h-4" />
            <span>Launch Gemini Multimodal Scan</span>
          </Link>
        </div>

        {/* Metric Cards Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          <StatCard
            title={t('dash.score')}
            value={`${user?.guardianScore || 94}/100`}
            change="+4.2%"
            isPositive
            icon={ShieldCheck}
            iconColor="text-emerald-400"
            subtitle="Tier 1 Defense Posture"
          />
          <StatCard
            title={t('dash.totalScans')}
            value={user?.totalScans || 142}
            change="+18%"
            isPositive
            icon={ScanSearch}
            iconColor="text-brand-400"
            subtitle="Multimodal Scans Executed"
          />
          <StatCard
            title={t('dash.threatsPrevented')}
            value={user?.threatsPrevented || 38}
            change="+12%"
            isPositive
            icon={AlertTriangle}
            iconColor="text-warning font-bold"
            subtitle="Neutralized Attack Vectors"
          />
          <StatCard
            title={t('dash.savedAmount')}
            value={user?.savedAmountEst || '$24,500'}
            change="+24%"
            isPositive
            icon={DollarSign}
            iconColor="text-cyan-400"
            subtitle="Estimated Assets Shielded"
          />
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Main Area Trend Chart (2 cols) */}
          <GlassCard className="lg:col-span-2 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-heading font-semibold text-white">7-Day Threat Neutralization Velocity</h3>
                <p className="text-xs text-slate-400">Scans vs Threat Mitigation rate</p>
              </div>
              <div className="flex items-center gap-2">
                <span className="flex items-center gap-1 text-[10px] font-mono text-brand-400">
                  <span className="w-2 h-2 rounded-full bg-brand-500" /> Scans
                </span>
                <span className="flex items-center gap-1 text-[10px] font-mono text-emerald-400">
                  <span className="w-2 h-2 rounded-full bg-emerald-500" /> Neutralized
                </span>
              </div>
            </div>
            <ThreatTrendChart />
          </GlassCard>

          {/* Scam Category Breakdown Pie (1 col) */}
          <GlassCard className="space-y-4">
            <div>
              <h3 className="text-sm font-heading font-semibold text-white">Detected Fraud Vectors</h3>
              <p className="text-xs text-slate-400">Dominant scam categories</p>
            </div>
            <ThreatDistributionChart />
            <div className="grid grid-cols-2 gap-2 pt-2 text-[11px] font-medium border-t border-slate-800">
              <span className="text-danger flex items-center gap-1">● UPI Phishing (45%)</span>
              <span className="text-warning flex items-center gap-1">● Fake Jobs (25%)</span>
              <span className="text-brand-400 flex items-center gap-1">● KYC Fraud (20%)</span>
              <span className="text-purple-400 flex items-center gap-1">● Crypto (10%)</span>
            </div>
          </GlassCard>
        </div>

        {/* Recent Analyses & Community Alerts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Recent Scans Table (2 cols) */}
          <GlassCard className="lg:col-span-2 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-heading font-semibold text-white">Recent Multimodal Scans</h3>
              <Link to="/history" className="text-xs text-cyan-400 hover:underline flex items-center gap-1">
                View All Audit Logs <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 font-mono">
                    <th className="py-2.5 px-3">Type</th>
                    <th className="py-2.5 px-3">Input Summary</th>
                    <th className="py-2.5 px-3">Risk Level</th>
                    <th className="py-2.5 px-3">Score</th>
                    <th className="py-2.5 px-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {recentScans.slice(0, 4).map((scan) => {
                    const isHigh = scan.riskLevel === 'CRITICAL' || scan.riskLevel === 'HIGH';
                    return (
                      <tr key={scan.id} className="hover:bg-slate-800/40 transition-colors">
                        <td className="py-3 px-3">
                          <span className="uppercase font-mono text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                            {scan.type}
                          </span>
                        </td>
                        <td className="py-3 px-3 max-w-xs truncate text-slate-200">
                          {scan.inputContent}
                        </td>
                        <td className="py-3 px-3">
                          <span className={`px-2.5 py-0.5 rounded-full font-mono text-[10px] font-bold border ${
                            isHigh ? 'bg-danger/20 text-danger border-danger/40' : 'bg-success/20 text-success border-success/40'
                          }`}>
                            {scan.riskLevel}
                          </span>
                        </td>
                        <td className="py-3 px-3 font-mono font-bold text-white">
                          {scan.riskScore}/100
                        </td>
                        <td className="py-3 px-3 text-right">
                          <button
                            onClick={() => navigate(`/analyze?id=${scan.id}`)}
                            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-cyan-400 transition-colors"
                            title="Inspect Detailed Report"
                          >
                            <ExternalLink className="w-3.5 h-3.5" />
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </GlassCard>

          {/* Real-time Community Telemetry Feed (1 col) */}
          <GlassCard className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Users className="w-4 h-4 text-cyan-400" />
                <h3 className="text-sm font-heading font-semibold text-white">Live Community Telemetry</h3>
              </div>
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
            </div>

            <div className="space-y-3">
              {communityAlerts.slice(0, 3).map((alert) => (
                <div key={alert.id} className="p-3 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono text-cyan-300 font-bold">{alert.category}</span>
                    <span className="text-[9px] text-slate-500">{alert.timestamp}</span>
                  </div>
                  <h4 className="text-xs font-semibold text-white leading-tight">{alert.title}</h4>
                  <p className="text-[11px] text-slate-400 line-clamp-2">{alert.description}</p>
                </div>
              ))}
            </div>

            <Link
              to="/community"
              className="w-full py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 text-xs font-medium flex items-center justify-center gap-1.5 transition-colors"
            >
              <span>Explore Community Threats</span>
              <ArrowUpRight className="w-3.5 h-3.5 text-cyan-400" />
            </Link>
          </GlassCard>
        </div>

      </main>
    </div>
  );
};

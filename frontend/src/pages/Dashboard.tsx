import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  ShieldCheck,
  ScanSearch,
  AlertTriangle,
  DollarSign,
  ExternalLink,
  ChevronRight,
  Sparkles,
  Users,
  ArrowRight
} from 'lucide-react';
import { Sidebar } from '../components/Sidebar';
import { StatCard } from '../components/StatCard';
import { CardSkeleton } from '../components/Loader';
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
    <div className="flex min-h-screen bg-[#F8FAFC]">
      <Sidebar />

      <main className="flex-1 p-6 lg:p-10 max-w-7xl mx-auto space-y-8 overflow-x-hidden">

        {/* Top Header Banner */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-heading font-extrabold text-slate-900 flex items-center gap-2">
              Operator Control Center <Sparkles className="w-5 h-5 text-indigo-600" />
            </h1>
            <p className="text-xs sm:text-sm text-slate-600 mt-1">
              Welcome back, <span className="text-indigo-600 font-bold">{user?.name || 'Sentinel Operator'}</span> — Defense rank <span className="text-emerald-700 font-mono font-bold">{user?.guardianRank || 'Sentinel Prime'}</span>
            </p>
          </div>

          <Link
            to="/analyze"
            className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-soft-sm transition-colors"
          >
            <ScanSearch className="w-4 h-4" />
            <span>Launch Multimodal Scan</span>
          </Link>
        </div>

        {/* Metric Cards Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {loading ? (
            <>
              <CardSkeleton />
              <CardSkeleton />
              <CardSkeleton />
              <CardSkeleton />
            </>
          ) : (
            <>
              <StatCard
                title={t('dash.score')}
                value={user?.guardianScore ? `${user.guardianScore}/100` : '94/100'}
                change="+4.2%"
                isPositive
                icon={ShieldCheck}
                iconColor="text-indigo-600"
                subtitle="Tier 1 Defense Posture"
              />
              <StatCard
                title={t('dash.totalScans')}
                value={user?.totalScans ?? 142}
                change="+18%"
                isPositive
                icon={ScanSearch}
                iconColor="text-violet-600"
                subtitle="Multimodal Scans Executed"
              />
              <StatCard
                title={t('dash.threatsPrevented')}
                value={user?.threatsPrevented ?? 118}
                change="+12%"
                isPositive
                icon={AlertTriangle}
                iconColor="text-amber-600 font-bold"
                subtitle="Neutralized Attack Vectors"
              />
              <StatCard
                title={t('dash.savedAmount')}
                value={user?.savedAmountEst ?? '₹24,500'}
                change="+24%"
                isPositive
                icon={DollarSign}
                iconColor="text-emerald-600"
                subtitle="Estimated Assets Shielded"
              />
            </>
          )}
        </div>

        {/* Charts & Analytics Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <GlassCard className="lg:col-span-2 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-heading font-semibold text-slate-900">7-Day Threat Neutralization Velocity</h3>
                <p className="text-xs text-slate-500">Scans vs Threat Mitigation rate</p>
              </div>
              <div className="flex items-center gap-3 text-[10px] font-mono font-semibold">
                <span className="flex items-center gap-1 text-indigo-600">● Scans</span>
                <span className="flex items-center gap-1 text-emerald-600">● Blocked</span>
              </div>
            </div>
            <ThreatTrendChart />
          </GlassCard>

          <GlassCard className="space-y-4">
            <div>
              <h3 className="text-sm font-heading font-semibold text-slate-900">Fraud Vectors Breakdown</h3>
              <p className="text-xs text-slate-500">Dominant scam categories</p>
            </div>
            <ThreatDistributionChart />
            <div className="grid grid-cols-2 gap-2 pt-2 text-[10px] font-medium border-t border-slate-100">
              <span className="text-rose-600">● UPI Phishing (45%)</span>
              <span className="text-amber-600">● Fake Jobs (25%)</span>
              <span className="text-indigo-600">● KYC Fraud (20%)</span>
              <span className="text-purple-600">● Crypto (10%)</span>
            </div>
          </GlassCard>
        </div>

        {/* Recent Audit Logs & Telemetry */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          <GlassCard className="lg:col-span-2 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-heading font-semibold text-slate-900">Recent Multimodal Audit Vault</h3>
              <Link to="/history" className="text-xs text-indigo-600 hover:underline flex items-center gap-1 font-bold">
                View Audit Vault <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-200 text-slate-500 font-mono">
                    <th className="py-2.5 px-3">Type</th>
                    <th className="py-2.5 px-3">Input Summary</th>
                    <th className="py-2.5 px-3">Risk Level</th>
                    <th className="py-2.5 px-3">Score</th>
                    <th className="py-2.5 px-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {recentScans.slice(0, 4).map((scan) => {
                    const isHigh = scan.riskLevel === 'CRITICAL' || scan.riskLevel === 'HIGH';
                    return (
                      <tr key={scan.id} className="hover:bg-slate-50 transition-colors">
                        <td className="py-3 px-3">
                          <span className="uppercase font-mono text-[10px] px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700 font-bold">
                            {scan.type}
                          </span>
                        </td>
                        <td className="py-3 px-3 max-w-xs truncate text-slate-800 font-medium">
                          {scan.inputContent}
                        </td>
                        <td className="py-3 px-3">
                          <span className={`px-2.5 py-0.5 rounded-full font-mono text-[10px] font-bold ${
                            isHigh ? 'bg-rose-50 text-rose-700 border border-rose-200' : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          }`}>
                            {scan.riskLevel}
                          </span>
                        </td>
                        <td className="py-3 px-3 font-mono font-bold text-slate-900">
                          {scan.riskScore}/100
                        </td>
                        <td className="py-3 px-3 text-right">
                          <button
                            onClick={() => navigate(`/analyze?id=${scan.id}`)}
                            className="p-1.5 rounded-xl bg-slate-100 hover:bg-indigo-50 text-indigo-600 transition-colors"
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

          <GlassCard className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Users className="w-4 h-4 text-indigo-600" />
                <h3 className="text-sm font-heading font-semibold text-slate-900">Live Community Feed</h3>
              </div>
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
            </div>

            <div className="space-y-3">
              {communityAlerts.slice(0, 3).map((alert) => (
                <div key={alert.id} className="p-3 rounded-2xl bg-slate-50 border border-slate-100 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono text-indigo-600 font-bold">{alert.category}</span>
                    <span className="text-[9px] text-slate-400">{alert.timestamp}</span>
                  </div>
                  <h4 className="text-xs font-bold text-slate-900 leading-tight">{alert.title}</h4>
                  <p className="text-[11px] text-slate-600 line-clamp-2">{alert.description}</p>
                </div>
              ))}
            </div>

            <Link
              to="/community"
              className="w-full py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold flex items-center justify-center gap-1.5 transition-colors"
            >
              <span>Explore Community Feed</span>
              <ChevronRight className="w-3.5 h-3.5 text-indigo-600" />
            </Link>
          </GlassCard>

        </div>

      </main>
    </div>
  );
};

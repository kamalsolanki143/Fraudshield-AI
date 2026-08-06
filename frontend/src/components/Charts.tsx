import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

const trendData = [
  { name: 'Mon', scans: 42, blocked: 38 },
  { name: 'Tue', scans: 58, blocked: 51 },
  { name: 'Wed', scans: 89, blocked: 82 },
  { name: 'Thu', scans: 64, blocked: 59 },
  { name: 'Fri', scans: 112, blocked: 104 },
  { name: 'Sat', scans: 95, blocked: 89 },
  { name: 'Sun', scans: 130, blocked: 121 },
];

const categoryData = [
  { name: 'UPI Phishing', value: 45, color: '#EF4444' },
  { name: 'Fake Jobs', value: 25, color: '#F59E0B' },
  { name: 'Bank KYC Fraud', value: 20, color: '#2563EB' },
  { name: 'Crypto Deposit', value: 10, color: '#A855F7' },
];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="glass-panel p-3 rounded-xl border border-slate-700 shadow-2xl text-xs space-y-1">
        <p className="font-mono text-cyan-400 font-bold mb-1">{label}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} style={{ color: entry.color }} className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
            {entry.name}: <span className="font-mono font-bold text-white">{entry.value}</span>
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export const ThreatTrendChart: React.FC = () => {
  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={trendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="scansGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#2563EB" stopOpacity={0.6} />
              <stop offset="95%" stopColor="#2563EB" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="blockedGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#22C55E" stopOpacity={0.6} />
              <stop offset="95%" stopColor="#22C55E" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" />
          <XAxis dataKey="name" stroke="#64748B" fontSize={11} tickLine={false} />
          <YAxis stroke="#64748B" fontSize={11} tickLine={false} />
          <Tooltip content={<CustomTooltip />} />
          <Area type="monotone" dataKey="scans" stroke="#2563EB" strokeWidth={2.5} fillOpacity={1} fill="url(#scansGrad)" name="Threat Scans" />
          <Area type="monotone" dataKey="blocked" stroke="#22C55E" strokeWidth={2.5} fillOpacity={1} fill="url(#blockedGrad)" name="Neutralized" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export const ThreatDistributionChart: React.FC = () => {
  return (
    <div className="w-full h-64 flex items-center justify-center">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={categoryData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={85}
            paddingAngle={4}
            dataKey="value"
          >
            {categoryData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} stroke="#070B14" strokeWidth={2} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

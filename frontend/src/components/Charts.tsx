import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
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
  { name: 'Crypto Deposit', value: 10, color: '#6366F1' },
];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 rounded-xl border border-slate-200 shadow-soft-md text-xs space-y-1">
        <p className="font-mono text-blue-600 font-bold mb-1">{label}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} style={{ color: entry.color }} className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
            {entry.name}: <span className="font-mono font-bold text-slate-900">{entry.value}</span>
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
              <stop offset="5%" stopColor="#2563EB" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#2563EB" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="blockedGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
          <XAxis dataKey="name" stroke="#64748B" fontSize={11} tickLine={false} />
          <YAxis stroke="#64748B" fontSize={11} tickLine={false} />
          <Tooltip content={<CustomTooltip />} />
          <Area type="monotone" dataKey="scans" stroke="#2563EB" strokeWidth={2.5} fillOpacity={1} fill="url(#scansGrad)" name="Threat Scans" />
          <Area type="monotone" dataKey="blocked" stroke="#10B981" strokeWidth={2.5} fillOpacity={1} fill="url(#blockedGrad)" name="Neutralized" />
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
              <Cell key={`cell-${index}`} fill={entry.color} stroke="#FFFFFF" strokeWidth={2} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

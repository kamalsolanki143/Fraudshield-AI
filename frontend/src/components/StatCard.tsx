import React from 'react';
import { motion } from 'framer-motion';
import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react';
import { GlassCard } from './GlassCard';

interface StatCardProps {
  title: string;
  value: string | number;
  change?: string;
  isPositive?: boolean;
  icon: LucideIcon;
  iconColor?: string;
  subtitle?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  change,
  isPositive = true,
  icon: Icon,
  iconColor = 'text-brand-400',
  subtitle,
}) => {
  return (
    <GlassCard hoverEffect>
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">{title}</span>
          <div className="text-2xl font-heading font-extrabold text-white tracking-tight">
            {value}
          </div>
          {subtitle && <p className="text-[11px] text-slate-500">{subtitle}</p>}
        </div>

        <div className={`p-3 rounded-2xl bg-slate-900/80 border border-slate-800 ${iconColor}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>

      {change && (
        <div className="mt-4 pt-3 border-t border-slate-800/60 flex items-center gap-1.5 text-xs font-medium">
          {isPositive ? (
            <span className="flex items-center text-emerald-400 font-mono">
              <TrendingUp className="w-3.5 h-3.5 mr-0.5" />
              {change}
            </span>
          ) : (
            <span className="flex items-center text-danger font-mono">
              <TrendingDown className="w-3.5 h-3.5 mr-0.5" />
              {change}
            </span>
          )}
          <span className="text-slate-500">vs last month</span>
        </div>
      )}
    </GlassCard>
  );
};

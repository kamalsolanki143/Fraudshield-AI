import React from 'react';
import { motion } from 'framer-motion';
import { RiskLevel } from '../types';
import { ShieldCheck, AlertTriangle, ShieldX } from 'lucide-react';

interface RiskMeterProps {
  score: number; // 0 to 100
  riskLevel: RiskLevel;
}

export const RiskMeter: React.FC<RiskMeterProps> = ({ score, riskLevel }) => {
  const getConfig = () => {
    switch (riskLevel) {
      case 'CRITICAL':
        return {
          color: '#EF4444',
          badgeBg: 'bg-rose-50 text-rose-700 border-rose-200',
          icon: ShieldX,
          label: 'CRITICAL THREAT',
        };
      case 'HIGH':
        return {
          color: '#F97316',
          badgeBg: 'bg-orange-50 text-orange-700 border-orange-200',
          icon: AlertTriangle,
          label: 'HIGH RISK',
        };
      case 'MEDIUM':
        return {
          color: '#F59E0B',
          badgeBg: 'bg-amber-50 text-amber-700 border-amber-200',
          icon: AlertTriangle,
          label: 'MODERATE RISK',
        };
      case 'SAFE':
      default:
        return {
          color: '#10B981',
          badgeBg: 'bg-emerald-50 text-emerald-700 border-emerald-200',
          icon: ShieldCheck,
          label: 'VERIFIED SAFE',
        };
    }
  };

  const config = getConfig();
  const IconComp = config.icon;
  const angle = (score / 100) * 180 - 90; // -90 deg to 90 deg

  return (
    <div className="relative flex flex-col items-center justify-center p-6 bg-white rounded-3xl overflow-hidden border border-slate-200 shadow-soft-sm">
      <div className="relative w-64 h-36 flex items-center justify-center">
        <svg className="w-full h-full overflow-visible" viewBox="0 0 200 120">
          <defs>
            <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#10B981" />
              <stop offset="50%" stopColor="#F59E0B" />
              <stop offset="100%" stopColor="#EF4444" />
            </linearGradient>
          </defs>

          {/* Track background arc */}
          <path
            d="M 20 100 A 80 80 0 0 1 180 100"
            fill="none"
            stroke="#F1F5F9"
            strokeWidth="16"
            strokeLinecap="round"
          />

          {/* Color Gradient Track */}
          <path
            d="M 20 100 A 80 80 0 0 1 180 100"
            fill="none"
            stroke="url(#gaugeGradient)"
            strokeWidth="16"
            strokeLinecap="round"
          />

          {/* Animated Needle */}
          <g transform="translate(100, 100)">
            <motion.g
              initial={{ rotate: -90 }}
              animate={{ rotate: angle }}
              transition={{ type: 'spring', stiffness: 60, damping: 15 }}
            >
              <line
                x1="0"
                y1="0"
                x2="0"
                y2="-68"
                stroke={config.color}
                strokeWidth="4"
                strokeLinecap="round"
              />
              <circle cx="0" cy="0" r="8" fill="#FFFFFF" stroke={config.color} strokeWidth="3" />
            </motion.g>
          </g>
        </svg>
      </div>

      {/* Numerical score & badge */}
      <div className="text-center mt-2 z-10">
        <motion.div
          initial={{ scale: 0.5, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          key={score}
          className="text-4xl font-heading font-extrabold tracking-tight text-slate-900 flex items-center justify-center gap-1"
        >
          {score} <span className="text-sm text-slate-500 font-normal">/ 100</span>
        </motion.div>

        <div className={`mt-2 inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full text-xs font-mono font-bold border ${config.badgeBg} shadow-soft-sm`}>
          <IconComp className="w-3.5 h-3.5" />
          <span>{config.label}</span>
        </div>
      </div>
    </div>
  );
};

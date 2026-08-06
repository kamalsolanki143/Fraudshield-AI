import React from 'react';
import { motion } from 'framer-motion';
import { RiskLevel } from '../types';
import { ShieldAlert, ShieldCheck, AlertTriangle, ShieldX } from 'lucide-react';

interface RiskMeterProps {
  score: number; // 0 to 100
  riskLevel: RiskLevel;
}

export const RiskMeter: React.FC<RiskMeterProps> = ({ score, riskLevel }) => {
  // Determine color theme based on riskLevel
  const getConfig = () => {
    switch (riskLevel) {
      case 'CRITICAL':
        return {
          color: '#EF4444',
          gradientFrom: '#EF4444',
          gradientTo: '#991B1B',
          bgGlow: 'rgba(239, 68, 68, 0.25)',
          badgeBg: 'bg-danger/20 text-danger border-danger/40',
          icon: ShieldX,
          label: 'CRITICAL THREAT',
        };
      case 'HIGH':
        return {
          color: '#F97316',
          gradientFrom: '#F97316',
          gradientTo: '#C2410C',
          bgGlow: 'rgba(249, 115, 22, 0.25)',
          badgeBg: 'bg-orange-500/20 text-orange-400 border-orange-500/40',
          icon: AlertTriangle,
          label: 'HIGH RISK',
        };
      case 'MEDIUM':
        return {
          color: '#F59E0B',
          gradientFrom: '#F59E0B',
          gradientTo: '#B45309',
          bgGlow: 'rgba(245, 158, 11, 0.25)',
          badgeBg: 'bg-warning/20 text-warning border-warning/40',
          icon: AlertTriangle,
          label: 'MODERATE RISK',
        };
      case 'SAFE':
      default:
        return {
          color: '#22C55E',
          gradientFrom: '#22C55E',
          gradientTo: '#15803D',
          bgGlow: 'rgba(34, 197, 94, 0.25)',
          badgeBg: 'bg-success/20 text-success border-success/40',
          icon: ShieldCheck,
          label: 'VERIFIED SAFE',
        };
    }
  };

  const config = getConfig();
  const IconComp = config.icon;

  // Arc math for semi-circle (from -180 deg to 0 deg)
  const angle = (score / 100) * 180 - 90; // -90 deg to 90 deg

  return (
    <div className="relative flex flex-col items-center justify-center p-6 glass-panel rounded-3xl overflow-hidden border border-slate-700/80">
      
      {/* Background ambient glow */}
      <div 
        className="absolute w-48 h-48 rounded-full blur-3xl transition-all duration-700 pointer-events-none"
        style={{ backgroundColor: config.bgGlow }}
      />

      <div className="relative w-64 h-36 flex items-center justify-center">
        {/* SVG Semi-circle gauge */}
        <svg className="w-full h-full overflow-visible" viewBox="0 0 200 120">
          <defs>
            <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#22C55E" />
              <stop offset="50%" stopColor="#F59E0B" />
              <stop offset="100%" stopColor="#EF4444" />
            </linearGradient>

            <filter id="glowFilter" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="4" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Track background arc */}
          <path
            d="M 20 100 A 80 80 0 0 1 180 100"
            fill="none"
            stroke="rgba(255, 255, 255, 0.08)"
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
            opacity="0.85"
            filter="url(#glowFilter)"
          />

          {/* Animated Needle */}
          <g transform="translate(100, 100)">
            <motion.g
              initial={{ rotate: -90 }}
              animate={{ rotate: angle }}
              transition={{ type: 'spring', stiffness: 60, damping: 15 }}
            >
              {/* Needle shaft */}
              <line
                x1="0"
                y1="0"
                x2="0"
                y2="-68"
                stroke={config.color}
                strokeWidth="4"
                strokeLinecap="round"
              />
              <circle cx="0" cy="0" r="8" fill="#070B14" stroke={config.color} strokeWidth="3" />
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
          className="text-4xl font-heading font-extrabold tracking-tight text-white flex items-center justify-center gap-1"
        >
          {score} <span className="text-sm text-slate-400 font-normal">/ 100</span>
        </motion.div>

        <div className={`mt-2 inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-bold border ${config.badgeBg} shadow-glow-sm`}>
          <IconComp className="w-3.5 h-3.5" />
          <span>{config.label}</span>
        </div>
      </div>
    </div>
  );
};

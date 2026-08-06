import React from 'react';
import { motion } from 'framer-motion';
import { ShieldAlert } from 'lucide-react';

export const RadarLoader: React.FC<{ label?: string }> = ({ label = 'Gemini AI Multimodal Scanning...' }) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 space-y-4">
      <div className="relative w-24 h-24 flex items-center justify-center">
        {/* Radar Ring 1 */}
        <motion.div
          animate={{ scale: [1, 1.8, 1], opacity: [0.8, 0, 0.8] }}
          transition={{ repeat: Infinity, duration: 2.5, ease: 'easeInOut' }}
          className="absolute inset-0 rounded-full border border-cyan-500/50"
        />

        {/* Radar Ring 2 */}
        <motion.div
          animate={{ scale: [1, 1.4, 1], opacity: [0.6, 0.1, 0.6] }}
          transition={{ repeat: Infinity, duration: 2.5, delay: 0.5, ease: 'easeInOut' }}
          className="absolute inset-2 rounded-full border border-brand-500/50"
        />

        {/* Radar Sweep line */}
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 2, ease: 'linear' }}
          className="absolute inset-0 rounded-full bg-gradient-to-tr from-cyan-500/20 to-transparent"
        />

        {/* Center Icon */}
        <div className="relative z-10 w-10 h-10 rounded-xl bg-brand-600 flex items-center justify-center shadow-glow-md">
          <ShieldAlert className="w-5 h-5 text-white animate-pulse" />
        </div>
      </div>

      <p className="text-xs font-mono font-semibold text-cyan-300 animate-pulse tracking-wide">
        {label}
      </p>
    </div>
  );
};

export const CardSkeleton: React.FC = () => {
  return (
    <div className="p-6 glass-panel rounded-3xl space-y-4 animate-pulse">
      <div className="h-4 bg-slate-800 rounded-full w-1/3" />
      <div className="h-8 bg-slate-800 rounded-2xl w-1/2" />
      <div className="space-y-2 pt-2">
        <div className="h-3 bg-slate-800/60 rounded-full w-full" />
        <div className="h-3 bg-slate-800/60 rounded-full w-4/5" />
      </div>
    </div>
  );
};

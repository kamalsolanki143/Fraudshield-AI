import React from 'react';
import { motion } from 'framer-motion';
import { ShieldCheck } from 'lucide-react';

export const RadarLoader: React.FC<{ label?: string }> = ({ label = 'Gemini AI Multimodal Scanning...' }) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 space-y-4">
      <div className="relative w-20 h-20 flex items-center justify-center">
        {/* Radar Ring 1 */}
        <motion.div
          animate={{ scale: [1, 1.8, 1], opacity: [0.6, 0, 0.6] }}
          transition={{ repeat: Infinity, duration: 2.5, ease: 'easeInOut' }}
          className="absolute inset-0 rounded-full border border-blue-400"
        />

        {/* Radar Ring 2 */}
        <motion.div
          animate={{ scale: [1, 1.4, 1], opacity: [0.5, 0.1, 0.5] }}
          transition={{ repeat: Infinity, duration: 2.5, delay: 0.5, ease: 'easeInOut' }}
          className="absolute inset-2 rounded-full border border-blue-600"
        />

        {/* Center Icon */}
        <div className="relative z-10 w-10 h-10 rounded-2xl bg-blue-600 flex items-center justify-center shadow-soft-md">
          <ShieldCheck className="w-5 h-5 text-white animate-pulse" />
        </div>
      </div>

      <p className="text-xs font-mono font-semibold text-blue-600 animate-pulse tracking-wide">
        {label}
      </p>
    </div>
  );
};

export const CardSkeleton: React.FC = () => {
  return (
    <div className="p-6 bg-white border border-slate-200 rounded-3xl space-y-4 animate-pulse shadow-soft-sm">
      <div className="h-4 bg-slate-100 rounded-full w-1/3" />
      <div className="h-8 bg-slate-200 rounded-2xl w-1/2" />
      <div className="space-y-2 pt-2">
        <div className="h-3 bg-slate-100 rounded-full w-full" />
        <div className="h-3 bg-slate-100 rounded-full w-4/5" />
      </div>
    </div>
  );
};

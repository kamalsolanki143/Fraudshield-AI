import React from 'react';
import { motion } from 'framer-motion';
import { FraudTimelineItem } from '../types';
import { ShieldAlert, AlertTriangle, ChevronRight } from 'lucide-react';

interface FraudTimelineProps {
  timeline: FraudTimelineItem[];
}

export const FraudTimeline: React.FC<FraudTimelineProps> = ({ timeline }) => {
  if (!timeline || timeline.length === 0) return null;

  return (
    <div className="p-6 glass-panel rounded-3xl space-y-4 border border-slate-700/80">
      <div className="flex items-center gap-2">
        <ShieldAlert className="w-5 h-5 text-brand-400" />
        <h3 className="text-sm font-heading font-semibold text-white">Scam Execution Attack Vector</h3>
      </div>

      <div className="relative pt-2 pl-4 border-l-2 border-slate-800 space-y-6">
        {timeline.map((item, idx) => {
          const isHigh = item.risk === 'HIGH';
          return (
            <motion.div
              key={idx}
              initial={{ opacity: 0, x: -15 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.15 }}
              className="relative group"
            >
              {/* Dot Node */}
              <div className={`absolute -left-[23px] top-1 w-3.5 h-3.5 rounded-full border-2 border-[#070B14] transition-transform group-hover:scale-125 ${
                isHigh ? 'bg-danger shadow-danger-glow' : 'bg-warning shadow-glow-sm'
              }`} />

              <div className="bg-slate-900/60 p-3.5 rounded-2xl border border-slate-800 hover:border-slate-700 transition-colors">
                <div className="flex items-center justify-between gap-2 mb-1">
                  <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-cyan-400">
                    Step 0{item.step} — {item.phase}
                  </span>
                  <span className={`text-[9px] font-mono px-2 py-0.5 rounded-full font-bold border ${
                    isHigh ? 'bg-danger/20 text-danger border-danger/30' : 'bg-warning/20 text-warning border-warning/30'
                  }`}>
                    {item.risk} SEVERITY
                  </span>
                </div>
                <h4 className="text-xs font-bold text-white mb-1 flex items-center gap-1">
                  {item.title} <ChevronRight className="w-3 h-3 text-slate-500" />
                </h4>
                <p className="text-xs text-slate-400 leading-relaxed">{item.description}</p>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

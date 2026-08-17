import React from 'react';
import { motion } from 'framer-motion';
import { FraudTimelineItem } from '../types';
import { ShieldCheck, ChevronRight } from 'lucide-react';

interface FraudTimelineProps {
  timeline: FraudTimelineItem[];
}

export const FraudTimeline: React.FC<FraudTimelineProps> = ({ timeline }) => {
  if (!timeline || timeline.length === 0) return null;

  return (
    <div className="p-6 bg-white rounded-3xl space-y-4 border border-slate-200 shadow-soft-sm">
      <div className="flex items-center gap-2">
        <ShieldCheck className="w-5 h-5 text-blue-600" />
        <h3 className="text-sm font-heading font-semibold text-slate-900">Scam Execution Attack Vector</h3>
      </div>

      <div className="relative pt-2 pl-4 border-l-2 border-slate-200 space-y-5">
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
              <div className={`absolute -left-[23px] top-1.5 w-3.5 h-3.5 rounded-full border-2 border-white ring-1 ring-slate-200 ${
                isHigh ? 'bg-rose-500' : 'bg-amber-500'
              }`} />

              <div className="bg-slate-50 p-4 rounded-2xl border border-slate-200/80 hover:border-slate-300 transition-colors">
                <div className="flex items-center justify-between gap-2 mb-1">
                  <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-blue-700">
                    Step 0{item.step} — {item.phase}
                  </span>
                  <span className={`text-[9px] font-mono px-2 py-0.5 rounded-full font-bold border ${
                    isHigh ? 'bg-rose-50 text-rose-700 border-rose-200' : 'bg-amber-50 text-amber-700 border-amber-200'
                  }`}>
                    {item.risk} SEVERITY
                  </span>
                </div>
                <h4 className="text-xs font-bold text-slate-900 mb-1 flex items-center gap-1">
                  {item.title} <ChevronRight className="w-3 h-3 text-slate-400" />
                </h4>
                <p className="text-xs text-slate-600 leading-relaxed">{item.description}</p>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

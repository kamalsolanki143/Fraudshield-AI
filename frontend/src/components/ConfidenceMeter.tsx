import React from 'react';
import { motion } from 'framer-motion';
import { Cpu, Eye, FileText, Globe } from 'lucide-react';

interface ConfidenceMeterProps {
  confidenceScore: number;
  breakdown: {
    geminiVisionScore: number;
    nlpUrgencyScore: number;
    domainReputationScore: number;
    ocrConfidence: number;
  };
}

export const ConfidenceMeter: React.FC<ConfidenceMeterProps> = ({ confidenceScore, breakdown }) => {
  const metrics = [
    { label: 'Gemini Vision Model', val: breakdown.geminiVisionScore, icon: Eye, color: 'from-blue-500 to-cyan-400' },
    { label: 'NLP Coercion Detection', val: breakdown.nlpUrgencyScore, icon: FileText, color: 'from-purple-500 to-blue-500' },
    { label: 'Domain & Threat Registry', val: breakdown.domainReputationScore, icon: Globe, color: 'from-emerald-400 to-cyan-400' },
    { label: 'OCR Text Accuracy', val: breakdown.ocrConfidence, icon: Cpu, color: 'from-cyan-400 to-blue-600' },
  ];

  return (
    <div className="p-6 glass-panel rounded-3xl space-y-4 border border-slate-700/80">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Cpu className="w-5 h-5 text-cyan-400 animate-pulse" />
          <h3 className="text-sm font-heading font-semibold text-white">Gemini AI Model Signals</h3>
        </div>
        <div className="flex items-center gap-1 bg-cyan-500/10 px-2.5 py-1 rounded-full border border-cyan-500/30">
          <span className="text-xs font-mono font-bold text-cyan-300">{confidenceScore}%</span>
          <span className="text-[10px] text-slate-400">Certitude</span>
        </div>
      </div>

      {/* Signal Bars */}
      <div className="space-y-3 pt-2">
        {metrics.map((item, idx) => {
          const Icon = item.icon;
          return (
            <div key={idx} className="space-y-1">
              <div className="flex justify-between text-xs font-medium">
                <span className="text-slate-300 flex items-center gap-1.5">
                  <Icon className="w-3.5 h-3.5 text-slate-400" />
                  {item.label}
                </span>
                <span className="font-mono text-cyan-400">{item.val}%</span>
              </div>
              <div className="w-full h-2 rounded-full bg-slate-800/80 overflow-hidden p-0.5 border border-slate-700/50">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${item.val}%` }}
                  transition={{ duration: 1, delay: idx * 0.15 }}
                  className={`h-full rounded-full bg-gradient-to-r ${item.color} shadow-glow-sm`}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

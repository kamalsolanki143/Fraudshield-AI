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
    { label: 'Gemini Vision Model', val: breakdown.geminiVisionScore, icon: Eye },
    { label: 'NLP Coercion Detection', val: breakdown.nlpUrgencyScore, icon: FileText },
    { label: 'Domain & Threat Registry', val: breakdown.domainReputationScore, icon: Globe },
    { label: 'OCR Text Accuracy', val: breakdown.ocrConfidence, icon: Cpu },
  ];

  return (
    <div className="p-6 bg-white rounded-3xl space-y-4 border border-slate-200 shadow-soft-sm">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Cpu className="w-5 h-5 text-blue-600" />
          <h3 className="text-sm font-heading font-semibold text-slate-900">Gemini AI Model Signals</h3>
        </div>
        <div className="flex items-center gap-1 bg-blue-50 px-3 py-1 rounded-full border border-blue-200">
          <span className="text-xs font-mono font-bold text-blue-700">{confidenceScore}%</span>
          <span className="text-[10px] text-slate-500 font-medium">Certitude</span>
        </div>
      </div>

      {/* Signal Bars */}
      <div className="space-y-3 pt-2">
        {metrics.map((item, idx) => {
          const Icon = item.icon;
          return (
            <div key={idx} className="space-y-1">
              <div className="flex justify-between text-xs font-medium">
                <span className="text-slate-700 flex items-center gap-1.5 font-sans">
                  <Icon className="w-3.5 h-3.5 text-slate-400" />
                  {item.label}
                </span>
                <span className="font-mono text-blue-700 font-bold">{item.val}%</span>
              </div>
              <div className="w-full h-2 rounded-full bg-slate-100 overflow-hidden p-0.5 border border-slate-200">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${item.val}%` }}
                  transition={{ duration: 1, delay: idx * 0.15 }}
                  className="h-full rounded-full bg-blue-600"
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

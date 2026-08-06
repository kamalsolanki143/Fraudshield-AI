import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldAlert, Sparkles, Github, Twitter, Linkedin, Heart } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

export const Footer: React.FC = () => {
  const { t } = useLanguage();

  return (
    <footer className="w-full bg-[#04070D] border-t border-slate-800/80 pt-12 pb-8 px-4 sm:px-6 lg:px-8 mt-auto">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
        
        {/* Col 1: Brand & Tagline */}
        <div className="space-y-4 md:col-span-1">
          <div className="flex items-center gap-2.5">
            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-brand-600 shadow-glow-sm">
              <ShieldAlert className="w-4 h-4 text-white" />
            </div>
            <span className="font-heading text-lg font-bold text-white">
              FraudShield <span className="text-brand-500">AI</span>
            </span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Real-time multimodal scam detection and threat neutralization built for Google Build with Gemini XPrize.
          </p>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/90 border border-emerald-500/30 w-fit">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-[10px] font-mono text-emerald-400 font-medium">
              {t('footer.status')}
            </span>
          </div>
        </div>

        {/* Col 2: Product Links */}
        <div className="space-y-3">
          <h4 className="text-xs font-mono uppercase tracking-wider text-slate-300 font-bold">Platform</h4>
          <ul className="space-y-2 text-xs text-slate-400">
            <li><Link to="/analyze" className="hover:text-cyan-400 transition-colors">Multimodal Scanner</Link></li>
            <li><Link to="/dashboard" className="hover:text-cyan-400 transition-colors">Executive Dashboard</Link></li>
            <li><Link to="/community" className="hover:text-cyan-400 transition-colors">Crowdsourced Alerts</Link></li>
            <li><Link to="/pricing" className="hover:text-cyan-400 transition-colors">Enterprise Sentinel</Link></li>
          </ul>
        </div>

        {/* Col 3: Technology */}
        <div className="space-y-3">
          <h4 className="text-xs font-mono uppercase tracking-wider text-slate-300 font-bold">Powered By</h4>
          <ul className="space-y-2 text-xs text-slate-400">
            <li className="flex items-center gap-1.5 text-cyan-300">
              <Sparkles className="w-3 h-3 text-cyan-400" /> Google Gemini 1.5 Pro
            </li>
            <li>Gemini Vision OCR Pipeline</li>
            <li>NLP Coercion Semantics</li>
            <li>FastAPI Microservices Backend</li>
          </ul>
        </div>

        {/* Col 4: Community & Legal */}
        <div className="space-y-3">
          <h4 className="text-xs font-mono uppercase tracking-wider text-slate-300 font-bold">Social & Legal</h4>
          <div className="flex items-center gap-3">
            <a href="https://github.com" target="_blank" rel="noreferrer" className="p-2 rounded-lg bg-slate-900 text-slate-400 hover:text-white border border-slate-800 transition-colors">
              <Github className="w-4 h-4" />
            </a>
            <a href="https://twitter.com" target="_blank" rel="noreferrer" className="p-2 rounded-lg bg-slate-900 text-slate-400 hover:text-white border border-slate-800 transition-colors">
              <Twitter className="w-4 h-4" />
            </a>
            <a href="https://linkedin.com" target="_blank" rel="noreferrer" className="p-2 rounded-lg bg-slate-900 text-slate-400 hover:text-white border border-slate-800 transition-colors">
              <Linkedin className="w-4 h-4" />
            </a>
          </div>
          <p className="text-[11px] text-slate-500">
            National Cyber Crime Helpline (India): <span className="text-brand-400 font-mono font-bold">1930</span>
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto pt-6 border-t border-slate-900 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-4">
        <p>© 2026 FraudShield AI Inc. All rights reserved. Built for Google Build with Gemini XPrize.</p>
        <p className="flex items-center gap-1">
          Crafted with <Heart className="w-3.5 h-3.5 text-danger animate-pulse" /> by Senior Engineering Team
        </p>
      </div>
    </footer>
  );
};

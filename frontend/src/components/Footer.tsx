import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, Sparkles, Github, Twitter, Linkedin, Heart } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

export const Footer: React.FC = () => {
  const { t } = useLanguage();

  return (
    <footer className="w-full bg-white border-t border-slate-200/80 pt-12 pb-8 px-4 sm:px-6 lg:px-8 mt-auto">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">

        {/* Col 1: Brand & Tagline */}
        <div className="space-y-4 md:col-span-1">
          <div className="flex items-center gap-2.5">
            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-blue-600 text-white shadow-soft-sm">
              <ShieldCheck className="w-4 h-4" />
            </div>
            <span className="font-heading text-base font-bold text-slate-900">
              FraudShield <span className="text-blue-600">AI</span>
            </span>
          </div>
          <p className="text-xs text-slate-500 leading-relaxed">
            Real-time multimodal scam detection and threat protection built for Google Build with Gemini XPrize.
          </p>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-200 w-fit">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-[10px] font-mono text-emerald-700 font-medium">
              {t('footer.status')}
            </span>
          </div>
        </div>

        {/* Col 2: Product Links */}
        <div className="space-y-3">
          <h4 className="text-xs font-mono uppercase tracking-wider text-slate-900 font-bold">Platform</h4>
          <ul className="space-y-2 text-xs text-slate-600">
            <li><Link to="/analyze" className="hover:text-blue-600 transition-colors">Multimodal Scanner</Link></li>
            <li><Link to="/dashboard" className="hover:text-blue-600 transition-colors">Executive Dashboard</Link></li>
            <li><Link to="/community" className="hover:text-blue-600 transition-colors">Crowdsourced Alerts</Link></li>
            <li><Link to="/pricing" className="hover:text-blue-600 transition-colors">Enterprise Protection</Link></li>
          </ul>
        </div>

        {/* Col 3: Technology */}
        <div className="space-y-3">
          <h4 className="text-xs font-mono uppercase tracking-wider text-slate-900 font-bold">Powered By</h4>
          <ul className="space-y-2 text-xs text-slate-600">
            <li className="flex items-center gap-1.5 text-blue-600 font-medium">
              <Sparkles className="w-3 h-3 text-blue-600" /> Google Gemini 1.5 Pro
            </li>
            <li>Gemini Vision OCR Pipeline</li>
            <li>NLP Coercion Reasoning</li>
            <li>FastAPI Microservices Backend</li>
          </ul>
        </div>

        {/* Col 4: Community & Helpline */}
        <div className="space-y-3">
          <h4 className="text-xs font-mono uppercase tracking-wider text-slate-900 font-bold">Helpline & Social</h4>
          <div className="flex items-center gap-3">
            <a href="https://github.com" target="_blank" rel="noreferrer" className="p-2 rounded-lg bg-slate-100 text-slate-600 hover:text-blue-600 border border-slate-200 transition-colors">
              <Github className="w-4 h-4" />
            </a>
            <a href="https://twitter.com" target="_blank" rel="noreferrer" className="p-2 rounded-lg bg-slate-100 text-slate-600 hover:text-blue-600 border border-slate-200 transition-colors">
              <Twitter className="w-4 h-4" />
            </a>
            <a href="https://linkedin.com" target="_blank" rel="noreferrer" className="p-2 rounded-lg bg-slate-100 text-slate-600 hover:text-blue-600 border border-slate-200 transition-colors">
              <Linkedin className="w-4 h-4" />
            </a>
          </div>
          <p className="text-[11px] text-slate-600">
            National Cyber Crime Helpline (India): <span className="text-blue-600 font-mono font-bold">1930</span>
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto pt-6 border-t border-slate-200/60 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-4">
        <p>© 2026 FraudShield AI Inc. All rights reserved. Built for Google Build with Gemini XPrize.</p>
        <p className="flex items-center gap-1">
          Crafted with <Heart className="w-3.5 h-3.5 text-rose-500 fill-rose-500" /> for Google Gemini XPrize
        </p>
      </div>
    </footer>
  );
};

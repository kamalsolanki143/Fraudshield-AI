import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { AlertOctagon, Home, LayoutDashboard, Sparkles } from 'lucide-react';

export const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden bg-[#070B14] text-center">
      <div className="absolute w-[500px] h-[500px] bg-danger/10 rounded-full blur-[150px] animate-pulse-glow" />

      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="max-w-lg glass-panel rounded-3xl p-8 border border-danger/30 shadow-danger-glow space-y-6 relative z-10"
      >
        <div className="w-16 h-16 rounded-2xl bg-danger/20 border border-danger/40 mx-auto flex items-center justify-center text-danger shadow-glow-sm">
          <AlertOctagon className="w-8 h-8 animate-bounce" />
        </div>

        <div className="space-y-2">
          <span className="text-xs font-mono font-bold text-danger uppercase tracking-widest">
            ERROR 404 — RADAR SIGNAL LOST
          </span>
          <h1 className="text-4xl sm:text-5xl font-heading font-extrabold text-white">
            Uncharted Security Zone
          </h1>
          <p className="text-xs sm:text-sm text-slate-300">
            The telemetry coordinate or route you requested does not exist in Gemini AI threat registry.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
          <Link
            to="/dashboard"
            className="w-full sm:w-auto px-6 py-3 rounded-xl bg-gradient-to-r from-brand-600 to-cyan-500 text-white font-semibold text-xs flex items-center justify-center gap-2 shadow-glow-sm hover:opacity-95 transition-opacity"
          >
            <LayoutDashboard className="w-4 h-4" />
            <span>Return to Control Center</span>
          </Link>

          <Link
            to="/"
            className="w-full sm:w-auto px-6 py-3 rounded-xl bg-slate-900 border border-slate-800 text-slate-200 hover:text-white font-semibold text-xs flex items-center justify-center gap-2 transition-colors"
          >
            <Home className="w-4 h-4" />
            <span>Back to Home</span>
          </Link>
        </div>
      </motion.div>
    </div>
  );
};

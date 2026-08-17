import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { AlertOctagon, Home, LayoutDashboard } from 'lucide-react';

export const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden bg-[#F8FAFC] text-center">
      <div className="absolute w-[500px] h-[500px] bg-rose-100/50 rounded-full blur-[150px]" />

      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="max-w-lg bg-white rounded-3xl p-8 border border-slate-200 shadow-soft-lg space-y-6 relative z-10"
      >
        <div className="w-16 h-16 rounded-2xl bg-rose-50 border border-rose-200 mx-auto flex items-center justify-center text-rose-600 shadow-soft-sm">
          <AlertOctagon className="w-8 h-8" />
        </div>

        <div className="space-y-2">
          <span className="text-xs font-mono font-bold text-rose-600 uppercase tracking-widest">
            ERROR 404 — PAGE NOT FOUND
          </span>
          <h1 className="text-4xl sm:text-5xl font-heading font-extrabold text-slate-900">
            Uncharted Territory
          </h1>
          <p className="text-xs sm:text-sm text-slate-600">
            The page or route you requested does not exist in Gemini AI threat registry.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
          <Link
            to="/dashboard"
            className="w-full sm:w-auto px-6 py-3 rounded-xl bg-blue-600 text-white font-semibold text-xs flex items-center justify-center gap-2 shadow-soft-sm hover:bg-blue-700 transition-colors"
          >
            <LayoutDashboard className="w-4 h-4" />
            <span>Return to Control Center</span>
          </Link>

          <Link
            to="/"
            className="w-full sm:w-auto px-6 py-3 rounded-xl bg-slate-100 border border-slate-200 text-slate-700 hover:bg-slate-200 font-semibold text-xs flex items-center justify-center gap-2 transition-colors"
          >
            <Home className="w-4 h-4" />
            <span>Back to Home</span>
          </Link>
        </div>
      </motion.div>
    </div>
  );
};

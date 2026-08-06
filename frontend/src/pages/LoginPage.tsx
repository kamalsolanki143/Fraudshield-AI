import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ShieldAlert, Sparkles, Eye, EyeOff, Lock, Mail, ArrowRight } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState('alex.vance@geminixprize.org');
  const [password, setPassword] = useState('GeminiXPrize2026!');
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (email && password) {
      login(email, 'jwt_demo_token_gemini');
      toast.success('Authenticated to FraudShield AI Sentinel Base!');
      navigate('/dashboard');
    }
  };

  const handleDemoSignIn = () => {
    setEmail('demo.judge@geminixprize.org');
    setPassword('GoogleGemini2026!');
    login('demo.judge@geminixprize.org', 'jwt_demo_judge_token');
    toast.success('Signed in as Judge Evaluator!');
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden bg-[#070B14]">
      {/* Background Animated Blobs */}
      <div className="absolute top-1/4 left-1/3 w-96 h-96 bg-brand-600/20 rounded-full blur-[120px] animate-pulse-glow" />
      <div className="absolute bottom-1/4 right-1/3 w-96 h-96 bg-cyan-500/20 rounded-full blur-[120px] animate-pulse-glow" style={{ animationDelay: '1.5s' }} />

      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-md glass-panel rounded-3xl p-8 border border-slate-700/80 shadow-2xl space-y-6 relative z-10"
      >
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-brand-600 mx-auto flex items-center justify-center shadow-glow-sm">
            <ShieldAlert className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-2xl font-heading font-extrabold text-white">Sign In to FraudShield AI</h1>
          <p className="text-xs text-slate-400">Access your multimodal threat control center</p>
        </div>

        {/* Judge Quick Demo Button */}
        <button
          onClick={handleDemoSignIn}
          className="w-full py-2.5 px-3 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 text-xs font-mono font-semibold border border-cyan-500/30 flex items-center justify-center gap-2 transition-colors"
        >
          <Sparkles className="w-4 h-4 text-cyan-400 animate-spin-slow" />
          <span>One-Click Judge Evaluator Access</span>
        </button>

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          <div>
            <label className="block text-slate-300 mb-1 font-mono">Email Address</label>
            <div className="flex items-center gap-2 px-3 py-3 rounded-xl bg-slate-950 border border-slate-800 focus-within:border-cyan-500">
              <Mail className="w-4 h-4 text-slate-500" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full bg-transparent border-none outline-none text-white placeholder-slate-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-slate-300 mb-1 font-mono">Password</label>
            <div className="flex items-center gap-2 px-3 py-3 rounded-xl bg-slate-950 border border-slate-800 focus-within:border-cyan-500">
              <Lock className="w-4 h-4 text-slate-500" />
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full bg-transparent border-none outline-none text-white placeholder-slate-500"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="text-slate-500 hover:text-slate-300"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            className="w-full py-3.5 rounded-xl bg-gradient-to-r from-brand-600 via-blue-500 to-cyan-500 text-white font-semibold shadow-glow-sm hover:opacity-95 transition-opacity flex items-center justify-center gap-2"
          >
            <span>Sign In to Defense Platform</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <p className="text-center text-xs text-slate-400">
          Don't have an account?{' '}
          <Link to="/register" className="text-cyan-400 hover:underline font-semibold">
            Register Here
          </Link>
        </p>
      </motion.div>
    </div>
  );
};

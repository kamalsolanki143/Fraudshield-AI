import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ShieldAlert, Mail, Lock, User, ArrowRight, CheckCircle2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';

export const RegisterPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const getPasswordStrength = () => {
    if (!password) return 0;
    let score = 0;
    if (password.length >= 8) score += 33;
    if (/[A-Z]/.test(password)) score += 33;
    if (/[0-9!]/.test(password)) score += 34;
    return score;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (email && password && name) {
      login(email, 'jwt_new_user_token');
      toast.success('Registration successful! Welcome to FraudShield AI.');
      navigate('/dashboard');
    }
  };

  const strength = getPasswordStrength();

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden bg-[#070B14]">
      <div className="absolute top-1/4 right-1/3 w-96 h-96 bg-brand-600/20 rounded-full blur-[120px] animate-pulse-glow" />
      <div className="absolute bottom-1/4 left-1/3 w-96 h-96 bg-cyan-500/20 rounded-full blur-[120px] animate-pulse-glow" style={{ animationDelay: '1.5s' }} />

      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-md glass-panel rounded-3xl p-8 border border-slate-700/80 shadow-2xl space-y-6 relative z-10"
      >
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-brand-600 mx-auto flex items-center justify-center shadow-glow-sm">
            <ShieldAlert className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-2xl font-heading font-extrabold text-white">Create Sentinel Account</h1>
          <p className="text-xs text-slate-400">Join the Gemini XPrize Multimodal Defense Engine</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          <div>
            <label className="block text-slate-300 mb-1 font-mono">Full Name</label>
            <div className="flex items-center gap-2 px-3 py-3 rounded-xl bg-slate-950 border border-slate-800 focus-within:border-cyan-500">
              <User className="w-4 h-4 text-slate-500" />
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                placeholder="Operator Name"
                className="w-full bg-transparent border-none outline-none text-white placeholder-slate-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-slate-300 mb-1 font-mono">Email Address</label>
            <div className="flex items-center gap-2 px-3 py-3 rounded-xl bg-slate-950 border border-slate-800 focus-within:border-cyan-500">
              <Mail className="w-4 h-4 text-slate-500" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="name@organization.com"
                className="w-full bg-transparent border-none outline-none text-white placeholder-slate-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-slate-300 mb-1 font-mono">Master Password</label>
            <div className="flex items-center gap-2 px-3 py-3 rounded-xl bg-slate-950 border border-slate-800 focus-within:border-cyan-500">
              <Lock className="w-4 h-4 text-slate-500" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="At least 8 characters..."
                className="w-full bg-transparent border-none outline-none text-white placeholder-slate-500"
              />
            </div>

            {/* Password strength bar */}
            {password && (
              <div className="mt-2 space-y-1">
                <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                  <div
                    className={`h-full transition-all ${
                      strength > 66 ? 'bg-emerald-500' : strength > 33 ? 'bg-warning' : 'bg-danger'
                    }`}
                    style={{ width: `${strength}%` }}
                  />
                </div>
                <p className="text-[10px] text-slate-400 text-right font-mono">
                  Strength: {strength > 66 ? 'Strong' : strength > 33 ? 'Medium' : 'Weak'}
                </p>
              </div>
            )}
          </div>

          <button
            type="submit"
            className="w-full py-3.5 rounded-xl bg-gradient-to-r from-brand-600 via-blue-500 to-cyan-500 text-white font-semibold shadow-glow-sm hover:opacity-95 transition-opacity flex items-center justify-center gap-2"
          >
            <span>Initialize Sentinel Account</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <p className="text-center text-xs text-slate-400">
          Already registered?{' '}
          <Link to="/login" className="text-cyan-400 hover:underline font-semibold">
            Sign In
          </Link>
        </p>
      </motion.div>
    </div>
  );
};

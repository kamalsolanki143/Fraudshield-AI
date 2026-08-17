import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ShieldCheck, Mail, Lock, User, ArrowRight } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';

export const RegisterPage: React.FC = () => {
  const { verifyOTP } = useAuth();
  const navigate = useNavigate();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const getPasswordStrength = () => {
    if (!password) return 0;
    let score = 0;
    if (password.length >= 8) score += 33;
    if (/[A-Z]/.test(password)) score += 33;
    if (/[0-9!]/.test(password)) score += 34;
    return score;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (email && password && name) {
      setIsLoading(true);
      try {
        await verifyOTP(email, '123456');
        toast.success('Registration successful! Welcome to FraudShield AI.');
        navigate('/dashboard');
      } catch (err: any) {
        toast.error(err.message || 'Registration failed.');
      } finally {
        setIsLoading(false);
      }
    }
  };

  const strength = getPasswordStrength();

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden bg-[#F8FAFC]">
      <div className="absolute top-1/4 right-1/3 w-96 h-96 bg-blue-100/60 rounded-full blur-[120px]" />

      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-md bg-white rounded-3xl p-8 border border-slate-200 shadow-soft-lg space-y-6 relative z-10"
      >
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-blue-600 mx-auto flex items-center justify-center shadow-soft-sm text-white">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-heading font-extrabold text-slate-900">Create Sentinel Account</h1>
          <p className="text-xs text-slate-500">Join the Gemini XPrize Multimodal Defense Engine</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          <div>
            <label className="block text-slate-700 mb-1 font-mono font-semibold">Full Name</label>
            <div className="flex items-center gap-2 px-3 py-3 rounded-xl bg-slate-50 border border-slate-200 focus-within:border-blue-600">
              <User className="w-4 h-4 text-slate-400" />
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                placeholder="Operator Name"
                className="w-full bg-transparent border-none outline-none text-slate-900 placeholder-slate-400"
              />
            </div>
          </div>

          <div>
            <label className="block text-slate-700 mb-1 font-mono font-semibold">Email Address</label>
            <div className="flex items-center gap-2 px-3 py-3 rounded-xl bg-slate-50 border border-slate-200 focus-within:border-blue-600">
              <Mail className="w-4 h-4 text-slate-400" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="name@organization.com"
                className="w-full bg-transparent border-none outline-none text-slate-900 placeholder-slate-400"
              />
            </div>
          </div>

          <div>
            <label className="block text-slate-700 mb-1 font-mono font-semibold">Master Password</label>
            <div className="flex items-center gap-2 px-3 py-3 rounded-xl bg-slate-50 border border-slate-200 focus-within:border-blue-600">
              <Lock className="w-4 h-4 text-slate-400" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="At least 8 characters..."
                className="w-full bg-transparent border-none outline-none text-slate-900 placeholder-slate-400"
              />
            </div>

            {/* Password strength bar */}
            {password && (
              <div className="mt-2 space-y-1">
                <div className="w-full h-1.5 rounded-full bg-slate-100 overflow-hidden">
                  <div
                    className={`h-full transition-all ${
                      strength > 66 ? 'bg-emerald-500' : strength > 33 ? 'bg-amber-500' : 'bg-rose-500'
                    }`}
                    style={{ width: `${strength}%` }}
                  />
                </div>
                <p className="text-[10px] text-slate-500 text-right font-mono font-medium">
                  Strength: {strength > 66 ? 'Strong' : strength > 33 ? 'Medium' : 'Weak'}
                </p>
              </div>
            )}
          </div>

          <button
            type="submit"
            className="w-full py-3.5 rounded-xl bg-blue-600 text-white font-semibold shadow-soft-sm hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
          >
            <span>Initialize Account</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <p className="text-center text-xs text-slate-500">
          Already registered?{' '}
          <Link to="/login" className="text-blue-600 hover:underline font-semibold">
            Sign In
          </Link>
        </p>
      </motion.div>
    </div>
  );
};

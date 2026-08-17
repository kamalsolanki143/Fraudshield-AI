import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldCheck, Sparkles, Mail, ArrowRight, CheckCircle2, Loader2, KeyRound } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';

export const LoginPage: React.FC = () => {
  const { requestOTP, verifyOTP } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [step, setStep] = useState<'EMAIL' | 'OTP'>('EMAIL');
  const [isLoading, setIsLoading] = useState(false);

  const from = location.state?.from?.pathname || '/dashboard';

  const handleRequestOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    setIsLoading(true);
    try {
      await requestOTP(email);
      setStep('OTP');
      toast.success('Secure OTP sent to your email.');
    } catch (error) {
      toast.error('Failed to send OTP. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!otp) return;

    setIsLoading(true);
    try {
      await verifyOTP(email, otp);
      toast.success('Authentication successful.');
      navigate(from, { replace: true });
    } catch (error: any) {
      toast.error(error.message || 'Invalid OTP code.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoSignIn = async () => {
    setIsLoading(true);
    try {
      await verifyOTP('demo.judge@geminixprize.org', '123456');
      toast.success('Signed in as Judge Evaluator!');
      navigate(from, { replace: true });
    } catch (error) {
      toast.error('Demo login failed.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden bg-[#F3F4F9]">

      {/* Background Soft Purple Gradients */}
      <div className="absolute top-1/4 left-1/3 w-96 h-96 bg-purple-200/40 rounded-full blur-[120px]" />
      <div className="absolute bottom-1/4 right-1/3 w-96 h-96 bg-indigo-200/40 rounded-full blur-[120px]" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="w-full max-w-md bg-white rounded-3xl p-8 border border-slate-100 shadow-soft-lg space-y-8 relative z-10"
      >
        <div className="text-center space-y-3">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-violet-600 to-indigo-600 text-white mx-auto flex items-center justify-center shadow-soft-md">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-heading font-extrabold text-slate-900">FraudShield AI</h1>
            <p className="text-xs text-slate-500 mt-1">Access your threat protection dashboard</p>
          </div>
        </div>

        <AnimatePresence mode="wait">
          {step === 'EMAIL' ? (
            <motion.form
              key="email-form"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              onSubmit={handleRequestOTP}
              className="space-y-5"
            >
              <div className="space-y-1.5">
                <label className="text-xs font-mono uppercase tracking-wider text-slate-500 font-semibold ml-1">Work Email</label>
                <div className="flex items-center gap-3 px-4 py-3.5 rounded-2xl bg-slate-50 border border-slate-200 focus-within:border-indigo-600 focus-within:bg-white transition-colors">
                  <Mail className="w-4 h-4 text-slate-400" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    placeholder="alex@company.com"
                    className="w-full bg-transparent border-none outline-none text-slate-900 text-sm placeholder-slate-400"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-indigo-600 to-violet-600 hover:opacity-95 text-white font-bold text-xs shadow-soft-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <>
                    <span>Send Login Code</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>

              <div className="relative flex items-center py-2">
                <div className="flex-grow border-t border-slate-200"></div>
                <span className="flex-shrink-0 mx-4 text-slate-400 text-xs font-mono uppercase">Or</span>
                <div className="flex-grow border-t border-slate-200"></div>
              </div>

              <button
                type="button"
                onClick={handleDemoSignIn}
                disabled={isLoading}
                className="w-full py-3 px-3 rounded-2xl bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-xs font-bold border border-indigo-200 flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
              >
                {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4 text-indigo-600" />}
                <span>One-Click Judge Evaluator Access</span>
              </button>
            </motion.form>
          ) : (
            <motion.form
              key="otp-form"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              onSubmit={handleVerifyOTP}
              className="space-y-5"
            >
              <div className="space-y-1.5 text-center mb-6">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-emerald-50 mb-2">
                  <CheckCircle2 className="w-6 h-6 text-emerald-600" />
                </div>
                <p className="text-xs text-slate-600">
                  We sent a temporary login code to <br/>
                  <strong className="text-slate-900">{email}</strong>
                </p>
                <button
                  type="button"
                  onClick={() => setStep('EMAIL')}
                  className="text-xs text-indigo-600 hover:underline mt-1 font-semibold"
                >
                  Wrong email?
                </button>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-mono uppercase tracking-wider text-slate-500 font-semibold ml-1">Passcode (Use 123456)</label>
                <div className="flex items-center gap-3 px-4 py-3.5 rounded-2xl bg-slate-50 border border-slate-200 focus-within:border-emerald-600 focus-within:bg-white transition-colors">
                  <KeyRound className="w-4 h-4 text-slate-400" />
                  <input
                    type="text"
                    value={otp}
                    onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                    required
                    maxLength={6}
                    placeholder="• • • • • •"
                    className="w-full bg-transparent border-none outline-none text-slate-900 text-center text-lg tracking-[0.5em] font-mono placeholder-slate-400"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading || otp.length < 6}
                className="w-full py-3.5 rounded-2xl bg-emerald-600 text-white font-bold text-xs shadow-soft-sm hover:bg-emerald-700 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <span>Verify & Sign In</span>
                )}
              </button>
            </motion.form>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
};

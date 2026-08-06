import React, { useState } from 'react';
import { motion } from 'framer-motion';
import confetti from 'canvas-confetti';
import { 
  CreditCard, 
  Check, 
  Sparkles, 
  ShieldCheck, 
  Zap, 
  Building2, 
  Lock,
  ArrowRight
} from 'lucide-react';
import toast from 'react-hot-toast';
import { Sidebar } from '../components/Sidebar';
import { GlassCard } from '../components/GlassCard';
import { Modal } from '../components/Modal';
import { useLanguage } from '../context/LanguageContext';

export const PricingPage: React.FC = () => {
  const { t } = useLanguage();
  const [isAnnual, setIsAnnual] = useState(true);
  const [selectedPlanModal, setSelectedPlanModal] = useState<string | null>(null);

  const plans = [
    {
      id: 'plan_free',
      name: 'Guardian Free',
      description: 'Essential scam protection for individual users & families.',
      priceMonthly: 0,
      priceAnnual: 0,
      features: [
        '50 Multimodal Gemini AI Scans / month',
        'Text & URL Fraud Analysis',
        'Hindi & English Dual Language',
        'Community Threat Alerts Access',
      ],
      cta: 'Current Plan',
      popular: false,
    },
    {
      id: 'plan_pro',
      name: 'Shield Pro',
      description: 'Advanced real-time AI security for power users & freelancers.',
      priceMonthly: 12,
      priceAnnual: 9,
      features: [
        'Unlimited Gemini 1.5 Pro Vision Scans',
        'High-Resolution Screenshot OCR Inspection',
        'Priority Cyber Crime 1930 Direct Filing Helper',
        'WhatsApp Automated Scam Radar Bot',
        'Custom Risk Threshold Alerts',
      ],
      cta: 'Upgrade to Shield Pro',
      popular: true,
    },
    {
      id: 'plan_enterprise',
      name: 'Sentinel Enterprise',
      description: 'Dedicated anti-fraud SDK & API for banks, fintech, and apps.',
      priceMonthly: 89,
      priceAnnual: 75,
      features: [
        'Full REST API & SDK Access (Vite/Node/Python)',
        'Sub-second Multimodal Inference SLA',
        'Custom AI Model Fine-tuning on Local Fraud Data',
        '24/7 Dedicated Cyber Security Engineer SLA',
        '99.99% Uptime Guarantee',
      ],
      cta: 'Contact Enterprise Team',
      popular: false,
    },
  ];

  const handleSelectPlan = (planName: string) => {
    setSelectedPlanModal(planName);
  };

  const handleConfirmCheckout = () => {
    confetti({
      particleCount: 100,
      spread: 70,
      origin: { y: 0.6 },
    });
    toast.success(`Successfully subscribed to ${selectedPlanModal}!`);
    setSelectedPlanModal(null);
  };

  return (
    <div className="flex min-h-[calc(100vh-4rem)]">
      <Sidebar />

      <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-12 overflow-x-hidden">
        
        {/* Header */}
        <div className="text-center space-y-4 max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/30 text-brand-400 text-xs font-mono font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Funded Startup Tier Security</span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-heading font-extrabold text-white">
            Transparent Pricing for <span className="gradient-text-blue">Uncompromised Protection</span>
          </h1>

          <p className="text-xs sm:text-sm text-slate-300">
            Scale your fraud defense with Google Gemini XPrize multimodal intelligence. Cancel anytime.
          </p>

          {/* Billing Switcher */}
          <div className="pt-4 flex items-center justify-center gap-3">
            <span className={`text-xs font-medium ${!isAnnual ? 'text-white' : 'text-slate-400'}`}>Monthly</span>
            <button
              onClick={() => setIsAnnual(!isAnnual)}
              className="relative w-14 h-7 rounded-full bg-slate-800 p-1 border border-slate-700 transition-colors"
            >
              <motion.div
                animate={{ x: isAnnual ? 26 : 0 }}
                transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                className="w-5 h-5 rounded-full bg-gradient-to-r from-brand-500 to-cyan-400 shadow-glow-sm"
              />
            </button>
            <span className={`text-xs font-medium flex items-center gap-1.5 ${isAnnual ? 'text-white' : 'text-slate-400'}`}>
              Annual <span className="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 text-[10px] font-mono font-bold border border-emerald-500/30">Save 20%</span>
            </span>
          </div>
        </div>

        {/* Pricing Cards Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {plans.map((plan) => {
            const price = isAnnual ? plan.priceAnnual : plan.priceMonthly;

            return (
              <GlassCard
                key={plan.id}
                hoverEffect
                glowColor={plan.popular ? 'blue' : 'purple'}
                className={`relative flex flex-col justify-between p-8 space-y-6 ${
                  plan.popular ? 'border-brand-500/60 shadow-glow-md bg-slate-900/80' : ''
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-gradient-to-r from-brand-600 to-cyan-500 text-white text-[10px] font-mono font-bold uppercase tracking-wider shadow-glow-sm">
                    Most Popular Choice
                  </div>
                )}

                <div className="space-y-4">
                  <h3 className="text-xl font-heading font-bold text-white">{plan.name}</h3>
                  <p className="text-xs text-slate-400 leading-relaxed">{plan.description}</p>

                  <div className="flex items-baseline gap-1">
                    <span className="text-4xl font-heading font-extrabold text-white">${price}</span>
                    <span className="text-xs text-slate-400 font-mono">/ user / month</span>
                  </div>

                  <ul className="space-y-3 pt-4 border-t border-slate-800 text-xs">
                    {plan.features.map((feat, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-slate-300">
                        <Check className="w-4 h-4 text-cyan-400 mt-0.5 flex-shrink-0" />
                        <span>{feat}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <button
                  onClick={() => handleSelectPlan(plan.name)}
                  className={`w-full py-3 rounded-2xl font-semibold text-xs transition-all shadow-glow-sm ${
                    plan.popular
                      ? 'bg-gradient-to-r from-brand-600 via-blue-500 to-cyan-500 text-white hover:opacity-95'
                      : 'bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-800'
                  }`}
                >
                  {plan.cta}
                </button>
              </GlassCard>
            );
          })}
        </div>

        {/* Modal Simulation */}
        <Modal
          isOpen={!!selectedPlanModal}
          onClose={() => setSelectedPlanModal(null)}
          title={`Activate ${selectedPlanModal}`}
        >
          <div className="space-y-4 text-xs">
            <p className="text-slate-300 leading-relaxed">
              You are activating <span className="text-cyan-400 font-bold">{selectedPlanModal}</span> with 14-day zero-risk trial access powered by Google Gemini XPrize.
            </p>
            <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-2 font-mono">
              <div className="flex justify-between text-slate-400">
                <span>Selected Plan</span>
                <span className="text-white">{selectedPlanModal}</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Billing Interval</span>
                <span className="text-white">{isAnnual ? 'Annual (20% Off)' : 'Monthly'}</span>
              </div>
              <div className="flex justify-between font-bold text-white pt-2 border-t border-slate-800">
                <span>Total Due Today</span>
                <span className="text-emerald-400">$0.00 (14-Day Free Trial)</span>
              </div>
            </div>

            <div className="pt-2 flex justify-end gap-3">
              <button
                onClick={() => setSelectedPlanModal(null)}
                className="px-4 py-2 rounded-xl bg-slate-900 text-slate-300 hover:bg-slate-800"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmCheckout}
                className="px-5 py-2 rounded-xl bg-gradient-to-r from-brand-600 to-cyan-500 text-white font-semibold shadow-glow-sm"
              >
                Confirm Trial Activation
              </button>
            </div>
          </div>
        </Modal>
      </main>
    </div>
  );
};

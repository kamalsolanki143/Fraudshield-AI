import React, { useState } from 'react';
import { motion } from 'framer-motion';
import confetti from 'canvas-confetti';
import {
  Check,
  Sparkles
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
      priceMonthly: 499,
      priceAnnual: 399,
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
      priceMonthly: 4999,
      priceAnnual: 3999,
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
    <div className="flex min-h-screen bg-[#F3F4F9]">
      <Sidebar />

      <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-5xl space-y-8 overflow-x-hidden">

        {/* Header */}
        <div className="text-center space-y-3 max-w-2xl mx-auto">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 text-xs font-bold">
            <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
            <span>Funded Startup Tier Security</span>
          </div>

          <h1 className="text-3xl sm:text-4xl font-heading font-extrabold text-slate-900">
            Transparent Pricing for <span className="text-indigo-600">Uncompromised Protection</span>
          </h1>

          <p className="text-xs sm:text-sm text-slate-600">
            Scale your fraud defense with Google Gemini XPrize multimodal intelligence. Cancel anytime.
          </p>

          {/* Billing Switcher (NovaShop Pill) */}
          <div className="pt-4 flex items-center justify-center gap-3">
            <span className={`text-xs font-semibold ${!isAnnual ? 'text-slate-900' : 'text-slate-500'}`}>Monthly</span>
            <button
              onClick={() => setIsAnnual(!isAnnual)}
              className="relative w-14 h-7 rounded-full bg-slate-200 p-1 border border-slate-300 transition-colors"
            >
              <motion.div
                animate={{ x: isAnnual ? 26 : 0 }}
                transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                className="w-5 h-5 rounded-full bg-indigo-600 shadow-soft-sm"
              />
            </button>
            <span className={`text-xs font-semibold flex items-center gap-1.5 ${isAnnual ? 'text-slate-900' : 'text-slate-500'}`}>
              Annual <span className="px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 text-[10px] font-mono font-bold border border-emerald-200">Save 20%</span>
            </span>
          </div>
        </div>

        {/* Pricing Cards Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {plans.map((plan) => {
            const price = isAnnual ? plan.priceAnnual : plan.priceMonthly;

            return (
              <GlassCard
                key={plan.id}
                hoverEffect
                className={`relative flex flex-col justify-between p-8 space-y-6 ${
                  plan.popular ? 'border-2 border-indigo-600 shadow-soft-lg bg-white' : ''
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-gradient-to-r from-indigo-600 to-violet-600 text-white text-[10px] font-mono font-bold uppercase tracking-wider shadow-soft-sm">
                    Most Popular Choice
                  </div>
                )}

                <div className="space-y-4">
                  <h3 className="text-xl font-heading font-bold text-slate-900">{plan.name}</h3>
                  <p className="text-xs text-slate-600 leading-relaxed">{plan.description}</p>

                  <div className="flex items-baseline gap-1">
                    <span className="text-4xl font-heading font-extrabold text-slate-900">₹{price}</span>
                    <span className="text-xs text-slate-500 font-mono">/ user / month</span>
                  </div>

                  <ul className="space-y-3 pt-4 border-t border-slate-100 text-xs">
                    {plan.features.map((feat, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-slate-700">
                        <Check className="w-4 h-4 text-indigo-600 mt-0.5 flex-shrink-0" />
                        <span>{feat}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <button
                  onClick={() => handleSelectPlan(plan.name)}
                  className={`w-full py-3 rounded-2xl font-bold text-xs transition-all shadow-soft-sm ${
                    plan.popular
                      ? 'bg-gradient-to-r from-indigo-600 to-violet-600 text-white hover:opacity-95'
                      : 'bg-slate-100 hover:bg-slate-200 text-slate-800 border border-slate-200'
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
            <p className="text-slate-600 leading-relaxed">
              You are activating <span className="text-indigo-600 font-bold">{selectedPlanModal}</span> with 14-day zero-risk trial access powered by Google Gemini XPrize.
            </p>
            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2 font-mono">
              <div className="flex justify-between text-slate-600">
                <span>Selected Plan</span>
                <span className="text-slate-900 font-semibold">{selectedPlanModal}</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Billing Interval</span>
                <span className="text-slate-900 font-semibold">{isAnnual ? 'Annual (20% Off)' : 'Monthly'}</span>
              </div>
              <div className="flex justify-between font-bold text-slate-900 pt-2 border-t border-slate-200">
                <span>Total Due Today</span>
                <span className="text-emerald-600">₹0.00 (14-Day Free Trial)</span>
              </div>
            </div>

            <div className="pt-2 flex justify-end gap-3">
              <button
                onClick={() => setSelectedPlanModal(null)}
                className="px-4 py-2 rounded-xl bg-slate-100 text-slate-700 font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmCheckout}
                className="px-5 py-2 rounded-xl bg-indigo-600 text-white font-bold shadow-soft-sm hover:bg-indigo-700"
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

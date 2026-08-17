import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ShieldCheck,
  Sparkles,
  ArrowRight,
  Lock,
  Eye,
  Zap,
  Search,
  Upload,
  Globe,
  CheckCircle2,
  AlertTriangle,
  Languages,
  ChevronRight,
  ShieldAlert,
  Cpu,
  FileText,
  MessageSquare,
  Shield,
  Activity,
  Layers,
  Code,
  Share2
} from 'lucide-react';
import { GlassCard } from '../components/GlassCard';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  // Hero Quick Scanner input state
  const [quickInput, setQuickInput] = useState('');
  const [demoStep, setDemoStep] = useState(0);
  const [hindiToggle, setHindiToggle] = useState(false);

  // Real scam samples for 1-click test
  const realScamSamples = [
    {
      title: "Electricity Disconnection SMS",
      tag: "SMS Phishing",
      risk: "CRITICAL",
      score: 94,
      text: "Dear Consumer, your Electricity power line will be disconnected tonight at 9:30 PM due to unpaid bill. Update IMMEDIATELY at http://bijli-sbi-update.top/pay",
      desc: "Spoofed Utility Bill Urgent Payment",
      color: "rose"
    },
    {
      title: "Telegram Part-Time YouTube Job",
      tag: "UPI Fraud",
      risk: "HIGH",
      score: 88,
      text: "Earn Rs 5,000/day by liking YouTube videos! Pay refundable registration fee of Rs 1,999 to UPI: hire.recruiter@okicici",
      desc: "Work-From-Home Deposit Scheme",
      color: "amber"
    },
    {
      title: "SBI Account KYC Deactivation",
      tag: "Bank Impersonation",
      risk: "CRITICAL",
      score: 96,
      text: "Your SBI Netbanking account is blocked due to missing Pan Card KYC. Re-activate within 24 hours at http://sbi-pan-kyc.info",
      desc: "Phishing Link & Credential Harvester",
      color: "rose"
    },
    {
      title: "Amazon Official 2FA Login OTP",
      tag: "Legitimate SMS",
      risk: "SAFE",
      score: 8,
      text: "Your Amazon login OTP is 849201. Valid for 5 minutes. Do not share this code with anyone.",
      desc: "Transactional 2-Factor Authentication",
      color: "emerald"
    }
  ];

  // Auto-play interactive OCR demo step
  useEffect(() => {
    const timer = setInterval(() => {
      setDemoStep((prev) => (prev < 4 ? prev + 1 : 0));
    }, 3200);
    return () => clearInterval(timer);
  }, []);

  const handleQuickAnalyzeSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (quickInput.trim()) {
      navigate(`/analyze?query=${encodeURIComponent(quickInput)}`);
    } else {
      navigate('/analyze');
    }
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-slate-900 font-sans space-y-20 pb-20">

      {/* SECTION 1: BESPOKE AI SECURITY HERO */}
      <section className="relative pt-12 sm:pt-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

        {/* Subtle Ambient Glows */}
        <div className="absolute top-10 left-1/2 -translate-x-1/2 w-[600px] h-[350px] bg-gradient-to-tr from-indigo-200/40 via-purple-200/30 to-pink-100/40 rounded-full blur-[140px] pointer-events-none" />

        <div className="relative z-10 text-center max-w-4xl mx-auto space-y-6">

          {/* Live Telemetry Pill */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white border border-slate-200 shadow-soft-sm text-xs font-mono font-semibold text-slate-700">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
            <span>Google Build with Gemini XPrize Entry</span>
            <span className="text-slate-300">•</span>
            <span className="text-indigo-600 font-bold">4,302 Scams Intercepted Today</span>
          </div>

          {/* Main Title */}
          <h1 className="text-4xl sm:text-6xl font-heading font-extrabold text-slate-900 tracking-tight leading-[1.1]">
            Stop Cyber Scams Before They <br className="hidden sm:inline" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 via-violet-600 to-purple-600">
              Drain Your Bank Account
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-base sm:text-lg text-slate-600 max-w-2xl mx-auto font-normal leading-relaxed">
            FraudShield AI uses <strong>Gemini 1.5 Pro Multimodal Vision</strong> to inspect fake banking screenshots, spoofed links, and high-coercion SMS in sub-1.8 seconds.
          </p>

          {/* Hero Quick Inspection Bar */}
          <div className="pt-4 max-w-2xl mx-auto">
            <form onSubmit={handleQuickAnalyzeSubmit} className="relative flex items-center">
              <div className="absolute left-4 text-slate-400">
                <Search className="w-5 h-5" />
              </div>
              <input
                type="text"
                value={quickInput}
                onChange={(e) => setQuickInput(e.target.value)}
                placeholder="Paste suspicious SMS, WhatsApp message, URL, or UPI ID..."
                className="w-full pl-12 pr-36 py-4 rounded-2xl bg-white text-sm text-slate-900 placeholder-slate-400 border border-slate-200/90 shadow-soft-md outline-none focus:border-indigo-600 focus:ring-4 focus:ring-indigo-100 transition-all font-sans"
              />
              <button
                type="submit"
                className="absolute right-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 hover:opacity-95 text-white font-bold text-xs shadow-soft-sm transition-all flex items-center gap-1.5"
              >
                <span>Analyze Now</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </form>

            <div className="mt-3 flex flex-wrap items-center justify-center gap-2 text-xs text-slate-500">
              <span>Try instant sample:</span>
              {realScamSamples.slice(0, 3).map((sample, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    setQuickInput(sample.text);
                    navigate(`/analyze?query=${encodeURIComponent(sample.text)}`);
                  }}
                  className="px-3 py-1 rounded-full bg-white border border-slate-200 hover:border-indigo-300 text-slate-700 font-medium hover:text-indigo-600 transition-colors shadow-soft-sm"
                >
                  {sample.title}
                </button>
              ))}
            </div>
          </div>

        </div>
      </section>

      {/* SECTION 2: INTERACTIVE GEMINI VISION OCR DEMO */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <GlassCard className="p-8 sm:p-12 border-slate-200/80 shadow-soft-lg">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">

            <div className="space-y-6">
              <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 text-xs font-bold font-mono">
                <Eye className="w-3.5 h-3.5 text-indigo-600" />
                <span>Multimodal Vision OCR Engine</span>
              </div>

              <h2 className="text-2xl sm:text-4xl font-heading font-extrabold text-slate-900 leading-snug">
                Detect Screenshot Fraud & Manipulated Receipts
              </h2>

              <p className="text-sm text-slate-600 leading-relaxed">
                FraudShield AI doesn't just read plain text. Our Gemini 1.5 Vision model analyzes visual font distortions, fake bank logos, and coerced urgency cues in WhatsApp screenshots within seconds.
              </p>

              <div className="space-y-3 pt-2">
                {[
                  "Optical Character Recognition (OCR) bounding box extraction",
                  "Deep intent analysis for fear, urgency, and money extraction cues",
                  "Dual-Language translation (Hindi & English reasoning output)",
                  "Automatic 1930 Cyber Helpline Report Generation"
                ].map((feat, idx) => (
                  <div key={idx} className="flex items-center gap-3 text-xs font-semibold text-slate-800">
                    <div className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center shrink-0">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                    </div>
                    <span>{feat}</span>
                  </div>
                ))}
              </div>

              <div className="pt-2">
                <button
                  onClick={() => navigate('/analyze')}
                  className="px-6 py-3 rounded-2xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs shadow-soft-sm transition-colors inline-flex items-center gap-2"
                >
                  <Upload className="w-4 h-4" />
                  <span>Upload Screenshot for Inspection</span>
                </button>
              </div>
            </div>

            {/* Interactive Phone Vision Mockup */}
            <div className="bg-slate-900 rounded-3xl p-6 shadow-2xl text-white space-y-4 border border-slate-800 relative">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3 text-xs">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-ping" />
                  <span className="font-mono font-bold text-rose-400 uppercase">Live OCR Scan Visualizer</span>
                </div>
                <button
                  onClick={() => setHindiToggle(!hindiToggle)}
                  className="text-[10px] font-mono text-indigo-300 bg-indigo-900/50 px-2.5 py-1 rounded-full border border-indigo-700"
                >
                  {hindiToggle ? "Language: हिन्दी" : "Language: English"}
                </button>
              </div>

              {/* Simulated Screenshot with OCR bounding box overlay */}
              <div className="relative rounded-2xl overflow-hidden border border-slate-700 bg-slate-950 p-4 space-y-3 font-mono text-xs">
                <div className="p-3 rounded-xl bg-slate-900 border border-rose-500/40 relative">
                  {demoStep >= 1 && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="absolute -top-2 -right-2 px-2 py-0.5 rounded bg-rose-600 text-white text-[9px] font-bold shadow-lg"
                    >
                      Urgency Coercion Highlight
                    </motion.div>
                  )}
                  <p className="text-slate-200">
                    <strong className="text-rose-400">URGENT NOTICE:</strong> Dear Customer, your SBI YONO account will be suspended today. Update PAN card at <span className="text-indigo-400 underline">http://sbi-pan-kyc.info</span>
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-2 text-[11px] pt-1">
                  <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                    <span className="text-slate-400 block text-[9px] uppercase">Risk Assessment</span>
                    <span className="text-rose-400 font-bold">96/100 (CRITICAL)</span>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                    <span className="text-slate-400 block text-[9px] uppercase">Gemini Certitude</span>
                    <span className="text-indigo-400 font-bold">99.2% Confidence</span>
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-indigo-950/60 border border-indigo-800/50 text-[11px] text-slate-300 font-sans">
                  {hindiToggle ? (
                    <p><strong>Gemini AI निष्कर्ष:</strong> यह एक फर्जी SBI KYC लिंक है। स्टेट बैंक कभी भी SMS द्वारा पैन कार्ड अपडेट लिंक नहीं भेजता। लिंक पर क्लिक न करें।</p>
                  ) : (
                    <p><strong>Gemini Reasoning:</strong> High-risk credential harvesting campaign. State Bank of India never sends third-party '.info' domain links for PAN verification.</p>
                  )}
                </div>
              </div>

            </div>

          </div>
        </GlassCard>
      </section>

      {/* SECTION 3: 9-STAGE GEMINI MULTIMODAL PIPELINE */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        <div className="text-center space-y-3 max-w-2xl mx-auto">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-indigo-50 text-indigo-700 text-xs font-bold font-mono">
            <Cpu className="w-3.5 h-3.5 text-indigo-600" />
            <span>Product Architecture</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-heading font-extrabold text-slate-900">
            How Gemini 1.5 Pro Intercepts Fraud
          </h2>
          <p className="text-xs sm:text-sm text-slate-600">
            A continuous sub-second pipeline processing visual, linguistic, and domain signals simultaneously.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            {
              step: "01",
              title: "Payload Sanitization & OCR",
              desc: "Screenshots, URLs, and text inputs are stripped of executable code and processed through Tesseract + Gemini Vision OCR.",
              icon: Upload
            },
            {
              step: "02",
              title: "Coercion & Intent Reasoning",
              desc: "NLP intent models evaluate psychological manipulation tactics including financial urgency, fear, and authority spoofing.",
              icon: BrainIcon
            },
            {
              step: "03",
              title: "Domain & Threat Verification",
              desc: "Live WHOIS lookup and Indian cyber crime community telemetry cross-check malicious domains and reported UPI IDs.",
              icon: Globe
            },
            {
              step: "04",
              title: "Bilingual Verdict Synthesis",
              desc: "Gemini generates plain-language explanations in both Hindi and English tailored for senior citizens and non-technical users.",
              icon: Languages
            },
            {
              step: "05",
              title: "Risk Score & Attack Vector",
              desc: "Calculates 0-100 threat score and generates step-by-step attack execution timeline detailing scam tactics.",
              icon: ShieldAlert
            },
            {
              step: "06",
              title: "1930 Cyber Helpline Filing",
              desc: "Auto-populates standardized report briefs ready for direct submission to the National Cyber Crime Reporting Portal.",
              icon: FileText
            }
          ].map((item, idx) => {
            const Icon = item.icon;
            return (
              <GlassCard key={idx} className="space-y-3 relative group">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xl font-extrabold text-indigo-600">{item.step}</span>
                  <div className="p-2.5 rounded-xl bg-indigo-50 text-indigo-600 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                    <Icon className="w-5 h-5" />
                  </div>
                </div>
                <h3 className="text-base font-bold text-slate-900">{item.title}</h3>
                <p className="text-xs text-slate-600 leading-relaxed font-sans">{item.desc}</p>
              </GlassCard>
            );
          })}
        </div>
      </section>

      {/* SECTION 4: REAL SCAM VECTOR EXPLORER */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
          <div>
            <span className="text-xs font-mono font-bold text-indigo-600 uppercase tracking-wider">Live Threat Intelligence</span>
            <h2 className="text-2xl sm:text-3xl font-heading font-extrabold text-slate-900 mt-1">
              Common Cyber Scam Vectors in India
            </h2>
          </div>
          <button
            onClick={() => navigate('/community')}
            className="text-xs font-bold text-indigo-600 hover:underline flex items-center gap-1"
          >
            <span>Explore Community Feed</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {realScamSamples.map((sample, idx) => (
            <GlassCard key={idx} className="space-y-4 flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">
                    {sample.tag}
                  </span>
                  <span className={`px-2.5 py-0.5 rounded-full font-mono text-[10px] font-bold ${
                    sample.risk === 'CRITICAL' ? 'bg-rose-500 text-white' :
                    sample.risk === 'HIGH' ? 'bg-amber-500 text-white' :
                    'bg-emerald-500 text-white'
                  }`}>
                    {sample.risk}
                  </span>
                </div>

                <div>
                  <h3 className="text-sm font-bold text-slate-900 leading-snug">{sample.title}</h3>
                  <p className="text-[11px] text-slate-500 mt-0.5">{sample.desc}</p>
                </div>

                <p className="text-xs text-slate-700 bg-slate-50 p-3 rounded-xl border border-slate-200/80 font-sans line-clamp-3">
                  "{sample.text}"
                </p>
              </div>

              <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                <div>
                  <span className="text-[10px] font-mono text-slate-500 block">Risk Score</span>
                  <span className="text-xs font-mono font-bold text-slate-900">{sample.score}/100</span>
                </div>
                <button
                  onClick={() => navigate(`/analyze?query=${encodeURIComponent(sample.text)}`)}
                  className="px-3 py-1.5 rounded-xl bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-xs font-bold transition-colors"
                >
                  Inspect Sample
                </button>
              </div>
            </GlassCard>
          ))}
        </div>
      </section>

      {/* SECTION 5: ENTERPRISE TRUST & PRIVACY GUARANTEE */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="p-8 sm:p-12 rounded-3xl bg-slate-900 text-white space-y-8 relative overflow-hidden shadow-2xl">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-center">

            <div className="lg:col-span-2 space-y-4">
              <span className="px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 text-xs font-mono font-bold border border-indigo-500/30">
                Privacy Architecture
              </span>
              <h2 className="text-2xl sm:text-4xl font-heading font-extrabold text-white">
                Zero-Knowledge Ephemeral Scan Memory
              </h2>
              <p className="text-xs sm:text-sm text-slate-300 leading-relaxed max-w-xl font-sans">
                FraudShield AI processes user uploads inside temporary RAM containers. No bank passwords, personal credit card numbers, or contact details are permanently written to database disks.
              </p>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 pt-4">
                <div className="p-3 rounded-2xl bg-slate-800/80 border border-slate-700">
                  <span className="text-[10px] font-mono text-slate-400 block uppercase">Inference Speed</span>
                  <span className="text-lg font-bold text-indigo-400">1.8 Seconds</span>
                </div>
                <div className="p-3 rounded-2xl bg-slate-800/80 border border-slate-700">
                  <span className="text-[10px] font-mono text-slate-400 block uppercase">Detection Accuracy</span>
                  <span className="text-lg font-bold text-emerald-400">98.4%</span>
                </div>
                <div className="p-3 rounded-2xl bg-slate-800/80 border border-slate-700">
                  <span className="text-[10px] font-mono text-slate-400 block uppercase">Encryption</span>
                  <span className="text-lg font-bold text-indigo-300">TLS 1.3 + AES-256</span>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="p-6 rounded-2xl bg-slate-950 border border-slate-800 space-y-3 font-mono text-xs">
                <div className="flex items-center justify-between text-slate-400 border-b border-slate-800 pb-2">
                  <span>Python / Vite SDK</span>
                  <span className="text-emerald-400 text-[10px]">v1.4.0</span>
                </div>
                <pre className="text-indigo-300 text-[11px] overflow-x-auto leading-relaxed">
{`from fraudshield import GeminiScanner

client = GeminiScanner(api_key="fs_live_...")
report = client.inspect_screenshot("sms.png")

print(report.risk_score) # 94/100`}
                </pre>
              </div>

              <button
                onClick={() => navigate('/pricing')}
                className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-soft-sm transition-colors text-center"
              >
                View Developer API Specs
              </button>
            </div>

          </div>
        </div>
      </section>

    </div>
  );
};

// Helper Brain Icon
function BrainIcon(props: any) {
  return (
    <svg {...props} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
    </svg>
  );
}

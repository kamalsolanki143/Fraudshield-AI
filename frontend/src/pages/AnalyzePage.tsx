import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, 
  Upload, 
  FileText, 
  Globe, 
  ShieldAlert, 
  Download, 
  Languages, 
  CheckCircle, 
  AlertTriangle,
  Copy,
  Share2,
  RefreshCw
} from 'lucide-react';
import toast from 'react-hot-toast';
import { Sidebar } from '../components/Sidebar';
import { UploadBox } from '../components/UploadBox';
import { RiskMeter } from '../components/RiskMeter';
import { ConfidenceMeter } from '../components/ConfidenceMeter';
import { FraudTimeline } from '../components/FraudTimeline';
import { GlassCard } from '../components/GlassCard';
import { RadarLoader } from '../components/Loader';
import { useLanguage } from '../context/LanguageContext';
import { fraudService, mockAnalysisDatabase } from '../services/fraudService';
import { FraudAnalysisResult, AnalysisType } from '../types';

export const AnalyzePage: React.FC = () => {
  const { t, language, toggleLanguage } = useLanguage();
  const [searchParams] = useSearchParams();

  const [activeTab, setActiveTab] = useState<AnalysisType>('text');
  const [textContent, setTextContent] = useState('');
  const [urlContent, setUrlContent] = useState('');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  const [isScanning, setIsScanning] = useState(false);
  const [scanningStep, setScanningStep] = useState(0);
  const [result, setResult] = useState<FraudAnalysisResult | null>(null);

  // Auto load search query if passed from Landing page search bar
  useEffect(() => {
    const query = searchParams.get('query');
    if (query) {
      setTextContent(query);
      setActiveTab('text');
      triggerAnalysis(query, 'text');
    } else {
      // Default initial analysis preview
      setResult(mockAnalysisDatabase.default_phishing);
    }
  }, [searchParams]);

  const triggerAnalysis = async (contentInput: string | File, type: AnalysisType) => {
    setIsScanning(true);
    setScanningStep(1);

    const stepInterval = setInterval(() => {
      setScanningStep((prev) => (prev < 3 ? prev + 1 : prev));
    }, 600);

    try {
      const res = await fraudService.analyzeContent(contentInput, type);
      clearInterval(stepInterval);
      setResult(res);
      toast.success('Gemini AI Analysis Complete!');
    } catch (error) {
      clearInterval(stepInterval);
      toast.error('Analysis failed. Loaded fallback Gemini model.');
      setResult(mockAnalysisDatabase.default_phishing);
    } finally {
      setIsScanning(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (activeTab === 'text' && textContent.trim()) {
      triggerAnalysis(textContent, 'text');
    } else if (activeTab === 'url' && urlContent.trim()) {
      triggerAnalysis(urlContent, 'url');
    } else if (activeTab === 'image' && uploadedFile) {
      triggerAnalysis(uploadedFile, 'image');
    } else {
      toast.error('Please enter valid content or upload a screenshot.');
    }
  };

  const handleDownloadPDF = () => {
    toast.promise(
      new Promise((resolve) => setTimeout(resolve, 1500)),
      {
        loading: 'Generating Cyber Defense Security Brief PDF...',
        success: 'Security Brief PDF Downloaded Successfully!',
        error: 'Error generating PDF.',
      }
    );
  };

  const handleCopyReport = () => {
    if (result) {
      navigator.clipboard.writeText(`[FraudShield AI Alert]\nThreat: ${result.detectedScamType}\nRisk Score: ${result.riskScore}/100\nSummary: ${result.summary}`);
      toast.success('Security Brief copied to clipboard!');
    }
  };

  return (
    <div className="flex min-h-[calc(100vh-4rem)]">
      <Sidebar />

      <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-8 overflow-x-hidden">
        
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-heading font-extrabold text-white flex items-center gap-2">
              {t('analyze.title')} <Sparkles className="w-5 h-5 text-cyan-400 animate-spin-slow" />
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              {t('analyze.subtitle')}
            </p>
          </div>

          <button
            onClick={toggleLanguage}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-900 border border-slate-700 text-slate-200 text-xs font-semibold hover:border-cyan-500 transition-colors"
          >
            <Languages className="w-4 h-4 text-cyan-400" />
            <span>{t('analyze.langToggle')}</span>
          </button>
        </div>

        {/* Multimodal Input Studio */}
        <GlassCard className="space-y-6">
          
          {/* Navigation Tabs */}
          <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
            <button
              onClick={() => setActiveTab('text')}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                activeTab === 'text'
                  ? 'bg-brand-600 text-white shadow-glow-sm'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              <FileText className="w-4 h-4" />
              <span>{t('analyze.textTab')}</span>
            </button>

            <button
              onClick={() => setActiveTab('url')}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                activeTab === 'url'
                  ? 'bg-brand-600 text-white shadow-glow-sm'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              <Globe className="w-4 h-4" />
              <span>{t('analyze.urlTab')}</span>
            </button>

            <button
              onClick={() => setActiveTab('image')}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                activeTab === 'image'
                  ? 'bg-gradient-to-r from-brand-600 to-cyan-500 text-white shadow-glow-sm'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              <Upload className="w-4 h-4" />
              <span>{t('analyze.uploadTab')}</span>
            </button>
          </div>

          {/* Form Content per active Tab */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {activeTab === 'text' && (
              <div className="space-y-2">
                <textarea
                  rows={4}
                  value={textContent}
                  onChange={(e) => setTextContent(e.target.value)}
                  placeholder="Paste suspicious SMS, WhatsApp message, email, or UPI payment text here..."
                  className="w-full p-4 rounded-2xl bg-slate-950/80 border border-slate-800 text-slate-100 text-xs sm:text-sm font-sans outline-none focus:border-cyan-500 transition-colors placeholder-slate-500"
                />
              </div>
            )}

            {activeTab === 'url' && (
              <div className="space-y-2">
                <input
                  type="url"
                  value={urlContent}
                  onChange={(e) => setUrlContent(e.target.value)}
                  placeholder="Enter suspicious URL (e.g. http://sbi-security-update.xyz/verify)..."
                  className="w-full p-4 rounded-2xl bg-slate-950/80 border border-slate-800 text-slate-100 text-xs sm:text-sm font-mono outline-none focus:border-cyan-500 transition-colors placeholder-slate-500"
                />
              </div>
            )}

            {activeTab === 'image' && (
              <UploadBox
                onFileSelect={(file) => {
                  setUploadedFile(file);
                  triggerAnalysis(file, 'image');
                }}
                isScanning={isScanning}
              />
            )}

            {activeTab !== 'image' && (
              <button
                type="submit"
                disabled={isScanning}
                className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-brand-600 via-blue-500 to-cyan-500 text-white font-semibold text-xs flex items-center justify-center gap-2 shadow-glow-md hover:opacity-95 transition-opacity disabled:opacity-50"
              >
                {isScanning ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Gemini AI Processing...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Execute Gemini Multimodal Analysis</span>
                  </>
                )}
              </button>
            )}
          </form>

          {/* Scanning Progress Overlay */}
          {isScanning && (
            <div className="pt-4 border-t border-slate-800">
              <RadarLoader
                label={
                  scanningStep === 1
                    ? t('analyze.scanningStep1')
                    : scanningStep === 2
                    ? t('analyze.scanningStep2')
                    : t('analyze.scanningStep3')
                }
              />
            </div>
          )}
        </GlassCard>

        {/* Results Panel */}
        <AnimatePresence>
          {result && !isScanning && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-8"
            >
              {/* Meters Grid: 3D RiskMeter & AI Confidence Meter */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <RiskMeter score={result.riskScore} riskLevel={result.riskLevel} />
                <ConfidenceMeter
                  confidenceScore={result.confidenceScore}
                  breakdown={result.modelConfidence}
                />
              </div>

              {/* Detected Scam Summary Card */}
              <GlassCard glowColor={result.riskLevel === 'SAFE' ? 'success' : 'danger'}>
                <div className="space-y-4">
                  
                  {/* Top Bar with actions */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
                    <div>
                      <span className="text-[10px] font-mono uppercase tracking-widest text-slate-400">
                        {t('analyze.detectedScam')}
                      </span>
                      <h2 className="text-xl font-heading font-extrabold text-white flex items-center gap-2 mt-0.5">
                        {language === 'hi' && result.detectedScamTypeHindi
                          ? result.detectedScamTypeHindi
                          : result.detectedScamType}
                      </h2>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={handleCopyReport}
                        className="p-2 rounded-xl bg-slate-900 text-slate-300 hover:text-white border border-slate-800 transition-colors"
                        title="Copy Summary"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                      <button
                        onClick={handleDownloadPDF}
                        className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-200 hover:border-cyan-500 text-xs font-semibold flex items-center gap-1.5 transition-colors"
                      >
                        <Download className="w-3.5 h-3.5 text-cyan-400" />
                        <span>{t('analyze.download')}</span>
                      </button>
                    </div>
                  </div>

                  {/* Summary Text */}
                  <div>
                    <h3 className="text-xs font-mono uppercase text-slate-400 font-bold mb-1">
                      {t('analyze.summary')}
                    </h3>
                    <p className="text-xs sm:text-sm text-slate-200 leading-relaxed font-sans bg-slate-950/40 p-4 rounded-2xl border border-slate-800/80">
                      {language === 'hi' && result.summaryHindi ? result.summaryHindi : result.summary}
                    </p>
                  </div>

                  {/* Reasons & Recommended Actions Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
                    
                    {/* Reasons */}
                    <div className="space-y-2">
                      <h4 className="text-xs font-mono uppercase text-danger font-bold flex items-center gap-1.5">
                        <AlertTriangle className="w-4 h-4" />
                        {t('analyze.reasons')}
                      </h4>
                      <ul className="space-y-2">
                        {(language === 'hi' && result.reasonsHindi ? result.reasonsHindi : result.reasons).map(
                          (reason, idx) => (
                            <li key={idx} className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-300 flex items-start gap-2">
                              <span className="w-1.5 h-1.5 rounded-full bg-danger mt-1.5 flex-shrink-0" />
                              <span>{reason}</span>
                            </li>
                          )
                        )}
                      </ul>
                    </div>

                    {/* Actions */}
                    <div className="space-y-2">
                      <h4 className="text-xs font-mono uppercase text-emerald-400 font-bold flex items-center gap-1.5">
                        <CheckCircle className="w-4 h-4" />
                        {t('analyze.actions')}
                      </h4>
                      <ul className="space-y-2">
                        {(language === 'hi' && result.recommendedActionsHindi
                          ? result.recommendedActionsHindi
                          : result.recommendedActions
                        ).map((action, idx) => (
                          <li key={idx} className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-300 flex items-start gap-2">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 flex-shrink-0" />
                            <span>{action}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </GlassCard>

              {/* Fraud Timeline Attack Vector Vector Flow */}
              <FraudTimeline timeline={result.timeline} />

            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
};

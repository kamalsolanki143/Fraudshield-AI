import React, { createContext, useContext, useState } from 'react';
import { Language } from '../types';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  toggleLanguage: () => void;
  t: (key: string) => string;
}

const translations: Record<Language, Record<string, string>> = {
  en: {
    // Nav
    'nav.home': 'Home',
    'nav.dashboard': 'Dashboard',
    'nav.analyze': 'Analyze AI',
    'nav.history': 'History',
    'nav.community': 'Community Alerts',
    'nav.pricing': 'Pricing',
    'nav.profile': 'Profile',
    'nav.settings': 'Settings',
    'nav.login': 'Sign In',
    'nav.getStarted': 'Protect Now',

    // Landing
    'hero.badge': 'Google Build with Gemini XPrize Entry',
    'hero.title': 'Real-Time Multimodal AI Fraud & Scam Defense System',
    'hero.subtitle': 'Instantly detect UPI phishing, fake job offers, malicious links, and document scams using Google Gemini Vision & Deep NLP reasoning.',
    'hero.cta': 'Scan Suspicious Text or Image',
    'hero.demo': 'View Live Demo',

    // Analyze Page
    'analyze.title': 'Multimodal AI Threat Analyzer',
    'analyze.subtitle': 'Upload a screenshot, paste SMS text, or enter suspicious URL to receive real-time Gemini AI risk analysis.',
    'analyze.uploadTab': 'Screenshot / File',
    'analyze.textTab': 'SMS / Message',
    'analyze.urlTab': 'URL / Link',
    'analyze.scanning': 'Multimodal AI Scanning in Progress...',
    'analyze.scanningStep1': 'OCR Extracting Text from Screenshot...',
    'analyze.scanningStep2': 'Gemini Vision Model Analyzing Visual Spoofing Patterns...',
    'analyze.scanningStep3': 'NLP Deep Reasoning & Domain Authority Check...',
    'analyze.riskScore': 'Fraud Risk Level',
    'analyze.confidence': 'AI Model Confidence',
    'analyze.detectedScam': 'Detected Threat Type',
    'analyze.summary': 'Executive Analysis Summary',
    'analyze.reasons': 'Key Fraud Indicators',
    'analyze.actions': 'Recommended Safeguards',
    'analyze.timeline': 'Scam Attack Vector Timeline',
    'analyze.download': 'Export PDF Security Brief',
    'analyze.langToggle': 'View Report in Hindi',

    // Dashboard
    'dash.title': 'Executive Threat Control Center',
    'dash.subtitle': 'Real-time overview of active cyber threats, fraud prevention metrics, and community protection posture.',
    'dash.score': 'Guardian Shield Score',
    'dash.totalScans': 'Total Threat Scans',
    'dash.threatsPrevented': 'Scams Neutralized',
    'dash.savedAmount': 'Estimated Assets Protected',

    // Footer
    'footer.status': 'Gemini XPrize Engine Operational',
    'footer.tagline': 'Powered by Google Gemini 1.5 Pro multimodal intelligence.',
  },
  hi: {
    // Nav
    'nav.home': 'होम',
    'nav.dashboard': 'डैशबोर्ड',
    'nav.analyze': 'एआई विश्लेषण',
    'nav.history': 'इतिहास',
    'nav.community': 'कम्युनिटी अलर्ट',
    'nav.pricing': 'कीमतें',
    'nav.profile': 'प्रोफ़ाइल',
    'nav.settings': 'सेटिंग्स',
    'nav.login': 'लॉग इन करें',
    'nav.getStarted': 'सुरक्षा शुरू करें',

    // Landing
    'hero.badge': 'गूगल बिल्ड विथ जेमिनी एक्सप्राइज',
    'hero.title': 'वास्तविक समय मल्टीमॉडल एआई धोखाधड़ी और स्कैम सुरक्षा',
    'hero.subtitle': 'गूगल जेमिनी विजन और डीप एनएलपी का उपयोग करके यूपीआई फ़िशिंग, फर्जी नौकरी ऑफ़र और संदिग्ध लिंक का तुरंत पता लगाएं।',
    'hero.cta': 'स्कैम मैसेज या स्क्रीनशॉट स्कैन करें',
    'hero.demo': 'लाइव डेमो देखें',

    // Analyze Page
    'analyze.title': 'मल्टीमॉडल एआई थ्रेट विश्लेषक',
    'analyze.subtitle': 'स्क्रीनशॉट अपलोड करें, एसएमएस टेक्स्ट पेस्ट करें या संदिग्ध यूआरएल दर्ज करें।',
    'analyze.uploadTab': 'स्क्रीनशॉट / फ़ाइल',
    'analyze.textTab': 'एसएमएस / मैसेज',
    'analyze.urlTab': 'यूआरएल / लिंक',
    'analyze.scanning': 'मल्टीमॉडल एआई स्कैनिंग प्रगति पर है...',
    'analyze.scanningStep1': 'स्क्रीनशॉट से टेक्स्ट निकाला जा रहा है...',
    'analyze.scanningStep2': 'जेमिनी विज़न मॉडल नकली विज़ुअल पैटर्न का विश्लेषण कर रहा है...',
    'analyze.scanningStep3': 'डीप रीज़निंग और डोमेन सुरक्षा जांच...',
    'analyze.riskScore': 'धोखाधड़ी जोखिम स्तर',
    'analyze.confidence': 'एआई मॉडल विश्वसनीयता',
    'analyze.detectedScam': 'पहचाना गया स्कैम प्रकार',
    'analyze.summary': 'विस्तृत विश्लेषण सारांश',
    'analyze.reasons': 'मुख्य धोखाधड़ी संकेतक',
    'analyze.actions': 'अनुशंसित सुरक्षा कदम',
    'analyze.timeline': 'स्कैम हमला टाइमलाइन',
    'analyze.download': 'सुरक्षा रिपोर्ट पीडीएफ डाउनलोड करें',
    'analyze.langToggle': 'अंग्रेजी में रिपोर्ट देखें',

    // Dashboard
    'dash.title': 'थ्रेट नियंत्रण केंद्र',
    'dash.subtitle': 'सक्रिय साइबर खतरों, धोखाधड़ी रोकथाम मेट्रिक्स और सुरक्षा स्थिति का वास्तविक समय अवलोकन।',
    'dash.score': 'गार्डियन शील्ड स्कोर',
    'dash.totalScans': 'कुल थ्रेट स्कैन',
    'dash.threatsPrevented': 'स्कैम बेअसर किए गए',
    'dash.savedAmount': 'अनुमानित सुरक्षित संपत्तियां',

    // Footer
    'footer.status': 'जेमिनी एक्सप्राइज इंजन सक्रिय है',
    'footer.tagline': 'गूगल जेमिनी 1.5 प्रो मल्टीमॉडल इंटेलिजेंस द्वारा संचालित।',
  },
};

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguage] = useState<Language>('en');

  const toggleLanguage = () => {
    setLanguage((prev) => (prev === 'en' ? 'hi' : 'en'));
  };

  const t = (key: string): string => {
    return translations[language][key] || translations['en'][key] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, toggleLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

export type RiskLevel = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'SAFE';

export type AnalysisType = 'text' | 'url' | 'image';

export interface FraudAnalysisResult {
  id: string;
  type: AnalysisType;
  inputContent: string;
  riskScore: number; // 0 to 100
  riskLevel: RiskLevel;
  confidenceScore: number; // 0 to 100
  summary: string;
  summaryHindi?: string;
  detectedScamType: string;
  detectedScamTypeHindi?: string;
  reasons: string[];
  reasonsHindi?: string[];
  recommendedActions: string[];
  recommendedActionsHindi?: string[];
  timeline: FraudTimelineItem[];
  modelConfidence: {
    geminiVisionScore: number;
    nlpUrgencyScore: number;
    domainReputationScore: number;
    ocrConfidence: number;
  };
  createdAt: string;
}

export interface FraudTimelineItem {
  step: number;
  phase: string;
  title: string;
  description: string;
  risk: 'HIGH' | 'MEDIUM' | 'LOW';
}

export interface CommunityAlert {
  id: string;
  author: string;
  authorAvatar?: string;
  title: string;
  category: 'UPI Scam' | 'Fake Job' | 'Bank Impersonation' | 'Crypto Fraud' | 'Phishing Link' | 'Other';
  description: string;
  riskLevel: RiskLevel;
  location: string;
  votes: number;
  verified: boolean;
  timestamp: string;
  tags: string[];
}

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  guardianScore: number; // e.g. 94/100
  guardianRank: string; // e.g. "Sentinel Prime"
  totalScans: number;
  threatsPrevented: number;
  savedAmountEst: string;
  plan: 'FREE' | 'PRO' | 'ENTERPRISE';
  joinedDate: string;
  apiKey?: string;
}

export interface PricingPlan {
  id: string;
  name: string;
  priceMonthly: number;
  priceAnnual: number;
  description: string;
  popular?: boolean;
  features: string[];
  cta: string;
}

export type Language = 'en' | 'hi';

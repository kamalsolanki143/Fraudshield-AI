import api from './api';
import { FraudAnalysisResult } from '../types';
import { mockAnalysisDatabase } from './fraudService';

const mockHistoryList: FraudAnalysisResult[] = [
  mockAnalysisDatabase.default_phishing,
  mockAnalysisDatabase.safe_sample,
  {
    id: 'an_gemini_8812',
    type: 'url',
    inputContent: 'http://free-iphone16-giveaway.club/claim',
    riskScore: 88,
    riskLevel: 'HIGH',
    confidenceScore: 95,
    summary: 'Survey reward scam harvesting personal details and credit card shipping fee.',
    detectedScamType: 'Reward Survey Fraud',
    reasons: ['Unregistered domain suffix', 'Suspicious free item lure'],
    recommendedActions: ['Do not pay shipping charges or enter credit card.'],
    timeline: [],
    modelConfidence: { geminiVisionScore: 92, nlpUrgencyScore: 88, domainReputationScore: 99, ocrConfidence: 90 },
    createdAt: new Date(Date.now() - 3600000 * 24).toISOString(),
  },
  {
    id: 'an_gemini_7741',
    type: 'image',
    inputContent: 'Screenshot_PartTimeJobOffer.png',
    riskScore: 78,
    riskLevel: 'HIGH',
    confidenceScore: 93,
    summary: 'Fake WhatsApp recruitment offer promising Rs 5000/day for minimal effort.',
    detectedScamType: 'Prepaid Task Fraud',
    reasons: ['Unrealistic salary promises', 'Requests upfront security deposit'],
    recommendedActions: ['Block WhatsApp business number.'],
    timeline: [],
    modelConfidence: { geminiVisionScore: 96, nlpUrgencyScore: 82, domainReputationScore: 50, ocrConfidence: 94 },
    createdAt: new Date(Date.now() - 3600000 * 48).toISOString(),
  },
];

export const historyService = {
  getHistory: async (): Promise<FraudAnalysisResult[]> => {
    try {
      const response = await api.get<FraudAnalysisResult[]>('/history');
      return response.data;
    } catch {
      return mockHistoryList;
    }
  },

  deleteHistoryItem: async (id: string): Promise<boolean> => {
    try {
      await api.delete(`/history/${id}`);
      return true;
    } catch {
      const idx = mockHistoryList.findIndex((item) => item.id === id);
      if (idx !== -1) mockHistoryList.splice(idx, 1);
      return true;
    }
  },
};

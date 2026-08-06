import api from './api';
import { CommunityAlert } from '../types';

export const initialCommunityAlerts: CommunityAlert[] = [
  {
    id: 'cm_991',
    author: 'Vikram Sharma',
    authorAvatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=150',
    title: 'New WhatsApp "Electricity Bill Disconnection" Scam in Delhi NCR',
    category: 'UPI Scam',
    description: 'Received SMS from fake BSES number claiming power will be cut at 9:30 PM today unless Rs. 15 is paid via APK download link.',
    riskLevel: 'CRITICAL',
    location: 'Delhi, India',
    votes: 412,
    verified: true,
    timestamp: '15 mins ago',
    tags: ['APK Virus', 'Power Bill', 'WhatsApp Fraud'],
  },
  {
    id: 'cm_992',
    author: 'Priya Patel',
    authorAvatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&q=80&w=150',
    title: 'Fake Work-from-Home Telegram Task Scam (Like YouTube Videos for Rs 500/day)',
    category: 'Fake Job',
    description: 'Initial payout of Rs 150 given to build trust, then demanded Rs 10,000 "crypto investment deposit" for VIP level.',
    riskLevel: 'HIGH',
    location: 'Mumbai, India',
    votes: 289,
    verified: true,
    timestamp: '2 hours ago',
    tags: ['Telegram Job', 'Crypto Deposit', 'Prepaid Task'],
  },
  {
    id: 'cm_993',
    author: 'CyberGuard Alpha',
    authorAvatar: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&q=80&w=150',
    title: 'Spoofed HDFC NetBanking Domain `hdfc-secure-verify.live` Active',
    category: 'Phishing Link',
    description: 'Identified malicious domain mimicking HDFC login. Steals PAN number and Debit Card PIN via fake KYC form.',
    riskLevel: 'CRITICAL',
    location: 'Bengaluru, India',
    votes: 654,
    verified: true,
    timestamp: '4 hours ago',
    tags: ['HDFC Phishing', 'KYC Fraud', 'Card PIN Harvest'],
  },
];

export const communityService = {
  getAlerts: async (): Promise<CommunityAlert[]> => {
    try {
      const response = await api.get<CommunityAlert[]>('/community/alerts');
      return response.data;
    } catch {
      return initialCommunityAlerts;
    }
  },

  voteAlert: async (alertId: string, delta: number): Promise<{ success: boolean; votes: number }> => {
    try {
      const response = await api.post(`/community/alerts/${alertId}/vote`, { delta });
      return response.data;
    } catch {
      const found = initialCommunityAlerts.find((a) => a.id === alertId);
      const newVotes = (found?.votes || 0) + delta;
      if (found) found.votes = newVotes;
      return { success: true, votes: newVotes };
    }
  },

  createAlert: async (alert: Omit<CommunityAlert, 'id' | 'votes' | 'verified' | 'timestamp'>): Promise<CommunityAlert> => {
    try {
      const response = await api.post<CommunityAlert>('/community/alerts', alert);
      return response.data;
    } catch {
      const newAlert: CommunityAlert = {
        ...alert,
        id: `cm_${Math.floor(1000 + Math.random() * 9000)}`,
        votes: 1,
        verified: false,
        timestamp: 'Just now',
      };
      initialCommunityAlerts.unshift(newAlert);
      return newAlert;
    }
  },
};

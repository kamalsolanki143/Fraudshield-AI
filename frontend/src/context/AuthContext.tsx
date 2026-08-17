import React, { createContext, useContext, useState, useEffect } from 'react';
import { UserProfile } from '../types';

interface AuthContextType {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isInitializing: boolean;
  token: string | null;
  requestOTP: (email: string) => Promise<void>;
  verifyOTP: (email: string, otp: string) => Promise<void>;
  logout: () => void;
  updateUser: (updatedFields: Partial<UserProfile>) => void;
}

const mockUserTemplate: UserProfile = {
  id: 'usr_gemini_9921',
  name: 'User',
  email: '',
  avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=200',
  guardianScore: 94,
  guardianRank: 'Sentinel Prime',
  totalScans: 142,
  threatsPrevented: 38,
  savedAmountEst: '$24,500',
  plan: 'PRO',
  joinedDate: new Date().toLocaleDateString('en-US', { month: 'short', year: 'numeric' }),
  apiKey: 'fs_live_99f82a174c82b01e',
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isInitializing, setIsInitializing] = useState(true);

  // Initialize session from local storage on mount
  useEffect(() => {
    const savedUser = localStorage.getItem('fraudshield_user');
    const savedToken = localStorage.getItem('fraudshield_token');

    if (savedUser && savedToken) {
      setUser(JSON.parse(savedUser));
      setToken(savedToken);
    }

    // Simulate network latency for initialization
    const timer = setTimeout(() => {
      setIsInitializing(false);
    }, 500);

    return () => clearTimeout(timer);
  }, []);

  const requestOTP = async (email: string): Promise<void> => {
    // Simulate API call to send OTP
    return new Promise((resolve) => setTimeout(resolve, 1500));
  };

  const verifyOTP = async (email: string, otp: string): Promise<void> => {
    // Simulate API call to verify OTP
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (otp === '123456') {
          const loggedInUser: UserProfile = {
            ...mockUserTemplate,
            email,
            name: email.split('@')[0].toUpperCase(),
          };
          const jwt = 'demo_jwt_token_gemini_xprize_' + Date.now();
          setUser(loggedInUser);
          setToken(jwt);
          localStorage.setItem('fraudshield_user', JSON.stringify(loggedInUser));
          localStorage.setItem('fraudshield_token', jwt);
          resolve();
        } else {
          reject(new Error('Invalid OTP code. Please use 123456 for demo.'));
        }
      }, 2000);
    });
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('fraudshield_token');
    localStorage.removeItem('fraudshield_user');
  };

  const updateUser = (updatedFields: Partial<UserProfile>) => {
    if (user) {
      const newUser = { ...user, ...updatedFields };
      setUser(newUser);
      localStorage.setItem('fraudshield_user', JSON.stringify(newUser));
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isInitializing,
        token,
        requestOTP,
        verifyOTP,
        logout,
        updateUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

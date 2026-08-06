import React, { createContext, useContext, useState, useEffect } from 'react';
import { UserProfile } from '../types';

interface AuthContextType {
  user: UserProfile | null;
  isAuthenticated: boolean;
  token: string | null;
  login: (email: string, token: string) => void;
  logout: () => void;
  updateUser: (updatedFields: Partial<UserProfile>) => void;
}

const mockUser: UserProfile = {
  id: 'usr_gemini_9921',
  name: 'Alex Vance',
  email: 'alex.vance@geminixprize.org',
  avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=200',
  guardianScore: 94,
  guardianRank: 'Sentinel Prime',
  totalScans: 142,
  threatsPrevented: 38,
  savedAmountEst: '$24,500',
  plan: 'PRO',
  joinedDate: 'Jan 2026',
  apiKey: 'fs_live_99f82a174c82b01e',
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(() => {
    const saved = localStorage.getItem('fraudshield_user');
    return saved ? JSON.parse(saved) : mockUser;
  });

  const [token, setToken] = useState<string | null>(() => {
    return localStorage.getItem('fraudshield_token') || 'demo_jwt_token_gemini_xprize';
  });

  useEffect(() => {
    if (user) {
      localStorage.setItem('fraudshield_user', JSON.stringify(user));
    } else {
      localStorage.removeItem('fraudshield_user');
    }
  }, [user]);

  const login = (email: string, jwtToken: string) => {
    const loggedInUser: UserProfile = {
      ...mockUser,
      email,
      name: email.split('@')[0].toUpperCase(),
    };
    setUser(loggedInUser);
    setToken(jwtToken);
    localStorage.setItem('fraudshield_token', jwtToken);
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('fraudshield_token');
    localStorage.removeItem('fraudshield_user');
  };

  const updateUser = (updatedFields: Partial<UserProfile>) => {
    if (user) {
      setUser((prev) => (prev ? { ...prev, ...updatedFields } : null));
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        token,
        login,
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

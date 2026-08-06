import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ShieldAlert, 
  Sparkles, 
  Languages, 
  User, 
  LogOut, 
  Settings, 
  Bell, 
  Menu, 
  X,
  ChevronDown
} from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';
import { useAuth } from '../context/AuthContext';

export const Navbar: React.FC = () => {
  const { language, toggleLanguage, t } = useLanguage();
  const { user, isAuthenticated, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);
  const [unreadNotifications] = useState(2);

  const isCurrent = (path: string) => location.pathname === path;

  return (
    <header className="sticky top-0 z-50 w-full backdrop-blur-xl bg-[#070B14]/80 border-b border-slate-800/60 shadow-glass">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Brand Logo & Gemini Badge */}
          <div className="flex items-center gap-4">
            <Link to="/" className="flex items-center gap-3 group">
              <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 via-blue-500 to-cyan-400 p-[1px] shadow-glow-sm transition-transform group-hover:scale-105">
                <div className="w-full h-full bg-[#070B14] rounded-[11px] flex items-center justify-center">
                  <ShieldAlert className="w-5 h-5 text-brand-500 group-hover:text-cyan-400 transition-colors" />
                </div>
              </div>
              <div className="flex flex-col">
                <span className="font-heading text-lg font-bold tracking-tight text-white flex items-center gap-1.5">
                  FraudShield <span className="text-brand-500 font-extrabold">AI</span>
                </span>
                <span className="text-[10px] font-mono tracking-widest text-cyan-400 uppercase -mt-1 flex items-center gap-1">
                  <Sparkles className="w-2.5 h-2.5 animate-pulse" /> Gemini XPrize
                </span>
              </div>
            </Link>
          </div>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center gap-1 bg-slate-900/50 p-1.5 rounded-full border border-slate-800">
            <Link
              to="/dashboard"
              className={`px-4 py-1.5 text-xs font-medium rounded-full transition-all ${
                isCurrent('/dashboard')
                  ? 'bg-brand-600 text-white shadow-glow-sm font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              {t('nav.dashboard')}
            </Link>
            <Link
              to="/analyze"
              className={`px-4 py-1.5 text-xs font-medium rounded-full transition-all flex items-center gap-1.5 ${
                isCurrent('/analyze')
                  ? 'bg-gradient-to-r from-brand-600 to-cyan-500 text-white shadow-glow-sm font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <Sparkles className="w-3 h-3 text-cyan-300 animate-spin-slow" />
              {t('nav.analyze')}
            </Link>
            <Link
              to="/history"
              className={`px-4 py-1.5 text-xs font-medium rounded-full transition-all ${
                isCurrent('/history')
                  ? 'bg-brand-600 text-white shadow-glow-sm font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              {t('nav.history')}
            </Link>
            <Link
              to="/community"
              className={`px-4 py-1.5 text-xs font-medium rounded-full transition-all ${
                isCurrent('/community')
                  ? 'bg-brand-600 text-white shadow-glow-sm font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              {t('nav.community')}
            </Link>
            <Link
              to="/pricing"
              className={`px-4 py-1.5 text-xs font-medium rounded-full transition-all ${
                isCurrent('/pricing')
                  ? 'bg-brand-600 text-white shadow-glow-sm font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              {t('nav.pricing')}
            </Link>
          </nav>

          {/* Right Action Menu: Language, Notifications, Auth */}
          <div className="flex items-center gap-3">
            
            {/* Language Switcher */}
            <button
              onClick={toggleLanguage}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-900/80 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-800 transition-colors"
              title="Toggle English / Hindi"
            >
              <Languages className="w-3.5 h-3.5 text-cyan-400" />
              <span>{language === 'en' ? 'EN' : 'हिन्दी'}</span>
            </button>

            {/* Notification Bell */}
            <button className="relative p-2 rounded-lg bg-slate-900/80 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-800 transition-colors">
              <Bell className="w-4 h-4" />
              {unreadNotifications > 0 && (
                <span className="absolute top-1 right-1 w-2 h-2 bg-danger rounded-full ring-2 ring-[#070B14] animate-pulse" />
              )}
            </button>

            {/* User Profile Dropdown or Sign In */}
            {isAuthenticated && user ? (
              <div className="relative">
                <button
                  onClick={() => setProfileDropdownOpen(!profileDropdownOpen)}
                  className="flex items-center gap-2 p-1 rounded-lg hover:bg-slate-800/60 transition-colors"
                >
                  <img
                    src={user.avatar}
                    alt={user.name}
                    className="w-8 h-8 rounded-lg object-cover ring-2 ring-brand-500/50"
                  />
                  <div className="hidden sm:flex flex-col text-left">
                    <span className="text-xs font-semibold text-white">{user.name}</span>
                    <span className="text-[10px] text-cyan-400 font-mono">{user.guardianRank}</span>
                  </div>
                  <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                </button>

                <AnimatePresence>
                  {profileDropdownOpen && (
                    <motion.div
                      initial={{ opacity: 0, y: 8, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: 8, scale: 0.95 }}
                      transition={{ duration: 0.15 }}
                      className="absolute right-0 mt-2 w-56 glass-panel rounded-2xl p-2 shadow-2xl z-50 border border-slate-700/60"
                    >
                      <div className="px-3 py-2 border-b border-slate-800">
                        <p className="text-xs font-semibold text-white">{user.name}</p>
                        <p className="text-[11px] text-slate-400 truncate">{user.email}</p>
                        <div className="mt-2 flex items-center justify-between bg-brand-950/40 p-1.5 rounded-lg border border-brand-800/40">
                          <span className="text-[10px] text-slate-300">Guardian Score</span>
                          <span className="text-xs font-bold text-cyan-400">{user.guardianScore}/100</span>
                        </div>
                      </div>

                      <div className="py-1">
                        <button
                          onClick={() => {
                            setProfileDropdownOpen(false);
                            navigate('/profile');
                          }}
                          className="w-full flex items-center gap-2.5 px-3 py-2 text-xs text-slate-300 hover:text-white hover:bg-slate-800/60 rounded-xl transition-colors text-left"
                        >
                          <User className="w-3.5 h-3.5 text-brand-400" />
                          <span>View Profile</span>
                        </button>

                        <button
                          onClick={() => {
                            setProfileDropdownOpen(false);
                            navigate('/settings');
                          }}
                          className="w-full flex items-center gap-2.5 px-3 py-2 text-xs text-slate-300 hover:text-white hover:bg-slate-800/60 rounded-xl transition-colors text-left"
                        >
                          <Settings className="w-3.5 h-3.5 text-brand-400" />
                          <span>System Settings</span>
                        </button>
                      </div>

                      <div className="pt-1 border-t border-slate-800">
                        <button
                          onClick={() => {
                            setProfileDropdownOpen(false);
                            logout();
                          }}
                          className="w-full flex items-center gap-2.5 px-3 py-2 text-xs text-danger hover:bg-danger/10 rounded-xl transition-colors text-left"
                        >
                          <LogOut className="w-3.5 h-3.5" />
                          <span>Sign Out</span>
                        </button>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ) : (
              <Link
                to="/login"
                className="px-4 py-2 text-xs font-semibold rounded-xl bg-gradient-to-r from-brand-600 to-cyan-500 text-white shadow-glow-sm hover:opacity-95 transition-opacity"
              >
                {t('nav.login')}
              </Link>
            )}

            {/* Mobile Hamburger Toggle */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-xl bg-slate-900 text-slate-300 hover:text-white border border-slate-800"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden glass-panel border-b border-slate-800 px-4 pt-2 pb-6 space-y-2"
          >
            <Link
              to="/dashboard"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-xl text-sm font-medium text-slate-300 hover:bg-slate-800"
            >
              {t('nav.dashboard')}
            </Link>
            <Link
              to="/analyze"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-xl text-sm font-medium text-cyan-400 hover:bg-slate-800"
            >
              {t('nav.analyze')}
            </Link>
            <Link
              to="/history"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-xl text-sm font-medium text-slate-300 hover:bg-slate-800"
            >
              {t('nav.history')}
            </Link>
            <Link
              to="/community"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-xl text-sm font-medium text-slate-300 hover:bg-slate-800"
            >
              {t('nav.community')}
            </Link>
            <Link
              to="/pricing"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-xl text-sm font-medium text-slate-300 hover:bg-slate-800"
            >
              {t('nav.pricing')}
            </Link>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
};

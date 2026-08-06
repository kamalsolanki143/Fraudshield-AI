import React from 'react';
import { motion } from 'framer-motion';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  glowColor?: 'blue' | 'danger' | 'success' | 'warning' | 'purple';
  hoverEffect?: boolean;
}

export const GlassCard: React.FC<GlassCardProps> = ({
  children,
  className = '',
  glowColor = 'blue',
  hoverEffect = true,
}) => {
  const getGlow = () => {
    switch (glowColor) {
      case 'danger': return 'hover:border-danger/40 hover:shadow-danger-glow';
      case 'success': return 'hover:border-success/40 hover:shadow-success-glow';
      case 'purple': return 'hover:border-purple-500/40 hover:shadow-glow-md';
      case 'warning': return 'hover:border-warning/40 hover:shadow-glow-md';
      case 'blue':
      default: return 'hover:border-brand-500/40 hover:shadow-glow-md';
    }
  };

  return (
    <motion.div
      whileHover={hoverEffect ? { y: -4, scale: 1.01 } : undefined}
      transition={{ duration: 0.2 }}
      className={`glass-panel rounded-3xl p-6 border border-slate-800/80 backdrop-blur-xl relative overflow-hidden transition-all ${
        hoverEffect ? getGlow() : ''
      } ${className}`}
    >
      {children}
    </motion.div>
  );
};

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
  hoverEffect = true,
}) => {
  return (
    <motion.div
      whileHover={hoverEffect ? { y: -2 } : undefined}
      transition={{ duration: 0.2 }}
      className={`bg-white rounded-[24px] p-6 border border-slate-100 shadow-soft-sm relative overflow-hidden transition-all ${
        hoverEffect ? 'hover:shadow-soft-md hover:border-slate-200' : ''
      } ${className}`}
    >
      {children}
    </motion.div>
  );
};

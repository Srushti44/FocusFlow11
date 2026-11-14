import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'lime' | 'blue' | 'black' | 'white' | 'coral' | 'amber';
  size?: 'sm' | 'md';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'lime',
  size = 'sm',
  className = '',
}) => {
  const variantStyles = {
    lime: 'bg-[#D7FF38] text-[#151515]',
    blue: 'bg-[#2455FF] text-white',
    black: 'bg-[#151515] text-[#D7FF38]',
    white: 'bg-white text-[#151515]',
    coral: 'bg-[#FF5E5B] text-white',
    amber: 'bg-[#FFA400] text-[#151515]',
  }[variant];

  const sizeStyles = {
    sm: 'text-[11px] px-2 py-0.5 border-[2px]',
    md: 'text-xs px-2.5 py-1 border-[2px]',
  }[size];

  return (
    <span
      className={`inline-flex items-center font-extrabold uppercase tracking-wider border-[#151515] shadow-[2px_2px_0px_#151515] ${variantStyles} ${sizeStyles} ${className}`}
    >
      {children}
    </span>
  );
};

import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'white' | 'warm' | 'lime' | 'blue' | 'dark';
  shadow?: 'none' | 'sm' | 'md' | 'lg';
  borderThick?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  variant = 'white',
  shadow = 'md',
  borderThick = false,
  className = '',
  ...props
}) => {
  const bgStyles = {
    white: 'bg-white text-[#151515]',
    warm: 'bg-[#F4F0E8] text-[#151515]',
    lime: 'bg-[#D7FF38] text-[#151515]',
    blue: 'bg-[#2455FF] text-white',
    dark: 'bg-[#151515] text-[#F4F0E8]',
  }[variant];

  const shadowStyles = {
    none: '',
    sm: 'shadow-[2px_2px_0px_#151515]',
    md: 'shadow-[4px_4px_0px_#151515]',
    lg: 'shadow-[6px_6px_0px_#151515]',
  }[shadow];

  const borderStyles = borderThick ? 'border-4 border-[#151515]' : 'border-2 sm:border-[3px] border-[#151515]';

  return (
    <div className={`p-4 sm:p-6 ${bgStyles} ${borderStyles} ${shadowStyles} ${className}`} {...props}>
      {children}
    </div>
  );
};

import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'lime' | 'secondary' | 'ghost' | 'danger' | 'amber';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  icon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'secondary',
  size = 'md',
  fullWidth = false,
  icon,
  className = '',
  disabled,
  ...props
}) => {
  const baseStyles = 'inline-flex items-center justify-center font-extrabold uppercase tracking-wide transition-all select-none border-2 sm:border-[3px] border-[#151515] focus-visible:outline-none';

  const sizeStyles = {
    sm: 'px-3 py-1.5 text-xs gap-1.5',
    md: 'px-4 py-2.5 text-sm gap-2',
    lg: 'px-6 py-3.5 text-base gap-2.5',
  }[size];

  const variantStyles = {
    primary: 'bg-[#2455FF] text-white hover:bg-[#1b43d4] shadow-[3px_3px_0px_#151515] hover:shadow-[2px_2px_0px_#151515] hover:translate-x-[1px] hover:translate-y-[1px]',
    lime: 'bg-[#D7FF38] text-[#151515] hover:bg-[#cbf528] shadow-[3px_3px_0px_#151515] hover:shadow-[2px_2px_0px_#151515] hover:translate-x-[1px] hover:translate-y-[1px]',
    secondary: 'bg-[#FFFFFF] text-[#151515] hover:bg-[#F4F0E8] shadow-[3px_3px_0px_#151515] hover:shadow-[2px_2px_0px_#151515] hover:translate-x-[1px] hover:translate-y-[1px]',
    ghost: 'bg-transparent text-[#151515] dark:text-white hover:bg-[#151515]/10 shadow-[2px_2px_0px_#151515] hover:shadow-[1px_1px_0px_#151515]',
    danger: 'bg-[#FF5E5B] text-white hover:bg-[#e64e4b] shadow-[3px_3px_0px_#151515] hover:shadow-[2px_2px_0px_#151515] hover:translate-x-[1px] hover:translate-y-[1px]',
    amber: 'bg-[#FFA400] text-[#151515] hover:bg-[#e09100] shadow-[3px_3px_0px_#151515] hover:shadow-[2px_2px_0px_#151515] hover:translate-x-[1px] hover:translate-y-[1px]',
  }[variant];

  const disabledStyles = disabled
    ? 'opacity-40 cursor-not-allowed shadow-none translate-x-0 translate-y-0 hover:translate-x-0 hover:translate-y-0'
    : 'cursor-pointer active:translate-x-[2px] active:translate-y-[2px] active:shadow-[1px_1px_0px_#151515]';

  return (
    <button
      disabled={disabled}
      className={`${baseStyles} ${sizeStyles} ${variantStyles} ${disabledStyles} ${fullWidth ? 'w-full' : ''} ${className}`}
      {...props}
    >
      {icon && <span className="flex-shrink-0">{icon}</span>}
      <span>{children}</span>
    </button>
  );
};

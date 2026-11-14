import React, { useEffect } from 'react';
import { X } from 'lucide-react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl';
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  maxWidth = 'md',
}) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const maxWidthStyles = {
    sm: 'max-w-md',
    md: 'max-w-xl',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
  }[maxWidth];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#151515]/60 backdrop-blur-sm animate-in fade-in duration-100">
      <div
        className={`w-full ${maxWidthStyles} bg-[#F4F0E8] border-4 border-[#151515] shadow-[8px_8px_0px_#151515] overflow-hidden`}
        role="dialog"
        aria-modal="true"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 bg-[#D7FF38] border-b-4 border-[#151515]">
          <h3 className="font-extrabold text-base sm:text-lg uppercase tracking-tight text-[#151515]">
            {title}
          </h3>
          <button
            onClick={onClose}
            className="p-1 border-2 border-[#151515] bg-white hover:bg-[#FF5E5B] hover:text-white transition-colors shadow-[2px_2px_0px_#151515] active:translate-x-[1px] active:translate-y-[1px]"
            aria-label="Close modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-5 sm:p-6 max-h-[80vh] overflow-y-auto">
          {children}
        </div>
      </div>
    </div>
  );
};

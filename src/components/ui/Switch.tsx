import React from 'react';

interface SwitchProps {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  description?: string;
  badge?: string;
}

export const Switch: React.FC<SwitchProps> = ({
  label,
  checked,
  onChange,
  description,
  badge,
}) => {
  return (
    <div
      onClick={() => onChange(!checked)}
      className="flex items-center justify-between p-3.5 bg-white border-2 sm:border-[3px] border-[#151515] shadow-[3px_3px_0px_#151515] cursor-pointer hover:bg-[#FAF8F5] transition-all select-none"
    >
      <div className="pr-4">
        <div className="flex items-center gap-2">
          <span className="font-extrabold uppercase text-sm">{label}</span>
          {badge && (
            <span className="bg-[#D7FF38] border border-[#151515] px-1.5 py-0.5 text-[10px] font-bold">
              {badge}
            </span>
          )}
        </div>
        {description && <p className="text-xs text-gray-600 font-medium mt-0.5">{description}</p>}
      </div>

      <div
        className={`w-12 h-6 border-2 border-[#151515] p-0.5 transition-colors relative flex items-center ${
          checked ? 'bg-[#D7FF38]' : 'bg-[#E6E1D5]'
        }`}
      >
        <div
          className={`w-4 h-4 bg-[#151515] transition-transform ${
            checked ? 'translate-x-6' : 'translate-x-0'
          }`}
        />
      </div>
    </div>
  );
};

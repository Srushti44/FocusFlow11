import React from 'react';

interface SliderProps {
  label: string;
  value: number;
  min: number;
  max: number;
  step?: number;
  unit?: string;
  onChange: (value: number) => void;
  description?: string;
}

export const Slider: React.FC<SliderProps> = ({
  label,
  value,
  min,
  max,
  step = 1,
  unit = '',
  onChange,
  description,
}) => {
  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between text-xs sm:text-sm font-extrabold uppercase tracking-wide">
        <span>{label}</span>
        <span className="bg-[#D7FF38] border-2 border-[#151515] px-2 py-0.5 text-xs font-mono shadow-[2px_2px_0px_#151515]">
          {value}{unit}
        </span>
      </div>
      {description && <p className="text-xs text-gray-600 font-medium">{description}</p>}
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full h-3 bg-[#E6E1D5] appearance-none cursor-pointer border-2 border-[#151515] accent-[#2455FF] shadow-[2px_2px_0px_#151515]"
      />
      <div className="flex justify-between text-[10px] font-mono text-gray-500 font-bold">
        <span>{min}{unit}</span>
        <span>{max}{unit}</span>
      </div>
    </div>
  );
};

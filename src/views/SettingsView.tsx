import React, { useState, useEffect } from 'react';
import { UserSettings } from '../types';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Slider } from '../components/ui/Slider';
import { Switch } from '../components/ui/Switch';
import { api } from '../services/api';
import {
  Type,
  Layout,
  Volume2,
  Sparkles,
  Server,
  RotateCcw,
  Check,
  ShieldCheck,
  Cpu
} from 'lucide-react';

interface SettingsViewProps {
  settings: UserSettings;
  onUpdateSettings: (newSettings: Partial<UserSettings>) => void;
  onResetSettings: () => void;
}

export const SettingsView: React.FC<SettingsViewProps> = ({
  settings,
  onUpdateSettings,
  onResetSettings,
}) => {
  const [backendHealth, setBackendHealth] = useState<{ status: string; ai_provider: string }>({
    status: 'checking...',
    ai_provider: 'loading'
  });
  const [saveBanner, setSaveBanner] = useState(false);

  useEffect(() => {
    api.getHealth().then(setBackendHealth);
  }, []);

  const handleUpdate = (partial: Partial<UserSettings>) => {
    onUpdateSettings(partial);
    setSaveBanner(true);
    setTimeout(() => setSaveBanner(false), 2000);
  };

  const fontOptions: Array<{ id: UserSettings['font_family']; label: string; desc: string }> = [
    { id: 'lexend', label: 'Lexend', desc: 'Designed specifically to reduce visual stress and improve reading speed.' },
    { id: 'atkinson', label: 'Atkinson Hyperlegible', desc: 'Designed by the Braille Institute for maximum character distinction.' },
    { id: 'dyslexic', label: 'OpenDyslexic', desc: 'Weighted bottom characters to prevent letter rotation and inversion.' },
    { id: 'sans', label: 'System Sans', desc: 'Clean, modern sans-serif (Space Grotesk / Inter).' },
    { id: 'serif', label: 'Editorial Serif', desc: 'High-legibility traditional Georgia / Charter serif.' },
    { id: 'mono', label: 'Monospace', desc: 'Fixed-width characters for unambiguous technical reading.' },
  ];

  return (
    <div className="w-full min-h-screen pb-16 px-4 sm:px-6">
      <div className="max-w-4xl mx-auto pt-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Badge variant="lime">ACCESSIBILITY PREFERENCES</Badge>
              {saveBanner && (
                <span className="text-xs font-mono font-extrabold bg-[#D7FF38] border border-[#151515] px-2 py-0.5 animate-in fade-in">
                  SAVED AUTOMATICALLY ✓
                </span>
              )}
            </div>
            <h1 className="text-2xl sm:text-4xl font-black uppercase text-[#151515] dark:text-white tracking-tight">
              Settings & Ergonomics
            </h1>
          </div>

          <Button
            onClick={onResetSettings}
            variant="ghost"
            size="sm"
            icon={<RotateCcw className="w-4 h-4" />}
          >
            RESET DEFAULTS
          </Button>
        </div>

        <div className="space-y-6">
          {/* 1. Typography System */}
          <div className="bg-white dark:bg-[#1E1E1E] border-3 sm:border-4 border-[#151515] dark:border-white shadow-[6px_6px_0px_#151515] p-5 sm:p-7">
            <div className="flex items-center gap-2 pb-3 mb-5 border-b-2 border-[#151515]">
              <Type className="w-5 h-5 text-[#2455FF]" />
              <h2 className="font-black text-base sm:text-lg uppercase text-[#151515] dark:text-white">
                Cognitive Typography
              </h2>
            </div>

            <div className="space-y-6">
              {/* Typeface Selection */}
              <div>
                <label className="block text-xs font-extrabold uppercase mb-2 text-[#151515] dark:text-[#F4F0E8]">
                  Primary Reading Typeface
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                  {fontOptions.map(f => (
                    <button
                      key={f.id}
                      onClick={() => handleUpdate({ font_family: f.id })}
                      className={`p-3.5 border-2 sm:border-3 border-[#151515] text-left transition-all ${
                        settings.font_family === f.id
                          ? 'bg-[#2455FF] text-white shadow-[3px_3px_0px_#151515] translate-x-[1px] translate-y-[1px]'
                          : 'bg-white hover:bg-[#F4F0E8] text-[#151515]'
                      }`}
                    >
                      <span className="font-extrabold text-sm block mb-1 uppercase">{f.label}</span>
                      <p className={`text-[11px] leading-tight ${settings.font_family === f.id ? 'text-white/80' : 'text-gray-600'}`}>
                        {f.desc}
                      </p>
                    </button>
                  ))}
                </div>
              </div>

              {/* Sliders */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5 pt-3 border-t-2 border-dashed border-gray-300 dark:border-gray-700">
                <Slider
                  label="Text Size"
                  value={settings.font_size}
                  min={14}
                  max={28}
                  unit="px"
                  onChange={(v) => handleUpdate({ font_size: v })}
                  description="Adjust baseline font size for comfortable reading without squinting."
                />

                <Slider
                  label="Line Spacing (Leading)"
                  value={settings.line_spacing}
                  min={1.4}
                  max={2.4}
                  step={0.1}
                  unit="x"
                  onChange={(v) => handleUpdate({ line_spacing: v })}
                  description="Increases vertical breathing room between sentences to stop line-skipping."
                />

                <Slider
                  label="Letter Spacing (Tracking)"
                  value={settings.letter_spacing}
                  min={0}
                  max={3}
                  step={0.2}
                  unit="px"
                  onChange={(v) => handleUpdate({ letter_spacing: v })}
                  description="Adds horizontal kerning space between characters to aid dyslexia parsing."
                />

                <Slider
                  label="Reading Column Width"
                  value={settings.content_width}
                  min={500}
                  max={900}
                  step={20}
                  unit="px"
                  onChange={(v) => handleUpdate({ content_width: v })}
                  description="Restricts paragraph width to 50-75 characters per line."
                />
              </div>
            </div>
          </div>

          {/* 2. Cognitive Reading Modes */}
          <div className="bg-white dark:bg-[#1E1E1E] border-3 sm:border-4 border-[#151515] dark:border-white shadow-[6px_6px_0px_#151515] p-5 sm:p-7">
            <div className="flex items-center gap-2 pb-3 mb-5 border-b-2 border-[#151515]">
              <Layout className="w-5 h-5 text-[#2455FF]" />
              <h2 className="font-black text-base sm:text-lg uppercase text-[#151515] dark:text-white">
                Reading Modes & Guides
              </h2>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Switch
                label="Chunk Mode by Default"
                badge="RECOMMENDED"
                checked={settings.chunk_mode}
                onChange={(checked) => handleUpdate({ chunk_mode: checked })}
                description="Displays one isolated 60-90 word atomic chunk per screen to eliminate extraneous load."
              />

              <Switch
                label="Bionic Reading"
                badge="SACCADIC"
                checked={settings.bionic_reading}
                onChange={(checked) => handleUpdate({ bionic_reading: checked })}
                description="Bolds the initial letters of words to guide natural saccadic eye jumps."
              />

              <Switch
                label="Focus Reading Ruler"
                checked={settings.focus_ruler}
                onChange={(checked) => handleUpdate({ focus_ruler: checked })}
                description="Displays an assistive horizontal reading mask to track lines."
              />

              <Switch
                label="Reduced Motion"
                checked={settings.reduced_motion}
                onChange={(checked) => handleUpdate({ reduced_motion: checked })}
                description="Disables transitions and confetti animations for vestibular accessibility."
              />
            </div>
          </div>

          {/* 3. Audio & Palette */}
          <div className="bg-white dark:bg-[#1E1E1E] border-3 sm:border-4 border-[#151515] dark:border-white shadow-[6px_6px_0px_#151515] p-5 sm:p-7">
            <div className="flex items-center gap-2 pb-3 mb-5 border-b-2 border-[#151515]">
              <Volume2 className="w-5 h-5 text-[#2455FF]" />
              <h2 className="font-black text-base sm:text-lg uppercase text-[#151515] dark:text-white">
                Theme & Narration
              </h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Theme Palette */}
              <div>
                <label className="block text-xs font-extrabold uppercase mb-2 text-[#151515] dark:text-[#F4F0E8]">
                  Reading Color Palette
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { id: 'warm', label: 'Warm Cream (#F4F0E8)', bg: 'bg-[#F4F0E8]', text: 'text-black' },
                    { id: 'white', label: 'Crisp White (#FFFFFF)', bg: 'bg-white', text: 'text-black' },
                    { id: 'dark', label: 'Ink Dark (#121212)', bg: 'bg-[#121212]', text: 'text-white' },
                    { id: 'slate', label: 'Soft Slate (#E5E7EB)', bg: 'bg-[#E5E7EB]', text: 'text-black' },
                  ].map(t => (
                    <button
                      key={t.id}
                      onClick={() => handleUpdate({ theme: t.id as any })}
                      className={`p-3 border-2 border-[#151515] font-extrabold text-xs text-left transition-all ${t.bg} ${t.text} ${
                        settings.theme === t.id ? 'ring-3 ring-[#2455FF] shadow-[3px_3px_0px_#151515]' : ''
                      }`}
                    >
                      {t.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* TTS Pace */}
              <div>
                <Slider
                  label="Text-to-Speech Speed"
                  value={settings.tts_speed}
                  min={0.75}
                  max={1.5}
                  step={0.25}
                  unit="x"
                  onChange={(v) => handleUpdate({ tts_speed: v })}
                  description="Adjust audio reading narration pace for synchronized listening."
                />
              </div>
            </div>
          </div>

          {/* 4. Backend & AI Integration Status */}
          <div className="bg-[#FAF8F5] dark:bg-[#1E1E1E] border-3 sm:border-4 border-[#151515] dark:border-white shadow-[6px_6px_0px_#151515] p-5 sm:p-7">
            <div className="flex items-center gap-2 pb-3 mb-4 border-b-2 border-[#151515]">
              <Server className="w-5 h-5 text-[#2455FF]" />
              <h2 className="font-black text-base sm:text-lg uppercase text-[#151515] dark:text-white">
                Backend & AI Engine Status
              </h2>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs font-mono">
              <div className="p-3 bg-white dark:bg-[#252525] border-2 border-[#151515]">
                <span className="font-extrabold text-gray-500 uppercase block mb-1">FastAPI Backend</span>
                <span className="font-bold text-[#151515] dark:text-white">
                  http://localhost:8000 ({backendHealth.status})
                </span>
              </div>

              <div className="p-3 bg-white dark:bg-[#252525] border-2 border-[#151515]">
                <span className="font-extrabold text-gray-500 uppercase block mb-1">Active AI Engine</span>
                <span className="font-bold text-[#2455FF] dark:text-[#D7FF38] uppercase">
                  {backendHealth.ai_provider}
                </span>
              </div>
            </div>

            <p className="text-[11px] font-medium text-gray-600 dark:text-gray-400 mt-3">
              To use live Gemini or OpenAI APIs, set <code className="bg-[#E6E1D5] dark:bg-black px-1 py-0.5 font-mono">GEMINI_API_KEY</code> or <code className="bg-[#E6E1D5] dark:bg-black px-1 py-0.5 font-mono">OPENAI_API_KEY</code> in your backend <code className="bg-[#E6E1D5] dark:bg-black px-1 py-0.5 font-mono">.env</code> file. FocusFlow automatically falls back to its deterministic cognitive NLP engine if no key is provided.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

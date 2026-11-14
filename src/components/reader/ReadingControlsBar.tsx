import React, { useState, useEffect } from 'react';
import { UserSettings } from '../../types';
import { Button } from '../ui/Button';
import {
  Type,
  Maximize2,
  Minimize2,
  BookOpen,
  Volume2,
  VolumeX,
  Play,
  Pause,
  Sliders,
  Sparkles,
  Eye,
  EyeOff,
  Sun,
  Moon,
  Coffee,
  Highlighter,
  Crosshair,
  Layers
} from 'lucide-react';
import { speechService } from '../../services/speech';

interface ReadingControlsBarProps {
  settings: UserSettings;
  onUpdateSettings: (newSettings: Partial<UserSettings>) => void;
  onOpenLearningTools: () => void;
  currentChunkText?: string;
}

export const ReadingControlsBar: React.FC<ReadingControlsBarProps> = ({
  settings,
  onUpdateSettings,
  onOpenLearningTools,
  currentChunkText = ''
}) => {
  const [audioState, setAudioState] = useState(speechService.getState());
  const [showTypographyDrawer, setShowTypographyDrawer] = useState(false);

  useEffect(() => {
    return speechService.subscribe(setAudioState);
  }, []);

  const handleToggleAudio = () => {
    if (audioState.isSpeaking) {
      speechService.stop();
    } else {
      if (currentChunkText) {
        speechService.speak(currentChunkText, settings.tts_speed);
      }
    }
  };

  const fontOptions: Array<{ id: UserSettings['font_family']; label: string }> = [
    { id: 'lexend', label: 'Lexend' },
    { id: 'atkinson', label: 'Atkinson' },
    { id: 'dyslexic', label: 'OpenDyslexic' },
    { id: 'sans', label: 'Sans-Serif' },
    { id: 'serif', label: 'Serif' },
    { id: 'mono', label: 'Monospace' },
  ];

  return (
    <div className="w-full max-w-4xl mx-auto my-3">
      {/* Top Floating Control Bar */}
      <div className="bg-[#FFFFFF] dark:bg-[#1A1A1A] border-3 sm:border-4 border-[#151515] dark:border-white shadow-[4px_4px_0px_#151515] p-2 sm:p-2.5 flex flex-wrap items-center justify-between gap-2 select-none">
        {/* Left: Reading Mode Switcher */}
        <div className="flex items-center gap-1">
          <button
            onClick={() => onUpdateSettings({ chunk_mode: true })}
            className={`px-2.5 py-1.5 text-xs font-extrabold uppercase border-2 border-[#151515] transition-all flex items-center gap-1.5 ${
              settings.chunk_mode
                ? 'bg-[#2455FF] text-white shadow-[2px_2px_0px_#151515]'
                : 'bg-white text-[#151515] hover:bg-[#F4F0E8]'
            }`}
          >
            <Minimize2 className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Chunk Mode</span>
          </button>

          <button
            onClick={() => onUpdateSettings({ chunk_mode: false })}
            className={`px-2.5 py-1.5 text-xs font-extrabold uppercase border-2 border-[#151515] transition-all flex items-center gap-1.5 ${
              !settings.chunk_mode
                ? 'bg-[#2455FF] text-white shadow-[2px_2px_0px_#151515]'
                : 'bg-white text-[#151515] hover:bg-[#F4F0E8]'
            }`}
          >
            <Maximize2 className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Full Reader</span>
          </button>

          {/* Zen Focus Mode Button */}
          <button
            onClick={() => onUpdateSettings({ focus_mode: !settings.focus_mode })}
            className={`px-2.5 py-1.5 text-xs font-extrabold uppercase border-2 border-[#151515] transition-all flex items-center gap-1 ${
              settings.focus_mode
                ? 'bg-[#FF5E5B] text-white shadow-[2px_2px_0px_#151515]'
                : 'bg-[#D7FF38] text-[#151515] hover:bg-[#cbf528] shadow-[2px_2px_0px_#151515]'
            }`}
            title="Focus Mode: hides all controls, headers, and clutter for pure reading"
          >
            <Crosshair className="w-3.5 h-3.5" />
            <span>ZEN</span>
          </button>
        </div>

        {/* Center: Cognitive Helpers (Bionic, Highlights, Ruler, Typography) */}
        <div className="flex items-center gap-1">
          <button
            onClick={() => onUpdateSettings({ bionic_reading: !settings.bionic_reading })}
            className={`px-2 py-1.5 text-xs font-extrabold uppercase border-2 border-[#151515] transition-all flex items-center gap-1 ${
              settings.bionic_reading
                ? 'bg-[#D7FF38] text-[#151515] shadow-[2px_2px_0px_#151515]'
                : 'bg-white text-[#151515] hover:bg-[#FAF8F5]'
            }`}
            title="Bold initial syllables to guide saccadic eye movement"
          >
            <span className="font-mono"><strong>Bio</strong>nic</span>
          </button>

          <button
            onClick={() => onUpdateSettings({ enable_semantic_highlights: !settings.enable_semantic_highlights })}
            className={`px-2 py-1.5 text-xs font-extrabold uppercase border-2 border-[#151515] transition-all flex items-center gap-1 ${
              settings.enable_semantic_highlights
                ? 'bg-[#2455FF] text-white shadow-[2px_2px_0px_#151515]'
                : 'bg-white text-gray-500 hover:bg-[#FAF8F5]'
            }`}
            title="Toggle semantic highlights for concepts, definitions, and evidence"
          >
            <Highlighter className="w-3.5 h-3.5" />
            <span className="hidden md:inline">HL</span>
          </button>

          <button
            onClick={() => onUpdateSettings({ focus_ruler: !settings.focus_ruler })}
            className={`px-2 py-1.5 text-xs font-extrabold uppercase border-2 border-[#151515] transition-all flex items-center gap-1 ${
              settings.focus_ruler
                ? 'bg-[#D7FF38] text-[#151515] shadow-[2px_2px_0px_#151515]'
                : 'bg-white text-[#151515] hover:bg-[#FAF8F5]'
            }`}
            title="Horizontal focus ruler tracks your reading line"
          >
            <Eye className="w-3.5 h-3.5" />
            <span className="hidden md:inline">Ruler</span>
          </button>

          <button
            onClick={() => setShowTypographyDrawer(!showTypographyDrawer)}
            className={`px-2.5 py-1.5 text-xs font-extrabold uppercase border-2 border-[#151515] transition-all flex items-center gap-1 ${
              showTypographyDrawer
                ? 'bg-[#151515] text-[#D7FF38]'
                : 'bg-white text-[#151515] hover:bg-[#F4F0E8]'
            }`}
            title="Adjust typography, chunk size, and spacing"
          >
            <Type className="w-3.5 h-3.5" />
            <span>{settings.font_size}px</span>
          </button>

          {/* Audio TTS Button */}
          <button
            onClick={handleToggleAudio}
            className={`px-2 py-1.5 text-xs font-extrabold uppercase border-2 border-[#151515] transition-all flex items-center gap-1 ${
              audioState.isSpeaking
                ? 'bg-[#FF5E5B] text-white shadow-[2px_2px_0px_#151515]'
                : 'bg-white text-[#151515] hover:bg-[#FAF8F5]'
            }`}
            title="Read aloud using Text-to-Speech"
          >
            {audioState.isSpeaking ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
            <span className="hidden sm:inline">{audioState.isSpeaking ? 'Stop' : 'Audio'}</span>
          </button>
        </div>

        {/* Right: AI Retention Tools & Theme */}
        <div className="flex items-center gap-1">
          <Button
            onClick={onOpenLearningTools}
            variant="lime"
            size="sm"
            icon={<Sparkles className="w-3.5 h-3.5 text-[#151515]" />}
          >
            AI TOOLS
          </Button>

          {/* Theme Quick Switcher */}
          <button
            onClick={() => {
              const themes: UserSettings['theme'][] = ['warm', 'white', 'dark'];
              const nextIndex = (themes.indexOf(settings.theme) + 1) % themes.length;
              onUpdateSettings({ theme: themes[nextIndex] });
            }}
            className="p-1.5 border-2 border-[#151515] bg-white hover:bg-[#FAF8F5] shadow-[2px_2px_0px_#151515]"
            title={`Current theme: ${settings.theme}. Click to switch.`}
          >
            {settings.theme === 'dark' ? (
              <Moon className="w-3.5 h-3.5 text-[#2455FF]" />
            ) : settings.theme === 'white' ? (
              <Sun className="w-3.5 h-3.5 text-[#FFA400]" />
            ) : (
              <Coffee className="w-3.5 h-3.5 text-[#151515]" />
            )}
          </button>
        </div>
      </div>

      {/* Expandable Typography & Chunk Sizing Drawer */}
      {showTypographyDrawer && (
        <div className="mt-2 bg-[#F4F0E8] dark:bg-[#222222] border-3 border-[#151515] dark:border-white shadow-[4px_4px_0px_#151515] p-4 animate-in slide-in-from-top-2">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Font Family */}
            <div>
              <label className="block text-xs font-extrabold uppercase mb-1.5 text-[#151515] dark:text-[#F4F0E8]">
                Accessible Typeface
              </label>
              <div className="grid grid-cols-2 gap-1.5">
                {fontOptions.map(f => (
                  <button
                    key={f.id}
                    onClick={() => onUpdateSettings({ font_family: f.id })}
                    className={`px-2 py-1 text-xs font-bold border-2 border-[#151515] text-left transition-all ${
                      settings.font_family === f.id
                        ? 'bg-[#2455FF] text-white shadow-[2px_2px_0px_#151515]'
                        : 'bg-white text-[#151515] hover:bg-[#D7FF38]'
                    }`}
                  >
                    {f.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Font Size & Chunk Size Config */}
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-xs font-extrabold uppercase mb-1">
                  <span>Font Size</span>
                  <span className="font-mono">{settings.font_size}px</span>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => onUpdateSettings({ font_size: Math.max(14, settings.font_size - 1) })}
                    className="w-8 h-8 font-extrabold text-sm border-2 border-[#151515] bg-white hover:bg-[#D7FF38]"
                  >
                    -
                  </button>
                  <input
                    type="range"
                    min={14}
                    max={28}
                    value={settings.font_size}
                    onChange={(e) => onUpdateSettings({ font_size: parseInt(e.target.value) })}
                    className="w-full accent-[#2455FF]"
                  />
                  <button
                    onClick={() => onUpdateSettings({ font_size: Math.min(28, settings.font_size + 1) })}
                    className="w-8 h-8 font-extrabold text-sm border-2 border-[#151515] bg-white hover:bg-[#D7FF38]"
                  >
                    +
                  </button>
                </div>
              </div>

              {/* Configurable Chunk Size Target (Part B) */}
              <div>
                <div className="flex justify-between text-xs font-extrabold uppercase mb-1">
                  <span>Chunk Size</span>
                  <span className="font-mono">{settings.chunk_size_words || 80} words</span>
                </div>
                <div className="grid grid-cols-3 gap-1">
                  {[
                    { label: 'Compact', words: 55 },
                    { label: 'Balanced', words: 80 },
                    { label: 'Deep', words: 120 }
                  ].map(cs => (
                    <button
                      key={cs.words}
                      onClick={() => onUpdateSettings({ chunk_size_words: cs.words })}
                      className={`py-1 text-[11px] font-extrabold uppercase border-2 border-[#151515] ${
                        (settings.chunk_size_words || 80) === cs.words
                          ? 'bg-[#2455FF] text-white shadow-[1px_1px_0px_#151515]'
                          : 'bg-white text-[#151515] hover:bg-[#F4F0E8]'
                      }`}
                    >
                      {cs.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Line Spacing & Audio Pace */}
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-xs font-extrabold uppercase mb-1">
                  <span>Line Spacing</span>
                  <span className="font-mono">{settings.line_spacing}x</span>
                </div>
                <input
                  type="range"
                  min={1.4}
                  max={2.4}
                  step={0.1}
                  value={settings.line_spacing}
                  onChange={(e) => onUpdateSettings({ line_spacing: parseFloat(e.target.value) })}
                  className="w-full accent-[#2455FF]"
                />
              </div>

              <div>
                <div className="flex justify-between text-xs font-extrabold uppercase mb-1">
                  <span>Audio Speed</span>
                  <span className="font-mono">{settings.tts_speed}x</span>
                </div>
                <div className="grid grid-cols-4 gap-1">
                  {[0.75, 1.0, 1.25, 1.5].map((speed) => (
                    <button
                      key={speed}
                      onClick={() => onUpdateSettings({ tts_speed: speed })}
                      className={`py-1 text-xs font-bold border-2 border-[#151515] ${
                        settings.tts_speed === speed
                          ? 'bg-[#D7FF38] text-[#151515]'
                          : 'bg-white hover:bg-[#F4F0E8]'
                      }`}
                    >
                      {speed}x
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

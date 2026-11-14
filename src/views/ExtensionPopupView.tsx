import React, { useState } from 'react';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Card } from '../components/ui/Card';
import {
  Chrome,
  Zap,
  Layers,
  Sparkles,
  AlertTriangle,
  RefreshCw,
  ExternalLink,
  Sliders,
  CheckCircle2
} from 'lucide-react';

interface ExtensionPopupViewProps {
  onTransformSample: (url?: string, title?: string) => void;
  onOpenSidePanel: () => void;
}

export const ExtensionPopupView: React.FC<ExtensionPopupViewProps> = ({
  onTransformSample,
  onOpenSidePanel,
}) => {
  // Test scenario selector for simulating different browser tab states
  const [simulatedTabState, setSimulatedTabState] = useState<'article' | 'loading' | 'unsupported' | 'error'>('article');
  const [quickChunks, setQuickChunks] = useState(true);
  const [quickBionic, setQuickBionic] = useState(true);

  return (
    <div className="w-full min-h-screen pb-16 px-4 sm:px-6">
      <div className="max-w-4xl mx-auto pt-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Badge variant="blue">CHROME EXTENSION MANIFEST V3</Badge>
              <Badge variant="lime">INTERACTIVE PREVIEW</Badge>
            </div>
            <h1 className="text-2xl sm:text-4xl font-black uppercase text-[#151515] dark:text-white tracking-tight">
              Extension Companion & Popup
            </h1>
          </div>
        </div>

        {/* Instructions banner */}
        <div className="bg-[#D7FF38] border-3 border-[#151515] shadow-[4px_4px_0px_#151515] p-4 mb-8">
          <div className="flex items-start gap-3">
            <Chrome className="w-5 h-5 text-[#151515] flex-shrink-0 mt-0.5" />
            <div className="text-xs font-bold text-[#151515] leading-relaxed">
              <span className="font-black uppercase block text-sm mb-0.5">Ready for Chrome!</span>
              The full Manifest V3 extension lives in the <code className="bg-white px-1 py-0.5 font-mono">/extension</code> directory. Load it as an unpacked extension at <code className="bg-white px-1 py-0.5 font-mono">chrome://extensions</code> to transform real tabs with 1 click! Below is the live interactive simulation of the popup.
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
          {/* Left Column: Simulated Browser Extension Popup Device */}
          <div className="md:col-span-6 flex flex-col items-center">
            <span className="text-xs font-black uppercase tracking-wider text-gray-500 mb-2">
              Popup Window Preview (360px × 500px)
            </span>

            {/* The Neo-Brutalist Popup Container */}
            <div className="w-full max-w-[360px] bg-[#F4F0E8] border-4 border-[#151515] shadow-[8px_8px_0px_#151515] p-4 select-none">
              {/* Header */}
              <div className="flex items-center justify-between border-b-3 border-[#151515] pb-3 mb-4">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 bg-[#D7FF38] border-2 border-[#151515] font-black text-xs flex items-center justify-center">
                    FF
                  </div>
                  <span className="font-extrabold text-sm tracking-tight">FOCUSFLOW</span>
                </div>
                <span className="bg-[#D7FF38] border border-[#151515] text-[10px] font-black px-1.5 py-0.5 shadow-[1px_1px_0px_#151515]">
                  V1.0 MVP
                </span>
              </div>

              {/* State 1: Active Article Detected */}
              {simulatedTabState === 'article' && (
                <div className="space-y-3">
                  <div className="bg-white border-3 border-[#151515] shadow-[3px_3px_0px_#151515] p-3.5">
                    <span className="text-[10px] font-mono font-bold text-gray-500 uppercase block mb-1">
                      Detected Active Tab
                    </span>
                    <h3 className="font-black text-sm text-[#151515] leading-snug mb-2 line-clamp-2">
                      Attention Restoration in High-Friction Digital Workspaces
                    </h3>
                    <div className="flex items-center gap-2 text-[11px] font-bold text-gray-600 mb-3">
                      <span>psychology.umich.edu</span>
                      <span>•</span>
                      <span>420 words</span>
                      <span>•</span>
                      <span>~2m read</span>
                    </div>

                    <Button
                      onClick={() => onTransformSample('https://psychology.umich.edu/restoration-theory', 'Attention Restoration in High-Friction Digital Workspaces')}
                      variant="primary"
                      size="md"
                      fullWidth
                      icon={<Zap className="w-4 h-4" />}
                    >
                      ⚡ TRANSFORM NOW
                    </Button>

                    <button
                      onClick={onOpenSidePanel}
                      className="w-full mt-2 py-2 bg-white hover:bg-[#D7FF38] border-2 border-[#151515] text-xs font-black uppercase shadow-[2px_2px_0px_#151515] transition-all flex items-center justify-center gap-1.5"
                    >
                      <Layers className="w-3.5 h-3.5 text-[#2455FF]" />
                      <span>Open in Side Panel</span>
                    </button>
                  </div>

                  {/* Quick Controls Card */}
                  <div className="bg-white border-2 border-[#151515] p-3 shadow-[2px_2px_0px_#151515]">
                    <span className="text-[10px] font-black uppercase text-gray-600 block mb-2">
                      Quick Cognitive Controls
                    </span>
                    <div className="grid grid-cols-2 gap-2 text-xs font-bold">
                      <button
                        onClick={() => setQuickChunks(!quickChunks)}
                        className={`p-1.5 border border-[#151515] text-left ${quickChunks ? 'bg-[#D7FF38]' : 'bg-gray-100 text-gray-400'}`}
                      >
                        Chunks: {quickChunks ? 'ON' : 'OFF'}
                      </button>
                      <button
                        onClick={() => setQuickBionic(!quickBionic)}
                        className={`p-1.5 border border-[#151515] text-left ${quickBionic ? 'bg-[#D7FF38]' : 'bg-gray-100 text-gray-400'}`}
                      >
                        Bionic: {quickBionic ? 'ON' : 'OFF'}
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* State 2: Scanning / Loading */}
              {simulatedTabState === 'loading' && (
                <div className="bg-white border-3 border-[#151515] p-6 text-center shadow-[3px_3px_0px_#151515] my-4">
                  <RefreshCw className="w-6 h-6 animate-spin text-[#2455FF] mx-auto mb-2" />
                  <h4 className="font-black text-sm uppercase">Scanning Active Tab...</h4>
                  <p className="text-[11px] text-gray-600 mt-1">
                    Inspecting DOM structure and readability indicators.
                  </p>
                </div>
              )}

              {/* State 3: Unsupported Page */}
              {simulatedTabState === 'unsupported' && (
                <div className="bg-[#FFF0F0] border-3 border-[#FF5E5B] p-4 shadow-[3px_3px_0px_#151515] my-2">
                  <div className="flex items-center gap-2 text-[#FF5E5B] font-black text-xs uppercase mb-1">
                    <AlertTriangle className="w-4 h-4" />
                    <span>Unsupported Page</span>
                  </div>
                  <p className="text-xs font-bold text-gray-800 leading-snug mb-3">
                    Internal pages (chrome://, about:blank) cannot be transformed. Navigate to any news article, blog, or documentation.
                  </p>
                  <Button
                    onClick={() => setSimulatedTabState('article')}
                    variant="secondary"
                    size="sm"
                    fullWidth
                  >
                    Simulate Article Page
                  </Button>
                </div>
              )}

              {/* State 4: Error State */}
              {simulatedTabState === 'error' && (
                <div className="bg-red-50 border-3 border-[#151515] p-4 shadow-[3px_3px_0px_#151515] my-2">
                  <h4 className="font-black text-xs uppercase text-[#FF5E5B] mb-1">
                    Extraction Error
                  </h4>
                  <p className="text-xs font-medium text-gray-700 mb-3">
                    Failed to communicate with tab content script. Tab may have reloaded.
                  </p>
                  <Button
                    onClick={() => setSimulatedTabState('article')}
                    variant="lime"
                    size="sm"
                    fullWidth
                  >
                    RETRY SCAN
                  </Button>
                </div>
              )}

              <div className="mt-4 pt-3 border-t border-gray-300 text-center text-[10px] font-mono font-bold text-gray-500">
                FocusFlow Extension • Manifest V3
              </div>
            </div>
          </div>

          {/* Right Column: State Switcher & Extension Architecture */}
          <div className="md:col-span-6 space-y-6">
            {/* Interactive State Tester */}
            <div className="bg-white dark:bg-[#1E1E1E] border-3 sm:border-4 border-[#151515] dark:border-white shadow-[6px_6px_0px_#151515] p-5">
              <h3 className="font-black text-base uppercase text-[#151515] dark:text-white mb-2">
                Simulate Extension Edge Cases
              </h3>
              <p className="text-xs text-gray-600 dark:text-gray-400 font-medium mb-4">
                Click any condition to test how the Chrome Extension gracefully handles diverse browser scenarios:
              </p>

              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => setSimulatedTabState('article')}
                  className={`p-2.5 text-xs font-extrabold uppercase border-2 border-[#151515] text-left transition-all ${
                    simulatedTabState === 'article'
                      ? 'bg-[#D7FF38] text-[#151515] shadow-[2px_2px_0px_#151515]'
                      : 'bg-white hover:bg-[#F4F0E8] text-[#151515]'
                  }`}
                >
                  ✓ Readable Article
                </button>

                <button
                  onClick={() => setSimulatedTabState('loading')}
                  className={`p-2.5 text-xs font-extrabold uppercase border-2 border-[#151515] text-left transition-all ${
                    simulatedTabState === 'loading'
                      ? 'bg-[#2455FF] text-white shadow-[2px_2px_0px_#151515]'
                      : 'bg-white hover:bg-[#F4F0E8] text-[#151515]'
                  }`}
                >
                  ⏳ Scanning State
                </button>

                <button
                  onClick={() => setSimulatedTabState('unsupported')}
                  className={`p-2.5 text-xs font-extrabold uppercase border-2 border-[#151515] text-left transition-all ${
                    simulatedTabState === 'unsupported'
                      ? 'bg-[#FFA400] text-[#151515] shadow-[2px_2px_0px_#151515]'
                      : 'bg-white hover:bg-[#F4F0E8] text-[#151515]'
                  }`}
                >
                  ⚠️ Unsupported Page
                </button>

                <button
                  onClick={() => setSimulatedTabState('error')}
                  className={`p-2.5 text-xs font-extrabold uppercase border-2 border-[#151515] text-left transition-all ${
                    simulatedTabState === 'error'
                      ? 'bg-[#FF5E5B] text-white shadow-[2px_2px_0px_#151515]'
                      : 'bg-white hover:bg-[#F4F0E8] text-[#151515]'
                  }`}
                >
                  ❌ Extraction Error
                </button>
              </div>
            </div>

            {/* How to load unpacked extension in Chrome */}
            <div className="bg-[#FAF8F5] dark:bg-[#1E1E1E] border-3 sm:border-4 border-[#151515] dark:border-white shadow-[6px_6px_0px_#151515] p-5">
              <h3 className="font-black text-base uppercase text-[#151515] dark:text-white mb-2">
                How to Install in Chrome
              </h3>
              <ol className="space-y-2 text-xs font-medium text-gray-800 dark:text-gray-200 list-decimal list-inside">
                <li>Open Google Chrome and navigate to <code className="bg-[#E6E1D5] dark:bg-black px-1 py-0.5 font-mono font-bold">chrome://extensions</code>.</li>
                <li>Enable <strong className="font-black uppercase">Developer mode</strong> toggle in top-right corner.</li>
                <li>Click <strong className="font-black uppercase">Load unpacked</strong> button.</li>
                <li>Select the <code className="bg-[#E6E1D5] dark:bg-black px-1 py-0.5 font-mono font-bold">focusflow/extension</code> directory from this workspace.</li>
                <li>Click the FocusFlow puzzle icon in Chrome to transform any web article!</li>
              </ol>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

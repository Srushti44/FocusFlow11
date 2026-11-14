import React, { useState, useEffect } from 'react';
import { Chunk, UserSettings, SemanticHighlight } from '../../types';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { Modal } from '../ui/Modal';
import { renderBionicText } from '../../utils/bionic';
import { renderSemanticHighlights } from '../../utils/highlights';
import {
  ChevronLeft,
  ChevronRight,
  Volume2,
  VolumeX,
  Sparkles,
  CheckCircle2,
  Bookmark,
  Clock,
  ArrowRight,
  Lightbulb,
  BookOpen,
  Eye,
  EyeOff,
  Maximize2,
  Brain
} from 'lucide-react';
import { speechService } from '../../services/speech';
import { api } from '../../services/api';
import { SHAPExplanationModal } from '../ml/SHAPExplanationModal';
import { ExplainDifficultyResponse } from '../../types';

interface ChunkViewerProps {
  chunk: Chunk;
  chunkIndex: number;
  totalChunks: number;
  settings: UserSettings;
  highlights?: SemanticHighlight[];
  onNext: () => void;
  onPrev: () => void;
  onJumpToChunk: (index: number) => void;
  onCompleteArticle?: () => void;
  onSwitchToFullReader?: () => void;
  onToggleHighlights?: () => void;
  isArticleCompleted?: boolean;
}

export const ChunkViewer: React.FC<ChunkViewerProps> = ({
  chunk,
  chunkIndex,
  totalChunks,
  settings,
  highlights = [],
  onNext,
  onPrev,
  onJumpToChunk,
  onCompleteArticle,
  onSwitchToFullReader,
  onToggleHighlights,
  isArticleCompleted
}) => {
  const isFirst = chunkIndex === 0;
  const isLast = chunkIndex === totalChunks - 1;
  const progressPercent = Math.round(((chunkIndex + 1) / totalChunks) * 100);

  // Text selection explanation state
  const [selectedText, setSelectedText] = useState<string>('');
  const [selectionPosition, setSelectionPosition] = useState<{ x: number; y: number } | null>(null);
  const [explanationData, setExplanationData] = useState<{
    original_text: string;
    simple_explanation: string;
    key_takeaway: string;
    analogy?: string;
  } | null>(null);
  const [isExplaining, setIsExplaining] = useState(false);
  const [showExplanationModal, setShowExplanationModal] = useState(false);

  // ACLI SHAP explainability state
  const [isSHAPOpen, setIsSHAPOpen] = useState(false);
  const [shapData, setShapData] = useState<ExplainDifficultyResponse | null>(null);
  const [isShapLoading, setIsShapLoading] = useState(false);

  const handleOpenSHAP = async () => {
    setIsSHAPOpen(true);
    setIsShapLoading(true);
    try {
      const res = await api.explainDifficulty(chunk.text);
      setShapData(res);
    } catch (e) {
      console.error('[SHAP error]', e);
    } finally {
      setIsShapLoading(false);
    }
  };

  // Keyboard navigation
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName)) return;

      if (e.key === 'ArrowRight' || e.key === 'j' || e.key === ' ') {
        if (e.key === ' ') e.preventDefault();
        if (!isLast) onNext();
      } else if (e.key === 'ArrowLeft' || e.key === 'k') {
        if (!isFirst) onPrev();
      }
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [chunkIndex, isFirst, isLast, onNext, onPrev]);

  // Handle text selection in chunk
  const handleMouseUp = () => {
    const selection = window.getSelection();
    const text = selection?.toString()?.trim();
    if (text && text.length > 12) {
      const range = selection?.getRangeAt(0);
      const rect = range?.getBoundingClientRect();
      if (rect) {
        setSelectedText(text);
        setSelectionPosition({
          x: Math.min(window.innerWidth - 180, Math.max(10, rect.left + rect.width / 2 - 80)),
          y: rect.bottom + window.scrollY + 8
        });
      }
    } else {
      setSelectedText('');
      setSelectionPosition(null);
    }
  };

  const handleExplainSelection = async () => {
    if (!selectedText) return;
    setIsExplaining(true);
    setShowExplanationModal(true);
    setSelectionPosition(null);

    try {
      const result = await api.explainText(selectedText, chunk.text);
      setExplanationData(result);
    } catch {
      setExplanationData({
        original_text: selectedText,
        simple_explanation: `In simple terms: this explains that ${selectedText.split('.')[0].toLowerCase()}.`,
        key_takeaway: selectedText.split('.')[0] + '.',
        analogy: 'Think of this like mental working memory having a maximum capacity: too much noise blocks out core ideas.'
      });
    } finally {
      setIsExplaining(false);
    }
  };

  const [audioState, setAudioState] = useState(speechService.getState());

  useEffect(() => {
    return speechService.subscribe(setAudioState);
  }, []);

  const handleToggleSpeak = () => {
    if (audioState.isSpeaking) {
      speechService.stop();
    } else {
      speechService.speak(chunk.text, settings.tts_speed, () => {
        if (!isLast) {
          onNext();
        }
      });
    }
  };

  // Font styling resolution
  const fontClass = {
    lexend: 'font-lexend',
    atkinson: 'font-atkinson',
    dyslexic: 'font-dyslexic',
    sans: 'font-sans',
    serif: 'font-serif',
    mono: 'font-mono'
  }[settings.font_family] || 'font-lexend';

  return (
    <div className="w-full max-w-4xl mx-auto flex flex-col items-center select-text relative">
      {/* Chunk Meta Header */}
      <div className="w-full flex items-center justify-between mb-3 px-1">
        <div className="flex items-center gap-2">
          <Badge variant="blue" size="md">
            CHUNK {chunkIndex + 1} OF {totalChunks}
          </Badge>
          <span className="text-xs font-mono font-bold text-gray-600 dark:text-gray-300 flex items-center gap-1">
            <Clock className="w-3.5 h-3.5" />
            {chunk.estimated_seconds}s
          </span>
          <Badge
            variant={
              chunk.cognitive_difficulty === 'dense' || chunk.cognitive_difficulty === 'Hard' || chunk.cognitive_difficulty === 'Very Hard' ? 'coral' :
              chunk.cognitive_difficulty === 'easy' || chunk.cognitive_difficulty === 'Easy' ? 'lime' : 'amber'
            }
          >
            {chunk.cognitive_difficulty}
          </Badge>

          {/* ACLI SHAP Insights Trigger */}
          <button
            onClick={handleOpenSHAP}
            className="flex items-center gap-1.5 px-2 py-0.5 bg-white dark:bg-[#1E1E1E] border-2 border-[#151515] text-[11px] font-black uppercase shadow-[2px_2px_0px_#151515] hover:bg-[#D7FF38] hover:text-[#151515] transition-all cursor-pointer"
            title="Inspect machine-learned cognitive difficulty and TreeExplainer SHAP values"
          >
            <Brain className="w-3.5 h-3.5 text-[#2455FF]" />
            <span>SHAP Insights</span>
          </button>
        </div>

        <div className="flex items-center gap-2">
          {onSwitchToFullReader && (
            <button
              onClick={onSwitchToFullReader}
              className="hidden sm:flex items-center gap-1.5 px-3 py-1 bg-white dark:bg-[#1E1E1E] border-2 border-[#151515] dark:border-white text-xs font-extrabold shadow-[2px_2px_0px_#151515] hover:bg-[#F4F0E8] transition-all"
              title="Switch to full article continuous reading view"
            >
              <BookOpen className="w-3.5 h-3.5" />
              <span>FULL ARTICLE</span>
            </button>
          )}

          <button
            onClick={handleToggleSpeak}
            className={`flex items-center gap-1.5 px-3 py-1 border-2 border-[#151515] dark:border-white text-xs font-extrabold shadow-[2px_2px_0px_#151515] transition-all ${
              audioState.isSpeaking
                ? 'bg-[#FF5E5B] text-white hover:bg-[#e04845]'
                : 'bg-white dark:bg-[#1E1E1E] hover:bg-[#D7FF38] hover:text-[#151515]'
            }`}
            title={audioState.isSpeaking ? 'Stop audio reading' : 'Listen to this chunk with auto-next'}
          >
            {audioState.isSpeaking ? (
              <VolumeX className="w-4 h-4 text-white" />
            ) : (
              <Volume2 className="w-4 h-4 text-[#2455FF]" />
            )}
            <span>{audioState.isSpeaking ? 'STOP AUDIO' : 'LISTEN'}</span>
          </button>
        </div>
      </div>

      {/* Floating Selection Tooltip for Simplification */}
      {selectionPosition && selectedText && (
        <div
          className="fixed z-50 animate-bounce"
          style={{ left: `${selectionPosition.x}px`, top: `${selectionPosition.y}px` }}
        >
          <button
            onClick={handleExplainSelection}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-[#2455FF] text-white border-2 border-[#151515] font-extrabold text-xs shadow-[3px_3px_0px_#151515] hover:bg-[#1940d0] transition-all"
          >
            <Lightbulb className="w-3.5 h-3.5 text-[#D7FF38]" />
            <span>⚡ SIMPLIFY SELECTION</span>
          </button>
        </div>
      )}

      {/* Primary Focus Chunk Card */}
      <div
        onMouseUp={handleMouseUp}
        className="w-full bg-white dark:bg-[#1E1E1E] border-4 border-[#151515] dark:border-white shadow-[8px_8px_0px_#151515] p-6 sm:p-10 relative transition-all"
      >
        {/* Visual Accent Top Bar */}
        <div className="absolute top-0 left-0 right-0 h-2 bg-[#2455FF]" />

        {/* Chunk Text Container */}
        <div
          className={`${fontClass} leading-relaxed text-[#151515] dark:text-[#F4F0E8] transition-all`}
          style={{
            fontSize: `${settings.font_size}px`,
            lineHeight: settings.line_spacing,
            letterSpacing: `${settings.letter_spacing}px`,
          }}
        >
          {settings.bionic_reading ? (
            renderBionicText(chunk.text, true)
          ) : (
            renderSemanticHighlights(chunk.text, settings.enable_semantic_highlights, highlights)
          )}
        </div>

        {/* Semantic Highlighting Legend Bar */}
        {settings.enable_semantic_highlights && !settings.bionic_reading && (
          <div className="mt-6 pt-3 border-t-2 border-dashed border-gray-300 dark:border-gray-700 flex flex-wrap items-center justify-between gap-2 text-xs font-bold font-mono">
            <div className="flex flex-wrap items-center gap-3">
              <span className="text-gray-500 uppercase">LEGEND:</span>
              <span className="flex items-center gap-1 bg-[#FFF380] text-[#151515] px-1.5 py-0.5 border border-[#151515]">
                🟡 KEY CONCEPT
              </span>
              <span className="flex items-center gap-1 bg-[#C8F7DC] text-[#0B4A2B] px-1.5 py-0.5 border border-[#151515]">
                🟢 DEFINITION
              </span>
              <span className="flex items-center gap-1 bg-[#D2E2FF] text-[#0A2E80] px-1.5 py-0.5 border border-[#151515]">
                🔵 DATA & EVIDENCE
              </span>
            </div>

            {onToggleHighlights && (
              <button
                onClick={onToggleHighlights}
                className="text-[11px] font-bold text-gray-600 dark:text-gray-400 hover:underline flex items-center gap-1"
              >
                <EyeOff className="w-3.5 h-3.5" />
                <span>HIDE HIGHLIGHTS</span>
              </button>
            )}
          </div>
        )}

        {/* Key Takeaway Banner */}
        {chunk.key_takeaway && (
          <div className="mt-6 p-4 bg-[#F4F0E8] dark:bg-[#2A2A2A] border-2 border-[#151515] dark:border-gray-500 shadow-[3px_3px_0px_#151515]">
            <div className="flex items-center gap-2 text-xs font-extrabold uppercase text-[#2455FF] dark:text-[#D7FF38] mb-1">
              <Sparkles className="w-4 h-4" />
              <span>COGNITIVE ANCHOR / CORE TAKEAWAY</span>
            </div>
            <p className="text-sm font-semibold text-gray-800 dark:text-gray-200">
              {chunk.key_takeaway}
            </p>
          </div>
        )}

        {/* Semantic Entities */}
        {chunk.entities && chunk.entities.length > 0 && (
          <div className="mt-4 flex flex-wrap items-center gap-2 pt-3 border-t-2 border-dashed border-gray-300 dark:border-gray-700">
            <span className="text-[11px] font-mono font-bold text-gray-500 uppercase">Tags:</span>
            {chunk.entities.map((ent, idx) => (
              <span
                key={idx}
                className="text-xs font-bold px-2 py-0.5 bg-[#FAF8F5] dark:bg-[#333] border border-[#151515] text-[#151515] dark:text-white"
              >
                #{ent}
              </span>
            ))}
          </div>
        )}

        {/* Cognitive Assistance Recommendation for Hard / Dense chunks */}
        {(chunk.cognitive_difficulty === 'dense' || chunk.cognitive_difficulty === 'Hard' || chunk.cognitive_difficulty === 'Very Hard') && (
          <div className="mt-5 p-3.5 bg-[#FFF9D2] dark:bg-[#332E12] border-2 border-[#151515] shadow-[3px_3px_0px_#151515] flex flex-wrap items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-2 font-bold text-gray-800 dark:text-gray-200">
              <Lightbulb className="w-4 h-4 text-[#FF5E5B] shrink-0" />
              <span>Elevated cognitive difficulty detected by ACLI model.</span>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <button
                onClick={handleOpenSHAP}
                className="px-2.5 py-1 bg-white dark:bg-[#1E1E1E] border border-[#151515] font-extrabold text-[11px] uppercase hover:bg-[#D7FF38] hover:text-[#151515] shadow-[1px_1px_0px_#151515] transition-all"
              >
                🧠 Inspect SHAP Factors
              </button>
              <button
                onClick={() => {
                  setSelectedText(chunk.text);
                  handleExplainSelection();
                }}
                className="px-2.5 py-1 bg-[#2455FF] text-white border border-[#151515] font-extrabold text-[11px] uppercase hover:bg-[#1940d0] shadow-[1px_1px_0px_#151515] transition-all flex items-center gap-1"
              >
                <Sparkles className="w-3 h-3 text-[#D7FF38]" />
                <span>⚡ Simplify with AI</span>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Navigation Controls */}
      <div className="w-full mt-6 flex flex-col sm:flex-row items-center justify-between gap-4">
        <Button
          onClick={onPrev}
          disabled={isFirst}
          variant="secondary"
          size="md"
          icon={<ChevronLeft className="w-5 h-5" />}
          className="w-full sm:w-auto"
        >
          PREVIOUS (K)
        </Button>

        {/* Progress Bar */}
        <div className="flex flex-col items-center gap-1 w-full max-w-xs">
          <div className="w-full bg-[#E6E1D5] border-2 border-[#151515] h-4 shadow-[2px_2px_0px_#151515] relative overflow-hidden">
            <div
              className="bg-[#D7FF38] h-full border-r-2 border-[#151515] transition-all duration-200"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
          <span className="text-[11px] font-mono font-bold text-gray-600 dark:text-gray-300">
            {progressPercent}% READ ({chunkIndex + 1}/{totalChunks})
          </span>
        </div>

        {isLast ? (
          <Button
            onClick={onCompleteArticle}
            variant="lime"
            size="md"
            icon={<CheckCircle2 className="w-5 h-5 text-[#151515]" />}
            className="w-full sm:w-auto"
          >
            {isArticleCompleted ? 'COMPLETED ✓' : 'FINISH ARTICLE'}
          </Button>
        ) : (
          <Button
            onClick={onNext}
            variant="primary"
            size="md"
            icon={<ChevronRight className="w-5 h-5" />}
            className="w-full sm:w-auto"
          >
            NEXT CHUNK (J / SPACE)
          </Button>
        )}
      </div>

      {/* Quick Jump Bar */}
      <div className="w-full mt-6 pt-4 border-t-2 border-[#151515]/20 flex flex-wrap items-center justify-center gap-1.5">
        <span className="text-[11px] font-mono font-bold text-gray-500 mr-2">CHUNKS:</span>
        {Array.from({ length: totalChunks }).map((_, idx) => (
          <button
            key={idx}
            onClick={() => onJumpToChunk(idx)}
            className={`w-7 h-7 font-mono text-xs font-extrabold border-2 border-[#151515] transition-all ${
              idx === chunkIndex
                ? 'bg-[#2455FF] text-white shadow-[2px_2px_0px_#151515] scale-110'
                : 'bg-white hover:bg-[#D7FF38] text-[#151515]'
            }`}
          >
            {idx + 1}
          </button>
        ))}
      </div>

      {/* Text Simplification Modal */}
      <Modal
        isOpen={showExplanationModal}
        onClose={() => setShowExplanationModal(false)}
        title="⚡ FocusFlow Cognitive Simplifier"
        maxWidth="md"
      >
        <div className="space-y-4 font-mono">
          <div className="p-3 bg-[#FAF8F5] border-2 border-[#151515] text-xs italic text-gray-700">
            "{selectedText}"
          </div>

          {isExplaining ? (
            <div className="py-6 text-center text-sm font-bold animate-pulse text-[#2455FF]">
              Generating cognitive simplification & everyday analogy...
            </div>
          ) : (
            explanationData && (
              <div className="space-y-3">
                <div className="p-4 bg-white border-3 border-[#151515] shadow-[4px_4px_0px_#151515]">
                  <div className="text-xs font-black uppercase text-[#2455FF] mb-1">
                    IN PLAIN TERMS:
                  </div>
                  <p className="text-sm font-bold text-[#151515] leading-relaxed">
                    {explanationData.simple_explanation}
                  </p>
                </div>

                {explanationData.analogy && (
                  <div className="p-3 bg-[#D7FF38] border-2 border-[#151515] text-xs font-bold text-[#151515]">
                    💡 <strong>EVERYDAY ANALOGY:</strong> {explanationData.analogy}
                  </div>
                )}

                <div className="p-3 bg-[#FAF8F5] border-2 border-[#151515] text-xs font-semibold text-gray-700">
                  🎯 <strong>KEY TAKEAWAY:</strong> {explanationData.key_takeaway}
                </div>
              </div>
            )
          )}

          <div className="pt-2 flex justify-end">
            <Button
              onClick={() => setShowExplanationModal(false)}
              variant="secondary"
              size="sm"
            >
              CLOSE
            </Button>
          </div>
        </div>
      </Modal>

      {/* Real SHAP Feature Contribution Modal */}
      <SHAPExplanationModal
        isOpen={isSHAPOpen}
        onClose={() => setIsSHAPOpen(false)}
        explanation={shapData}
        isLoading={isShapLoading}
        onTriggerSimplify={() => {
          setSelectedText(chunk.text);
          handleExplainSelection();
        }}
      />
    </div>
  );
};

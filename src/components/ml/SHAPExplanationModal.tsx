import React from 'react';
import { ExplainDifficultyResponse, DifficultyClass } from '../../types';
import { Modal } from '../ui/Modal';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import {
  Brain,
  HelpCircle,
  Lightbulb,
  BookOpen,
  ArrowRight,
  TrendingUp,
  TrendingDown,
  Info,
  Layers,
  AlertTriangle,
  Sparkles
} from 'lucide-react';

interface SHAPExplanationModalProps {
  isOpen: boolean;
  onClose: () => void;
  explanation: ExplainDifficultyResponse | null;
  isLoading: boolean;
  onTriggerSimplify?: () => void;
  onSwitchToSmallChunks?: () => void;
}

export const SHAPExplanationModal: React.FC<SHAPExplanationModalProps> = ({
  isOpen,
  onClose,
  explanation,
  isLoading,
  onTriggerSimplify,
  onSwitchToSmallChunks
}) => {
  if (!isOpen) return null;

  const getDifficultyBadge = (diff?: DifficultyClass) => {
    switch (diff) {
      case 'Easy':
        return <Badge variant="lime" size="md">EASY COMPLEXITY</Badge>;
      case 'Medium':
        return <Badge variant="amber" size="md">MEDIUM COMPLEXITY</Badge>;
      case 'Hard':
        return <Badge variant="coral" size="md">HARD COMPLEXITY</Badge>;
      case 'Very Hard':
        return <Badge variant="coral" size="md">VERY HARD (ACADEMIC)</Badge>;
      default:
        return <Badge variant="blue" size="md">DIFFICULTY ANALYSIS</Badge>;
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="🧠 ACLI Cognitive Load & SHAP Explainability"
      maxWidth="lg"
    >
      {isLoading ? (
        <div className="py-12 flex flex-col items-center justify-center gap-3">
          <div className="w-8 h-8 border-4 border-[#2455FF] border-t-transparent animate-spin" />
          <p className="font-mono text-xs font-bold uppercase tracking-wider text-gray-600 dark:text-gray-300">
            Computing TreeExplainer SHAP values & feature contributions...
          </p>
        </div>
      ) : !explanation || !explanation.available ? (
        <div className="p-6 bg-[#FAF8F5] dark:bg-[#1E1E1E] border-3 border-[#151515] text-center space-y-3">
          <AlertTriangle className="w-8 h-8 text-[#FF5E5B] mx-auto" />
          <h4 className="font-black text-sm uppercase">Explainability Unavailable</h4>
          <p className="font-mono text-xs text-gray-600 dark:text-gray-300">
            {explanation?.error || 'SHAP feature attribution could not be computed for this paragraph.'}
          </p>
        </div>
      ) : (
        <div className="space-y-6 select-text">
          {/* Header Summary Banner */}
          <div className="p-4 bg-[#F4F0E8] dark:bg-[#252525] border-3 border-[#151515] shadow-[4px_4px_0px_#151515] flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              {getDifficultyBadge(explanation.predicted_class)}
              <span className="font-mono text-xs font-black text-gray-700 dark:text-gray-300">
                CONFIDENCE: {Math.round((explanation.confidence || 0) * 100)}%
              </span>
            </div>
            <div className="text-[11px] font-mono font-bold text-gray-500">
              MODEL: v{explanation.model_version || '1.0.0'} (RandomForest)
            </div>
          </div>

          {/* Natural Language Narrative Rationale */}
          <div className="p-4 bg-white dark:bg-[#1E1E1E] border-3 border-[#151515] shadow-[4px_4px_0px_#151515]">
            <div className="flex items-center gap-2 mb-2 text-xs font-black uppercase text-[#2455FF] dark:text-[#D7FF38]">
              <Sparkles className="w-4 h-4" />
              <span>Grounded SHAP Feature Narrative</span>
            </div>
            <p className="text-xs sm:text-sm font-semibold leading-relaxed text-[#151515] dark:text-[#F4F0E8]">
              {explanation.human_explanation}
            </p>
          </div>

          {/* Real SHAP Feature Contributions Chart */}
          <div className="p-4 bg-white dark:bg-[#1E1E1E] border-3 border-[#151515] shadow-[4px_4px_0px_#151515]">
            <div className="flex items-center justify-between mb-4 border-b-2 border-[#151515] pb-2">
              <span className="text-xs font-black uppercase tracking-wider text-[#151515] dark:text-white flex items-center gap-1.5">
                <Brain className="w-4 h-4 text-[#2455FF]" />
                FEATURE ATTRIBUTION BREAKDOWN (SHAP VALUES)
              </span>
              <span className="text-[10px] font-mono font-bold text-gray-500">
                BASE VALUE: {explanation.base_value}
              </span>
            </div>

            <div className="space-y-3">
              {explanation.feature_contributions.map((fc, idx) => {
                const isPositive = fc.shap_value > 0;
                const barWidth = Math.min(100, Math.round(fc.abs_impact * 250));

                return (
                  <div key={idx} className="space-y-1 text-xs">
                    <div className="flex items-center justify-between font-mono font-bold">
                      <span className="text-gray-800 dark:text-gray-200">
                        {fc.feature}
                        <span className="text-[10px] text-gray-500 font-normal ml-1.5">
                          (raw: {fc.raw_value})
                        </span>
                      </span>
                      <span
                        className={`font-black ${
                          isPositive
                            ? 'text-[#FF5E5B]'
                            : 'text-[#0B4A2B] dark:text-[#D7FF38]'
                        }`}
                      >
                        {isPositive ? `+${fc.shap_value}` : fc.shap_value}
                      </span>
                    </div>

                    {/* Visual contribution bar */}
                    <div className="w-full bg-[#E6E1D5] dark:bg-[#333] h-2.5 border border-[#151515] relative overflow-hidden flex">
                      <div
                        className={`h-full transition-all duration-300 ${
                          isPositive ? 'bg-[#FF5E5B]' : 'bg-[#2455FF] dark:bg-[#D7FF38]'
                        }`}
                        style={{ width: `${Math.max(4, barWidth)}%` }}
                      />
                    </div>
                    <p className="text-[10px] font-sans text-gray-500 dark:text-gray-400">
                      {fc.description}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Tailored Cognitive Reading Adjustments */}
          {(explanation.predicted_class === 'Hard' || explanation.predicted_class === 'Very Hard') && (
            <div className="p-4 bg-[#FFF9D2] dark:bg-[#332E12] border-3 border-[#151515] shadow-[4px_4px_0px_#151515]">
              <div className="flex items-center gap-2 mb-2 text-xs font-black uppercase text-[#151515] dark:text-[#FFF380]">
                <Lightbulb className="w-4 h-4 text-[#FF5E5B]" />
                <span>RECOMMENDED READING ASSISTANCE</span>
              </div>
              <p className="text-xs font-medium text-gray-800 dark:text-gray-200 mb-3">
                This paragraph has high syntactic and vocabulary friction. FocusFlow recommends:
              </p>
              <div className="flex flex-wrap gap-2">
                {onTriggerSimplify && (
                  <button
                    onClick={() => {
                      onClose();
                      onTriggerSimplify();
                    }}
                    className="px-3 py-1.5 bg-[#2455FF] text-white border-2 border-[#151515] font-extrabold text-xs shadow-[2px_2px_0px_#151515] hover:bg-[#1940d0] flex items-center gap-1.5"
                  >
                    <Sparkles className="w-3.5 h-3.5 text-[#D7FF38]" />
                    <span>⚡ SIMPLIFY WITH AI</span>
                  </button>
                )}
                {onSwitchToSmallChunks && (
                  <button
                    onClick={() => {
                      onClose();
                      onSwitchToSmallChunks();
                    }}
                    className="px-3 py-1.5 bg-[#D7FF38] text-[#151515] border-2 border-[#151515] font-extrabold text-xs shadow-[2px_2px_0px_#151515] hover:bg-[#c5f025] flex items-center gap-1.5"
                  >
                    <Layers className="w-3.5 h-3.5" />
                    <span>BREAK INTO SMALLER CHUNKS (45 WORDS)</span>
                  </button>
                )}
              </div>
            </div>
          )}

          {/* Footnote on Medical Disclaimer */}
          <div className="p-3 bg-gray-100 dark:bg-[#1A1A1A] border border-gray-300 dark:border-gray-700 text-[10px] font-mono text-gray-500">
            <strong>Methodology Note:</strong> ACLI measures textual and syntactic readability features using an empirical Random Forest model. It does not measure human neurocognitive states or diagnose cognitive conditions.
          </div>
        </div>
      )}
    </Modal>
  );
};

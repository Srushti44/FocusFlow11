import React, { useState } from 'react';
import { Article, UserSettings, ExplainDifficultyResponse } from '../../types';
import { renderBionicText } from '../../utils/bionic';
import { Badge } from '../ui/Badge';
import { Eye, CheckCircle2, Brain } from 'lucide-react';
import { Button } from '../ui/Button';
import { SHAPExplanationModal } from '../ml/SHAPExplanationModal';
import { api } from '../../services/api';

interface FullReaderProps {
  article: Article;
  settings: UserSettings;
  onCompleteArticle?: () => void;
  isArticleCompleted?: boolean;
}

export const FullReader: React.FC<FullReaderProps> = ({
  article,
  settings,
  onCompleteArticle,
  isArticleCompleted
}) => {
  const [selectedShapChunk, setSelectedShapChunk] = useState<string | null>(null);
  const [shapData, setShapData] = useState<ExplainDifficultyResponse | null>(null);
  const [isShapLoading, setIsShapLoading] = useState<boolean>(false);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  const handleOpenShap = async (text: string) => {
    setIsModalOpen(true);
    setIsShapLoading(true);
    try {
      const res = await api.explainDifficulty(text);
      setShapData(res);
    } catch (e) {
      console.error(e);
    } finally {
      setIsShapLoading(false);
    }
  };

  const fontClass = {
    lexend: 'font-lexend',
    atkinson: 'font-atkinson',
    dyslexic: 'font-dyslexic',
    sans: 'font-sans',
    serif: 'font-serif',
    mono: 'font-mono'
  }[settings.font_family] || 'font-lexend';

  return (
    <div
      className="w-full mx-auto select-text relative"
      style={{ maxWidth: `${settings.content_width}px` }}
    >

      {/* Full Article Content Card */}
      <div className="bg-white dark:bg-[#1E1E1E] border-4 border-[#151515] dark:border-white shadow-[8px_8px_0px_#151515] p-6 sm:p-12">
        <div className="space-y-8">
          {article.chunks.map((chunk, idx) => (
            <div
              key={chunk.id || idx}
              className="relative group pb-6 border-b-2 border-dashed border-gray-200 dark:border-gray-800 last:border-b-0"
            >
              {/* Chunk marker */}
              <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                <div className="flex items-center gap-2">
                  <span className="text-[11px] font-mono font-extrabold uppercase px-2 py-0.5 bg-[#FAF8F5] dark:bg-[#2A2A2A] border border-[#151515] text-[#2455FF] dark:text-[#D7FF38]">
                    PARAGRAPH {idx + 1}
                  </span>
                  <Badge
                    variant={
                      chunk.cognitive_difficulty === 'dense' || chunk.cognitive_difficulty === 'Hard' || chunk.cognitive_difficulty === 'Very Hard' ? 'coral' :
                      chunk.cognitive_difficulty === 'easy' || chunk.cognitive_difficulty === 'Easy' ? 'lime' : 'amber'
                    }
                    size="sm"
                  >
                    ACLI: {chunk.cognitive_difficulty || 'Standard'}
                  </Badge>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-[11px] font-mono text-gray-500">
                    {chunk.word_count} words
                  </span>
                  <button
                    onClick={() => handleOpenShap(chunk.text)}
                    className="flex items-center gap-1 px-2 py-0.5 bg-white dark:bg-[#2A2A2A] border border-[#151515] text-[10px] font-mono font-extrabold uppercase shadow-[1px_1px_0px_#151515] hover:bg-[#D7FF38] hover:text-[#151515] transition-all"
                    title="View SHAP feature attributions for this paragraph"
                  >
                    <Brain className="w-3 h-3 text-[#2455FF]" />
                    <span>SHAP</span>
                  </button>
                </div>
              </div>

              {/* Chunk Body */}
              <p
                className={`${fontClass} leading-relaxed text-[#151515] dark:text-[#F4F0E8]`}
                style={{
                  fontSize: `${settings.font_size}px`,
                  lineHeight: settings.line_spacing,
                  letterSpacing: `${settings.letter_spacing}px`,
                }}
              >
                {renderBionicText(chunk.text, settings.bionic_reading)}
              </p>

              {/* Chunk Takeaway Tag */}
              {chunk.key_takeaway && (
                <div className="mt-3 text-xs font-medium text-gray-600 dark:text-gray-400 bg-[#F4F0E8] dark:bg-[#222] p-2.5 border-l-4 border-[#2455FF]">
                  <strong className="font-bold uppercase text-[#2455FF] mr-1">Anchor:</strong>
                  {chunk.key_takeaway}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* End of article call to action */}
        <div className="mt-10 pt-8 border-t-4 border-[#151515] flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>
            <h4 className="font-extrabold text-base uppercase text-[#151515] dark:text-white">
              End of Article
            </h4>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              Ready to verify comprehension with a quick 3-question quiz or flashcards?
            </p>
          </div>

          <Button
            onClick={onCompleteArticle}
            variant="lime"
            size="md"
            icon={<CheckCircle2 className="w-5 h-5 text-[#151515]" />}
          >
            {isArticleCompleted ? 'COMPLETED ✓' : 'MARK AS FINISHED'}
          </Button>
        </div>
      </div>

      {/* SHAP Explainability Modal */}
      <SHAPExplanationModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        explanation={shapData}
        isLoading={isShapLoading}
      />
    </div>
  );
};

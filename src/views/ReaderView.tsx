import React, { useState, useEffect, useMemo } from 'react';
import { Article, UserSettings, Chunk } from '../types';
import { ChunkViewer } from '../components/reader/ChunkViewer';
import { FullReader } from '../components/reader/FullReader';
import { ReadingControlsBar } from '../components/reader/ReadingControlsBar';
import { LearningTools } from '../components/reader/LearningTools';
import { Modal } from '../components/ui/Modal';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { api } from '../services/api';
import { speechService } from '../services/speech';
import confetti from 'canvas-confetti';
import {
  Sparkles,
  ExternalLink,
  Clock,
  Layers,
  Award,
  CheckCircle2,
  Bookmark,
  Share2,
  HelpCircle,
  ArrowLeft,
  FileText,
  Eye,
  Crosshair,
  RotateCcw,
  Brain
} from 'lucide-react';
import { SHAPExplanationModal } from '../components/ml/SHAPExplanationModal';
import { ExplainDifficultyResponse, DifficultyClass } from '../types';

interface ReaderViewProps {
  article: Article;
  settings: UserSettings;
  onUpdateSettings: (newSettings: Partial<UserSettings>) => void;
  onBackToDashboard: () => void;
  initialPracticeTab?: 'quiz' | 'flashcards' | null;
}

export const ReaderView: React.FC<ReaderViewProps> = ({
  article,
  settings,
  onUpdateSettings,
  onBackToDashboard,
  initialPracticeTab = null,
}) => {
  const [currentChunkIndex, setCurrentChunkIndex] = useState(article.current_chunk_index || 0);
  const [isCompleted, setIsCompleted] = useState(article.is_completed || false);
  const [showLearningTools, setShowLearningTools] = useState(!!initialPracticeTab);
  const [showCompletionModal, setShowCompletionModal] = useState(false);
  const [showShortcutsModal, setShowShortcutsModal] = useState(false);
  const [showOriginalTextModal, setShowOriginalTextModal] = useState(false);
  const [showArticleSHAPModal, setShowArticleSHAPModal] = useState(false);
  const [articleSHAPData, setArticleSHAPData] = useState<ExplainDifficultyResponse | null>(null);
  const [isArticleSHAPLoading, setIsArticleSHAPLoading] = useState(false);
  const [articleDifficulty, setArticleDifficulty] = useState<DifficultyClass | null>(
    (article.predicted_difficulty as DifficultyClass) || null
  );

  // Auto-predict difficulty for the article on mount if not already cached
  useEffect(() => {
    const textSample = article.raw_content || article.chunks?.[0]?.text || '';
    if (textSample) {
      api.predictDifficulty(textSample).then((res) => {
        if (res && res.predicted_difficulty) {
          setArticleDifficulty(res.predicted_difficulty);
        }
      }).catch(() => {});
    }
  }, [article.id, article.raw_content]);

  const handleOpenArticleSHAP = async () => {
    setShowArticleSHAPModal(true);
    if (!articleSHAPData) {
      setIsArticleSHAPLoading(true);
      try {
        const textSample = article.raw_content || article.chunks?.[0]?.text || '';
        const res = await api.explainDifficulty(textSample);
        setArticleSHAPData(res);
      } catch (e) {
        console.error('[ReaderView SHAP Error]', e);
      } finally {
        setIsArticleSHAPLoading(false);
      }
    }
  };

  // Dynamic chunk calculation if chunk_size_words changes
  const activeChunks: Chunk[] = useMemo(() => {
    const targetSize = settings.chunk_size_words || 80;
    // If standard 80 words and article already has precomputed chunks, use them
    if (targetSize === 80 && article.chunks && article.chunks.length > 0) {
      return article.chunks;
    }

    if (!article.raw_content) {
      return article.chunks;
    }

    // Dynamic client-side chunking respecting paragraph, heading, and sentence boundaries
    const paragraphs = article.raw_content.split(/\n\n+/).filter(p => p.trim());
    const rechunked: Chunk[] = [];
    let idx = 0;

    for (const para of paragraphs) {
      if (para.startsWith('#') || para.startsWith('==')) {
        const words = para.split(/\s+/).filter(Boolean);
        rechunked.push({
          id: `chunk-dyn-${idx}`,
          index: idx,
          text: para,
          key_takeaway: para.replace(/^#+\s*/, ''),
          word_count: words.length,
          estimated_seconds: Math.max(5, Math.round((words.length / 200) * 60)),
          entities: [],
          cognitive_difficulty: 'easy'
        });
        idx++;
        continue;
      }

      const sentences = para.split(/(?<=[.!?])\s+/).filter(s => s.trim());
      let curSentences: string[] = [];
      let curWords = 0;

      for (const sent of sentences) {
        const sWords = sent.split(/\s+/).filter(Boolean).length;
        if (curWords + sWords > targetSize + 15 && curSentences.length > 0) {
          const text = curSentences.join(' ');
          const wc = text.split(/\s+/).filter(Boolean).length;
          rechunked.push({
            id: `chunk-dyn-${idx}`,
            index: idx,
            text,
            key_takeaway: curSentences[0] || text.slice(0, 60) + '...',
            word_count: wc,
            estimated_seconds: Math.max(10, Math.round((wc / 200) * 60)),
            entities: [],
            cognitive_difficulty: wc > 90 ? 'dense' : (wc < 45 ? 'easy' : 'medium')
          });
          idx++;
          curSentences = [sent];
          curWords = sWords;
        } else {
          curSentences.push(sent);
          curWords += sWords;
        }
      }

      if (curSentences.length > 0) {
        const text = curSentences.join(' ');
        const wc = text.split(/\s+/).filter(Boolean).length;
        rechunked.push({
          id: `chunk-dyn-${idx}`,
          index: idx,
          text,
          key_takeaway: curSentences[0] || text.slice(0, 60) + '...',
          word_count: wc,
          estimated_seconds: Math.max(10, Math.round((wc / 200) * 60)),
          entities: [],
          cognitive_difficulty: wc > 90 ? 'dense' : (wc < 45 ? 'easy' : 'medium')
        });
        idx++;
      }
    }

    return rechunked.length > 0 ? rechunked : article.chunks;
  }, [article.chunks, article.raw_content, settings.chunk_size_words]);

  // Adjust chunk index if out of range after rechunking
  // Stop speech on unmount
  useEffect(() => {
    return () => {
      speechService.stop();
    };
  }, []);

  // Sync state when article prop changes
  useEffect(() => {
    speechService.stop();
    setCurrentChunkIndex(article.current_chunk_index || 0);
    setIsCompleted(article.is_completed || false);
  }, [article.id]);

  // Assistive Focus Ruler cursor tracking
  const [rulerTop, setRulerTop] = useState<number | null>(null);

  useEffect(() => {
    if (!settings.focus_ruler) {
      setRulerTop(null);
      return;
    }
    const handleMouseMove = (e: MouseEvent) => {
      setRulerTop(e.clientY);
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, [settings.focus_ruler]);

  useEffect(() => {
    if (currentChunkIndex >= activeChunks.length) {
      setCurrentChunkIndex(Math.max(0, activeChunks.length - 1));
    }
  }, [activeChunks.length, currentChunkIndex]);

  // Sync progress
  const handleChunkChange = (newIndex: number) => {
    speechService.stop();
    setCurrentChunkIndex(newIndex);
    const progress = Math.round(((newIndex + 1) / activeChunks.length) * 100);
    api.updateProgress(article.id, progress, newIndex);
  };

  const handleNextChunk = () => {
    if (currentChunkIndex < activeChunks.length - 1) {
      handleChunkChange(currentChunkIndex + 1);
    } else {
      handleFinishArticle();
    }
  };

  const handlePrevChunk = () => {
    if (currentChunkIndex > 0) {
      handleChunkChange(currentChunkIndex - 1);
    }
  };

  const handleFinishArticle = () => {
    setIsCompleted(true);
    api.updateProgress(article.id, 100, activeChunks.length - 1, true);
    setShowCompletionModal(true);
    confetti({
      particleCount: 100,
      spread: 80,
      origin: { y: 0.5 }
    });
  };

  // Keyboard shortcut listener for Esc (exit Zen mode) and '?'
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName)) return;

      if (e.key === 'Escape' && settings.focus_mode) {
        onUpdateSettings({ focus_mode: false });
      } else if (e.key === '?') {
        setShowShortcutsModal(prev => !prev);
      }
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [settings.focus_mode, onUpdateSettings]);

  const currentChunk = activeChunks[currentChunkIndex] || activeChunks[0];

  // ---------------- ZEN / PURE FOCUS MODE (PART C) ----------------
  if (settings.focus_mode) {
    return (
      <div className="w-full min-h-screen bg-[#F4F0E8] dark:bg-[#121212] p-4 sm:p-8 flex flex-col justify-between select-text animate-in fade-in duration-150 relative">
        {/* Assistive Focus Ruler Overlay */}
        {settings.focus_ruler && rulerTop !== null && (
          <div
            className="focus-ruler-overlay"
            style={{ top: `${rulerTop}px` }}
            aria-hidden="true"
          />
        )}

        {/* Minimal Zen Top Bar */}
        <div className="max-w-4xl w-full mx-auto flex items-center justify-between border-b-2 border-[#151515] pb-3 mb-6 select-none">
          <div className="flex items-center gap-2">
            <span className="bg-[#151515] text-[#D7FF38] font-mono font-black text-xs px-2 py-0.5 border border-black">
              ZEN FOCUS MODE
            </span>
            <span className="font-mono text-xs font-bold text-gray-600 dark:text-gray-300">
              Chunk {currentChunkIndex + 1} of {activeChunks.length}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => onUpdateSettings({ bionic_reading: !settings.bionic_reading })}
              className={`px-2 py-1 text-xs font-mono font-bold border border-[#151515] ${
                settings.bionic_reading ? 'bg-[#D7FF38]' : 'bg-white'
              }`}
            >
              Bionic: {settings.bionic_reading ? 'ON' : 'OFF'}
            </button>
            <button
              onClick={() => onUpdateSettings({ focus_mode: false })}
              className="px-3 py-1 bg-white hover:bg-[#FF5E5B] hover:text-white border-2 border-[#151515] text-xs font-black uppercase shadow-[2px_2px_0px_#151515] transition-all"
            >
              EXIT FOCUS (ESC)
            </button>
          </div>
        </div>

        {/* Centered Zen Chunk Card */}
        <div className="flex-1 flex flex-col justify-center">
          <ChunkViewer
            chunk={currentChunk}
            chunkIndex={currentChunkIndex}
            totalChunks={activeChunks.length}
            settings={settings}
            highlights={article.highlights}
            onNext={handleNextChunk}
            onPrev={handlePrevChunk}
            onJumpToChunk={handleChunkChange}
            onCompleteArticle={handleFinishArticle}
            isArticleCompleted={isCompleted}
          />
        </div>

        <div className="text-center text-xs font-mono text-gray-500 pt-4 select-none">
          Use ← / → or J / K to navigate • Esc to exit Focus Mode
        </div>
      </div>
    );
  }

  // ---------------- STANDARD READING WORKSPACE ----------------
  return (
    <div className="w-full min-h-screen pb-16 px-3 sm:px-6 relative">
      {/* Assistive Focus Ruler Overlay */}
      {settings.focus_ruler && rulerTop !== null && (
        <div
          className="focus-ruler-overlay"
          style={{ top: `${rulerTop}px` }}
          aria-hidden="true"
        />
      )}
      <div className="max-w-4xl mx-auto pt-4 sm:pt-6">
        {/* Navigation Breadcrumb / Actions */}
        <div className="flex items-center justify-between mb-4">
          <button
            onClick={onBackToDashboard}
            className="flex items-center gap-1.5 text-xs font-black uppercase text-[#151515] dark:text-[#F4F0E8] hover:text-[#2455FF] transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>BACK TO DASHBOARD</span>
          </button>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowOriginalTextModal(true)}
              className="text-xs font-mono font-extrabold text-[#151515] dark:text-white bg-white dark:bg-[#1E1E1E] border-2 border-[#151515] px-2.5 py-1 shadow-[2px_2px_0px_#151515] hover:bg-[#D7FF38] hover:text-black flex items-center gap-1 transition-all"
              title="View full original article un-chunked"
            >
              <FileText className="w-3.5 h-3.5" />
              <span>ORIGINAL TEXT</span>
            </button>

            <button
              onClick={() => setShowShortcutsModal(true)}
              className="text-xs font-mono font-bold text-gray-500 hover:text-black dark:hover:text-white flex items-center gap-1"
            >
              <HelpCircle className="w-3.5 h-3.5" />
              <span>Shortcuts (?)</span>
            </button>
          </div>
        </div>

        {/* Article Header Card */}
        <div className="bg-white dark:bg-[#1E1E1E] border-3 sm:border-4 border-[#151515] dark:border-white shadow-[6px_6px_0px_#151515] p-5 sm:p-7 mb-4">
          <div className="flex flex-wrap items-center gap-2 mb-2.5">
            <span className="text-[11px] font-mono font-extrabold uppercase px-2 py-0.5 bg-[#FAF8F5] dark:bg-[#2A2A2A] border border-[#151515] text-[#2455FF] dark:text-[#D7FF38]">
              {article.domain || 'Source Document'}
            </span>
            <Badge variant="lime" size="sm">
              FLESCH {article.flesch_score || 65} ({article.cognitive_rating || 'Accessible'})
            </Badge>
            {articleDifficulty && (
              <button
                onClick={handleOpenArticleSHAP}
                className="flex items-center gap-1.5 px-2 py-0.5 bg-white dark:bg-[#1E1E1E] border-2 border-[#151515] text-[11px] font-black uppercase shadow-[2px_2px_0px_#151515] hover:bg-[#D7FF38] hover:text-[#151515] transition-all cursor-pointer"
                title="Inspect model-predicted cognitive difficulty and TreeExplainer SHAP values"
              >
                <Brain className="w-3.5 h-3.5 text-[#2455FF]" />
                <span>ML: {articleDifficulty}</span>
                <span className="text-[10px] font-mono text-gray-500 underline ml-0.5">SHAP</span>
              </button>
            )}
            {isCompleted && (
              <Badge variant="blue" size="sm">
                COMPLETED ✓
              </Badge>
            )}
          </div>

          <h1 className="text-xl sm:text-3xl font-black uppercase tracking-tight text-[#151515] dark:text-white leading-tight mb-3">
            {article.title}
          </h1>

          <div className="flex flex-wrap items-center gap-4 text-xs font-bold text-gray-600 dark:text-gray-400">
            <span>By {article.author || 'Author'}</span>
            <span>•</span>
            <span className="flex items-center gap-1 font-mono">
              <Clock className="w-3.5 h-3.5" />
              ~{article.reading_time_minutes} MIN READ
            </span>
            <span>•</span>
            <span className="flex items-center gap-1 font-mono">
              <Layers className="w-3.5 h-3.5" />
              {activeChunks.length} COGNITIVE CHUNKS
            </span>
            {article.source_url && (
              <a
                href={article.source_url}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1 hover:text-[#2455FF] underline text-[11px]"
              >
                <span>Original Link</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            )}
          </div>
        </div>

        {/* Adaptive Cognitive Reading Assistance Banner */}
        {(articleDifficulty === 'Hard' || articleDifficulty === 'Very Hard') && (
          <div className="bg-[#FFF9D2] dark:bg-[#2A2610] border-3 border-[#151515] p-3.5 mb-4 shadow-[4px_4px_0px_#151515] flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <span className="bg-[#FF5E5B] text-white font-mono font-black text-xs px-2 py-0.5 border border-black">
                ADAPTIVE ASSIST
              </span>
              <p className="text-xs font-bold text-gray-800 dark:text-gray-200">
                {articleDifficulty} complexity detected by ML model. Suggested: 50-word chunks & Bionic eye guidance.
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => {
                  onUpdateSettings({ chunk_size_words: 50, bionic_reading: true });
                }}
                className="px-2.5 py-1 bg-[#2455FF] text-white text-xs font-extrabold uppercase border-2 border-[#151515] shadow-[2px_2px_0px_#151515] hover:bg-[#1a3ecc] transition-all cursor-pointer"
              >
                Apply Recommended Settings
              </button>
            </div>
          </div>
        )}

        {/* Reading Controls Toolbar */}
        <ReadingControlsBar
          settings={settings}
          onUpdateSettings={onUpdateSettings}
          onOpenLearningTools={() => setShowLearningTools(true)}
          currentChunkText={settings.chunk_mode ? currentChunk?.text : (article.raw_content || currentChunk?.text)}
        />

        {/* Main Content Area: Chunk Mode vs Full Reader */}
        <div className="mt-4">
          {settings.chunk_mode ? (
            <ChunkViewer
              chunk={currentChunk}
              chunkIndex={currentChunkIndex}
              totalChunks={activeChunks.length}
              settings={settings}
              highlights={article.highlights}
              onNext={handleNextChunk}
              onPrev={handlePrevChunk}
              onJumpToChunk={handleChunkChange}
              onCompleteArticle={handleFinishArticle}
              onSwitchToFullReader={() => onUpdateSettings({ chunk_mode: false })}
              onToggleHighlights={() => onUpdateSettings({ enable_semantic_highlights: !settings.enable_semantic_highlights })}
              isArticleCompleted={isCompleted}
            />
          ) : (
            <FullReader
              article={{ ...article, chunks: activeChunks }}
              settings={settings}
              onCompleteArticle={handleFinishArticle}
              isArticleCompleted={isCompleted}
            />
          )}
        </div>
      </div>

      {/* Original Source Text Modal (Part B) */}
      <Modal
        isOpen={showOriginalTextModal}
        onClose={() => setShowOriginalTextModal(false)}
        title="Original Source Article Text"
        maxWidth="lg"
      >
        <div className="space-y-4 select-text">
          <div className="p-3 bg-[#FAF8F5] border-2 border-[#151515] flex justify-between items-center text-xs font-mono font-bold">
            <span>TOTAL WORDS: {article.word_count || article.raw_content?.split(/\s+/).length || 0}</span>
            <button
              onClick={() => setShowOriginalTextModal(false)}
              className="bg-[#D7FF38] border border-black px-2 py-0.5 uppercase hover:bg-[#cbf528]"
            >
              Back to Focus Chunks →
            </button>
          </div>
          <div className="p-4 bg-white border-2 border-[#151515] max-h-[60vh] overflow-y-auto space-y-4 font-serif text-sm leading-relaxed text-[#151515]">
            {(article.raw_content || '').split(/\n\n+/).map((p, idx) => (
              <p key={idx}>{p}</p>
            ))}
          </div>
        </div>
      </Modal>

      {/* Learning Tools Modal (AI Summary, Concepts, Quiz, Flashcards) */}
      <Modal
        isOpen={showLearningTools}
        onClose={() => setShowLearningTools(false)}
        title="AI Retention & Comprehension Suite"
        maxWidth="xl"
      >
        <LearningTools
          summary={article.summary}
          concepts={article.concepts}
          quiz={article.quiz}
          flashcards={article.flashcards}
          articleTitle={article.title}
          articleText={article.raw_content || article.chunks.map(c => c.text).join('\n\n')}
        />
      </Modal>

      {/* Completion Modal */}
      <Modal
        isOpen={showCompletionModal}
        onClose={() => setShowCompletionModal(false)}
        title="Article Completed! 🎉"
        maxWidth="md"
      >
        <div className="text-center space-y-5 select-none">
          <div className="w-16 h-16 bg-[#D7FF38] border-3 border-[#151515] shadow-[4px_4px_0px_#151515] mx-auto flex items-center justify-center">
            <Award className="w-8 h-8 text-[#151515]" />
          </div>

          <div>
            <h3 className="text-xl font-black uppercase text-[#151515]">
              Outstanding Focus!
            </h3>
            <p className="text-xs sm:text-sm font-semibold text-gray-700 mt-1">
              You read all {activeChunks.length} chunks of "{article.title}" without visual regression.
            </p>
          </div>

          <div className="p-4 bg-white border-2 border-[#151515] shadow-[3px_3px_0px_#151515] text-xs font-mono font-bold flex justify-around">
            <div>
              <span className="block text-gray-500">CHUNKS</span>
              <span className="text-lg text-[#2455FF]">{activeChunks.length}</span>
            </div>
            <div>
              <span className="block text-gray-500">TIME SAVED</span>
              <span className="text-lg text-[#2455FF]">~{Math.round(article.reading_time_minutes * 0.4)}m</span>
            </div>
            <div>
              <span className="block text-gray-500">COMPREHENSION</span>
              <span className="text-lg text-[#2455FF]">100%</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 pt-2">
            <Button
              onClick={() => {
                setShowCompletionModal(false);
                setShowLearningTools(true);
              }}
              variant="lime"
              size="md"
            >
              TAKE 3-Q QUIZ
            </Button>
            <Button
              onClick={() => {
                setShowCompletionModal(false);
                onBackToDashboard();
              }}
              variant="primary"
              size="md"
            >
              BACK TO DASHBOARD
            </Button>
          </div>
        </div>
      </Modal>

      {/* Keyboard Shortcuts Reference Modal */}
      <Modal
        isOpen={showShortcutsModal}
        onClose={() => setShowShortcutsModal(false)}
        title="Keyboard Navigation Shortcuts"
        maxWidth="sm"
      >
        <div className="space-y-2.5 font-mono text-xs">
          <div className="flex justify-between items-center p-2 bg-white border border-[#151515]">
            <span className="font-bold">Next Chunk</span>
            <span className="bg-[#D7FF38] border border-black px-2 py-0.5 font-bold">J or → or Space</span>
          </div>
          <div className="flex justify-between items-center p-2 bg-white border border-[#151515]">
            <span className="font-bold">Previous Chunk</span>
            <span className="bg-[#D7FF38] border border-black px-2 py-0.5 font-bold">K or ←</span>
          </div>
          <div className="flex justify-between items-center p-2 bg-white border border-[#151515]">
            <span className="font-bold">Toggle Zen Focus Mode</span>
            <span className="bg-[#D7FF38] border border-black px-2 py-0.5 font-bold">Esc</span>
          </div>
          <div className="flex justify-between items-center p-2 bg-white border border-[#151515]">
            <span className="font-bold">Toggle Shortcuts Cheat Sheet</span>
            <span className="bg-[#D7FF38] border border-black px-2 py-0.5 font-bold">?</span>
          </div>
        </div>
      </Modal>

      {/* Article-Level SHAP Feature Attribution Modal */}
      <SHAPExplanationModal
        isOpen={showArticleSHAPModal}
        onClose={() => setShowArticleSHAPModal(false)}
        explanation={articleSHAPData}
        isLoading={isArticleSHAPLoading}
        onTriggerSimplify={() => setShowLearningTools(true)}
        onSwitchToSmallChunks={() => onUpdateSettings({ chunk_size_words: 45 })}
      />
    </div>
  );
};

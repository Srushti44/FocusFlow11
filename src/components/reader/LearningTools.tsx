import React, { useState, useRef, useEffect } from 'react';
import { ArticleSummary, KeyConcept, QuizQuestion, Flashcard, AIMessage } from '../../types';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import confetti from 'canvas-confetti';
import { api } from '../../services/api';
import {
  FileText,
  Lightbulb,
  HelpCircle,
  Layers,
  CheckCircle,
  XCircle,
  RotateCcw,
  Sparkles,
  ArrowRight,
  ArrowLeft,
  Search,
  MessageSquare,
  Send,
  Loader2,
  Bot,
  User,
  AlertCircle,
} from 'lucide-react';

interface LearningToolsProps {
  summary?: ArticleSummary;
  concepts: KeyConcept[];
  quiz: QuizQuestion[];
  flashcards: Flashcard[];
  articleTitle: string;
  articleText?: string;
}

type ActiveTab = 'summary' | 'concepts' | 'quiz' | 'flashcards' | 'askai';

export const LearningTools: React.FC<LearningToolsProps> = ({
  summary,
  concepts,
  quiz,
  flashcards,
  articleTitle,
  articleText = '',
}) => {
  const [activeTab, setActiveTab] = useState<ActiveTab>('summary');

  // ── Quiz state ───────────────────────────────────────────────────────────────
  const [currentQuizIndex, setCurrentQuizIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, number>>({});
  const [quizScore, setQuizScore] = useState<number | null>(null);

  // ── Flashcards state ─────────────────────────────────────────────────────────
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [masteredCards, setMasteredCards] = useState<Set<string>>(new Set());

  // ── Concepts search state ────────────────────────────────────────────────────
  const [conceptFilter, setConceptFilter] = useState('');

  // ── Ask AI state ─────────────────────────────────────────────────────────────
  const [chatHistory, setChatHistory] = useState<AIMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [chatError, setChatError] = useState('');
  const chatEndRef = useRef<HTMLDivElement>(null);
  const chatInputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll chat to bottom on new messages
  useEffect(() => {
    if (activeTab === 'askai') {
      chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatHistory, activeTab]);

  // ── Quiz handlers ─────────────────────────────────────────────────────────────
  const handleSelectOption = (questionIndex: number, optionIndex: number) => {
    if (selectedAnswers[questionIndex] !== undefined) return;

    const newSelected = { ...selectedAnswers, [questionIndex]: optionIndex };
    setSelectedAnswers(newSelected);

    if (Object.keys(newSelected).length === quiz.length) {
      let score = 0;
      quiz.forEach((q, idx) => {
        if (newSelected[idx] === q.correct_answer_index) score += 1;
      });
      setQuizScore(score);
      if (score >= Math.ceil(quiz.length * 0.7)) {
        confetti({ particleCount: 80, spread: 70, origin: { y: 0.6 } });
      }
    }
  };

  const handleResetQuiz = () => {
    setSelectedAnswers({});
    setQuizScore(null);
    setCurrentQuizIndex(0);
  };

  // ── Flashcard handlers ────────────────────────────────────────────────────────
  const currentCard = flashcards[currentCardIndex];
  const handleNextCard = () => {
    setIsFlipped(false);
    setCurrentCardIndex((prev) => (prev + 1) % flashcards.length);
  };
  const handlePrevCard = () => {
    setIsFlipped(false);
    setCurrentCardIndex((prev) => (prev - 1 + flashcards.length) % flashcards.length);
  };
  const handleToggleMastered = (cardId: string) => {
    setMasteredCards((prev) => {
      const next = new Set(prev);
      if (next.has(cardId)) next.delete(cardId);
      else next.add(cardId);
      return next;
    });
  };

  const filteredConcepts = concepts.filter(
    (c) =>
      c.term.toLowerCase().includes(conceptFilter.toLowerCase()) ||
      c.definition.toLowerCase().includes(conceptFilter.toLowerCase())
  );

  // ── Ask AI handler ────────────────────────────────────────────────────────────
  const handleSendMessage = async () => {
    const trimmedInput = chatInput.trim();
    if (!trimmedInput || isChatLoading) return;

    setChatError('');
    const userMessage: AIMessage = { role: 'user', content: trimmedInput };
    const newHistory = [...chatHistory, userMessage];
    setChatHistory(newHistory);
    setChatInput('');
    setIsChatLoading(true);

    try {
      const contextText = articleText || concepts.map((c) => `${c.term}: ${c.definition}`).join('\n');
      const answer = await api.askAI(trimmedInput, contextText, articleTitle, chatHistory);
      const modelMessage: AIMessage = { role: 'model', content: answer };
      setChatHistory((prev) => [...prev, modelMessage]);
    } catch (err: any) {
      setChatError(err?.message || 'Failed to get a response. Please try again.');
    } finally {
      setIsChatLoading(false);
      setTimeout(() => chatInputRef.current?.focus(), 100);
    }
  };

  const handleChatKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // ── Suggested questions ───────────────────────────────────────────────────────
  const suggestedQuestions = [
    `What is the main argument of this article?`,
    `Summarise the key points in 3 bullets`,
    `What are the most important concepts I should remember?`,
    `Give me a real-world example related to this article`,
    `What questions could appear in an exam about this topic?`,
  ];

  // ── Render ────────────────────────────────────────────────────────────────────
  return (
    <div className="w-full">
      {/* ── Tab Switcher ─────────────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 mb-6">
        {/* Summary */}
        <button
          onClick={() => setActiveTab('summary')}
          className={`p-3 font-extrabold text-xs uppercase tracking-wide border-3 border-[#151515] flex items-center justify-center gap-1.5 transition-all ${
            activeTab === 'summary'
              ? 'bg-[#2455FF] text-white shadow-[4px_4px_0px_#151515]'
              : 'bg-white hover:bg-[#F4F0E8] text-[#151515]'
          }`}
        >
          <FileText className="w-3.5 h-3.5" />
          <span>Summary</span>
        </button>

        {/* Concepts */}
        <button
          onClick={() => setActiveTab('concepts')}
          className={`p-3 font-extrabold text-xs uppercase tracking-wide border-3 border-[#151515] flex items-center justify-center gap-1.5 transition-all ${
            activeTab === 'concepts'
              ? 'bg-[#D7FF38] text-[#151515] shadow-[4px_4px_0px_#151515]'
              : 'bg-white hover:bg-[#F4F0E8] text-[#151515]'
          }`}
        >
          <Lightbulb className="w-3.5 h-3.5" />
          <span>Concepts ({concepts.length})</span>
        </button>

        {/* Quiz */}
        <button
          onClick={() => setActiveTab('quiz')}
          className={`p-3 font-extrabold text-xs uppercase tracking-wide border-3 border-[#151515] flex items-center justify-center gap-1.5 transition-all ${
            activeTab === 'quiz'
              ? 'bg-[#FFA400] text-[#151515] shadow-[4px_4px_0px_#151515]'
              : 'bg-white hover:bg-[#F4F0E8] text-[#151515]'
          }`}
        >
          <HelpCircle className="w-3.5 h-3.5" />
          <span>Quiz ({quiz.length})</span>
        </button>

        {/* Flashcards */}
        <button
          onClick={() => setActiveTab('flashcards')}
          className={`p-3 font-extrabold text-xs uppercase tracking-wide border-3 border-[#151515] flex items-center justify-center gap-1.5 transition-all ${
            activeTab === 'flashcards'
              ? 'bg-[#151515] text-[#D7FF38] shadow-[4px_4px_0px_#2455FF]'
              : 'bg-white hover:bg-[#F4F0E8] text-[#151515]'
          }`}
        >
          <Layers className="w-3.5 h-3.5" />
          <span>Cards ({flashcards.length})</span>
        </button>

        {/* Ask AI */}
        <button
          onClick={() => setActiveTab('askai')}
          className={`p-3 font-extrabold text-xs uppercase tracking-wide border-3 border-[#151515] flex items-center justify-center gap-1.5 transition-all col-span-2 sm:col-span-1 ${
            activeTab === 'askai'
              ? 'bg-[#FF5E5B] text-white shadow-[4px_4px_0px_#151515]'
              : 'bg-white hover:bg-[#F4F0E8] text-[#151515]'
          }`}
        >
          <MessageSquare className="w-3.5 h-3.5" />
          <span>Ask AI</span>
        </button>
      </div>

      {/* ── 1. SUMMARY TAB ───────────────────────────────────────────────────── */}
      {activeTab === 'summary' && (
        <div className="space-y-6">
          {summary ? (
            <>
              {/* TLDR Banner */}
              <div className="bg-[#D7FF38] border-3 border-[#151515] shadow-[4px_4px_0px_#151515] p-5">
                <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2 text-xs font-black uppercase tracking-wider text-[#151515]">
                    <Sparkles className="w-4 h-4 text-[#2455FF]" />
                    <span>ONE-SENTENCE TL;DR</span>
                  </div>
                  <span
                    className={`text-[10px] font-mono font-extrabold uppercase px-2 py-0.5 border border-[#151515] ${
                      summary.is_ai_generated
                        ? 'bg-[#2455FF] text-white'
                        : 'bg-[#FFA400] text-[#151515]'
                    }`}
                  >
                    {summary.is_ai_generated
                      ? `AI • ${summary.provider?.toUpperCase() || 'GEMINI'}`
                      : 'LOCAL SIMPLIFIED FALLBACK'}
                  </span>
                </div>
                <p className="text-base sm:text-lg font-bold leading-snug text-[#151515]">
                  "{summary.tldr}"
                </p>
                {summary.fallback_notice && (
                  <p className="text-[11px] font-mono font-medium text-gray-700 mt-2 bg-white/70 p-1.5 border border-[#151515]">
                    ℹ️ {summary.fallback_notice}
                  </p>
                )}
              </div>

              {/* Detailed Plain-English Breakdown */}
              {summary.detailed_explanation && (
                <div className="bg-[#FAF8F5] dark:bg-[#222] border-3 border-[#151515] dark:border-white shadow-[4px_4px_0px_#151515] p-5">
                  <div className="flex items-center gap-2 mb-2 text-xs font-black uppercase text-[#2455FF] dark:text-[#D7FF38]">
                    <FileText className="w-4 h-4" />
                    <span>Detailed Plain-English Explanation</span>
                  </div>
                  <p className="text-sm font-semibold text-gray-800 dark:text-gray-200 leading-relaxed">
                    {summary.detailed_explanation}
                  </p>
                </div>
              )}

              {/* Key Takeaways */}
              <div className="bg-white dark:bg-[#1E1E1E] border-3 border-[#151515] dark:border-white shadow-[4px_4px_0px_#151515] p-5">
                <h4 className="font-extrabold text-sm uppercase tracking-wider text-[#151515] dark:text-white mb-4">
                  Key Takeaways
                </h4>
                <div className="space-y-3">
                  {summary.key_takeaways.map((item, idx) => (
                    <div key={idx} className="flex items-start gap-3">
                      <span className="w-6 h-6 rounded-none bg-[#2455FF] text-white font-mono font-bold text-xs flex items-center justify-center border-2 border-[#151515] flex-shrink-0 mt-0.5">
                        {idx + 1}
                      </span>
                      <p className="text-sm font-semibold text-gray-800 dark:text-gray-200 leading-relaxed">
                        {item}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Cognitive Section Outline */}
              {summary.cognitive_outline && summary.cognitive_outline.length > 0 && (
                <div className="bg-[#FAF8F5] dark:bg-[#252525] border-3 border-[#151515] dark:border-white shadow-[4px_4px_0px_#151515] p-5">
                  <h4 className="font-extrabold text-sm uppercase tracking-wider text-[#151515] dark:text-white mb-4">
                    Cognitive Section Outline
                  </h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {summary.cognitive_outline.map((sec, idx) => (
                      <div
                        key={idx}
                        className="bg-white dark:bg-[#1A1A1A] border-2 border-[#151515] p-3 shadow-[2px_2px_0px_#151515]"
                      >
                        <span className="text-[11px] font-mono font-extrabold uppercase text-[#2455FF] dark:text-[#D7FF38] block mb-1">
                          {sec.section}
                        </span>
                        <p className="text-xs font-semibold text-gray-700 dark:text-gray-300">
                          {sec.takeaway}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-12 border-3 border-dashed border-[#151515] bg-white">
              <Sparkles className="w-8 h-8 mx-auto mb-3 text-gray-400" />
              <p className="text-sm font-bold text-gray-600">
                No summary available yet.
              </p>
              <p className="text-xs font-medium text-gray-400 mt-1">
                Transform an article with text to generate AI summaries.
              </p>
            </div>
          )}
        </div>
      )}

      {/* ── 2. CONCEPTS TAB ─────────────────────────────────────────────────── */}
      {activeTab === 'concepts' && (
        <div className="space-y-4">
          {/* Search bar */}
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-3.5 text-gray-500" />
            <input
              type="text"
              placeholder="Search concepts or definitions..."
              value={conceptFilter}
              onChange={(e) => setConceptFilter(e.target.value)}
              className="w-full pl-9 pr-4 py-2.5 bg-white border-2 border-[#151515] shadow-[2px_2px_0px_#151515] text-xs font-bold focus:outline-none"
            />
          </div>

          {filteredConcepts.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {filteredConcepts.map((c) => (
                <div
                  key={c.id}
                  className="bg-white dark:bg-[#1E1E1E] border-3 border-[#151515] dark:border-white shadow-[4px_4px_0px_#151515] p-4 flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-extrabold text-sm uppercase text-[#2455FF] dark:text-[#D7FF38]">
                        {c.term}
                      </span>
                      <Badge variant="lime" size="sm">TERM</Badge>
                    </div>
                    <p className="text-xs font-semibold text-gray-800 dark:text-gray-200 leading-relaxed mb-3">
                      {c.definition}
                    </p>
                    {c.analogy && (
                      <div className="text-[11px] font-medium text-amber-900 dark:text-amber-200 bg-[#FFF9D2] dark:bg-[#332E12] p-2 border-l-2 border-[#FFA400] mb-3">
                        <strong className="text-amber-950 dark:text-amber-100">Analogy: </strong>
                        {c.analogy}
                      </div>
                    )}
                  </div>
                  {c.context && (
                    <div className="text-[11px] font-medium text-gray-500 dark:text-gray-400 bg-[#F4F0E8] dark:bg-[#2A2A2A] p-2 border-l-2 border-[#151515]">
                      <strong className="text-gray-700 dark:text-gray-300">Context: </strong>
                      {c.context}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 border-3 border-dashed border-[#151515] bg-white">
              <Lightbulb className="w-8 h-8 mx-auto mb-3 text-gray-400" />
              <p className="text-sm font-bold text-gray-600">
                {conceptFilter ? 'No concepts match your search.' : 'No concepts extracted yet.'}
              </p>
            </div>
          )}
        </div>
      )}

      {/* ── 3. QUIZ TAB ─────────────────────────────────────────────────────── */}
      {activeTab === 'quiz' && (
        <div className="space-y-6">
          {quiz && quiz.length > 0 ? (
            <>
              {(() => {
                const q = quiz[currentQuizIndex];
                const answered = selectedAnswers[currentQuizIndex] !== undefined;
                const chosenOption = selectedAnswers[currentQuizIndex];

                return (
                  <div className="bg-white dark:bg-[#1E1E1E] border-4 border-[#151515] dark:border-white shadow-[6px_6px_0px_#151515] p-6">
                    {/* Header */}
                    <div className="flex items-center justify-between mb-4 pb-3 border-b-2 border-[#151515]">
                      <Badge variant="blue">
                        QUESTION {currentQuizIndex + 1} OF {quiz.length}
                      </Badge>
                      {quizScore !== null && (
                        <span className="font-mono text-xs font-extrabold bg-[#D7FF38] border border-[#151515] px-2 py-0.5">
                          FINAL SCORE: {quizScore}/{quiz.length}
                        </span>
                      )}
                    </div>

                    {/* Question text */}
                    <h4 className="font-extrabold text-base sm:text-lg text-[#151515] dark:text-white leading-snug mb-5">
                      {q.question}
                    </h4>

                    {/* Options */}
                    <div className="space-y-3 mb-6">
                      {q.options.map((opt, optIdx) => {
                        const isSelected = chosenOption === optIdx;
                        const isCorrect = q.correct_answer_index === optIdx;

                        let optStyles =
                          'bg-[#FAF8F5] dark:bg-[#252525] hover:bg-[#F4F0E8] text-[#151515] dark:text-white';
                        if (answered) {
                          if (isCorrect) {
                            optStyles =
                              'bg-[#D7FF38] text-[#151515] border-2 border-[#151515] shadow-[2px_2px_0px_#151515]';
                          } else if (isSelected && !isCorrect) {
                            optStyles =
                              'bg-[#FF5E5B] text-white border-2 border-[#151515] shadow-[2px_2px_0px_#151515]';
                          }
                        }

                        return (
                          <button
                            key={optIdx}
                            disabled={answered}
                            onClick={() => handleSelectOption(currentQuizIndex, optIdx)}
                            className={`w-full text-left p-3.5 border-2 border-[#151515] font-semibold text-xs sm:text-sm flex items-center justify-between transition-all select-none ${optStyles}`}
                          >
                            <span className="flex items-center gap-2">
                              <span className="w-5 h-5 bg-[#151515] text-white font-mono text-xs flex items-center justify-center font-bold">
                                {String.fromCharCode(65 + optIdx)}
                              </span>
                              <span>{opt}</span>
                            </span>
                            {answered && isCorrect && (
                              <CheckCircle className="w-5 h-5 text-[#151515] flex-shrink-0" />
                            )}
                            {answered && isSelected && !isCorrect && (
                              <XCircle className="w-5 h-5 text-white flex-shrink-0" />
                            )}
                          </button>
                        );
                      })}
                    </div>

                    {/* Explanation */}
                    {answered && (
                      <div className="p-4 bg-[#F4F0E8] dark:bg-[#2B2B2B] border-2 border-[#151515] shadow-[2px_2px_0px_#151515]">
                        <strong className="block text-xs font-black uppercase tracking-wider text-[#2455FF] dark:text-[#D7FF38] mb-1">
                          {chosenOption === q.correct_answer_index ? '✓ Correct!' : 'Explanation:'}
                        </strong>
                        <p className="text-xs font-semibold text-gray-800 dark:text-gray-200">
                          {q.explanation}
                        </p>
                      </div>
                    )}

                    {/* Navigation */}
                    <div className="mt-6 flex items-center justify-between pt-4 border-t-2 border-[#151515]">
                      <Button
                        onClick={() => setCurrentQuizIndex((prev) => Math.max(0, prev - 1))}
                        disabled={currentQuizIndex === 0}
                        size="sm"
                        variant="ghost"
                        icon={<ArrowLeft className="w-4 h-4" />}
                      >
                        PREV
                      </Button>

                      {currentQuizIndex < quiz.length - 1 ? (
                        <Button
                          onClick={() => setCurrentQuizIndex((prev) => prev + 1)}
                          size="sm"
                          variant="secondary"
                          icon={<ArrowRight className="w-4 h-4" />}
                        >
                          NEXT QUESTION
                        </Button>
                      ) : (
                        <Button
                          onClick={handleResetQuiz}
                          size="sm"
                          variant="ghost"
                          icon={<RotateCcw className="w-4 h-4" />}
                        >
                          RESET
                        </Button>
                      )}
                    </div>
                  </div>
                );
              })()}
            </>
          ) : (
            <div className="text-center py-12 border-3 border-dashed border-[#151515] bg-white">
              <HelpCircle className="w-8 h-8 mx-auto mb-3 text-gray-400" />
              <p className="text-sm font-bold text-gray-600">
                No quiz questions generated yet.
              </p>
              <p className="text-xs font-medium text-gray-400 mt-1">
                Paste article text and transform it to generate a quiz.
              </p>
            </div>
          )}
        </div>
      )}

      {/* ── 4. FLASHCARDS TAB ───────────────────────────────────────────────── */}
      {activeTab === 'flashcards' && (
        <div className="space-y-6">
          {flashcards && flashcards.length > 0 ? (
            <div className="max-w-xl mx-auto flex flex-col items-center">
              {/* Mastery bar */}
              <div className="w-full flex items-center justify-between mb-3 text-xs font-extrabold uppercase">
                <span>Card {currentCardIndex + 1} of {flashcards.length}</span>
                <span className="bg-[#D7FF38] border-2 border-[#151515] px-2 py-0.5">
                  {masteredCards.size} / {flashcards.length} Mastered
                </span>
              </div>

              {/* Flip Card */}
              <div
                onClick={() => setIsFlipped(!isFlipped)}
                className="w-full min-h-[240px] bg-white dark:bg-[#1E1E1E] border-4 border-[#151515] dark:border-white shadow-[8px_8px_0px_#151515] p-6 sm:p-8 flex flex-col justify-between cursor-pointer select-none transition-all hover:translate-x-[1px] hover:translate-y-[1px]"
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <Badge variant={isFlipped ? 'lime' : 'blue'}>
                      {isFlipped ? 'ANSWER / INSIGHT' : 'CONCEPT / PROMPT'}
                    </Badge>
                    <span className="text-xs font-mono font-bold text-gray-500">
                      {isFlipped ? '↷ Click to see question' : '↷ Click to reveal answer'}
                    </span>
                  </div>

                  {!isFlipped ? (
                    <div className="py-6 text-center">
                      <p className="text-base sm:text-xl font-extrabold leading-snug text-[#151515] dark:text-white">
                        {currentCard.front}
                      </p>
                      <span className="inline-block mt-3 text-xs font-mono font-bold text-gray-500 uppercase bg-[#F4F0E8] dark:bg-[#2A2A2A] px-2.5 py-1 border border-[#151515]">
                        Tap to reveal
                      </span>
                    </div>
                  ) : (
                    <div className="py-3 text-left space-y-2">
                      <span className="text-[11px] font-mono font-bold text-gray-500 uppercase block">
                        Q: {currentCard.front}
                      </span>
                      <div className="p-3.5 bg-[#FAF8F5] dark:bg-[#252525] border-2 border-[#151515] text-xs sm:text-sm font-bold leading-relaxed text-[#151515] dark:text-white">
                        {currentCard.back}
                      </div>
                    </div>
                  )}
                </div>

                <div className="text-center text-[11px] font-mono font-bold text-gray-400 mt-2">
                  CATEGORY: {currentCard.category}
                </div>
              </div>

              {/* Actions */}
              <div className="w-full mt-6 grid grid-cols-2 gap-3">
                <Button
                  onClick={() => {
                    handleToggleMastered(currentCard.id);
                    handleNextCard();
                  }}
                  variant={masteredCards.has(currentCard.id) ? 'lime' : 'secondary'}
                  size="md"
                >
                  {masteredCards.has(currentCard.id) ? 'MASTERED ✓' : 'MARK AS MASTERED'}
                </Button>

                <Button
                  onClick={handleNextCard}
                  variant="primary"
                  size="md"
                  icon={<ArrowRight className="w-4 h-4" />}
                >
                  NEXT CARD
                </Button>
              </div>

              {/* Prev / Next controls */}
              <div className="mt-4 flex items-center gap-4">
                <button
                  onClick={handlePrevCard}
                  className="p-2 border-2 border-[#151515] bg-white hover:bg-[#D7FF38] shadow-[2px_2px_0px_#151515]"
                >
                  <ArrowLeft className="w-4 h-4" />
                </button>
                <span className="text-xs font-mono font-bold">
                  {currentCardIndex + 1} / {flashcards.length}
                </span>
                <button
                  onClick={handleNextCard}
                  className="p-2 border-2 border-[#151515] bg-white hover:bg-[#D7FF38] shadow-[2px_2px_0px_#151515]"
                >
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 border-3 border-dashed border-[#151515] bg-white">
              <Layers className="w-8 h-8 mx-auto mb-3 text-gray-400" />
              <p className="text-sm font-bold text-gray-600">No flashcards available yet.</p>
              <p className="text-xs font-medium text-gray-400 mt-1">
                Transform text to generate AI-powered flashcards.
              </p>
            </div>
          )}
        </div>
      )}

      {/* ── 5. ASK AI TAB ───────────────────────────────────────────────────── */}
      {activeTab === 'askai' && (
        <div className="flex flex-col" style={{ height: '520px' }}>
          {/* Chat header */}
          <div className="bg-[#FF5E5B] border-3 border-[#151515] shadow-[4px_4px_0px_#151515] p-3 mb-4 flex items-center gap-3">
            <div className="w-8 h-8 bg-white border-2 border-[#151515] flex items-center justify-center flex-shrink-0">
              <Bot className="w-4 h-4 text-[#FF5E5B]" />
            </div>
            <div>
              <p className="font-black text-xs uppercase text-white">
                FocusFlow AI • OpenRouter
              </p>
              <p className="text-[10px] font-bold text-white/80">
                Ask me anything about "{articleTitle}"
              </p>
            </div>
          </div>

          {/* Message area */}
          <div className="flex-1 overflow-y-auto space-y-4 px-1 pb-2 min-h-0">
            {chatHistory.length === 0 && (
              <div className="space-y-3">
                <p className="text-xs font-bold text-gray-500 uppercase tracking-wider text-center">
                  Suggested questions
                </p>
                {suggestedQuestions.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      setChatInput(q);
                      setTimeout(() => chatInputRef.current?.focus(), 50);
                    }}
                    className="w-full text-left p-3 bg-white border-2 border-[#151515] shadow-[2px_2px_0px_#151515] text-xs font-semibold text-[#151515] hover:bg-[#D7FF38] transition-all"
                  >
                    <span className="text-[#2455FF] font-black mr-1">→</span>
                    {q}
                  </button>
                ))}
              </div>
            )}

            {chatHistory.map((msg, idx) => (
              <div
                key={idx}
                className={`flex gap-2.5 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.role === 'model' && (
                  <div className="w-7 h-7 bg-[#FF5E5B] border-2 border-[#151515] flex items-center justify-center flex-shrink-0 mt-0.5">
                    <Bot className="w-3.5 h-3.5 text-white" />
                  </div>
                )}
                <div
                  className={`max-w-[85%] p-3 border-2 border-[#151515] shadow-[2px_2px_0px_#151515] text-xs font-semibold leading-relaxed whitespace-pre-wrap ${
                    msg.role === 'user'
                      ? 'bg-[#2455FF] text-white'
                      : 'bg-white dark:bg-[#1E1E1E] text-[#151515] dark:text-white'
                  }`}
                >
                  {msg.content}
                </div>
                {msg.role === 'user' && (
                  <div className="w-7 h-7 bg-[#2455FF] border-2 border-[#151515] flex items-center justify-center flex-shrink-0 mt-0.5">
                    <User className="w-3.5 h-3.5 text-white" />
                  </div>
                )}
              </div>
            ))}

            {/* Loading indicator */}
            {isChatLoading && (
              <div className="flex gap-2.5 justify-start">
                <div className="w-7 h-7 bg-[#FF5E5B] border-2 border-[#151515] flex items-center justify-center flex-shrink-0">
                  <Bot className="w-3.5 h-3.5 text-white" />
                </div>
                <div className="bg-white border-2 border-[#151515] shadow-[2px_2px_0px_#151515] p-3 flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin text-[#FF5E5B]" />
                  <span className="text-xs font-bold text-gray-500">Thinking...</span>
                </div>
              </div>
            )}

            {/* Error */}
            {chatError && (
              <div className="flex items-center gap-2 p-3 bg-[#FF5E5B]/10 border-2 border-[#FF5E5B] text-xs font-bold text-[#151515]">
                <AlertCircle className="w-4 h-4 text-[#FF5E5B] flex-shrink-0" />
                <span>{chatError}</span>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>

          {/* Input area */}
          <div className="border-t-3 border-[#151515] pt-3 mt-2">
            {chatHistory.length > 0 && (
              <button
                onClick={() => setChatHistory([])}
                className="text-[10px] font-black uppercase text-gray-400 hover:text-[#FF5E5B] mb-2 block"
              >
                ↺ Clear conversation
              </button>
            )}
            <div className="flex gap-2">
              <textarea
                ref={chatInputRef}
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={handleChatKeyDown}
                placeholder="Ask anything about this article... (Enter to send, Shift+Enter for new line)"
                rows={2}
                className="flex-1 p-2.5 bg-white border-2 border-[#151515] shadow-[2px_2px_0px_#151515] text-xs font-semibold focus:outline-none resize-none placeholder:text-gray-400"
                disabled={isChatLoading}
              />
              <button
                onClick={handleSendMessage}
                disabled={isChatLoading || !chatInput.trim()}
                className="px-4 bg-[#FF5E5B] border-2 border-[#151515] shadow-[3px_3px_0px_#151515] text-white flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[#e54f4c] transition-all active:translate-x-[1px] active:translate-y-[1px] active:shadow-none"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
            <p className="text-[10px] font-mono text-gray-400 mt-1.5">
              Powered by OpenRouter AI • Answers based on article content only
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

import React, { useState } from 'react';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Card } from '../components/ui/Card';
import { renderBionicText } from '../utils/bionic';
import {
  Zap,
  BookOpen,
  Chrome,
  Layers,
  Eye,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  Sliders,
  Volume2
} from 'lucide-react';

interface LandingViewProps {
  onStartDemo: () => void;
  onOpenTransformModal: () => void;
  onGoToDashboard: () => void;
  onGoToExtension: () => void;
}

export const LandingView: React.FC<LandingViewProps> = ({
  onStartDemo,
  onOpenTransformModal,
  onGoToDashboard,
  onGoToExtension,
}) => {
  const [beforeAfterMode, setBeforeAfterMode] = useState<'after' | 'before'>('after');
  const [demoBionic, setDemoBionic] = useState(true);

  return (
    <div className="w-full pb-16">
      {/* Hero Section */}
      <section className="relative overflow-hidden py-12 sm:py-20 border-b-4 border-[#151515] bg-[#F4F0E8] dark:bg-[#121212]">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <div className="flex flex-col items-center text-center">
            {/* Top Tag */}
            <div className="flex items-center gap-2 mb-6">
              <Badge variant="lime" size="md">
                COGNITIVE-ACCESSIBLE READING PLATFORM
              </Badge>
              <Badge variant="black" size="md">
                NEO-BRUTALIST MVP
              </Badge>
            </div>

            {/* Giant Brutalist Headline */}
            <h1 className="text-4xl sm:text-6xl md:text-7xl lg:text-8xl font-black uppercase tracking-tight text-[#151515] dark:text-white leading-[0.95] mb-6">
              LESS NOISE.<br />
              <span className="text-[#2455FF] dark:text-[#D7FF38] underline decoration-4 underline-offset-8">
                MORE FOCUS.
              </span>
            </h1>

            {/* Subtitle */}
            <p className="max-w-3xl text-base sm:text-xl font-bold text-gray-800 dark:text-gray-200 leading-relaxed mb-8">
              FocusFlow converts dense, ad-riddled digital articles into calm, cognitive-friendly reading experiences. Powered by atomic focus chunking, saccadic eye guidance, accessible typography, and instant AI recall tools.
            </p>

            {/* Hero CTAs */}
            <div className="flex flex-wrap items-center justify-center gap-3 sm:gap-4 mb-10">
              <Button
                onClick={onStartDemo}
                variant="primary"
                size="lg"
                icon={<BookOpen className="w-5 h-5" />}
              >
                TRY DEMO ARTICLE
              </Button>

              <Button
                onClick={onOpenTransformModal}
                variant="lime"
                size="lg"
                icon={<Zap className="w-5 h-5 text-[#151515]" />}
              >
                TRANSFORM AN ARTICLE
              </Button>

              <Button
                onClick={onGoToExtension}
                variant="secondary"
                size="lg"
                icon={<Chrome className="w-5 h-5 text-[#2455FF]" />}
              >
                CHROME EXTENSION
              </Button>
            </div>

            {/* Quick Benefits pills */}
            <div className="flex flex-wrap justify-center items-center gap-2 text-xs font-mono font-bold text-gray-700 dark:text-gray-300">
              <span className="flex items-center gap-1 bg-white dark:bg-[#222] border-2 border-[#151515] px-2.5 py-1">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#2455FF]" /> ZERO AD CLUTTER
              </span>
              <span className="flex items-center gap-1 bg-white dark:bg-[#222] border-2 border-[#151515] px-2.5 py-1">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#2455FF]" /> 60-90 WORD CHUNKS
              </span>
              <span className="flex items-center gap-1 bg-white dark:bg-[#222] border-2 border-[#151515] px-2.5 py-1">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#2455FF]" /> BIONIC EYE GUIDANCE
              </span>
              <span className="flex items-center gap-1 bg-white dark:bg-[#222] border-2 border-[#151515] px-2.5 py-1">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#2455FF]" /> OPENDYSLEXIC & LEXEND
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Interactive Before / After Preview Section */}
      <section className="py-12 sm:py-16 max-w-6xl mx-auto px-4 sm:px-6">
        <div className="text-center mb-8">
          <Badge variant="blue" size="sm" className="mb-2">INTERACTIVE DEMONSTRATION</Badge>
          <h2 className="text-2xl sm:text-4xl font-black uppercase text-[#151515] dark:text-white">
            See The Cognitive Difference
          </h2>
          <p className="text-xs sm:text-sm font-semibold text-gray-600 dark:text-gray-400 mt-1">
            Compare a standard chaotic web article against the calm, structured FocusFlow architecture.
          </p>

          {/* Toggle Button */}
          <div className="inline-flex mt-6 p-1 bg-white dark:bg-[#222] border-3 border-[#151515] shadow-[4px_4px_0px_#151515]">
            <button
              onClick={() => setBeforeAfterMode('before')}
              className={`px-4 py-2 font-black text-xs uppercase transition-all ${
                beforeAfterMode === 'before'
                  ? 'bg-[#FF5E5B] text-white shadow-[2px_2px_0px_#151515]'
                  : 'text-gray-600 dark:text-gray-300 hover:text-black'
              }`}
            >
              ⚠️ Before: The Cluttered Web
            </button>
            <button
              onClick={() => setBeforeAfterMode('after')}
              className={`px-4 py-2 font-black text-xs uppercase transition-all ${
                beforeAfterMode === 'after'
                  ? 'bg-[#D7FF38] text-[#151515] shadow-[2px_2px_0px_#151515]'
                  : 'text-gray-600 dark:text-gray-300 hover:text-black'
              }`}
            >
              ✨ After: FocusFlow Calm Reader
            </button>
          </div>
        </div>

        {/* The Comparison Box */}
        <div className="relative">
          {beforeAfterMode === 'before' ? (
            /* Messy Before View */
            <div className="border-4 border-[#151515] bg-[#EAEAEA] p-6 shadow-[8px_8px_0px_#151515] relative overflow-hidden">
              {/* Simulated Annoying Ads and Popups */}
              <div className="absolute top-2 right-2 bg-[#FF5E5B] text-white text-[10px] font-mono px-2 py-0.5 border border-black animate-pulse">
                🔥 FLASH SALE! 90% OFF CLICK NOW 🔥
              </div>
              <div className="mb-4 bg-yellow-200 border border-yellow-600 p-2 text-xs flex justify-between items-center">
                <span>🍪 We use 453 cookies and sell your attention metrics. Accept?</span>
                <button className="bg-blue-600 text-white px-2 py-0.5 text-[10px] font-bold">ACCEPT ALL</button>
              </div>

              <div className="flex gap-4">
                {/* Simulated Article with Tiny Unreadable Text & Sidebar */}
                <div className="w-2/3 bg-white p-4 border border-gray-400">
                  <h3 className="text-sm font-bold text-gray-700 mb-1">
                    Cognitive Load Theory and Digital Reading Fatigue (Sponsored Post)
                  </h3>
                  <p className="text-[10px] text-gray-500 mb-3">By Anonymous Contributor • 14 mins ago</p>
                  <p className="text-[11px] leading-[1.3] text-gray-600 mb-2 font-serif">
                    Cognitive load theory, originally established by educational psychologist John Sweller in the late 1980s, posits that our working memory has a strictly finite capacity. When human readers encounter modern digital articles filled with animated advertisements, multi-column navigation sidebars, and unbroken blocks of dense text, our cognitive architecture suffers from extraneous load.
                  </p>
                  <div className="my-2 p-2 bg-gray-100 border border-dashed border-gray-400 text-center text-[10px] font-bold text-gray-500">
                    [ADVERTISEMENT: DOWNLOAD NOW TO BOOST YOUR CPU PERFORMANCE]
                  </div>
                  <p className="text-[11px] leading-[1.3] text-gray-600 font-serif">
                    When extraneous load exceeds our working threshold, attention fractures. Neuroimaging studies confirm that the prefrontal cortex quickly tires when continuously filtering irrelevant stimuli. Readers begin to experience visual regression—unconsciously re-reading the same sentence three or four times...
                  </p>
                </div>

                {/* Simulated Clutter Sidebar */}
                <div className="w-1/3 space-y-2">
                  <div className="bg-red-100 p-2 border border-red-300 text-[10px] font-bold">
                    🚨 BREAKING: 10 Foods You Must Avoid Right Now!
                  </div>
                  <div className="bg-blue-100 p-2 border border-blue-300 text-[10px]">
                    Newsletter Signup: Enter Email Here
                  </div>
                  <div className="bg-gray-200 h-24 border border-gray-400 flex items-center justify-center text-[10px] text-gray-500 font-bold">
                    Animated Video Ad (Auto-playing)
                  </div>
                </div>
              </div>

              <div className="mt-4 p-3 bg-[#FF5E5B]/20 border-2 border-[#FF5E5B] text-xs font-bold text-[#151515]">
                ❌ Result: Directed attention fatigue, sentence regression, eye strain, high abandonment rate.
              </div>
            </div>
          ) : (
            /* Clean FocusFlow After View */
            <div className="border-4 border-[#151515] bg-[#FFFFFF] dark:bg-[#1E1E1E] p-6 sm:p-10 shadow-[8px_8px_0px_#151515]">
              {/* Header */}
              <div className="flex items-center justify-between border-b-3 border-[#151515] pb-3 mb-6">
                <div className="flex items-center gap-2">
                  <Badge variant="blue" size="md">CHUNK 1 OF 3</Badge>
                  <span className="text-xs font-mono font-bold text-gray-600 dark:text-gray-300">~22s read</span>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setDemoBionic(!demoBionic)}
                    className="text-xs font-mono font-extrabold bg-[#D7FF38] border-2 border-[#151515] px-2 py-0.5 shadow-[2px_2px_0px_#151515]"
                  >
                    BIONIC: {demoBionic ? 'ON' : 'OFF'}
                  </button>
                </div>
              </div>

              {/* Chunk Content */}
              <div className="font-lexend text-base sm:text-lg leading-relaxed text-[#151515] dark:text-[#F4F0E8] mb-6">
                {renderBionicText(
                  "Cognitive load theory, established by John Sweller, posits that working memory has a strictly finite capacity. When readers encounter modern articles filled with animated ads and dense text walls, our cognitive architecture suffers from extraneous load—mental effort wasted on poor presentation rather than ideas.",
                  demoBionic
                )}
              </div>

              {/* Anchor Takeaway */}
              <div className="p-4 bg-[#F4F0E8] dark:bg-[#2B2B2B] border-2 border-[#151515] shadow-[3px_3px_0px_#151515] mb-6">
                <span className="text-[11px] font-extrabold uppercase text-[#2455FF] dark:text-[#D7FF38] block mb-1">
                  💡 Cognitive Anchor
                </span>
                <p className="text-xs sm:text-sm font-semibold text-gray-800 dark:text-gray-200">
                  Extraneous cognitive load is caused by presentation clutter, exhausting working memory before comprehension occurs.
                </p>
              </div>

              <div className="flex items-center justify-between pt-4 border-t-2 border-[#151515]">
                <span className="text-xs font-mono font-bold text-gray-600">
                  Progress: 33% • Reading Pace: Optimal
                </span>
                <Button onClick={onStartDemo} variant="primary" size="sm" icon={<ArrowRight className="w-4 h-4" />}>
                  READ FULL DEMO ARTICLE
                </Button>
              </div>

              <div className="mt-4 p-3 bg-[#D7FF38] border-2 border-[#151515] text-xs font-bold text-[#151515]">
                ✓ Result: Zero visual noise, 40% faster retention, zero line-skipping, protected working memory.
              </div>
            </div>
          )}
        </div>
      </section>

      {/* 4 Superpowers Feature Grid */}
      <section className="py-12 bg-white dark:bg-[#151515] border-t-4 border-b-4 border-[#151515]">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <div className="text-center mb-10">
            <Badge variant="lime" size="sm" className="mb-2">ENGINEERED FOR ATTENTION</Badge>
            <h2 className="text-2xl sm:text-4xl font-black uppercase text-[#151515] dark:text-white">
              The Cognitive Toolkit
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-[#FAF8F5] dark:bg-[#1E1E1E] border-3 border-[#151515] dark:border-white shadow-[4px_4px_0px_#151515] p-5">
              <div className="w-10 h-10 bg-[#2455FF] text-white border-2 border-[#151515] flex items-center justify-center font-bold mb-3 shadow-[2px_2px_0px_#151515]">
                <Layers className="w-5 h-5" />
              </div>
              <h3 className="font-extrabold text-base uppercase mb-1 text-[#151515] dark:text-white">
                Atomic Focus Chunks
              </h3>
              <p className="text-xs font-semibold text-gray-700 dark:text-gray-300 leading-relaxed">
                Breaks long documents into 60 to 90 word units, matching working memory capacity and eliminating sensory overload.
              </p>
            </div>

            <div className="bg-[#FAF8F5] dark:bg-[#1E1E1E] border-3 border-[#151515] dark:border-white shadow-[4px_4px_0px_#151515] p-5">
              <div className="w-10 h-10 bg-[#D7FF38] text-[#151515] border-2 border-[#151515] flex items-center justify-center font-bold mb-3 shadow-[2px_2px_0px_#151515]">
                <span className="font-mono text-base font-black">Aa</span>
              </div>
              <h3 className="font-extrabold text-base uppercase mb-1 text-[#151515] dark:text-white">
                Saccadic Eye Guidance
              </h3>
              <p className="text-xs font-semibold text-gray-700 dark:text-gray-300 leading-relaxed">
                Bionic highlighting anchors the initial syllables of each word, letting your visual cortex glide smoothly across lines.
              </p>
            </div>

            <div className="bg-[#FAF8F5] dark:bg-[#1E1E1E] border-3 border-[#151515] dark:border-white shadow-[4px_4px_0px_#151515] p-5">
              <div className="w-10 h-10 bg-[#FF5E5B] text-white border-2 border-[#151515] flex items-center justify-center font-bold mb-3 shadow-[2px_2px_0px_#151515]">
                <Eye className="w-5 h-5" />
              </div>
              <h3 className="font-extrabold text-base uppercase mb-1 text-[#151515] dark:text-white">
                Focus Reading Ruler
              </h3>
              <p className="text-xs font-semibold text-gray-700 dark:text-gray-300 leading-relaxed">
                A tinted horizontal tracking bar that follows your gaze or cursor, preventing visual line jumping and regression.
              </p>
            </div>

            <div className="bg-[#FAF8F5] dark:bg-[#1E1E1E] border-3 border-[#151515] dark:border-white shadow-[4px_4px_0px_#151515] p-5">
              <div className="w-10 h-10 bg-[#FFA400] text-[#151515] border-2 border-[#151515] flex items-center justify-center font-bold mb-3 shadow-[2px_2px_0px_#151515]">
                <Sparkles className="w-5 h-5" />
              </div>
              <h3 className="font-extrabold text-base uppercase mb-1 text-[#151515] dark:text-white">
                AI Retention Suite
              </h3>
              <p className="text-xs font-semibold text-gray-700 dark:text-gray-300 leading-relaxed">
                Automated TL;DR summaries, key concept glossaries, interactive quizzes, and study flashcards to lock in learning.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Final Call to Action */}
      <section className="py-12 max-w-4xl mx-auto px-4 text-center">
        <div className="bg-[#D7FF38] border-4 border-[#151515] shadow-[8px_8px_0px_#151515] p-8 sm:p-12">
          <h2 className="text-3xl sm:text-5xl font-black uppercase tracking-tight text-[#151515] leading-none mb-4">
            RECLAIM YOUR READING BRAIN.
          </h2>
          <p className="text-sm sm:text-base font-bold text-gray-900 max-w-xl mx-auto mb-6">
            Join neurodiverse readers, researchers, and engineers who read 3x faster with 90% less cognitive exhaustion.
          </p>
          <div className="flex flex-wrap justify-center gap-3">
            <Button
              onClick={onOpenTransformModal}
              variant="primary"
              size="lg"
              icon={<Zap className="w-5 h-5" />}
            >
              TRANSFORM ARTICLE NOW
            </Button>
            <Button
              onClick={onGoToDashboard}
              variant="secondary"
              size="lg"
              icon={<BookOpen className="w-5 h-5" />}
            >
              VIEW DASHBOARD
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
};

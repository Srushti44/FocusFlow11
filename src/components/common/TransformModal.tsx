import React, { useState } from 'react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { api } from '../../services/api';
import { Article } from '../../types';
import { Link2, FileText, Loader2, Sparkles, AlertCircle } from 'lucide-react';

interface TransformModalProps {
  isOpen: boolean;
  onClose: () => void;
  onTransformed: (article: Article) => void;
}

export const TransformModal: React.FC<TransformModalProps> = ({
  isOpen,
  onClose,
  onTransformed,
}) => {
  const [mode, setMode] = useState<'url' | 'text'>('url');
  const [urlInput, setUrlInput] = useState('');
  const [textInput, setTextInput] = useState('');
  const [titleInput, setTitleInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [loadingStep, setLoadingStep] = useState(0);

  const loadingSteps = [
    'Stripping advertisements, banners & sensory clutter...',
    'Evaluating Flesch-Kincaid readability score...',
    'Calibrating into 60-90 word atomic focus chunks...',
    'Synthesizing TL;DR, key concepts & interactive quiz...'
  ];

  const handleTransform = async () => {
    setErrorMsg('');
    if (mode === 'url' && !urlInput.trim()) {
      setErrorMsg('Please enter a valid URL.');
      return;
    }
    if (mode === 'text' && !textInput.trim()) {
      setErrorMsg('Please paste article text to transform.');
      return;
    }

    setIsLoading(true);
    setLoadingStep(0);

    // Step cycle animation
    const interval = setInterval(() => {
      setLoadingStep(prev => (prev < loadingSteps.length - 1 ? prev + 1 : prev));
    }, 700);

    try {
      const payload = mode === 'url'
        ? { url: urlInput.trim() }
        : { text: textInput.trim(), title: titleInput.trim() || 'Custom Reading Session' };

      const article = await api.extractArticle(payload);
      clearInterval(interval);
      setIsLoading(false);
      onTransformed(article);
      onClose();
    } catch (err: any) {
      clearInterval(interval);
      setIsLoading(false);
      setErrorMsg(err.message || 'Failed to extract article. Try pasting text directly.');
    }
  };

  const handleLoadDemo = () => {
    setMode('text');
    setTitleInput('The Science of Working Memory & Visual Fatigue');
    setTextInput(`Working memory capacity is strictly bounded by human neuroanatomy. The classic psychological principle established by George Miller asserted that humans hold roughly seven pieces of information at once, but modern cognitive neuroscience shows that for complex text, the real limit is closer to three or four ideas.

When readers attempt to process long, unbroken blocks of screen text, their eyes jump erratically in regressions. Cognitive fatigue compounds as the brain expends excessive energy maintaining spatial tracking across wide paragraphs. 

By restructuring continuous prose into isolated focus units, readers maintain high comprehension without experiencing visual burn-out. Combining this with high-contrast neo-brutalist styling creates an environment of absolute visual clarity.`);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Transform Article into FocusFlow" maxWidth="lg">
      <div className="space-y-5">
        {/* Mode selector */}
        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={() => setMode('url')}
            className={`py-2.5 px-4 font-extrabold text-xs uppercase border-2 border-[#151515] flex items-center justify-center gap-2 transition-all ${
              mode === 'url'
                ? 'bg-[#2455FF] text-white shadow-[2px_2px_0px_#151515]'
                : 'bg-white hover:bg-[#F4F0E8] text-[#151515]'
            }`}
          >
            <Link2 className="w-4 h-4" />
            <span>From Web URL</span>
          </button>

          <button
            onClick={() => setMode('text')}
            className={`py-2.5 px-4 font-extrabold text-xs uppercase border-2 border-[#151515] flex items-center justify-center gap-2 transition-all ${
              mode === 'text'
                ? 'bg-[#2455FF] text-white shadow-[2px_2px_0px_#151515]'
                : 'bg-white hover:bg-[#F4F0E8] text-[#151515]'
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>Paste Raw Text</span>
          </button>
        </div>

        {/* Inputs */}
        {mode === 'url' ? (
          <div>
            <label className="block text-xs font-black uppercase mb-1.5 text-[#151515]">
              Article URL
            </label>
            <input
              type="url"
              placeholder="https://example.com/deep-dive-article"
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              className="w-full p-3 bg-white border-3 border-[#151515] shadow-[3px_3px_0px_#151515] text-sm font-semibold focus:outline-none"
            />
            <p className="text-[11px] font-medium text-gray-600 mt-1.5">
              FocusFlow strips out navigation, sidebars, popups, and formats the core text into focus chunks.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            <div>
              <label className="block text-xs font-black uppercase mb-1 text-[#151515]">
                Article Title (Optional)
              </label>
              <input
                type="text"
                placeholder="e.g. Cognitive Ergonomics & Digital Reading"
                value={titleInput}
                onChange={(e) => setTitleInput(e.target.value)}
                className="w-full p-2.5 bg-white border-2 border-[#151515] shadow-[2px_2px_0px_#151515] text-sm font-semibold focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-black uppercase mb-1 text-[#151515]">
                Article Text Content
              </label>
              <textarea
                rows={6}
                placeholder="Paste the dense paragraphs or article text here..."
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                className="w-full p-3 bg-white border-3 border-[#151515] shadow-[3px_3px_0px_#151515] text-sm font-medium focus:outline-none"
              />
            </div>
          </div>
        )}

        {/* Quick Demo Helper */}
        <div className="flex items-center justify-between text-xs bg-[#E6E1D5] p-2.5 border-2 border-[#151515]">
          <span className="font-bold text-gray-700">Want to test with sample text?</span>
          <button
            onClick={handleLoadDemo}
            className="text-[11px] font-black uppercase underline hover:text-[#2455FF]"
          >
            Insert Cognitive Sample
          </button>
        </div>

        {/* Error message */}
        {errorMsg && (
          <div className="p-3 bg-[#FF5E5B]/20 border-2 border-[#FF5E5B] text-xs font-bold text-[#151515] flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-[#FF5E5B] flex-shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Loading state animation */}
        {isLoading && (
          <div className="p-4 bg-[#D7FF38] border-3 border-[#151515] shadow-[4px_4px_0px_#151515] animate-pulse">
            <div className="flex items-center gap-2 font-black text-xs uppercase mb-1 text-[#151515]">
              <Loader2 className="w-4 h-4 animate-spin text-[#2455FF]" />
              <span>TRANSFORMING ARTICLE...</span>
            </div>
            <p className="text-xs font-bold text-[#151515]">
              {loadingSteps[loadingStep]}
            </p>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center justify-end gap-2 pt-2 border-t-2 border-[#151515]">
          <Button onClick={onClose} variant="ghost" size="md">
            CANCEL
          </Button>
          <Button
            onClick={handleTransform}
            disabled={isLoading}
            variant="primary"
            size="md"
            icon={<Sparkles className="w-4 h-4" />}
          >
            {isLoading ? 'PROCESSING...' : 'TRANSFORM NOW'}
          </Button>
        </div>
      </div>
    </Modal>
  );
};

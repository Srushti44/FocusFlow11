import React, { useState, useEffect } from 'react';
import { Article, UserSettings } from '../types';
import { ChunkViewer } from '../components/reader/ChunkViewer';
import { LearningTools } from '../components/reader/LearningTools';
import { Modal } from '../components/ui/Modal';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { api } from '../services/api';
import {
  Layers,
  Sparkles,
  BookOpen,
  ExternalLink,
  RefreshCw,
  Zap,
  ChevronLeft,
  ChevronRight,
  Eye,
  Type
} from 'lucide-react';

interface SidePanelViewProps {
  settings: UserSettings;
  onUpdateSettings: (newSettings: Partial<UserSettings>) => void;
  onOpenFullApp: () => void;
}

export const SidePanelView: React.FC<SidePanelViewProps> = ({
  settings,
  onUpdateSettings,
  onOpenFullApp,
}) => {
  const [currentArticle, setCurrentArticle] = useState<Article | null>(null);
  const [currentChunkIndex, setCurrentChunkIndex] = useState(0);
  const [showLearningTools, setShowLearningTools] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [scanMessage, setScanMessage] = useState<string>('');

  useEffect(() => {
    loadSidePanelContent();
  }, []);

  const loadSidePanelContent = async () => {
    setIsLoading(true);

    // 1. Check URL parameters
    const params = new URLSearchParams(window.location.search);
    const urlParam = params.get('url');
    if (urlParam) {
      try {
        const art = await api.extractArticle({ url: urlParam });
        setCurrentArticle(art);
        setCurrentChunkIndex(art.current_chunk_index || 0);
        setIsLoading(false);
        return;
      } catch (e) {
        console.warn('[SidePanel] URL extract failed, checking storage:', e);
      }
    }

    // 2. Check Chrome Extension storage
    if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
      chrome.storage.local.get(['focusflow_active_article', 'focusflow_pending_article'], async (res) => {
        const pending = res.focusflow_active_article || res.focusflow_pending_article;
        if (pending && (pending.raw_content || pending.source_url)) {
          try {
            const art = await api.extractArticle({
              url: pending.source_url,
              text: pending.raw_content,
              title: pending.title
            });
            setCurrentArticle(art);
            setCurrentChunkIndex(0);
            setIsLoading(false);
            return;
          } catch (e) {
            console.error('[SidePanel] Storage extract error:', e);
          }
        }
        fallbackToDatabase();
      });
      return;
    }

    fallbackToDatabase();
  };

  const fallbackToDatabase = async () => {
    try {
      const list = await api.getArticles();
      if (list.length > 0) {
        const full = await api.getArticle(list[0].id);
        if (full) {
          setCurrentArticle(full);
          setCurrentChunkIndex(full.current_chunk_index || 0);
        }
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  // Direct active tab scan from side panel
  const handleScanActiveTab = async () => {
    if (typeof chrome === 'undefined' || !chrome.tabs) {
      setScanMessage('Browser tab API not available in preview mode.');
      setTimeout(() => setScanMessage(''), 3000);
      return;
    }

    setScanMessage('Scanning active tab content...');
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab || !tab.id) {
        setScanMessage('Could not connect to active tab.');
        setTimeout(() => setScanMessage(''), 3000);
        return;
      }

      chrome.tabs.sendMessage(tab.id, { action: 'EXTRACT_CONTENT' }, async (response) => {
        if (chrome.runtime.lastError || !response || !response.supported) {
          setScanMessage('Could not extract article from this tab.');
          setTimeout(() => setScanMessage(''), 3000);
          return;
        }

        const art = await api.extractArticle({
          url: response.sourceUrl || tab.url,
          text: response.fullText,
          title: response.title
        });
        setCurrentArticle(art);
        setCurrentChunkIndex(0);
        setScanMessage('Article transformed successfully!');
        setTimeout(() => setScanMessage(''), 2500);
      });
    } catch (err: any) {
      setScanMessage('Scan error: ' + err.message);
      setTimeout(() => setScanMessage(''), 3000);
    }
  };

  if (isLoading) {
    return (
      <div className="w-full h-screen flex flex-col items-center justify-center p-6 text-center bg-[#F4F0E8] select-none">
        <RefreshCw className="w-8 h-8 animate-spin text-[#2455FF] mb-3" />
        <h3 className="font-black text-sm uppercase">Loading Side Panel Reader...</h3>
        <p className="text-xs text-gray-600 mt-1">Connecting to active reading session</p>
      </div>
    );
  }

  if (!currentArticle) {
    return (
      <div className="w-full min-h-screen bg-[#F4F0E8] p-4 flex flex-col items-center justify-center text-center select-none">
        <div className="bg-white border-3 border-[#151515] p-5 shadow-[4px_4px_0px_#151515] max-w-sm">
          <Badge variant="blue" size="sm" className="mb-2">FOCUSFLOW SIDE PANEL</Badge>
          <h3 className="font-black text-sm uppercase mb-2">No Article Loaded</h3>
          <p className="text-xs text-gray-600 mb-4">
            Activate FocusFlow on any web article to read alongside your page.
          </p>
          <Button
            onClick={handleScanActiveTab}
            variant="lime"
            size="sm"
            fullWidth
            icon={<Zap className="w-4 h-4 text-[#151515]" />}
          >
            SCAN ACTIVE TAB NOW
          </Button>
          <Button
            onClick={onOpenFullApp}
            variant="secondary"
            size="sm"
            fullWidth
            className="mt-2"
          >
            Open Full Dashboard
          </Button>
          {scanMessage && (
            <p className="text-[11px] font-mono font-bold text-[#2455FF] mt-2">{scanMessage}</p>
          )}
        </div>
      </div>
    );
  }

  const currentChunk = currentArticle.chunks[currentChunkIndex] || currentArticle.chunks[0];

  return (
    <div className="w-full min-h-screen bg-[#F4F0E8] dark:bg-[#121212] p-3 text-[#151515] dark:text-[#F4F0E8] flex flex-col justify-between select-text">
      <div>
        {/* Top Header */}
        <div className="flex items-center justify-between border-b-3 border-[#151515] pb-2 mb-3">
          <div className="flex items-center gap-1.5 truncate max-w-[200px]">
            <span className="font-black text-xs uppercase bg-[#D7FF38] border border-[#151515] px-1.5 py-0.5">
              PANEL
            </span>
            <span className="font-black text-xs tracking-tight truncate" title={currentArticle.title}>
              {currentArticle.title}
            </span>
          </div>

          <div className="flex items-center gap-1 flex-shrink-0">
            <button
              onClick={handleScanActiveTab}
              className="p-1 border border-[#151515] bg-white hover:bg-[#D7FF38] text-[10px] font-mono font-bold shadow-[1px_1px_0px_#151515]"
              title="Rescan active tab"
            >
              SCAN
            </button>
            <button
              onClick={onOpenFullApp}
              className="text-[11px] font-mono font-black text-[#2455FF] hover:underline flex items-center gap-1 ml-1"
            >
              <span>FULL APP</span>
              <ExternalLink className="w-3 h-3" />
            </button>
          </div>
        </div>

        {scanMessage && (
          <div className="p-2 mb-2 bg-[#D7FF38] border-2 border-[#151515] text-[11px] font-bold text-center">
            {scanMessage}
          </div>
        )}

        {/* Compact Quick Controls Bar */}
        <div className="mb-3 flex items-center justify-between gap-1 select-none">
          <div className="flex items-center gap-1">
            <button
              onClick={() => onUpdateSettings({ bionic_reading: !settings.bionic_reading })}
              className={`px-2 py-1 text-[11px] font-black border border-[#151515] ${
                settings.bionic_reading ? 'bg-[#D7FF38]' : 'bg-white'
              }`}
              title="Toggle bionic eye guidance"
            >
              Bionic: {settings.bionic_reading ? 'ON' : 'OFF'}
            </button>

            <button
              onClick={() => onUpdateSettings({ enable_semantic_highlights: !settings.enable_semantic_highlights })}
              className={`px-2 py-1 text-[11px] font-black border border-[#151515] ${
                settings.enable_semantic_highlights ? 'bg-[#2455FF] text-white' : 'bg-white text-[#151515]'
              }`}
              title="Toggle semantic highlights"
            >
              Highlights: {settings.enable_semantic_highlights ? 'ON' : 'OFF'}
            </button>
          </div>

          <Button
            onClick={() => setShowLearningTools(true)}
            variant="lime"
            size="sm"
            icon={<Sparkles className="w-3 h-3" />}
          >
            AI TOOLS
          </Button>
        </div>

        {/* Chunk Viewer inside Side Panel */}
        <ChunkViewer
          chunk={currentChunk}
          chunkIndex={currentChunkIndex}
          totalChunks={currentArticle.chunks.length}
          settings={settings}
          highlights={currentArticle.highlights}
          onNext={() => {
            if (currentChunkIndex < currentArticle.chunks.length - 1) {
              const next = currentChunkIndex + 1;
              setCurrentChunkIndex(next);
              api.updateProgress(currentArticle.id, Math.round(((next + 1) / currentArticle.chunks.length) * 100), next);
            }
          }}
          onPrev={() => {
            if (currentChunkIndex > 0) {
              const prev = currentChunkIndex - 1;
              setCurrentChunkIndex(prev);
              api.updateProgress(currentArticle.id, Math.round(((prev + 1) / currentArticle.chunks.length) * 100), prev);
            }
          }}
          onJumpToChunk={(idx) => {
            setCurrentChunkIndex(idx);
            api.updateProgress(currentArticle.id, Math.round(((idx + 1) / currentArticle.chunks.length) * 100), idx);
          }}
          onToggleHighlights={() => onUpdateSettings({ enable_semantic_highlights: !settings.enable_semantic_highlights })}
        />
      </div>

      {/* AI Tools Modal */}
      <Modal
        isOpen={showLearningTools}
        onClose={() => setShowLearningTools(false)}
        title="Side Panel AI Retention Tools"
        maxWidth="md"
      >
        <LearningTools
          summary={currentArticle.summary}
          concepts={currentArticle.concepts}
          quiz={currentArticle.quiz}
          flashcards={currentArticle.flashcards}
          articleTitle={currentArticle.title}
        />
      </Modal>

      <div className="text-center text-[10px] font-mono text-gray-500 pt-3 border-t border-gray-300 mt-4 select-none">
        FocusFlow Chrome Side Panel API • v1.2.0
      </div>
    </div>
  );
};

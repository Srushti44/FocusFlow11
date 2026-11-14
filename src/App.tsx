import React, { useState, useEffect } from 'react';
import { ActiveTab, Article, ReadingStats } from './types';
import { useSettings } from './context/SettingsContext';
import { Navbar } from './components/Navbar';
import { LandingView } from './views/LandingView';
import { ReaderView } from './views/ReaderView';
import { DashboardView } from './views/DashboardView';
import { SettingsView } from './views/SettingsView';
import { ExtensionPopupView } from './views/ExtensionPopupView';
import { SidePanelView } from './views/SidePanelView';
import { MLOpsDashboardView } from './views/MLOpsDashboardView';
import { TransformModal } from './components/common/TransformModal';
import { OnboardingModal } from './components/common/OnboardingModal';
import { api } from './services/api';

export function App() {
  const { settings, updateSettings, resetSettings } = useSettings();

  const [activeTab, setActiveTab] = useState<ActiveTab>('landing');
  const [currentArticle, setCurrentArticle] = useState<Article | null>(null);
  const [practiceTab, setPracticeTab] = useState<'quiz' | 'flashcards' | null>(null);
  const [stats, setStats] = useState<ReadingStats | undefined>(undefined);

  // Modals
  const [isTransformOpen, setIsTransformOpen] = useState(false);
  const [isOnboardingOpen, setIsOnboardingOpen] = useState(false);

  // Initial load: parse URL params and check onboarding
  useEffect(() => {
    // Check onboarding
    const onboarded = localStorage.getItem('focusflow_onboarded');
    if (!onboarded) {
      setIsOnboardingOpen(true);
    }

    // Parse query params
    const params = new URLSearchParams(window.location.search);
    const viewParam = params.get('view');
    const urlParam = params.get('url');
    const pasteParam = params.get('paste');
    const articleIdParam = params.get('id');

    if (viewParam === 'sidepanel') {
      setActiveTab('sidepanel');
    } else if (viewParam === 'popup' || viewParam === 'extension-popup') {
      setActiveTab('extension-popup');
    } else if (viewParam === 'settings') {
      setActiveTab('settings');
    } else if (viewParam === 'dashboard') {
      setActiveTab('dashboard');
    } else if (viewParam === 'reader') {
      setActiveTab('reader');
    } else if (viewParam === 'mlops') {
      setActiveTab('mlops');
    }

    // Auto-extract if URL or paste is passed via query params (e.g. from extension background worker)
    if (urlParam) {
      api.extractArticle({ url: urlParam }).then((art) => {
        setCurrentArticle(art);
        setActiveTab('reader');
      }).catch((err) => {
        console.error('[FocusFlow] URL extract error:', err);
        setActiveTab('dashboard');
      });
    } else if (pasteParam) {
      api.extractArticle({ text: pasteParam, title: 'Extension Selection' }).then((art) => {
        setCurrentArticle(art);
        setActiveTab('reader');
      }).catch(() => {
        setActiveTab('dashboard');
      });
    } else if (articleIdParam) {
      api.getArticle(articleIdParam).then((art) => {
        if (art) {
          setCurrentArticle(art);
          setActiveTab('reader');
        }
      });
    } else {
      // Check last read article in local storage
      const lastId = localStorage.getItem('focusflow_last_article_id');
      if (lastId) {
        api.getArticle(lastId).then((art) => {
          if (art) {
            setCurrentArticle(art);
          }
        });
      }
    }

    // Fetch initial stats
    refreshStats();
  }, []);

  // Persist last active article
  useEffect(() => {
    if (currentArticle?.id) {
      localStorage.setItem('focusflow_last_article_id', currentArticle.id);
    }
  }, [currentArticle?.id]);

  const refreshStats = () => {
    api.getStats().then(setStats);
  };

  // Load default or last article if reader is selected but no article chosen yet
  const ensureArticleLoaded = async () => {
    if (!currentArticle) {
      const lastId = localStorage.getItem('focusflow_last_article_id');
      if (lastId) {
        const full = await api.getArticle(lastId);
        if (full) {
          setCurrentArticle(full);
          return;
        }
      }
      const articles = await api.getArticles();
      if (articles.length > 0) {
        const full = await api.getArticle(articles[0].id);
        setCurrentArticle(full);
      }
    }
  };

  const handleSelectTab = (tab: ActiveTab) => {
    if (tab === 'reader') {
      ensureArticleLoaded();
    }
    setActiveTab(tab);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleStartDemo = async () => {
    const articles = await api.getArticles();
    if (articles.length > 0) {
      const full = await api.getArticle(articles[0].id);
      setCurrentArticle(full);
    }
    setActiveTab('reader');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSelectArticle = async (articleId: string, initialPracticeTab?: 'quiz' | 'flashcards') => {
    const full = await api.getArticle(articleId);
    if (full) {
      setCurrentArticle(full);
      setPracticeTab(initialPracticeTab || null);
      setActiveTab('reader');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleTransformed = (article: Article) => {
    setCurrentArticle(article);
    setActiveTab('reader');
    refreshStats();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // If view is sidepanel, render dedicated side panel view directly
  if (activeTab === 'sidepanel') {
    return (
      <SidePanelView
        settings={settings}
        onUpdateSettings={updateSettings}
        onOpenFullApp={() => {
          setActiveTab('reader');
        }}
      />
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-[#F4F0E8] dark:bg-[#121212] text-[#151515] dark:text-[#F4F0E8] font-sans selection:bg-[#D7FF38] selection:text-[#151515]">
      {/* Neo-brutalist Global Navbar */}
      <Navbar
        activeTab={activeTab}
        onSelectTab={handleSelectTab}
        onOpenTransformModal={() => setIsTransformOpen(true)}
        stats={stats}
      />

      {/* Main Screen Views */}
      <main className="flex-1">
        {activeTab === 'landing' && (
          <LandingView
            onStartDemo={handleStartDemo}
            onOpenTransformModal={() => setIsTransformOpen(true)}
            onGoToDashboard={() => handleSelectTab('dashboard')}
            onGoToExtension={() => handleSelectTab('extension-popup')}
          />
        )}

        {activeTab === 'reader' && (
          currentArticle ? (
            <ReaderView
              article={currentArticle}
              settings={settings}
              onUpdateSettings={updateSettings}
              onBackToDashboard={() => handleSelectTab('dashboard')}
              initialPracticeTab={practiceTab}
            />
          ) : (
            <div className="w-full max-w-xl mx-auto py-20 px-4 text-center select-none">
              <div className="p-8 bg-white border-4 border-[#151515] shadow-[8px_8px_0px_#151515]">
                <h3 className="text-xl font-black uppercase mb-3">No Article Loaded</h3>
                <p className="text-xs font-semibold text-gray-600 mb-6">
                  Select an article from your library or transform a new URL.
                </p>
                <div className="flex justify-center gap-3">
                  <button
                    onClick={handleStartDemo}
                    className="px-4 py-2 bg-[#2455FF] text-white border-2 border-[#151515] font-extrabold text-xs uppercase shadow-[2px_2px_0px_#151515]"
                  >
                    Load Sample Article
                  </button>
                  <button
                    onClick={() => setIsTransformOpen(true)}
                    className="px-4 py-2 bg-[#D7FF38] text-[#151515] border-2 border-[#151515] font-extrabold text-xs uppercase shadow-[2px_2px_0px_#151515]"
                  >
                    Transform URL
                  </button>
                </div>
              </div>
            </div>
          )
        )}

        {activeTab === 'dashboard' && (
          <DashboardView
            onSelectArticle={handleSelectArticle}
            onOpenTransformModal={() => setIsTransformOpen(true)}
            stats={stats}
            onRefreshStats={refreshStats}
          />
        )}

        {activeTab === 'mlops' && (
          <MLOpsDashboardView />
        )}

        {activeTab === 'settings' && (
          <SettingsView
            settings={settings}
            onUpdateSettings={updateSettings}
            onResetSettings={resetSettings}
          />
        )}

        {activeTab === 'extension-popup' && (
          <ExtensionPopupView
            onTransformSample={(url, title) => {
              api.extractArticle({ url, title }).then(handleTransformed);
            }}
            onOpenSidePanel={() => setActiveTab('sidepanel')}
          />
        )}
      </main>

      {/* Global Modals */}
      <TransformModal
        isOpen={isTransformOpen}
        onClose={() => setIsTransformOpen(false)}
        onTransformed={handleTransformed}
      />

      <OnboardingModal
        isOpen={isOnboardingOpen}
        onClose={() => setIsOnboardingOpen(false)}
      />

      {/* Minimal Neo-brutalist Footer */}
      <footer className="border-t-4 border-[#151515] bg-[#FFFFFF] dark:bg-[#151515] py-6 px-4">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-mono font-bold text-gray-600 dark:text-gray-400">
          <div className="flex items-center gap-2">
            <span className="w-4 h-4 bg-[#D7FF38] border border-[#151515] inline-block" />
            <span>FOCUSFLOW COGNITIVE PLATFORM • NEO-BRUTALIST MVP</span>
          </div>
          <div className="flex items-center gap-4">
            <button onClick={() => setIsOnboardingOpen(true)} className="hover:underline">
              How It Works
            </button>
            <button onClick={() => setActiveTab('settings')} className="hover:underline">
              Preferences
            </button>
            <button onClick={() => setActiveTab('extension-popup')} className="hover:underline">
              Extension
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;

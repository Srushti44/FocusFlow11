import React, { useState, useEffect } from 'react';
import { ArticleListItem, ReadingStats } from '../types';
import { ArticleCard } from '../components/dashboard/ArticleCard';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Card } from '../components/ui/Card';
import { api } from '../services/api';
import {
  LayoutDashboard,
  Search,
  Filter,
  Flame,
  Clock,
  Layers,
  CheckCircle2,
  Zap,
  Plus,
  BookOpen
} from 'lucide-react';

interface DashboardViewProps {
  onSelectArticle: (articleId: string, initialPracticeTab?: 'quiz' | 'flashcards') => void;
  onOpenTransformModal: () => void;
  stats?: ReadingStats;
  onRefreshStats?: () => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  onSelectArticle,
  onOpenTransformModal,
  stats,
  onRefreshStats
}) => {
  const [articles, setArticles] = useState<ArticleListItem[]>([]);
  const [filter, setFilter] = useState<'all' | 'progress' | 'completed' | 'favorites'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  const fetchArticles = async () => {
    setIsLoading(true);
    try {
      const data = await api.getArticles();
      setArticles(data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchArticles();
  }, []);

  const handleToggleFavorite = async (id: string) => {
    await api.toggleFavorite(id);
    setArticles(prev => prev.map(a => a.id === id ? { ...a, is_favorite: !a.is_favorite } : a));
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Delete this article from FocusFlow?')) {
      await api.deleteArticle(id);
      setArticles(prev => prev.filter(a => a.id !== id));
      if (onRefreshStats) onRefreshStats();
    }
  };

  const filteredArticles = articles.filter(a => {
    if (filter === 'completed' && !a.is_completed) return false;
    if (filter === 'progress' && (a.is_completed || a.progress_percent === 0)) return false;
    if (filter === 'favorites' && !a.is_favorite) return false;

    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      const matchTitle = a.title.toLowerCase().includes(query);
      const matchAuthor = (a.author || '').toLowerCase().includes(query);
      const matchDomain = (a.domain || '').toLowerCase().includes(query);
      return matchTitle || matchAuthor || matchDomain;
    }
    return true;
  });

  return (
    <div className="w-full min-h-screen pb-16 px-4 sm:px-6">
      <div className="max-w-6xl mx-auto pt-6">
        {/* Top Header & Metrics Bar */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Badge variant="blue">COGNITIVE DASHBOARD</Badge>
              <span className="text-xs font-mono font-bold text-gray-500">v1.0.0</span>
            </div>
            <h1 className="text-2xl sm:text-4xl font-black uppercase text-[#151515] dark:text-white tracking-tight">
              Your Reading Library
            </h1>
          </div>

          <Button
            onClick={onOpenTransformModal}
            variant="lime"
            size="md"
            icon={<Zap className="w-4 h-4 text-[#151515]" />}
          >
            TRANSFORM NEW ARTICLE
          </Button>
        </div>

        {/* 4 Stats Metric Cards */}
        {stats && (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-8">
            <div className="bg-white dark:bg-[#1E1E1E] border-3 border-[#151515] dark:border-white shadow-[4px_4px_0px_#151515] p-4 flex items-center justify-between">
              <div>
                <span className="text-[11px] font-mono font-bold text-gray-500 uppercase block">
                  Transformed
                </span>
                <span className="text-2xl font-black text-[#151515] dark:text-white">
                  {articles.length}
                </span>
              </div>
              <div className="w-9 h-9 bg-[#2455FF] text-white border-2 border-[#151515] flex items-center justify-center font-bold">
                <BookOpen className="w-4 h-4" />
              </div>
            </div>

            <div className="bg-white dark:bg-[#1E1E1E] border-3 border-[#151515] dark:border-white shadow-[4px_4px_0px_#151515] p-4 flex items-center justify-between">
              <div>
                <span className="text-[11px] font-mono font-bold text-gray-500 uppercase block">
                  Completed
                </span>
                <span className="text-2xl font-black text-[#151515] dark:text-white">
                  {articles.filter(a => a.is_completed).length}
                </span>
              </div>
              <div className="w-9 h-9 bg-[#D7FF38] text-[#151515] border-2 border-[#151515] flex items-center justify-center font-bold">
                <CheckCircle2 className="w-4 h-4" />
              </div>
            </div>

            <div className="bg-white dark:bg-[#1E1E1E] border-3 border-[#151515] dark:border-white shadow-[4px_4px_0px_#151515] p-4 flex items-center justify-between">
              <div>
                <span className="text-[11px] font-mono font-bold text-gray-500 uppercase block">
                  Minutes Focused
                </span>
                <span className="text-2xl font-black text-[#151515] dark:text-white">
                  {stats.total_minutes_focused}m
                </span>
              </div>
              <div className="w-9 h-9 bg-[#FFA400] text-[#151515] border-2 border-[#151515] flex items-center justify-center font-bold">
                <Clock className="w-4 h-4" />
              </div>
            </div>

            <div className="bg-white dark:bg-[#1E1E1E] border-3 border-[#151515] dark:border-white shadow-[4px_4px_0px_#151515] p-4 flex items-center justify-between">
              <div>
                <span className="text-[11px] font-mono font-bold text-gray-500 uppercase block">
                  Streak
                </span>
                <span className="text-2xl font-black text-[#151515] dark:text-white">
                  {stats.streak_days} Days
                </span>
              </div>
              <div className="w-9 h-9 bg-[#FF5E5B] text-white border-2 border-[#151515] flex items-center justify-center font-bold">
                <Flame className="w-4 h-4" />
              </div>
            </div>
          </div>
        )}

        {/* Filter Tabs & Search Bar */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 mb-6">
          {/* Tabs */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
            {[
              { id: 'all', label: `All (${articles.length})` },
              { id: 'progress', label: 'In Progress' },
              { id: 'completed', label: 'Completed' },
              { id: 'favorites', label: 'Favorites' },
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setFilter(tab.id as any)}
                className={`px-3 py-1.5 text-xs font-extrabold uppercase border-2 border-[#151515] transition-all whitespace-nowrap ${
                  filter === tab.id
                    ? 'bg-[#2455FF] text-white shadow-[2px_2px_0px_#151515]'
                    : 'bg-white hover:bg-[#F4F0E8] text-[#151515]'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Search Input */}
          <div className="relative min-w-[240px]">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-gray-500" />
            <input
              type="text"
              placeholder="Search articles, authors..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 bg-white border-2 border-[#151515] shadow-[2px_2px_0px_#151515] text-xs font-bold focus:outline-none"
            />
          </div>
        </div>

        {/* Article Cards Grid */}
        {filteredArticles.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredArticles.map(article => (
              <ArticleCard
                key={article.id}
                article={article}
                onRead={(id) => onSelectArticle(id)}
                onPractice={(id) => onSelectArticle(id, 'quiz')}
                onToggleFavorite={handleToggleFavorite}
                onDelete={handleDelete}
              />
            ))}
          </div>
        ) : (
          /* Empty state */
          <div className="bg-white dark:bg-[#1E1E1E] border-4 border-[#151515] dark:border-white shadow-[8px_8px_0px_#151515] p-10 text-center select-none my-8">
            <div className="w-14 h-14 bg-[#D7FF38] border-3 border-[#151515] shadow-[3px_3px_0px_#151515] mx-auto flex items-center justify-center font-bold mb-4">
              <BookOpen className="w-7 h-7 text-[#151515]" />
            </div>
            <h3 className="text-xl font-black uppercase text-[#151515] dark:text-white mb-2">
              No Articles Found
            </h3>
            <p className="text-xs sm:text-sm font-semibold text-gray-600 dark:text-gray-400 max-w-md mx-auto mb-6">
              {searchQuery
                ? `No articles matched "${searchQuery}". Clear your search query to see all articles.`
                : 'Your reading library is empty for this filter. Transform a web article or paste text to get started!'}
            </p>
            <Button
              onClick={onOpenTransformModal}
              variant="lime"
              size="md"
              icon={<Zap className="w-4 h-4 text-[#151515]" />}
            >
              TRANSFORM AN ARTICLE
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

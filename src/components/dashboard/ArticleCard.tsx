import React from 'react';
import { ArticleListItem } from '../../types';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import {
  BookOpen,
  Clock,
  Layers,
  Star,
  Trash2,
  CheckCircle,
  HelpCircle,
  ExternalLink
} from 'lucide-react';

interface ArticleCardProps {
  article: ArticleListItem;
  onRead: (articleId: string) => void;
  onPractice: (articleId: string) => void;
  onToggleFavorite: (articleId: string) => void;
  onDelete: (articleId: string) => void;
}

export const ArticleCard: React.FC<ArticleCardProps> = ({
  article,
  onRead,
  onPractice,
  onToggleFavorite,
  onDelete,
}) => {
  return (
    <div className="bg-white dark:bg-[#1E1E1E] border-3 sm:border-4 border-[#151515] dark:border-white shadow-[4px_4px_0px_#151515] p-5 flex flex-col justify-between transition-all hover:translate-x-[1px] hover:translate-y-[1px]">
      <div>
        {/* Top Meta row */}
        <div className="flex items-center justify-between gap-2 mb-3">
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="text-[11px] font-mono font-extrabold uppercase px-2 py-0.5 bg-[#FAF8F5] dark:bg-[#2A2A2A] border border-[#151515] text-gray-700 dark:text-gray-300">
              {article.domain || 'Source'}
            </span>
            {article.is_completed ? (
              <Badge variant="lime" size="sm">COMPLETED</Badge>
            ) : article.progress_percent > 0 ? (
              <Badge variant="blue" size="sm">{article.progress_percent}% READ</Badge>
            ) : (
              <Badge variant="white" size="sm">UNREAD</Badge>
            )}
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={() => onToggleFavorite(article.id)}
              className={`p-1.5 border border-[#151515] transition-colors ${
                article.is_favorite
                  ? 'bg-[#FFA400] text-[#151515]'
                  : 'bg-white hover:bg-[#FAF8F5] text-gray-400'
              }`}
              title={article.is_favorite ? 'Remove favorite' : 'Add to favorites'}
            >
              <Star className="w-4 h-4 fill-current" />
            </button>
            <button
              onClick={() => onDelete(article.id)}
              className="p-1.5 border border-[#151515] bg-white hover:bg-[#FF5E5B] hover:text-white transition-colors text-gray-400"
              title="Delete article"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Title */}
        <h3
          onClick={() => onRead(article.id)}
          className="font-extrabold text-base sm:text-lg leading-snug text-[#151515] dark:text-white hover:text-[#2455FF] dark:hover:text-[#D7FF38] cursor-pointer mb-2 line-clamp-2"
        >
          {article.title}
        </h3>

        {/* Author & Stats */}
        <div className="flex items-center gap-3 text-xs font-semibold text-gray-600 dark:text-gray-400 mb-4">
          <span>{article.author || 'Author'}</span>
          <span>•</span>
          <span className="flex items-center gap-1 font-mono">
            <Clock className="w-3.5 h-3.5" />
            ~{article.reading_time_minutes}m
          </span>
          <span>•</span>
          <span className="flex items-center gap-1 font-mono">
            <Layers className="w-3.5 h-3.5" />
            {article.total_chunks} chunks
          </span>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-[#E6E1D5] border-2 border-[#151515] h-2.5 mb-5 overflow-hidden">
          <div
            className={`h-full border-r-2 border-[#151515] ${
              article.is_completed ? 'bg-[#D7FF38]' : 'bg-[#2455FF]'
            }`}
            style={{ width: `${article.progress_percent}%` }}
          />
        </div>
      </div>

      {/* Action Buttons */}
      <div className="grid grid-cols-2 gap-2 pt-3 border-t-2 border-dashed border-gray-300 dark:border-gray-700">
        <Button
          onClick={() => onRead(article.id)}
          variant="primary"
          size="sm"
          icon={<BookOpen className="w-3.5 h-3.5" />}
        >
          {article.progress_percent > 0 && !article.is_completed ? 'RESUME' : 'READ'}
        </Button>

        <Button
          onClick={() => onPractice(article.id)}
          variant="lime"
          size="sm"
          icon={<HelpCircle className="w-3.5 h-3.5" />}
        >
          PRACTICE
        </Button>
      </div>
    </div>
  );
};

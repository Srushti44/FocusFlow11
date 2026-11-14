import React from 'react';
import { ActiveTab, ReadingStats } from '../types';
import { Button } from './ui/Button';
import {
  Compass,
  BookOpen,
  LayoutDashboard,
  Settings,
  Chrome,
  Zap,
  Flame,
  Plus,
  Activity
} from 'lucide-react';

interface NavbarProps {
  activeTab: ActiveTab;
  onSelectTab: (tab: ActiveTab) => void;
  onOpenTransformModal: () => void;
  stats?: ReadingStats;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  onSelectTab,
  onOpenTransformModal,
  stats
}) => {
  const navItems: Array<{ id: ActiveTab; label: string; icon: React.ReactNode }> = [
    { id: 'landing', label: 'About', icon: <Compass className="w-4 h-4" /> },
    { id: 'reader', label: 'Reader', icon: <BookOpen className="w-4 h-4" /> },
    { id: 'dashboard', label: 'Dashboard', icon: <LayoutDashboard className="w-4 h-4" /> },
    { id: 'mlops', label: 'MLOps', icon: <Activity className="w-4 h-4" /> },
    { id: 'extension-popup', label: 'Extension', icon: <Chrome className="w-4 h-4" /> },
    { id: 'settings', label: 'Settings', icon: <Settings className="w-4 h-4" /> },
  ];

  return (
    <header className="w-full bg-[#FFFFFF] dark:bg-[#151515] border-b-4 border-[#151515] sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        {/* Brand */}
        <div
          onClick={() => onSelectTab('landing')}
          className="flex items-center gap-2.5 cursor-pointer select-none group"
        >
          <div className="w-9 h-9 bg-[#D7FF38] border-3 border-[#151515] shadow-[2px_2px_0px_#151515] flex items-center justify-center font-black text-lg transition-transform group-hover:rotate-6">
            FF
          </div>
          <div>
            <span className="font-extrabold text-lg sm:text-xl tracking-tighter text-[#151515] dark:text-white block leading-none">
              FOCUSFLOW
            </span>
            <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-[#2455FF] dark:text-[#D7FF38]">
              COGNITIVE ACCESS
            </span>
          </div>
        </div>

        {/* Center Nav tabs */}
        <nav className="hidden md:flex items-center gap-1.5">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`px-3 py-1.5 text-xs font-extrabold uppercase border-2 border-[#151515] transition-all flex items-center gap-1.5 ${
                activeTab === item.id
                  ? 'bg-[#2455FF] text-white shadow-[2px_2px_0px_#151515]'
                  : 'bg-white hover:bg-[#F4F0E8] text-[#151515]'
              }`}
            >
              {item.icon}
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        {/* Right Actions */}
        <div className="flex items-center gap-2.5">
          {/* Stats streak */}
          {stats && (
            <div className="hidden lg:flex items-center gap-1.5 bg-[#FAF8F5] dark:bg-[#252525] border-2 border-[#151515] px-2.5 py-1 text-xs font-mono font-bold">
              <Flame className="w-3.5 h-3.5 text-[#FF5E5B]" />
              <span>{stats.streak_days}D STREAK</span>
            </div>
          )}

          {/* Transform CTA Button */}
          <Button
            onClick={onOpenTransformModal}
            variant="lime"
            size="sm"
            icon={<Zap className="w-4 h-4 text-[#151515]" />}
          >
            TRANSFORM
          </Button>
        </div>
      </div>

      {/* Mobile nav bar */}
      <div className="md:hidden flex items-center justify-around border-t-2 border-[#151515] bg-[#F4F0E8] dark:bg-[#1A1A1A] p-1.5 overflow-x-auto">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => onSelectTab(item.id)}
            className={`px-2 py-1 text-[11px] font-extrabold uppercase border border-[#151515] flex items-center gap-1 whitespace-nowrap ${
              activeTab === item.id
                ? 'bg-[#2455FF] text-white'
                : 'bg-white text-[#151515]'
            }`}
          >
            {item.icon}
            <span>{item.label}</span>
          </button>
        ))}
      </div>
    </header>
  );
};

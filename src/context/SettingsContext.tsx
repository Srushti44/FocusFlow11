import React, { createContext, useContext, useState, useEffect } from 'react';
import { UserSettings } from '../types';

const DEFAULT_SETTINGS: UserSettings = {
  font_family: 'lexend',
  font_size: 19,
  line_spacing: 1.85,
  letter_spacing: 0.5,
  content_width: 740,
  bionic_reading: false,
  focus_ruler: false,
  chunk_mode: true,
  chunk_size_words: 80,
  enable_semantic_highlights: true,
  focus_mode: false,
  tts_speed: 1.0,
  theme: 'warm',
  reduced_motion: false,
  high_contrast: true,
};

interface SettingsContextType {
  settings: UserSettings;
  updateSettings: (newSettings: Partial<UserSettings>) => void;
  resetSettings: () => void;
}

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

export const SettingsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [settings, setSettings] = useState<UserSettings>(() => {
    const local = localStorage.getItem('focusflow_settings');
    if (local) {
      try {
        return { ...DEFAULT_SETTINGS, ...JSON.parse(local) };
      } catch {}
    }
    return DEFAULT_SETTINGS;
  });

  // Load initial settings from Chrome Storage API if running in extension
  useEffect(() => {
    if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
      chrome.storage.local.get(['focusflow_settings'], (result) => {
        if (result && result.focusflow_settings) {
          setSettings(prev => ({ ...prev, ...result.focusflow_settings }));
        }
      });
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('focusflow_settings', JSON.stringify(settings));

    // Also sync to chrome.storage if available
    if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
      chrome.storage.local.set({ focusflow_settings: settings });
    }

    // Apply theme classes to body
    const body = document.body;
    body.classList.remove('theme-warm', 'theme-white', 'theme-dark', 'theme-slate', 'dark');

    if (settings.theme === 'dark') {
      body.classList.add('dark');
      body.style.backgroundColor = '#121212';
      body.style.color = '#F4F0E8';
    } else if (settings.theme === 'white') {
      body.style.backgroundColor = '#FFFFFF';
      body.style.color = '#151515';
    } else if (settings.theme === 'slate') {
      body.style.backgroundColor = '#E5E7EB';
      body.style.color = '#111827';
    } else {
      // Warm default
      body.style.backgroundColor = '#F4F0E8';
      body.style.color = '#151515';
    }

    if (settings.reduced_motion) {
      document.documentElement.classList.add('reduce-motion');
    } else {
      document.documentElement.classList.remove('reduce-motion');
    }
  }, [settings]);

  const updateSettings = (partial: Partial<UserSettings>) => {
    setSettings(prev => ({ ...prev, ...partial }));
  };

  const resetSettings = () => {
    setSettings(DEFAULT_SETTINGS);
  };

  return (
    <SettingsContext.Provider value={{ settings, updateSettings, resetSettings }}>
      {children}
    </SettingsContext.Provider>
  );
};

export const useSettings = () => {
  const ctx = useContext(SettingsContext);
  if (!ctx) {
    throw new Error('useSettings must be used within SettingsProvider');
  }
  return ctx;
};

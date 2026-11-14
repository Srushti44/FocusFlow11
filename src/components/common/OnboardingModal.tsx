import React, { useState } from 'react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { renderBionicText } from '../../utils/bionic';
import { Layers, Eye, Sparkles, Check, ArrowRight } from 'lucide-react';

interface OnboardingModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const OnboardingModal: React.FC<OnboardingModalProps> = ({ isOpen, onClose }) => {
  const [demoBionic, setDemoBionic] = useState(true);

  const handleFinish = () => {
    localStorage.setItem('focusflow_onboarded', 'true');
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleFinish} title="Welcome to FocusFlow" maxWidth="lg">
      <div className="space-y-6 select-none">
        {/* Intro */}
        <div>
          <Badge variant="blue" size="sm" className="mb-2">COGNITIVE ACCESSIBILITY FOUNDATION</Badge>
          <h2 className="text-xl sm:text-2xl font-black tracking-tight text-[#151515]">
            Less Noise. More Focus.
          </h2>
          <p className="text-xs sm:text-sm font-semibold text-gray-700 mt-1 leading-relaxed">
            Most digital reading experiences trigger directed attention fatigue through visual clutter and unbroken text walls. FocusFlow re-architects how information enters your brain.
          </p>
        </div>

        {/* 4 Pillars Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="p-3.5 bg-white border-2 border-[#151515] shadow-[3px_3px_0px_#151515]">
            <div className="flex items-center gap-2 font-black text-xs uppercase text-[#2455FF] mb-1">
              <Layers className="w-4 h-4" />
              <span>1. Focus Chunks</span>
            </div>
            <p className="text-xs font-medium text-gray-700 leading-relaxed">
              Splits dense articles into 60-90 word atomic units that respect your working memory limit.
            </p>
          </div>

          <div className="p-3.5 bg-white border-2 border-[#151515] shadow-[3px_3px_0px_#151515]">
            <div className="flex items-center gap-2 font-black text-xs uppercase text-[#151515] mb-1">
              <span className="font-mono text-sm font-black">2. <strong>Bio</strong>nic</span>
            </div>
            <p className="text-xs font-medium text-gray-700 leading-relaxed">
              Bolds initial letter syllables to guide saccadic eye movement and accelerate word recognition.
            </p>
          </div>

          <div className="p-3.5 bg-white border-2 border-[#151515] shadow-[3px_3px_0px_#151515]">
            <div className="flex items-center gap-2 font-black text-xs uppercase text-[#2455FF] mb-1">
              <Eye className="w-4 h-4" />
              <span>3. Focus Ruler</span>
            </div>
            <p className="text-xs font-medium text-gray-700 leading-relaxed">
              A tracking horizontal guide that prevents line-skipping and unconscious sentence regression.
            </p>
          </div>

          <div className="p-3.5 bg-white border-2 border-[#151515] shadow-[3px_3px_0px_#151515]">
            <div className="flex items-center gap-2 font-black text-xs uppercase text-[#151515] mb-1">
              <Sparkles className="w-4 h-4 text-[#FFA400]" />
              <span>4. AI Retention Suite</span>
            </div>
            <p className="text-xs font-medium text-gray-700 leading-relaxed">
              Instant TL;DR summaries, key concept glossaries, interactive quizzes, and study flashcards.
            </p>
          </div>
        </div>

        {/* Live Interactive Demo Box */}
        <div className="p-4 bg-[#FAF8F5] border-3 border-[#151515] shadow-[4px_4px_0px_#151515]">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-extrabold uppercase text-[#151515]">
              Interactive Bionic Preview
            </span>
            <button
              onClick={() => setDemoBionic(!demoBionic)}
              className="text-[11px] font-mono font-extrabold bg-[#D7FF38] border border-[#151515] px-2 py-0.5"
            >
              TOGGLE: {demoBionic ? 'ACTIVE' : 'OFF'}
            </button>
          </div>
          <p className="text-sm font-lexend leading-relaxed text-gray-900">
            {renderBionicText(
              "Your brain reads faster than your eyes can scan. By highlighting key syllables, your visual network predicts words seamlessly.",
              demoBionic
            )}
          </p>
        </div>

        {/* CTA */}
        <div className="flex items-center justify-between pt-2 border-t-2 border-[#151515]">
          <span className="text-xs font-bold text-gray-500">
            Ready to explore?
          </span>
          <Button
            onClick={handleFinish}
            variant="lime"
            size="md"
            icon={<ArrowRight className="w-4 h-4" />}
          >
            START READING NOW
          </Button>
        </div>
      </div>
    </Modal>
  );
};

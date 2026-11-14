import React from 'react';

/**
 * Formats text with Bionic Reading saccadic eye guidance:
 * bolds the first portion of words to guide the eye across sentences.
 */
export function renderBionicText(text: string, isBionic: boolean): React.ReactNode {
  if (!isBionic) {
    return text;
  }

  const words = text.split(/(\s+)/);
  return words.map((token, index) => {
    // If token is whitespace, preserve
    if (/^\s+$/.test(token)) {
      return token;
    }

    const cleanWord = token.replace(/^[^\w]+|[^\w]+$/g, '');
    if (!cleanWord) {
      return token;
    }

    const midPoint = cleanWord.length <= 3 ? 1 : Math.ceil(cleanWord.length * 0.45);
    const prefix = cleanWord.slice(0, midPoint);
    const suffix = cleanWord.slice(midPoint);

    // Reconstruct with any leading or trailing punctuation
    const leadMatch = token.match(/^[^\w]+/);
    const trailMatch = token.match(/[^\w]+$/);
    const leadPunct = leadMatch ? leadMatch[0] : '';
    const trailPunct = trailMatch ? trailMatch[0] : '';

    return (
      <span key={index} className="inline">
        {leadPunct}
        <strong className="font-extrabold text-[#151515] dark:text-[#D7FF38]">{prefix}</strong>
        {suffix}
        {trailPunct}
      </span>
    );
  });
}

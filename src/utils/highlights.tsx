import React from 'react';
import { SemanticHighlight } from '../types';

interface SpanItem {
  start: number;
  end: number;
  category: 'concept' | 'definition' | 'evidence';
  label: string;
}

export function extractLocalHighlightsFromText(text: string): SpanItem[] {
  const spans: SpanItem[] = [];
  const seenIndices = new Set<number>();

  function isOverlapping(start: number, end: number) {
    for (let i = start; i < end; i++) {
      if (seenIndices.has(i)) return true;
    }
    return false;
  }

  function markIndices(start: number, end: number) {
    for (let i = start; i < end; i++) {
      seenIndices.add(i);
    }
  }

  // 1. Definition patterns: "X is defined as ...", "X refers to ..."
  const defRegex = /\b([A-Z][a-zA-Z\s]{2,25})\s+(?:is defined as|refers to|represents|means)\s+([^.!?]+[.!?])/g;
  let match: RegExpExecArray | null;
  while ((match = defRegex.exec(text)) !== null) {
    const start = match.index;
    const end = match.index + match[0].length;
    if (!isOverlapping(start, end)) {
      markIndices(start, end);
      spans.push({ start, end, category: 'definition', label: 'Definition' });
    }
  }

  // 2. Supporting details: numbers, percentages, dates, empirical phrases
  const evidenceRegex = /\b(?:\d+(?:\.\d+)?%|\$\d+(?:\.\d+)?|\d+\s*(?:percent|million|billion|thousand|users|seconds|minutes|words|participants)|in the late \d{4}s|in \d{4})\b|(?:studies|research|neuroimaging|data)\s+(?:show|confirm|demonstrate|indicate|reveal)[^.!?]+/gi;
  while ((match = evidenceRegex.exec(text)) !== null) {
    const start = match.index;
    const end = match.index + match[0].length;
    if (!isOverlapping(start, end)) {
      markIndices(start, end);
      spans.push({ start, end, category: 'evidence', label: 'Data / Evidence' });
    }
  }

  // 3. Key Concepts: Capitalized terminology phrases
  const conceptRegex = /\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\b/g;
  const stopwords = new Set([
    'The', 'This', 'That', 'When', 'Where', 'Why', 'How', 'There', 'Here',
    'With', 'After', 'Before', 'While', 'In', 'On', 'At', 'For', 'To', 'From'
  ]);
  while ((match = conceptRegex.exec(text)) !== null) {
    const word = match[0];
    if (!stopwords.has(word.split(' ')[0])) {
      const start = match.index;
      const end = match.index + word.length;
      if (!isOverlapping(start, end)) {
        markIndices(start, end);
        spans.push({ start, end, category: 'concept', label: 'Key Concept' });
      }
    }
  }

  spans.sort((a, b) => a.start - b.start);
  return spans;
}

export function renderSemanticHighlights(
  text: string,
  enableHighlights: boolean,
  serverHighlights?: SemanticHighlight[]
): React.ReactNode {
  if (!enableHighlights || !text) return text;

  // Use server highlights if available and aligned, otherwise compute deterministic local highlights
  let spans: SpanItem[] = [];
  if (serverHighlights && serverHighlights.length > 0) {
    spans = serverHighlights
      .filter(h => text.includes(h.text))
      .map(h => {
        const start = text.indexOf(h.text);
        return {
          start,
          end: start + h.text.length,
          category: h.category,
          label: h.label
        };
      })
      .filter(s => s.start !== -1)
      .sort((a, b) => a.start - b.start);
  }

  if (spans.length === 0) {
    spans = extractLocalHighlightsFromText(text);
  }

  if (spans.length === 0) {
    return text;
  }

  const elements: React.ReactNode[] = [];
  let lastIndex = 0;

  spans.forEach((span, idx) => {
    // Skip overlapping spans to prevent word duplication or text corruption
    if (span.start < lastIndex) {
      return;
    }

    // Append leading plain text
    if (span.start > lastIndex) {
      elements.push(text.slice(lastIndex, span.start));
    }

    const highlightText = text.slice(span.start, span.end);
    let bgClass = 'bg-[#FFF380] text-[#151515] border-b-2 border-[#D4A000]';
    let icon = '🟡';

    if (span.category === 'definition') {
      bgClass = 'bg-[#C8F7DC] text-[#0B4A2B] border-b-2 border-[#10B981]';
      icon = '🟢';
    } else if (span.category === 'evidence') {
      bgClass = 'bg-[#D2E2FF] text-[#0A2E80] border-b-2 border-[#2455FF]';
      icon = '🔵';
    }

    elements.push(
      <mark
        key={`hl-${idx}`}
        title={`${icon} ${span.label}`}
        className={`px-1 py-0.5 font-bold transition-all rounded-none ${bgClass}`}
      >
        {highlightText}
      </mark>
    );

    lastIndex = span.end;
  });

  if (lastIndex < text.length) {
    elements.push(text.slice(lastIndex));
  }

  return <>{elements}</>;
}

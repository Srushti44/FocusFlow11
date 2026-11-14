// FocusFlow Content Script - High-Fidelity Reading Extraction & In-Page Bridge

function getPageMetadata() {
  const url = window.location.href;
  const isRestrictedScheme = 
    url.startsWith('chrome://') || 
    url.startsWith('chrome-extension://') || 
    url.startsWith('about:') || 
    url.startsWith('edge://') || 
    url.startsWith('view-source:') ||
    url.includes('chromewebstore.google.com');

  if (isRestrictedScheme) {
    return {
      supported: false,
      reason: 'Browser internal and protected pages (chrome://) cannot be accessed by extensions.',
      url
    };
  }

  // Use FocusFlowReadability if available
  if (typeof window.FocusFlowReadability !== 'undefined') {
    try {
      const parsed = window.FocusFlowReadability.parse(document, url);
      return parsed;
    } catch (err) {
      console.error('[FocusFlow] Readability parse error:', err);
    }
  }

  // Fallback simple extraction if readability failed
  const title = document.querySelector('h1')?.innerText?.trim() || document.title || 'Untitled Web Page';
  const author = document.querySelector('meta[name="author"]')?.getAttribute('content') || 'Web Author';
  const articleEl = document.querySelector('article, [role="main"], main, #content') || document.body;
  const rawText = articleEl ? articleEl.innerText.trim() : '';
  const wordCount = rawText ? rawText.split(/\s+/).filter(Boolean).length : 0;

  if (wordCount < 50) {
    return {
      supported: false,
      isArticle: false,
      reason: 'This page does not contain sufficient readable article content (found only ' + wordCount + ' words).',
      url
    };
  }

  return {
    supported: true,
    isArticle: wordCount >= 80,
    title,
    author,
    sourceUrl: url,
    domain: window.location.hostname.replace('www.', ''),
    wordCount,
    readingTimeMinutes: Math.max(1, Math.round(wordCount / 200)),
    fullText: rawText,
    previewSnippet: rawText.slice(0, 360) + (rawText.length > 360 ? '...' : '')
  };
}

// Listen for messages from popup, sidepanel, or background
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'EXTRACT_CONTENT') {
    const data = getPageMetadata();
    // Include user selection if available
    const selection = window.getSelection()?.toString()?.trim();
    if (selection && selection.length > 20) {
      data.selectedText = selection;
    }
    sendResponse(data);
  } else if (request.action === 'GET_SELECTION') {
    const sel = window.getSelection()?.toString()?.trim() || '';
    sendResponse({ selection: sel });
  } else if (request.action === 'PING') {
    sendResponse({ status: 'alive', url: window.location.href });
  }
  return true;
});

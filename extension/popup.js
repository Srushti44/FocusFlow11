// FocusFlow Extension Popup Controller (Manifest V3)

let currentArticleData = null;

async function initPopup() {
  const statusLabel = document.getElementById('status-label');
  const headerStatus = document.getElementById('header-status');
  const previewBox = document.getElementById('article-preview');
  const unsupportedBox = document.getElementById('unsupported-box');
  const unsupportedMsg = document.getElementById('unsupported-msg');

  const pageTitle = document.getElementById('page-title');
  const pageDomain = document.getElementById('page-domain');
  const pageWords = document.getElementById('page-words');
  const pageTime = document.getElementById('page-time');
  const pageAuthor = document.getElementById('page-author');
  const pageSnippet = document.getElementById('page-snippet');

  const btnTransform = document.getElementById('btn-transform');
  const btnSidePanel = document.getElementById('btn-sidepanel');
  const btnOpenWorkspace = document.getElementById('btn-open-workspace');

  // 1. Web Preview / Standalone fallback
  if (typeof chrome === 'undefined' || !chrome.tabs || !chrome.tabs.query) {
    statusLabel.style.display = 'none';
    headerStatus.innerText = 'DEMO PREVIEW';
    headerStatus.className = 'status-badge status-ready';
    previewBox.style.display = 'block';

    pageTitle.innerText = '[Sample Article] Cognitive Load Theory and Digital Reading Architecture';
    pageDomain.innerText = 'Sample Content • nature.cognitive.org';
    pageWords.innerText = '420 words';
    pageTime.innerText = '~2 min read';
    pageSnippet.innerText = 'Working memory possesses a strictly finite capacity that is rapidly exhausted by digital clutter, advertisements, and dense walls of text...';

    btnTransform.onclick = () => {
      window.open('http://localhost:5173/?view=reader', '_blank');
    };
    btnSidePanel.onclick = () => {
      window.open('http://localhost:5173/?view=sidepanel', '_blank');
    };
    return;
  }

  // 2. Active Tab Detection in Chrome
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab || !tab.url) {
      showUnsupported('Unable to access active tab.');
      return;
    }

    const restrictedPrefixes = ['chrome://', 'edge://', 'about:', 'view-source:', 'chrome-extension://'];
    if (restrictedPrefixes.some(p => tab.url.startsWith(p)) || tab.url.includes('chromewebstore.google.com')) {
      showUnsupported('Internal browser pages (chrome://) and store pages are protected by Chrome security policies. Navigate to any news or blog article.');
      return;
    }

    // Try communicating with content script
    chrome.tabs.sendMessage(tab.id, { action: 'EXTRACT_CONTENT' }, async (response) => {
      if (chrome.runtime.lastError || !response) {
        // If content script wasn't injected yet, inject dynamically
        try {
          await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            files: ['readability.js', 'content.js']
          });
          // Retry extraction after injection
          chrome.tabs.sendMessage(tab.id, { action: 'EXTRACT_CONTENT' }, (retryResponse) => {
            if (retryResponse && retryResponse.supported && retryResponse.fullText) {
              handleExtractionSuccess(retryResponse);
            } else {
              showUnsupported(retryResponse?.reason || 'This webpage does not contain sufficient readable article content to transform.');
            }
          });
          return;
        } catch (injectionErr) {
          showUnsupported('Cannot access or extract text from this page. Protected browser or restricted page.');
          return;
        }
      }

      if (!response.supported || !response.fullText) {
        showUnsupported(response.reason || 'This webpage structure could not be parsed as a readable article.');
        return;
      }

      handleExtractionSuccess(response);
    });

  } catch (err) {
    showUnsupported('Failed scanning active tab: ' + err.message);
  }

  function handleExtractionSuccess(data) {
    currentArticleData = data;
    statusLabel.style.display = 'none';
    unsupportedBox.style.display = 'none';
    previewBox.style.display = 'block';

    headerStatus.innerText = 'ARTICLE DETECTED';
    headerStatus.className = 'status-badge status-ready';

    pageTitle.innerText = data.title || 'Untitled Web Page';
    pageDomain.innerText = data.domain || 'web source';
    pageWords.innerText = `${data.wordCount || '~300'} words`;
    pageTime.innerText = `~${data.readingTimeMinutes || 2} min read`;

    if (data.author && data.author !== 'Web Author') {
      pageAuthor.style.display = 'inline';
      pageAuthor.innerText = `By ${data.author}`;
    }

    if (data.previewSnippet) {
      pageSnippet.innerText = `"${data.previewSnippet}"`;
    }

    // Explicit Action 1: Open in FocusFlow Web Reader
    btnTransform.onclick = async () => {
      btnTransform.innerText = 'TRANSFORMING...';
      btnTransform.disabled = true;

      // First attempt: post actual extracted text to backend API
      try {
        const res = await fetch('http://localhost:8000/api/extract', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            text: data.fullText,
            title: data.title,
            author: data.author,
            url: data.sourceUrl
          })
        });

        if (res.ok) {
          const createdArt = await res.json();
          await chrome.storage.local.set({
            focusflow_active_article: createdArt
          });
          chrome.tabs.create({ url: `http://localhost:5173/?view=reader&id=${createdArt.id}` });
          window.close();
          return;
        }
      } catch (err) {
        console.warn('[FocusFlow Extension] Backend direct extract failed, using fallback navigation', err);
      }

      // Fallback: store extracted article in chrome.storage.local
      await chrome.storage.local.set({
        focusflow_pending_article: {
          title: data.title,
          source_url: data.sourceUrl,
          domain: data.domain,
          raw_content: data.fullText,
          author: data.author,
          extracted_at: new Date().toISOString()
        }
      });

      const targetUrl = `http://localhost:5173/?view=reader&url=${encodeURIComponent(data.sourceUrl)}&title=${encodeURIComponent(data.title)}`;
      chrome.tabs.create({ url: targetUrl });
      window.close();
    };

    // Explicit Action 2: Open in Chrome Side Panel
    btnSidePanel.onclick = async () => {
      btnSidePanel.innerText = 'OPENING PANEL...';
      btnSidePanel.disabled = true;

      // Store article for side panel
      await chrome.storage.local.set({
        focusflow_active_article: {
          title: data.title,
          source_url: data.sourceUrl,
          domain: data.domain,
          raw_content: data.fullText || data.previewSnippet,
          author: data.author,
          extracted_at: new Date().toISOString()
        }
      });

      if (chrome.sidePanel && chrome.sidePanel.open) {
        chrome.windows.getCurrent((w) => {
          chrome.sidePanel.open({ windowId: w.id }).then(() => {
            window.close();
          }).catch(() => {
            chrome.tabs.create({ url: `http://localhost:5173/?view=sidepanel&url=${encodeURIComponent(data.sourceUrl)}` });
            window.close();
          });
        });
      } else {
        chrome.tabs.create({ url: `http://localhost:5173/?view=sidepanel&url=${encodeURIComponent(data.sourceUrl)}` });
        window.close();
      }
    };
  }

  function showUnsupported(msg) {
    statusLabel.style.display = 'none';
    previewBox.style.display = 'none';
    unsupportedBox.style.display = 'block';
    unsupportedMsg.innerText = msg;

    headerStatus.innerText = 'UNSUPPORTED';
    headerStatus.className = 'status-badge status-warn';

    btnOpenWorkspace.onclick = () => {
      chrome.tabs.create({ url: 'http://localhost:5173/?view=dashboard' });
      window.close();
    };
  }
}

document.addEventListener('DOMContentLoaded', initPopup);

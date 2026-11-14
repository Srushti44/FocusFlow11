/**
 * FocusFlow In-Browser Article Readability & Extraction Engine
 * Inspired by Mozilla Readability. Cleans web clutter, isolates primary article prose,
 * and extracts semantic headings, lists, author metadata, and publication dates.
 */

(function (global) {
  'use strict';

  const UNLIKELY_CANDIDATES = /combx|comment|community|disqus|extra|foot|header|menu|remark|rss|shoutbox|sidebar|sponsor|ad-break|agegate|pagination|pager|popup|tweet|twitter|fb-|facebook|meta-info|newsletter|cookie|promo|advert/i;
  const OK_MAYBE_CANDIDATE = /and|article|body|column|main|shadow|entry|post|content/i;
  const JUNK_SELECTORS = [
    'script', 'style', 'noscript', 'iframe', 'svg', 'form', 'nav', 'footer', 'header', 'aside',
    '[role="navigation"]', '[role="banner"]', '[role="complementary"]', '[role="search"]',
    '.ad', '.ads', '.advertisement', '.social-share', '.share-buttons', '.comments',
    '.sidebar', '.related-posts', '.newsletter-signup', '.cookie-banner', '.gdpr', '.promo-box'
  ];

  function cleanTitle(rawTitle, domain) {
    if (!rawTitle) return 'Untitled Web Page';
    let title = rawTitle.trim();
    // Remove trailing site name separators like " - Site", " | Site", " — Site"
    const separators = [' - ', ' | ', ' — ', ' :: ', ' » '];
    for (const sep of separators) {
      if (title.includes(sep)) {
        const parts = title.split(sep);
        if (parts[0].length > 15) {
          title = parts[0].trim();
          break;
        }
      }
    }
    return title;
  }

  function extractAuthor(doc) {
    const metaAuthor = doc.querySelector('meta[name="author"], meta[property="article:author"], meta[property="og:author"]');
    if (metaAuthor && metaAuthor.getAttribute('content')) {
      return metaAuthor.getAttribute('content').trim();
    }
    const schemaAuthor = doc.querySelector('[itemprop="author"]');
    if (schemaAuthor) {
      return (schemaAuthor.innerText || schemaAuthor.getAttribute('content') || '').trim();
    }
    const bylineEl = doc.querySelector('.byline, .author, .entry-author, [rel="author"], .c-byline');
    if (bylineEl) {
      const text = bylineEl.innerText.trim();
      // Remove "By " prefix if present
      return text.replace(/^by\s+/i, '').trim().slice(0, 80);
    }
    return null;
  }

  function extractPublishDate(doc) {
    const metaDate = doc.querySelector('meta[property="article:published_time"], meta[name="date"], meta[name="pubdate"], meta[name="dc.date.issued"]');
    if (metaDate && metaDate.getAttribute('content')) {
      return metaDate.getAttribute('content').trim();
    }
    const timeEl = doc.querySelector('time[datetime]');
    if (timeEl && timeEl.getAttribute('datetime')) {
      return timeEl.getAttribute('datetime').trim();
    }
    return null;
  }

  function parseArticle(doc, url) {
    const currentUrl = url || window.location.href;
    const domain = (new URL(currentUrl)).hostname.replace('www.', '');

    // 1. Identify Title
    const ogTitle = doc.querySelector('meta[property="og:title"], meta[name="twitter:title"]')?.getAttribute('content');
    const h1Title = doc.querySelector('h1')?.innerText;
    const rawTitle = ogTitle || h1Title || doc.title || 'Untitled Article';
    const title = cleanTitle(rawTitle, domain);

    // 2. Metadata
    const author = extractAuthor(doc) || 'Web Author';
    const publishedDate = extractPublishDate(doc);
    const excerpt = doc.querySelector('meta[name="description"], meta[property="og:description"]')?.getAttribute('content') || '';

    // 3. Find candidate root container
    const candidateSelectors = [
      'article',
      '[itemprop="articleBody"]',
      'main',
      '[role="main"]',
      '.post-content',
      '.article-content',
      '.article-body',
      '.entry-content',
      '#content',
      '.content-area'
    ];

    let root = null;
    for (const sel of candidateSelectors) {
      const el = doc.querySelector(sel);
      if (el && el.innerText && el.innerText.trim().length > 300) {
        root = el;
        break;
      }
    }

    if (!root) {
      root = doc.body;
    }

    if (!root) {
      return {
        supported: false,
        reason: 'Empty or inaccessible webpage body.',
        url: currentUrl
      };
    }

    // 4. Clone root and sanitize
    const clone = root.cloneNode(true);

    // Remove junk selectors
    JUNK_SELECTORS.forEach(sel => {
      clone.querySelectorAll(sel).forEach(el => el.remove());
    });

    // Remove nodes matching unlikely patterns unless they are main candidate containers
    const allElements = clone.querySelectorAll('*');
    allElements.forEach(el => {
      const tag = el.tagName.toLowerCase();
      if (['article', 'p', 'h1', 'h2', 'h3', 'h4', 'ul', 'ol', 'li', 'blockquote'].includes(tag)) {
        return;
      }
      const matchString = `${el.className || ''} ${el.id || ''}`;
      if (UNLIKELY_CANDIDATES.test(matchString) && !OK_MAYBE_CANDIDATE.test(matchString)) {
        el.remove();
      }
    });

    // 5. Extract structured components (headings, paragraphs, lists)
    const elements = Array.from(clone.querySelectorAll('p, h2, h3, h4, blockquote, ul, ol'));
    const structuredParagraphs = [];
    const headings = [];
    const lists = [];
    const seenParagraphs = new Set();

    elements.forEach(el => {
      const tag = el.tagName.toLowerCase();
      // Skip paragraphs that are already inside a blockquote, ul, or ol to avoid duplicate extraction
      if (tag === 'p' && el.closest('blockquote, ul, ol')) {
        return;
      }

      const text = el.innerText.trim();
      if (!text) return;

      const norm = text.toLowerCase().replace(/\s+/g, ' ');
      if (seenParagraphs.has(norm)) return;
      seenParagraphs.add(norm);

      if (['h2', 'h3', 'h4'].includes(tag)) {
        headings.push({
          level: parseInt(tag.charAt(1), 10),
          text: text
        });
        structuredParagraphs.push(`## ${text}`);
      } else if (tag === 'blockquote') {
        if (text.length > 20) {
          structuredParagraphs.push(`> ${text}`);
        }
      } else if (tag === 'ul' || tag === 'ol') {
        const items = Array.from(el.querySelectorAll('li'))
          .map(li => li.innerText.trim())
          .filter(t => t.length > 0);
        if (items.length > 0) {
          lists.push({ type: tag, items });
          items.forEach(it => structuredParagraphs.push(`• ${it}`));
        }
      } else if (tag === 'p') {
        // Discard short boilerplate navigation remnants
        const words = text.split(/\s+/).filter(Boolean);
        if (words.length >= 6) {
          structuredParagraphs.push(text);
        }
      }
    });

    // Fallback if structured pass yielded too little
    let fullText = structuredParagraphs.join('\n\n').trim();
    if (!fullText || fullText.split(/\s+/).length < 60) {
      fullText = (clone.innerText || '').trim();
    }

    const words = fullText.split(/\s+/).filter(Boolean);
    const wordCount = words.length;

    if (!fullText || wordCount < 50) {
      return {
        supported: false,
        isArticle: false,
        reason: 'This webpage does not contain sufficient readable article text (found ' + (wordCount || 0) + ' words).',
        url: currentUrl
      };
    }

    const isArticle = wordCount >= 80;
    const readingTime = Math.max(1, Math.round(wordCount / 200));

    return {
      supported: true,
      isArticle,
      title,
      author,
      publishedDate,
      sourceUrl: currentUrl,
      domain,
      excerpt: excerpt.slice(0, 240),
      headings,
      listsCount: lists.length,
      wordCount,
      readingTimeMinutes: readingTime,
      fullText,
      structuredParagraphs,
      previewSnippet: fullText.slice(0, 360) + (fullText.length > 360 ? '...' : '')
    };
  }

  global.FocusFlowReadability = {
    parse: parseArticle
  };
})(typeof window !== 'undefined' ? window : this);

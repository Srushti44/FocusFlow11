// Chrome Extension Manifest V3 Service Worker for FocusFlow

chrome.runtime.onInstalled.addListener(() => {
  console.log('[FocusFlow] Extension service worker initialized.');
  
  // Context Menu items
  chrome.contextMenus.create({
    id: 'focusflow-transform-selection',
    title: 'FocusFlow: Transform Selected Text',
    contexts: ['selection']
  });

  chrome.contextMenus.create({
    id: 'focusflow-transform-page',
    title: 'FocusFlow: Read in Focus Mode',
    contexts: ['page']
  });

  chrome.contextMenus.create({
    id: 'focusflow-open-sidepanel',
    title: 'FocusFlow: Open in Side Panel',
    contexts: ['page']
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'focusflow-transform-selection' && info.selectionText) {
    chrome.tabs.create({
      url: `http://localhost:5173/?view=reader&paste=${encodeURIComponent(info.selectionText)}`
    });
  } else if (info.menuItemId === 'focusflow-transform-page' && tab?.url) {
    chrome.tabs.create({
      url: `http://localhost:5173/?view=reader&url=${encodeURIComponent(tab.url)}`
    });
  } else if (info.menuItemId === 'focusflow-open-sidepanel' && tab?.id) {
    if (chrome.sidePanel && chrome.sidePanel.open) {
      chrome.sidePanel.open({ windowId: tab.windowId }).catch(console.error);
    }
  }
});

// Configure side panel behavior (does not hijack every click, but opens on request)
if (chrome.sidePanel && chrome.sidePanel.setPanelBehavior) {
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: false }).catch(() => {});
}

// Runtime message hub between popup, content script, and side panel
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'OPEN_SIDE_PANEL') {
    const windowId = request.windowId || sender.tab?.windowId;
    if (chrome.sidePanel && chrome.sidePanel.open && windowId) {
      chrome.sidePanel.open({ windowId }).then(() => {
        sendResponse({ status: 'opened' });
      }).catch(err => {
        sendResponse({ status: 'error', message: err.message });
      });
      return true;
    } else {
      sendResponse({ status: 'unsupported' });
    }
  } else if (request.action === 'OPEN_READER_TAB') {
    chrome.tabs.create({ url: request.url });
    sendResponse({ status: 'tab_created' });
  } else if (request.action === 'SET_ACTIVE_ARTICLE') {
    chrome.storage.local.set({ focusflow_active_article: request.article }, () => {
      sendResponse({ status: 'saved' });
    });
    return true;
  }
  return true;
});

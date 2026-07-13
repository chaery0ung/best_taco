// Runs both as an MV3 content script (real marketplace pages) and as a plain
// <script> include in demo.html (no chrome.* APIs available there) — every
// chrome API access is guarded so the same file works in both contexts.
//
// We deliberately do NOT hardcode per-site CSS selectors for eBay/OfferUp/
// Facebook Marketplace: their class names are hashed/obfuscated and the chat
// UI sits behind a login wall, so hand-picked selectors would be unverifiable
// and would break silently. Instead this uses two generic heuristics that
// hold across virtually every chat UI:
//   1. Chat bubbles are findable via common class/testid/aria-label/role hints.
//   2. The current user's own messages are right-aligned; the counterparty's
//      are left-aligned. We only score the counterparty (the seller).
// If a real integration needs tighter targeting, add a `data-sender="me"`
// attribute (see demo.html) to override the alignment heuristic outright.
(function () {
  const CHAT_CANDIDATE_SELECTOR =
    '[class*="message" i], [class*="msg" i], [class*="bubble" i], ' +
    '[data-testid*="message" i], [aria-label*="message" i], [role="row"]';

  const LISTING_TITLE_SELECTOR = 'h1';
  const LISTING_DESC_SELECTOR =
    '[class*="description" i], [data-testid*="description" i], [aria-label*="description" i]';

  const MIN_TEXT_LEN = 2;
  const MAX_TEXT_LEN = 600;

  const hasChrome = typeof chrome !== 'undefined' && !!chrome.storage;
  const processedMessages = new WeakSet();
  let sellerMax = 0;
  const sellerHits = new Map();
  let lastListingText = '';

  function levelFor(score) {
    return score >= 60 ? 'high' : score >= 30 ? 'medium' : 'low';
  }

  function getSetting(cb) {
    if (hasChrome) {
      chrome.storage.sync.get({ enabled: true }, (res) => cb(res.enabled !== false));
    } else {
      cb(true);
    }
  }

  function saveState() {
    if (!hasChrome) return;
    chrome.storage.local.set({
      lastRisk: {
        score: sellerMax,
        level: levelFor(sellerMax),
        hits: Array.from(sellerHits.values()),
        updatedAt: Date.now()
      }
    });
  }

  function applyResult(result) {
    if (result.score === 0) return;
    sellerMax = Math.max(sellerMax, result.score);
    result.hits.forEach((h) => sellerHits.set(h.id, h.label));
    SftFlag.updateFlag(sellerMax, levelFor(sellerMax));
    saveState();
  }

  // --- sender detection: only inspect the counterparty (seller), never "me" ---
  function isOutgoing(el) {
    if (el.dataset && el.dataset.sender) {
      return el.dataset.sender === 'me';
    }
    const parent = el.parentElement;
    if (!parent) return false;
    const rect = el.getBoundingClientRect();
    const parentRect = parent.getBoundingClientRect();
    if (rect.width === 0 || parentRect.width === 0) return false;
    const leftGap = rect.left - parentRect.left;
    const rightGap = parentRect.right - rect.right;
    // Hugs the right edge of its container: the near-universal convention
    // for "my own message" in chat UIs (iMessage, Messenger, OfferUp, eBay...).
    return rightGap < 40 && rightGap < leftGap * 0.6;
  }

  function leafCandidates() {
    const all = Array.from(document.querySelectorAll(CHAT_CANDIDATE_SELECTOR));
    return all.filter((el) => !all.some((other) => other !== el && el.contains(other)));
  }

  function badgeFor(level) {
    const span = document.createElement('span');
    span.className = `sft-badge sft-badge-${level}`;
    span.textContent = level === 'high' ? '⚠ high risk' : '⚠ caution';
    return span;
  }

  function handleCandidate(el) {
    if (processedMessages.has(el)) return;
    processedMessages.add(el);
    if (isOutgoing(el)) return; // buyer's own messages are never scored

    const text = el.textContent.trim();
    if (text.length < MIN_TEXT_LEN || text.length > MAX_TEXT_LEN) return;

    const result = FraudScorer.scoreMessage(text);
    applyResult(result); // flag reflects any signal, even below the badge threshold
    if (result.level === 'low') return;

    el.classList.add('sft-flagged', `sft-flagged-${result.level}`);
    el.appendChild(badgeFor(result.level));
    el.title = result.hits.map((h) => h.label).join(', ');
  }

  function scanChat() {
    leafCandidates().forEach(handleCandidate);
  }

  // --- listing/post scanning: the seller wrote this too, so it's in scope ---
  function scanListing() {
    const titleEl = document.querySelector(LISTING_TITLE_SELECTOR);
    const descEl = document.querySelector(LISTING_DESC_SELECTOR);
    const text = [titleEl && titleEl.textContent, descEl && descEl.textContent]
      .filter(Boolean)
      .join('. ')
      .trim();
    if (!text || text === lastListingText) return;
    lastListingText = text;
    applyResult(FraudScorer.scoreMessage(text));
  }

  function start() {
    getSetting((enabled) => {
      if (!enabled) return;
      SftFlag.updateFlag(0, 'low');
      scanListing();
      scanChat();
      const observer = new MutationObserver(() => {
        scanListing();
        scanChat();
      });
      observer.observe(document.body, { childList: true, subtree: true });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();

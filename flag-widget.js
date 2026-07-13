// Draggable "Green Flag" risk indicator shared by content.js (real pages) and
// demo.html (plain script include, no chrome.* APIs).
(function (global) {
  const STORAGE_KEY = 'sft_flag_position';
  let flagEl = null;
  let dragging = false;
  let dragOffset = { x: 0, y: 0 };

  function levelLabel(level) {
    return level === 'high' ? 'Danger' : level === 'medium' ? 'Caution' : 'Safe';
  }

  function readPosition(cb) {
    if (typeof chrome !== 'undefined' && chrome.storage) {
      chrome.storage.local.get({ [STORAGE_KEY]: null }, (res) => cb(res[STORAGE_KEY]));
      return;
    }
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      cb(raw ? JSON.parse(raw) : null);
    } catch (e) {
      cb(null);
    }
  }

  function writePosition(pos) {
    if (typeof chrome !== 'undefined' && chrome.storage) {
      chrome.storage.local.set({ [STORAGE_KEY]: pos });
      return;
    }
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(pos));
    } catch (e) {
      /* ignore */
    }
  }

  function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
  }

  function ensureFlag() {
    if (flagEl) return flagEl;

    flagEl = document.createElement('div');
    flagEl.id = 'sft-flag-widget';
    flagEl.className = 'sft-flag-level-low';
    flagEl.title = 'Drag to move · risk level of the seller’s messages';
    flagEl.innerHTML =
      '<svg class="sft-flag-icon" viewBox="0 0 24 24" width="18" height="18">' +
      '<path class="sft-flag-pole" d="M5 2v20" stroke="#6b7280" stroke-width="2" stroke-linecap="round" fill="none"/>' +
      '<path class="sft-flag-cloth" d="M5 3h14l-4 4.5 4 4.5H5z"/>' +
      '</svg>' +
      '<span class="sft-flag-pct">0%</span>';
    document.body.appendChild(flagEl);

    // Plain mouse events (not Pointer Events) so this works uniformly across
    // real users and automated input alike; preventDefault stops the drag
    // from being interpreted as a text selection.
    flagEl.addEventListener('mousedown', (e) => {
      e.preventDefault();
      dragging = true;
      const rect = flagEl.getBoundingClientRect();
      dragOffset.x = e.clientX - rect.left;
      dragOffset.y = e.clientY - rect.top;
      flagEl.classList.add('sft-dragging');
    });

    document.addEventListener('mousemove', (e) => {
      if (!dragging) return;
      const x = clamp(e.clientX - dragOffset.x, 0, window.innerWidth - flagEl.offsetWidth);
      const y = clamp(e.clientY - dragOffset.y, 0, window.innerHeight - flagEl.offsetHeight);
      flagEl.style.left = `${x}px`;
      flagEl.style.top = `${y}px`;
      flagEl.style.right = 'auto';
    });

    document.addEventListener('mouseup', () => {
      if (!dragging) return;
      dragging = false;
      flagEl.classList.remove('sft-dragging');
      writePosition({ left: flagEl.style.left, top: flagEl.style.top });
    });

    readPosition((pos) => {
      if (pos && pos.left && pos.top) {
        flagEl.style.left = pos.left;
        flagEl.style.top = pos.top;
        flagEl.style.right = 'auto';
      }
    });

    return flagEl;
  }

  function updateFlag(score, level) {
    const el = ensureFlag();
    el.querySelector('.sft-flag-pct').textContent = `${score}%`;
    el.className = `sft-flag-level-${level}`;
    if (dragging) el.classList.add('sft-dragging');
    el.title = `Risk level: ${levelLabel(level)} (${score}%) · drag to move`;
  }

  global.SftFlag = { updateFlag };
})(typeof window !== 'undefined' ? window : globalThis);

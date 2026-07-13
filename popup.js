const hasChrome = typeof chrome !== 'undefined' && !!chrome.storage;

function setBadge(el, level, text) {
  el.textContent = text;
  el.className = `risk-badge ${level}`;
}

function renderHitList(el, hits) {
  el.innerHTML = '';
  hits.forEach((h) => {
    const li = document.createElement('li');
    li.textContent = h;
    el.appendChild(li);
  });
}

function loadConversationRisk() {
  const riskBadge = document.getElementById('riskBadge');
  const riskScore = document.getElementById('riskScore');
  const hitList = document.getElementById('hitList');

  if (!hasChrome) {
    riskScore.textContent = 'Not running as an extension (demo preview)';
    return;
  }

  chrome.storage.local.get({ lastRisk: null }, (res) => {
    const risk = res.lastRisk;
    if (!risk) {
      setBadge(riskBadge, 'low', 'None');
      riskScore.textContent = 'No risk signals detected yet.';
      return;
    }
    setBadge(riskBadge, risk.level, risk.level === 'high' ? 'Danger' : risk.level === 'medium' ? 'Caution' : 'Safe');
    riskScore.textContent = `Risk score: ${risk.score} / 100`;
    renderHitList(hitList, risk.hits || []);
  });
}

function initToggle() {
  const toggle = document.getElementById('enabledToggle');
  if (!hasChrome) {
    toggle.disabled = true;
    return;
  }
  chrome.storage.sync.get({ enabled: true }, (res) => {
    toggle.checked = res.enabled !== false;
  });
  toggle.addEventListener('change', () => {
    chrome.storage.sync.set({ enabled: toggle.checked });
  });
}

function initTransactionCalculator() {
  const calcBtn = document.getElementById('calcBtn');
  calcBtn.addEventListener('click', () => {
    const price = Number(document.getElementById('price').value) || 0;
    const marketPrice = Number(document.getElementById('marketPrice').value) || 0;
    const payment = document.getElementById('payment').value;
    const lateNight = document.getElementById('lateNight').checked;

    const result = FraudScorer.scoreTransaction({ price, marketPrice, payment, lateNight });

    document.getElementById('txResultRow').style.display = 'flex';
    setBadge(
      document.getElementById('txRiskBadge'),
      result.level,
      result.level === 'high' ? 'Danger' : result.level === 'medium' ? 'Caution' : 'Safe'
    );
    document.getElementById('txRiskScore').textContent = `Risk score: ${result.score} / 100`;
    renderHitList(document.getElementById('txHitList'), result.hits);
  });
}

loadConversationRisk();
initToggle();
initTransactionCalculator();

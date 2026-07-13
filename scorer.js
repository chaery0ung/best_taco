// Rule-based stand-in for the PRD's "text-based deception detection dataset" model.
// Swap scoreMessage()'s body for a real model/API call later without touching callers.
// Patterns target English-language scam language seen on US marketplaces
// (eBay, OfferUp, Facebook Marketplace).
(function (global) {
  const RULES = [
    {
      id: 'urgency',
      label: 'Manufactured urgency',
      weight: 25,
      patterns: [
        /act\s*fast/i, /sell\s*fast/i,
        /sell\s*(it\s*)?to\s*(someone\s*else|another\s*buyer|them)/i,
        /won'?t\s*last/i, /(other|another)\s*(buyer|people)s?\s*(is\s+|are\s+)?(already\s+)?interested/i,
        /first\s*come,?\s*first\s*served/i, /today\s*only/i, /need\s*(an?\s*)?answer\s*(now|asap)/i,
        /decide\s*(right\s*)?now/i, /hurry/i
      ]
    },
    {
      id: 'off_platform',
      label: 'Redirect off-platform',
      weight: 20,
      patterns: [
        /text\s*me\s*(at|instead|directly)/i, /call\s*me\s*at/i, /email\s*me\s*at/i, /whatsapp/i, /telegram/i,
        /(outside|off)\s*(of\s*)?(the\s*)?(app|platform)/i, /reach\s*me\s*on/i, /message\s*me\s*on\s*(hangouts|whatsapp)/i,
        /\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}/, /[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}/i
      ]
    },
    {
      id: 'verification_phishing',
      label: 'Verification-code phishing',
      weight: 35,
      patterns: [
        /verification\s*code/i, /confirmation\s*code/i, /one[\s-]time\s*(code|password)/i,
        /\botp\b/i, /code\s*i\s*(just\s*)?(sent|texted)/i, /security\s*code/i,
        /code\s*to\s*confirm\s*you'?re\s*real/i
      ]
    },
    {
      id: 'payment_pressure',
      label: 'Overpayment / off-platform payment pressure',
      weight: 30,
      patterns: [
        /cashier'?s?\s*check/i, /send\s*(you\s*)?extra/i, /(refund|send\s*back)\s*(me\s*)?the\s*difference/i,
        /overpay/i, /zelle/i, /cash\s*app/i, /wire\s*transfer/i, /western\s*union/i, /moneygram/i,
        /friends\s*and\s*family/i, /pay\s*(me\s*)?first/i, /send\s*payment\s*first/i
      ]
    },
    {
      id: 'shipping_scam',
      label: 'Shipping / pickup scam',
      weight: 20,
      patterns: [
        /my\s*(own\s*)?shipp(er|ing)/i, /prepaid\s*label/i, /out\s*of\s*town/i,
        /have\s*(my\s*)?(shipper|driver|assistant)\s*(pick|come)/i, /ship\s*it\s*for\s*me/i
      ]
    }
  ];

  function levelFor(score) {
    return score >= 60 ? 'high' : score >= 30 ? 'medium' : 'low';
  }

  function scoreMessage(text) {
    if (!text) return { score: 0, level: 'low', hits: [] };
    const hits = [];
    let score = 0;
    for (const rule of RULES) {
      if (rule.patterns.some((p) => p.test(text))) {
        hits.push({ id: rule.id, label: rule.label });
        score += rule.weight;
      }
    }
    score = Math.min(score, 100);
    return { score, level: levelFor(score), hits };
  }

  // Simplified stand-in for the PRD's "transaction metadata fraud score" (P0).
  // A real version would read the listing's price/payment method automatically;
  // here the popup UI collects them manually for the demo.
  function scoreTransaction({ price, marketPrice, payment, lateNight }) {
    const hits = [];
    let score = 0;
    if (marketPrice && price && price < marketPrice * 0.6) {
      score += 30;
      hits.push('Priced far below market value');
    }
    if (payment === 'prepay_zelle') {
      score += 35;
      hits.push('Prepayment via Zelle/Cash App requested instead of secure checkout');
    }
    if (lateNight) {
      score += 15;
      hits.push('Requesting a late-night (12am-5am) meetup');
    }
    score = Math.min(score, 100);
    return { score, level: levelFor(score), hits };
  }

  global.FraudScorer = { scoreMessage, scoreTransaction, RULES };
})(typeof window !== 'undefined' ? window : globalThis);

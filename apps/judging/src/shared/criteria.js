(function (global) {
  const CRITERIA = {
    azure: [
      { id: 'alignment',    label: 'Alignment to Hackathon Use Case',     weight: 0.20 },
      { id: 'architecture', label: 'Agent Architecture & Foundry Use',    weight: 0.30, tieBreaker: true },
      { id: 'reliability',  label: 'Reliability, Grounding & Guardrails', weight: 0.20 },
      { id: 'ux',           label: 'User Experience & Voice/UI Polish',   weight: 0.15 },
      { id: 'demo',         label: 'Demo Quality & Adoption Readiness',   weight: 0.15 }
    ],
    copilot: [
      { id: 'alignment', label: 'Alignment to Assigned Use Case',      weight: 0.20 },
      { id: 'design',    label: 'Copilot Design & Orchestration',      weight: 0.30, tieBreaker: true },
      { id: 'actions',   label: 'Actions & Automation',                weight: 0.25 },
      { id: 'branding',  label: 'Agent Creativity & Branding',         weight: 0.15 },
      { id: 'demo',      label: 'Demo Quality & Adoption Readiness',   weight: 0.10 }
    ]
  };

  function computeTotal(track, criteria) {
    const defs = CRITERIA[track];
    if (!defs) return null;
    if (!criteria || typeof criteria !== 'object') return null;
    let total = 0;
    for (const d of defs) {
      const v = Number(criteria[d.id]);
      if (!Number.isFinite(v) || v < 1 || v > 5) return null;
      total += v * d.weight * 20;
    }
    return Math.round(total * 10) / 10;
  }

  function tier(total) {
    if (total === null || total === undefined || Number.isNaN(total)) return 'Needs work';
    if (total >= 90) return 'Exceptional';
    if (total >= 70) return 'Strong';
    if (total >= 50) return 'Developing';
    return 'Needs work';
  }

  function tieBreakerId(track) {
    const defs = CRITERIA[track];
    if (!defs) return null;
    const tb = defs.find(d => d.tieBreaker);
    return tb ? tb.id : null;
  }

  const API = { CRITERIA, computeTotal, tier, tieBreakerId };
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = API;
  } else {
    global.MTAHackCriteria = API;
  }
})(typeof window !== 'undefined' ? window : globalThis);

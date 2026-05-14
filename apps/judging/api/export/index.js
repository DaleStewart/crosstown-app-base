const { getContainer } = require('../_shared/cosmos');
const { requireAdmin } = require('../_shared/auth');
const { CRITERIA, tier, tieBreakerId } = require('../_shared/criteria');

function csvEscape(v) {
  if (v === null || v === undefined) return '';
  const s = String(v);
  if (/[",\r\n]/.test(s)) return '"' + s.replace(/"/g, '""') + '"';
  return s;
}

module.exports = async function (context, req) {
  const { res: authRes } = requireAdmin(req);
  if (authRes) { context.res = authRes; return; }

  const track = (req.query.track || '').toLowerCase();
  const defs = CRITERIA[track];
  if (!defs) {
    context.res = { status: 400, body: { error: 'track query param must be one of: azure, copilot' } };
    return;
  }

  try {
    const scoresContainer = getContainer('scores');
    const { resources: scores } = await scoresContainer.items.query({
      query: 'SELECT * FROM c WHERE c.track = @t',
      parameters: [{ name: '@t', value: track }]
    }, { partitionKey: track }).fetchAll();

    // Compute team ranks so we can stamp them on each row.
    const byTeam = new Map();
    for (const s of scores) {
      if (!byTeam.has(s.teamId)) byTeam.set(s.teamId, { teamId: s.teamId, teamName: s.teamName || s.teamId, totals: [], perCriterion: {} });
      const agg = byTeam.get(s.teamId);
      agg.totals.push(Number(s.total) || 0);
      for (const d of defs) {
        const v = Number(s.criteria && s.criteria[d.id]);
        if (Number.isFinite(v)) {
          if (!agg.perCriterion[d.id]) agg.perCriterion[d.id] = [];
          agg.perCriterion[d.id].push(v);
        }
      }
    }
    const avg = arr => (arr && arr.length ? arr.reduce((a, b) => a + b, 0) / arr.length : 0);
    const tbId = tieBreakerId(track);
    const summary = Array.from(byTeam.values()).map(a => ({
      teamId: a.teamId,
      teamName: a.teamName,
      avgTotal: Math.round(avg(a.totals) * 10) / 10,
      tieBreakerAvg: tbId ? Math.round(avg(a.perCriterion[tbId] || []) * 100) / 100 : 0
    }));
    summary.sort((a, b) => {
      if (b.avgTotal !== a.avgTotal) return b.avgTotal - a.avgTotal;
      if (b.tieBreakerAvg !== a.tieBreakerAvg) return b.tieBreakerAvg - a.tieBreakerAvg;
      return a.teamName.localeCompare(b.teamName);
    });
    const rankByTeam = new Map();
    summary.forEach((s, i) => rankByTeam.set(s.teamId, i + 1));

    const criterionIds = defs.map(d => d.id);
    const header = ['rank', 'team', 'judge', 'total', 'tier', ...criterionIds, 'notes'];
    const lines = [header.join(',')];

    scores.sort((a, b) => {
      const ra = rankByTeam.get(a.teamId) || 9999;
      const rb = rankByTeam.get(b.teamId) || 9999;
      if (ra !== rb) return ra - rb;
      return String(a.judgeEmail).localeCompare(String(b.judgeEmail));
    });

    for (const s of scores) {
      const notesCombined = criterionIds
        .map(id => (s.notes && s.notes[id] ? `${id}: ${s.notes[id]}` : null))
        .filter(Boolean)
        .join(' | ');
      const row = [
        rankByTeam.get(s.teamId) || '',
        s.teamName || s.teamId,
        s.judgeEmail,
        s.total,
        s.tier || tier(s.total),
        ...criterionIds.map(id => (s.criteria && s.criteria[id] != null ? s.criteria[id] : '')),
        notesCombined
      ];
      lines.push(row.map(csvEscape).join(','));
    }

    const iso = new Date().toISOString().replace(/[:.]/g, '-');
    context.res = {
      status: 200,
      headers: {
        'Content-Type': 'text/csv; charset=utf-8',
        'Content-Disposition': `attachment; filename="scores-${track}-${iso}.csv"`
      },
      body: lines.join('\r\n')
    };
  } catch (err) {
    context.log.error('export failed', err);
    context.res = { status: 500, body: { error: 'Failed to export scores' } };
  }
};

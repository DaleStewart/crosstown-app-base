const { getContainer } = require('../_shared/cosmos');
const { requireAuth } = require('../_shared/auth');
const { CRITERIA, tier, tieBreakerId } = require('../_shared/criteria');

module.exports = async function (context, req) {
  const { res: authRes } = requireAuth(req);
  if (authRes) { context.res = authRes; return; }

  const track = (req.query.track || '').toLowerCase();
  const defs = CRITERIA[track];
  if (!defs) {
    context.res = { status: 400, body: { error: 'track query param must be one of: azure, copilot' } };
    return;
  }
  const tbId = tieBreakerId(track);

  try {
    const container = getContainer('scores');
    const { resources: scores } = await container.items.query({
      query: 'SELECT * FROM c WHERE c.track = @t',
      parameters: [{ name: '@t', value: track }]
    }, { partitionKey: track }).fetchAll();

    const byTeam = new Map();
    for (const s of scores) {
      if (!byTeam.has(s.teamId)) {
        byTeam.set(s.teamId, { teamId: s.teamId, teamName: s.teamName || s.teamId, totals: [], perCriterion: {} });
      }
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

    const rows = Array.from(byTeam.values()).map(agg => {
      const avgTotal = Math.round(avg(agg.totals) * 10) / 10;
      const avgPerCriterion = {};
      for (const d of defs) {
        avgPerCriterion[d.id] = Math.round(avg(agg.perCriterion[d.id] || []) * 100) / 100;
      }
      return {
        teamId: agg.teamId,
        teamName: agg.teamName,
        judgeCount: agg.totals.length,
        avgTotal,
        avgPerCriterion,
        tieBreakerAvg: tbId ? avgPerCriterion[tbId] : 0,
        tier: tier(avgTotal)
      };
    });

    rows.sort((a, b) => {
      if (b.avgTotal !== a.avgTotal) return b.avgTotal - a.avgTotal;
      if (b.tieBreakerAvg !== a.tieBreakerAvg) return b.tieBreakerAvg - a.tieBreakerAvg;
      return a.teamName.localeCompare(b.teamName);
    });
    rows.forEach((r, i) => { r.rank = i + 1; });

    context.res = { status: 200, headers: { 'Content-Type': 'application/json' }, body: rows };
  } catch (err) {
    context.log.error('leaderboard failed', err);
    context.res = { status: 500, body: { error: 'Failed to build leaderboard' } };
  }
};

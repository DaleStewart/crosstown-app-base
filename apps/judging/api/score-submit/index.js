const { getContainer } = require('../_shared/cosmos');
const { requireAuth } = require('../_shared/auth');
const { CRITERIA, computeTotal, tier } = require('../_shared/criteria');
const { logEvent } = require('../_shared/audit');

async function isTrackLocked(track) {
  try {
    const events = getContainer('events');
    const { resource } = await events.item(`lock-status-${track}`, track).read();
    return !!(resource && resource.payload && resource.payload.locked);
  } catch (err) {
    if (err && err.code === 404) return false;
    throw err;
  }
}

module.exports = async function (context, req) {
  const { user, res: authRes } = requireAuth(req);
  if (authRes) { context.res = authRes; return; }

  const body = req.body || {};
  const teamId = typeof body.teamId === 'string' ? body.teamId.trim() : '';
  const track = typeof body.track === 'string' ? body.track.toLowerCase() : '';
  const criteria = body.criteria && typeof body.criteria === 'object' ? body.criteria : null;
  const notes = body.notes && typeof body.notes === 'object' ? body.notes : {};

  if (!teamId) { context.res = { status: 400, body: { error: 'teamId is required' } }; return; }
  const defs = CRITERIA[track];
  if (!defs) { context.res = { status: 400, body: { error: 'track must be one of: azure, copilot' } }; return; }
  if (!criteria) { context.res = { status: 400, body: { error: 'criteria object is required' } }; return; }

  const allowed = new Set(defs.map(d => d.id));
  for (const k of Object.keys(criteria)) {
    if (!allowed.has(k)) {
      context.res = { status: 400, body: { error: `Unknown criterion: ${k}` } };
      return;
    }
  }
  for (const d of defs) {
    const v = criteria[d.id];
    if (!Number.isInteger(v) || v < 1 || v > 5) {
      context.res = { status: 400, body: { error: `criteria.${d.id} must be an integer 1-5` } };
      return;
    }
  }
  const cleanNotes = {};
  for (const d of defs) {
    if (typeof notes[d.id] === 'string') cleanNotes[d.id] = notes[d.id].slice(0, 2000);
  }

  try {
    if (await isTrackLocked(track)) {
      context.res = { status: 423, body: { error: `Track '${track}' is locked for scoring` } };
      return;
    }

    const total = computeTotal(track, criteria);
    if (total === null) {
      context.res = { status: 400, body: { error: 'Invalid criteria values' } };
      return;
    }

    const teamsContainer = getContainer('teams');
    let teamName = teamId;
    try {
      const { resource: team } = await teamsContainer.item(teamId, track).read();
      if (!team) {
        context.res = { status: 404, body: { error: 'Team not found' } };
        return;
      }
      teamName = team.name || teamId;
    } catch (err) {
      if (err && err.code === 404) {
        context.res = { status: 404, body: { error: 'Team not found' } };
        return;
      }
      throw err;
    }

    const doc = {
      id: `${user.email}|${teamId}`,
      judgeEmail: user.email,
      judgeName: user.name,
      teamId,
      teamName,
      track,
      criteria,
      notes: cleanNotes,
      total,
      tier: tier(total),
      submittedAt: new Date().toISOString(),
      locked: false
    };

    const scores = getContainer('scores');
    const { resource } = await scores.items.upsert(doc);
    await logEvent({ action: 'score.submit', actor: user.email, track, payload: { teamId, total } });

    context.res = { status: 200, body: resource };
  } catch (err) {
    context.log.error('score-submit failed', err);
    context.res = { status: 500, body: { error: 'Failed to submit score' } };
  }
};

const crypto = require('crypto');
const { getContainer } = require('../_shared/cosmos');
const { requireAdmin } = require('../_shared/auth');
const { CRITERIA } = require('../_shared/criteria');
const { logEvent } = require('../_shared/audit');

module.exports = async function (context, req) {
  const { user, res: authRes } = requireAdmin(req);
  if (authRes) { context.res = authRes; return; }

  const body = req.body || {};
  const name = typeof body.name === 'string' ? body.name.trim() : '';
  const track = typeof body.track === 'string' ? body.track.toLowerCase() : '';
  const members = Array.isArray(body.members) ? body.members.map(m => String(m).trim()).filter(Boolean) : [];
  const room = typeof body.room === 'string' ? body.room.trim() : '';
  const slot = typeof body.slot === 'string' ? body.slot.trim() : '';

  if (!name) { context.res = { status: 400, body: { error: 'name is required' } }; return; }
  if (!CRITERIA[track]) { context.res = { status: 400, body: { error: 'track must be one of: azure, copilot' } }; return; }

  const team = {
    id: crypto.randomUUID(),
    name,
    track,
    members,
    room,
    slot,
    createdAt: new Date().toISOString(),
    createdBy: user.email
  };

  try {
    const container = getContainer('teams');
    const { resource } = await container.items.upsert(team);
    await logEvent({ action: 'team.create', actor: user.email, track, payload: { teamId: team.id, name } });
    context.res = { status: 201, body: resource };
  } catch (err) {
    context.log.error('teams-create failed', err);
    context.res = { status: 500, body: { error: 'Failed to create team' } };
  }
};

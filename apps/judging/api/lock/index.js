const { getContainer } = require('../_shared/cosmos');
const { requireAuth, requireAdmin } = require('../_shared/auth');
const { CRITERIA } = require('../_shared/criteria');
const { logEvent } = require('../_shared/audit');

async function readLockStatus(track) {
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
  const method = (req.method || 'GET').toUpperCase();

  if (method === 'GET') {
    const { res: authRes } = requireAuth(req);
    if (authRes) { context.res = authRes; return; }

    const track = ((req.query && req.query.track) || '').toLowerCase();
    if (!CRITERIA[track]) {
      context.res = { status: 400, body: { error: 'track query param must be one of: azure, copilot' } };
      return;
    }
    try {
      const locked = await readLockStatus(track);
      context.res = { status: 200, body: { track, locked } };
    } catch (err) {
      context.log.error('lock status read failed', err);
      context.res = { status: 500, body: { error: 'Failed to read lock status' } };
    }
    return;
  }

  const { user, res: authRes } = requireAdmin(req);
  if (authRes) { context.res = authRes; return; }

  const body = req.body || {};
  const track = typeof body.track === 'string' ? body.track.toLowerCase() : '';
  const locked = body.locked === true;

  if (!CRITERIA[track]) {
    context.res = { status: 400, body: { error: 'track must be one of: azure, copilot' } };
    return;
  }

  try {
    const events = getContainer('events');
    const statusDoc = {
      id: `lock-status-${track}`,
      track,
      action: locked ? 'lock' : 'unlock',
      actor: user.email,
      payload: { locked },
      ts: new Date().toISOString()
    };
    await events.items.upsert(statusDoc);
    await logEvent({ action: locked ? 'lock' : 'unlock', actor: user.email, track, payload: { locked } });

    context.res = { status: 200, body: { track, locked } };
  } catch (err) {
    context.log.error('lock failed', err);
    context.res = { status: 500, body: { error: 'Failed to update lock status' } };
  }
};

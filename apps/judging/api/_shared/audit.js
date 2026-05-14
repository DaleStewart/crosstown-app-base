const crypto = require('crypto');
const { getContainer } = require('./cosmos');

async function logEvent({ action, actor, track, payload }) {
  try {
    const events = getContainer('events');
    const doc = {
      id: crypto.randomUUID(),
      action: action || 'unknown',
      actor: actor || null,
      track: track || 'system',
      payload: payload || null,
      ts: new Date().toISOString()
    };
    await events.items.upsert(doc);
    return doc;
  } catch (err) {
    // Audit failures should not break the request flow.
    // eslint-disable-next-line no-console
    console.error('audit.logEvent failed', err && err.message);
    return null;
  }
}

module.exports = { logEvent };

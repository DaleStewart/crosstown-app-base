const { getContainer } = require('../_shared/cosmos');
const { requireAdmin } = require('../_shared/auth');

module.exports = async function (context, req) {
  const { res: authRes } = requireAdmin(req);
  if (authRes) { context.res = authRes; return; }

  const limit = Math.min(Math.max(parseInt(req.query.limit, 10) || 200, 1), 1000);

  try {
    const events = getContainer('events');
    const { resources } = await events.items.query({
      query: 'SELECT TOP @n c.id, c.actor, c.ts, c.payload FROM c WHERE c.action = "auth.login" AND c.track = "system" ORDER BY c.ts DESC',
      parameters: [{ name: '@n', value: limit }]
    }, { partitionKey: 'system' }).fetchAll();

    // Group by actor for a unique-user summary
    const byActor = new Map();
    for (const r of resources) {
      const a = (r.actor || 'unknown').toLowerCase();
      if (!byActor.has(a)) {
        byActor.set(a, {
          actor: a,
          name: (r.payload && r.payload.name) || null,
          email: (r.payload && r.payload.email) || null,
          provider: (r.payload && r.payload.identityProvider) || null,
          roles: (r.payload && r.payload.roles) || [],
          firstSeen: r.ts,
          lastSeen: r.ts,
          loginCount: 0
        });
      }
      const e = byActor.get(a);
      e.loginCount += 1;
      if (r.ts < e.firstSeen) e.firstSeen = r.ts;
      if (r.ts > e.lastSeen) e.lastSeen = r.ts;
    }

    const summary = Array.from(byActor.values()).sort((a, b) => b.lastSeen.localeCompare(a.lastSeen));

    context.res = {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
      body: {
        totalLogins: resources.length,
        uniqueUsers: summary.length,
        users: summary,
        recent: resources.slice(0, 50)
      }
    };
  } catch (err) {
    context.log.error('logins failed', err && err.message);
    context.res = {
      status: 500,
      body: { error: 'Failed to load logins', detail: err && err.message }
    };
  }
};

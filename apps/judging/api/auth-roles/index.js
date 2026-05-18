const { logEvent } = require('../_shared/audit');

module.exports = async function (context, req) {
  const principal = req.body || {};
  const adminList = (process.env.ADMIN_USERS || process.env.ADMIN_EMAILS || '')
    .split(',')
    .map(s => s.trim().toLowerCase())
    .filter(Boolean);
  const claims = Array.isArray(principal.claims) ? principal.claims : [];
  const emailClaim = claims.find(c => c.typ === 'preferred_username' || c.typ === 'emails' || c.typ === 'email');
  const nameClaim = claims.find(c => c.typ === 'name');
  const candidate = ((principal.userDetails || '') + '').toLowerCase();
  const emailCandidate = ((emailClaim && emailClaim.val) || '').toLowerCase();
  const roles = [];
  if (candidate && adminList.includes(candidate)) roles.push('admin');
  else if (emailCandidate && adminList.includes(emailCandidate)) roles.push('admin');

  // Best-effort login tracking — fire-and-forget so a Cosmos hiccup never blocks login.
  try {
    const actor = candidate || emailCandidate || (principal.userId || '');
    if (actor) {
      const ua = (req.headers && (req.headers['user-agent'] || req.headers['User-Agent'])) || '';
      const ip = (req.headers && (req.headers['x-forwarded-for'] || req.headers['client-ip'])) || '';
      logEvent({
        action: 'auth.login',
        actor,
        track: 'system',
        payload: {
          userDetails: principal.userDetails || null,
          name: (nameClaim && nameClaim.val) || null,
          identityProvider: principal.identityProvider || 'github',
          userId: principal.userId || null,
          email: emailCandidate || null,
          roles,
          userAgent: ua.slice(0, 240),
          remoteAddr: String(ip).split(',')[0].trim()
        }
      });
    }
  } catch (_e) { /* swallow */ }

  context.res = { status: 200, body: { roles } };
};


function getUser(req) {
  try {
    const header = req.headers && (req.headers['x-ms-client-principal'] || req.headers['X-MS-CLIENT-PRINCIPAL']);
    if (!header) return null;
    const decoded = Buffer.from(header, 'base64').toString('utf8');
    const principal = JSON.parse(decoded);
    const claims = Array.isArray(principal.claims) ? principal.claims : [];
    const emailClaim = claims.find(c => c.typ === 'preferred_username' || c.typ === 'emails' || c.typ === 'email');
    const nameClaim = claims.find(c => c.typ === 'name');
    const email = (principal.userDetails || (emailClaim && emailClaim.val) || '').toLowerCase();
    const name = (nameClaim && nameClaim.val) || principal.userDetails || email;
    const roles = Array.isArray(principal.userRoles) ? principal.userRoles : [];
    return { email, name, roles, identityProvider: principal.identityProvider };
  } catch (_e) {
    return null;
  }
}

function isAdmin(user) {
  if (!user) return false;
  if (Array.isArray(user.roles) && user.roles.includes('admin')) return true;
  const adminEmails = (process.env.ADMIN_EMAILS || '')
    .split(',')
    .map(s => s.trim().toLowerCase())
    .filter(Boolean);
  return !!user.email && adminEmails.includes(user.email);
}

function requireAuth(req) {
  const user = getUser(req);
  if (!user || !user.email) {
    return { user: null, res: { status: 401, body: { error: 'Authentication required' } } };
  }
  return { user, res: null };
}

function requireAdmin(req) {
  const { user, res } = requireAuth(req);
  if (res) return { user: null, res };
  if (!isAdmin(user)) {
    return { user: null, res: { status: 403, body: { error: 'Admin role required' } } };
  }
  return { user, res: null };
}

module.exports = { getUser, isAdmin, requireAuth, requireAdmin };

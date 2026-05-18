module.exports = async function (context, req) {
  const principal = req.body || {};
  const adminList = (process.env.ADMIN_USERS || process.env.ADMIN_EMAILS || '')
    .split(',')
    .map(s => s.trim().toLowerCase())
    .filter(Boolean);
  const claims = Array.isArray(principal.claims) ? principal.claims : [];
  const emailClaim = claims.find(c => c.typ === 'preferred_username' || c.typ === 'emails' || c.typ === 'email');
  const candidate = ((principal.userDetails || '') + '').toLowerCase();
  const emailCandidate = ((emailClaim && emailClaim.val) || '').toLowerCase();
  const roles = [];
  if (candidate && adminList.includes(candidate)) roles.push('admin');
  else if (emailCandidate && adminList.includes(emailCandidate)) roles.push('admin');
  context.res = { status: 200, body: { roles } };
};

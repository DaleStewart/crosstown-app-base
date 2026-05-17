/**
 * Thin wrapper around Azure Static Web Apps auth.
 * window.MTAAuth.getUser() returns a cached promise that resolves to
 *   { email, name, roles: string[], raw: clientPrincipal }
 * or null if not signed in.
 */
(function () {
  'use strict';
  let cached = null;

  function pickClaim(claims, types) {
    if (!Array.isArray(claims)) return null;
    for (const t of types) {
      const hit = claims.find(function (c) { return c && c.typ === t; });
      if (hit && hit.val) return hit.val;
    }
    return null;
  }

  function normalize(cp) {
    if (!cp) return null;
    const claims = cp.claims || [];
    const email =
      pickClaim(claims, [
        'preferred_username',
        'emails',
        'email',
        'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress'
      ]) || cp.userDetails || null;
    const name =
      pickClaim(claims, [
        'name',
        'given_name',
        'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name'
      ]) || cp.userDetails || email || 'Judge';
    return {
      email: email,
      name: name,
      roles: Array.isArray(cp.userRoles) ? cp.userRoles : [],
      raw: cp
    };
  }

  function getUser() {
    if (cached) return cached;
    cached = fetch('/.auth/me', { credentials: 'include' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) {
        if (!data || !data.clientPrincipal) return null;
        return normalize(data.clientPrincipal);
      })
      .catch(function () { return null; });
    return cached;
  }

  function isAdmin(user) {
    return !!(user && user.roles && user.roles.indexOf('admin') !== -1);
  }

  /**
   * Render the standard topbar (user + sign-out). Call after getUser resolves.
   * Mounts into the element with id="topbar-user" if present.
   */
  function mountTopbar(user) {
    const host = document.getElementById('topbar-user');
    if (!host) return;
    if (!user) {
      host.innerHTML =
        '<a href="/.auth/login/github"><i class="ti ti-login-2"></i> Sign in</a>';
      return;
    }
    const label = user.name || user.email || 'Signed in';
    host.innerHTML =
      '<span class="who"><i class="ti ti-user-circle"></i>' +
      escapeHtml(label) +
      '</span>' +
      '<a class="signout" href="/.auth/logout"><i class="ti ti-logout"></i> Sign out</a>';
  }

  function escapeHtml(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  window.MTAAuth = { getUser: getUser, isAdmin: isAdmin, mountTopbar: mountTopbar, escapeHtml: escapeHtml };
}());

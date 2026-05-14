/**
 * Tiny bottom-right toast.
 * Usage: toast('Saved', 'success'); toast('Failed', 'error');
 * Kinds: 'info' (default) | 'success' | 'error'
 */
(function () {
  'use strict';

  function container() {
    let el = document.getElementById('toast-container');
    if (!el) {
      el = document.createElement('div');
      el.id = 'toast-container';
      document.body.appendChild(el);
    }
    return el;
  }

  function toast(message, kind) {
    kind = kind || 'info';
    const host = container();
    const el = document.createElement('div');
    el.className = 'toast ' + kind;
    el.setAttribute('role', kind === 'error' ? 'alert' : 'status');
    el.setAttribute('aria-live', kind === 'error' ? 'assertive' : 'polite');
    el.textContent = String(message == null ? '' : message);
    host.appendChild(el);
    // Force reflow then animate in
    void el.offsetWidth;
    el.classList.add('show');
    const ttl = kind === 'error' ? 4500 : 2800;
    setTimeout(function () {
      el.classList.remove('show');
      setTimeout(function () { el.remove(); }, 250);
    }, ttl);
  }

  window.toast = toast;
}());

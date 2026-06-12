/**
 * api.js — Cliente central para a API REST do Mãos em Ação
 * Gerencia CSRF, autenticação e todas as chamadas HTTP.
 */

const API = (() => {
  // ─── CSRF ────────────────────────────────────────────────────────────────
  function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)'));
    return match ? match[2] : null;
  }

  async function ensureCsrf() {
    if (!getCookie('csrftoken')) {
      await fetch('/api/csrf/', { credentials: 'include' });
    }
    return getCookie('csrftoken');
  }

  // ─── BASE REQUEST ─────────────────────────────────────────────────────────
  async function request(method, url, body = null) {
    const csrfToken = await ensureCsrf();
    const options = {
      method,
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
    };
    if (body) options.body = JSON.stringify(body);

    const res = await fetch(url, options);
    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      const msg = data.error || data.detail || `Erro ${res.status}`;
      throw new Error(msg);
    }
    return data;
  }

  // ─── PROFILE ──────────────────────────────────────────────────────────────
  const profile = {
    get: () => request('GET', '/api/profile/'),
    create: (payload) => request('POST', '/api/profile/', payload),
    update: (payload) => request('PUT', '/api/profile/', payload),
  };

  // ─── VACANCIES ────────────────────────────────────────────────────────────
  const vacancies = {
    list: () => request('GET', '/api/vacancies/'),
    get: (id) => request('GET', `/api/vacancies/${id}/`),
    create: (payload) => request('POST', '/api/vacancies/', payload),
    update: (id, payload) => request('PUT', `/api/vacancies/${id}/`, payload),
    delete: (id) => request('DELETE', `/api/vacancies/${id}/`),
    apply: (id) => request('POST', `/api/vacancies/${id}/apply/`),
  };

  // ─── APPLICATIONS ─────────────────────────────────────────────────────────
  const applications = {
    list: () => request('GET', '/api/applications/'),
    updateStatus: (id, status) => request('PATCH', `/api/applications/${id}/`, { status }),
    cancel: (id) => request('DELETE', `/api/applications/${id}/`),
  };

  // ─── UI HELPERS ───────────────────────────────────────────────────────────
  function showToast(message, type = 'success') {
    const existing = document.querySelector('.toast-msg');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = 'toast-msg';
    toast.textContent = message;
    toast.style.cssText = `
      position: fixed; bottom: 1.5rem; right: 1.5rem; z-index: 9999;
      padding: 0.75rem 1.25rem; border-radius: 8px; font-size: 0.875rem;
      font-weight: 500; box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      background: ${type === 'success' ? '#16A34A' : '#DC2626'}; color: white;
      animation: fadeIn 0.2s ease;
    `;
    document.head.insertAdjacentHTML('beforeend', `<style>@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}</style>`);
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3500);
  }

  function setLoading(el, loading) {
    if (!el) return;
    if (loading) {
      el.dataset.originalText = el.textContent;
      el.textContent = 'Carregando...';
      el.disabled = true;
    } else {
      el.textContent = el.dataset.originalText || el.textContent;
      el.disabled = false;
    }
  }

  function statusBadge(status) {
    const map = {
      PENDING:  { label: 'Pendente',  cls: 'badge-warning' },
      ACCEPTED: { label: 'Aceito',    cls: 'badge-success' },
      REJECTED: { label: 'Rejeitado', cls: 'badge-danger'  },
    };
    const s = map[status] || { label: status, cls: 'badge-primary' };
    return `<span class="badge ${s.cls}">${s.label}</span>`;
  }

  function formatDate(iso) {
    if (!iso) return '—';
    return new Date(iso).toLocaleDateString('pt-BR');
  }

  // Lê ?id= da URL
  function getUrlId() {
    return new URLSearchParams(window.location.search).get('id');
  }

  return { profile, vacancies, applications, showToast, setLoading, statusBadge, formatDate, getUrlId };
})();
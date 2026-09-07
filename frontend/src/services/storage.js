/**
 * Safe session storage.
 *
 * This app is served inside a cross-origin preview iframe. Browsers may
 * partition or outright block `localStorage` there, and when it is blocked
 * merely *touching* the object throws a SecurityError. An unguarded
 * `localStorage.setItem` therefore aborts the caller — which in `login()`
 * meant the token never reached React state and the app bounced straight back
 * to the login page.
 *
 * So: React state is the source of truth for the session, and persistence is
 * best-effort. If storage is unavailable we keep an in-memory copy so the
 * session still works for the life of the tab.
 */

const memory = new Map();

function detectStore() {
  try {
    const probe = '__adaptivelearn_storage_probe__';
    window.localStorage.setItem(probe, '1');
    window.localStorage.removeItem(probe);
    return window.localStorage;
  } catch {
    return null;
  }
}

const store = typeof window === 'undefined' ? null : detectStore();

export const storage = {
  /** False when the browser blocked localStorage; the session is memory-only. */
  get persistent() {
    return store !== null;
  },

  get(key) {
    try {
      const value = store ? store.getItem(key) : null;
      if (value !== null && value !== undefined) return value;
    } catch {
      /* fall through to the in-memory copy */
    }
    return memory.has(key) ? memory.get(key) : null;
  },

  set(key, value) {
    memory.set(key, value);
    try {
      store?.setItem(key, value);
    } catch {
      /* memory-only is fine; the session still works this tab */
    }
  },

  remove(key) {
    memory.delete(key);
    try {
      store?.removeItem(key);
    } catch {
      /* nothing else to do */
    }
  },
};

export const TOKEN_KEY = 'token';
export const USER_KEY = 'user';

export default storage;

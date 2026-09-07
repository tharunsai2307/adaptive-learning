import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';
import storage, { TOKEN_KEY, USER_KEY } from '../services/storage';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const raw = storage.get(USER_KEY);
    try {
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  });
  const [token, setToken] = useState(() => storage.get(TOKEN_KEY));
  const [loading, setLoading] = useState(true);

  // Validate a stored token once on boot, so a stale session does not leave the
  // user on a page whose every API call 401s.
  useEffect(() => {
    let cancelled = false;

    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }

    authAPI
      .me()
      .then((res) => {
        if (cancelled) return;
        const u = res.data?.user;
        if (u) {
          setUser(u);
          storage.set(USER_KEY, JSON.stringify(u));
        }
      })
      .catch((err) => {
        if (cancelled) return;
        // Only a real 401 means the token is bad. A network blip or a 5xx must
        // not log the student out — keep the session and let them retry.
        if (err?.response?.status === 401) {
          storage.remove(TOKEN_KEY);
          storage.remove(USER_KEY);
          setToken(null);
          setUser(null);
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [token]);

  const login = (newToken, userData) => {
    // State first: the session must work even when the browser has blocked
    // localStorage (cross-origin preview iframe). Persistence is best-effort.
    setToken(newToken);
    setUser(userData);
    storage.set(TOKEN_KEY, newToken);
    storage.set(USER_KEY, JSON.stringify(userData));
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    storage.remove(TOKEN_KEY);
    storage.remove(USER_KEY);
  };

  return (
    <AuthContext.Provider
      value={{ user, token, loading, login, logout, storageIsPersistent: storage.persistent }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);

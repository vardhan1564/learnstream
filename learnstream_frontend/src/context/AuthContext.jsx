import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import api, { storage } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => (storage.getToken() ? storage.getUser() : null));

  const login = useCallback(async (email, password) => {
    const { data } = await api.post('/api/auth/login', { email, password });
    storage.save(data.token, data.user);
    setUser(data.user);
    return data.user;
  }, []);

  const logout = useCallback(() => {
    storage.clear();
    setUser(null);
  }, []);

  const updateUser = useCallback((next) => {
    setUser((prev) => {
      const merged = { ...prev, ...next };
      storage.saveUser(merged);
      return merged;
    });
  }, []);

  // Logged out by the API interceptor (expired token) or in another tab
  useEffect(() => {
    const onLogout = () => setUser(null);
    const onStorage = (e) => {
      if (e.key === 'ls_token' || e.key === 'ls_user') {
        setUser(storage.getToken() ? storage.getUser() : null);
      }
    };
    window.addEventListener('ls:logout', onLogout);
    window.addEventListener('storage', onStorage);
    return () => {
      window.removeEventListener('ls:logout', onLogout);
      window.removeEventListener('storage', onStorage);
    };
  }, []);

  // Refresh name/role from the server once per page load (role changes take effect without re-login)
  useEffect(() => {
    if (!storage.getToken()) return;
    api.get('/api/users/me')
      .then(({ data }) => updateUser({ id: data.id, fullName: data.fullName, email: data.email, role: data.role }))
      .catch(() => { /* interceptor handles 401 */ });
  }, [updateUser]);

  const value = useMemo(() => ({
    user,
    isLoggedIn: !!user,
    isAdmin: user?.role === 'ROLE_ADMIN',
    login,
    logout,
    updateUser,
  }), [user, login, logout, updateUser]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
}

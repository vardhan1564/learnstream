import axios from 'axios';

export const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8080').replace(/\/$/, '');

const api = axios.create({ baseURL: API_URL, timeout: 60000 });

const TOKEN_KEY = 'ls_token';
const USER_KEY = 'ls_user';

export const storage = {
  getToken: () => { try { return localStorage.getItem(TOKEN_KEY); } catch { return null; } },
  getUser: () => {
    try { return JSON.parse(localStorage.getItem(USER_KEY)); } catch { return null; }
  },
  save: (token, user) => {
    try {
      localStorage.setItem(TOKEN_KEY, token);
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    } catch { /* storage disabled */ }
  },
  saveUser: (user) => { try { localStorage.setItem(USER_KEY, JSON.stringify(user)); } catch { /* ignore */ } },
  clear: () => {
    try { localStorage.removeItem(TOKEN_KEY); localStorage.removeItem(USER_KEY); } catch { /* ignore */ }
  },
};

api.interceptors.request.use((config) => {
  const token = storage.getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// When the session expires the backend answers 401 -> log out everywhere.
api.interceptors.response.use(
  (res) => res,
  (error) => {
    const status = error.response?.status;
    const url = error.config?.url || '';
    if (status === 401 && !url.startsWith('/api/auth/') && storage.getToken()) {
      storage.clear();
      window.dispatchEvent(new Event('ls:logout'));
    }
    return Promise.reject(error);
  }
);

/** Human-readable message from any API error. */
export function errorMessage(error, fallback = 'Something went wrong. Please try again.') {
  if (!error) return fallback;
  if (error.code === 'ECONNABORTED') return 'The server took too long to respond. Please try again.';
  if (!error.response) return 'Cannot reach the server. Check that the backend is running and you are online.';
  const data = error.response.data;
  if (data && typeof data === 'object' && data.message) return data.message;
  if (typeof data === 'string' && data.length < 300) return data;
  return fallback;
}

/** Downloads a file from an authenticated endpoint. */
export async function downloadFile(path, fallbackName) {
  const res = await api.get(path, { responseType: 'blob' });
  const disposition = res.headers['content-disposition'] || '';
  const match = /filename="?([^";]+)"?/i.exec(disposition);
  const name = match ? match[1] : fallbackName;
  const url = URL.createObjectURL(res.data);
  const a = document.createElement('a');
  a.href = url;
  a.download = name;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 2000);
}

/** Blob error responses (e.g. failed PDF download) need to be read as text to get the message. */
export async function blobErrorMessage(error, fallback) {
  const data = error?.response?.data;
  if (data instanceof Blob) {
    try {
      const parsed = JSON.parse(await data.text());
      if (parsed.message) return parsed.message;
    } catch { /* not JSON */ }
  }
  return errorMessage(error, fallback);
}

export default api;

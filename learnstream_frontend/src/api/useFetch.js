import { useCallback, useEffect, useState } from 'react';
import api, { errorMessage } from './client';

/**
 * GET `url` when it changes. Returns { data, error, loading, reload, setData }.
 * Pass null as url to skip fetching.
 */
export default function useFetch(url) {
  const [state, setState] = useState({ url: null, data: null, error: '' });
  const [nonce, setNonce] = useState(0);

  useEffect(() => {
    if (!url) return undefined;
    let cancelled = false;
    api.get(url)
      .then((r) => { if (!cancelled) setState({ url, data: r.data, error: '' }); })
      .catch((e) => { if (!cancelled) setState({ url, data: null, error: errorMessage(e) }); });
    return () => { cancelled = true; };
  }, [url, nonce]);

  const reload = useCallback(() => setNonce((n) => n + 1), []);
  const setData = useCallback((next) => {
    setState((s) => ({ ...s, data: typeof next === 'function' ? next(s.data) : next }));
  }, []);

  const current = state.url === url;
  return {
    data: current ? state.data : null,
    error: current ? state.error : '',
    loading: !!url && !current,
    reload,
    setData,
  };
}

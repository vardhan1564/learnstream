import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FiInbox } from 'react-icons/fi';

export function Loader({ label = 'Loading' }) {
  return (
    <div className="loader" role="status" aria-live="polite">
      <div className="spinner" />
      <span className="sr-only">{label}</span>
    </div>
  );
}

export function EmptyState({ icon: Icon = FiInbox, title, children, action }) {
  return (
    <div className="empty">
      <Icon size={40} aria-hidden="true" />
      <h3>{title}</h3>
      {children && <p>{children}</p>}
      {action}
    </div>
  );
}

export function ErrorState({ message, onRetry }) {
  return (
    <div className="empty">
      <h3>Couldn't load this page</h3>
      <p>{message}</p>
      {onRetry && <button className="btn btn-outline" onClick={onRetry}>Try again</button>}
    </div>
  );
}

export function ProgressBar({ value = 0, gold = false, label }) {
  const v = Math.max(0, Math.min(100, Math.round(value)));
  return (
    <div className={`progress ${gold ? 'gold' : ''}`} role="progressbar" aria-valuenow={v} aria-valuemin={0} aria-valuemax={100} aria-label={label}>
      <div style={{ width: `${v}%` }} />
    </div>
  );
}

export function ConfirmDialog({ title, message, confirmLabel = 'Confirm', danger = false, busy = false, onConfirm, onCancel }) {
  useEffect(() => {
    const onKey = (e) => { if (e.key === 'Escape') onCancel(); };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [onCancel]);
  return (
    <div className="modal-backdrop" onMouseDown={(e) => e.target === e.currentTarget && onCancel()}>
      <div className="modal" role="dialog" aria-modal="true" aria-labelledby="confirm-title">
        <h3 id="confirm-title">{title}</h3>
        <p>{message}</p>
        <div className="modal-actions">
          <button className="btn btn-outline" onClick={onCancel} disabled={busy}>Cancel</button>
          <button className={`btn ${danger ? 'btn-danger' : 'btn-primary'}`} onClick={onConfirm} disabled={busy} autoFocus>
            {busy ? 'Working...' : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

export function NotFound() {
  return (
    <div className="wrap page">
      <EmptyState title="Page not found" action={<Link to="/" className="btn btn-primary">Go to home</Link>}>
        The page you're looking for doesn't exist or has moved.
      </EmptyState>
    </div>
  );
}

/** Sets the browser tab title. */
// eslint-disable-next-line react-refresh/only-export-components
export function usePageTitle(title) {
  useEffect(() => {
    document.title = title ? `${title} | LearnStream` : 'LearnStream';
  }, [title]);
}

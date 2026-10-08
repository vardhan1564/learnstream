import { useState } from 'react';
import { toast } from 'react-toastify';
import { FiArrowUp, FiArrowDown, FiTrash2 } from 'react-icons/fi';
import api, { errorMessage } from '../../api/client';
import { ConfirmDialog } from '../../components/Common';

/** Up / down / remove buttons for repeatable rows (lessons, questions, steps, tests). */
export function RowControls({ index, count, onMove, onRemove, label }) {
  return (
    <div className="row-controls">
      <button type="button" className="icon-btn" onClick={() => onMove(index, -1)} disabled={index === 0} aria-label={`Move ${label} up`}><FiArrowUp /></button>
      <button type="button" className="icon-btn" onClick={() => onMove(index, 1)} disabled={index === count - 1} aria-label={`Move ${label} down`}><FiArrowDown /></button>
      <button type="button" className="icon-btn danger" onClick={() => onRemove(index)} aria-label={`Remove ${label}`}><FiTrash2 /></button>
    </div>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function moveItem(list, index, dir) {
  const next = [...list];
  const target = index + dir;
  if (target < 0 || target >= next.length) return list;
  [next[index], next[target]] = [next[target], next[index]];
  return next;
}

/** Delete button with a confirmation dialog. */
export function DeleteButton({ path, what, warning, onDeleted }) {
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const run = async () => {
    setBusy(true);
    try {
      await api.delete(path);
      toast.success(`${what} deleted`);
      setOpen(false);
      onDeleted();
    } catch (e) {
      toast.error(errorMessage(e));
      setOpen(false);
    } finally {
      setBusy(false);
    }
  };
  return (
    <>
      <button className="icon-btn danger" onClick={() => setOpen(true)} aria-label={`Delete ${what}`} title="Delete"><FiTrash2 /></button>
      {open && (
        <ConfirmDialog title={`Delete this ${what.toLowerCase()}?`} message={warning || 'This cannot be undone.'}
                       confirmLabel="Delete" danger busy={busy} onConfirm={run} onCancel={() => setOpen(false)} />
      )}
    </>
  );
}

export function PublishedTag({ published }) {
  return published ? <span className="tag tag-green">Published</span> : <span className="tag tag-grey">Draft</span>;
}

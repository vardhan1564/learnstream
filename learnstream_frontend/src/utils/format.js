export function formatPrice(price) {
  if (!price || price <= 0) return 'Free';
  return '₹' + Number(price).toLocaleString('en-IN', { maximumFractionDigits: 2 });
}

export function formatMinutes(min) {
  if (!min) return null;
  const h = Math.floor(min / 60);
  const m = min % 60;
  if (h === 0) return `${m} min`;
  return m === 0 ? `${h} h` : `${h} h ${m} min`;
}

export function formatDate(value) {
  if (!value) return '';
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return '';
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}

export function formatDateTime(value) {
  if (!value) return '';
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return '';
  return d.toLocaleString('en-IN', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
}

export function initials(name = '') {
  return name.split(/\s+/).filter(Boolean).slice(0, 2).map((p) => p[0].toUpperCase()).join('') || '?';
}

export const VERDICT_LABELS = {
  ACCEPTED: 'Accepted',
  WRONG_ANSWER: 'Wrong answer',
  COMPILATION_ERROR: 'Compilation error',
  RUNTIME_ERROR: 'Runtime error',
  TIME_LIMIT_EXCEEDED: 'Time limit exceeded',
  ERROR: 'Execution error',
  EXECUTED: 'Ran successfully',
};

export function verdictLabel(status) {
  return VERDICT_LABELS[status] || status;
}

export function difficultyClass(d) {
  return `tag diff-${String(d || 'easy').toLowerCase()}`;
}

export function difficultyLabel(d) {
  const s = String(d || 'EASY').toLowerCase();
  return s.charAt(0).toUpperCase() + s.slice(1);
}

export function formatMoney(amount) {
  return '₹' + Number(amount || 0).toLocaleString('en-IN', { maximumFractionDigits: 2 });
}

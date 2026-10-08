import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api, { errorMessage } from '../../api/client';
import { usePageTitle } from '../../components/Common';
import AuthShell from './AuthShell';

const PASSWORD_RULE = /^(?=.*[A-Za-z])(?=.*\d).{8,72}$/;

export default function Register() {
  usePageTitle('Create account');
  const navigate = useNavigate();
  const [form, setForm] = useState({ fullName: '', email: '', password: '', confirm: '' });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });
  const passwordOk = PASSWORD_RULE.test(form.password);

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    if (form.fullName.trim().length < 2) return setError('Please enter your full name.');
    if (!passwordOk) return setError('Password must be at least 8 characters with a letter and a number.');
    if (form.password !== form.confirm) return setError("Passwords don't match.");
    setBusy(true);
    try {
      const { data } = await api.post('/api/auth/register', {
        fullName: form.fullName.trim(),
        email: form.email.trim(),
        password: form.password,
      });
      navigate(`/verify-email?email=${encodeURIComponent(data.email || form.email.trim())}`, {
        state: { notice: data.message },
      });
    } catch (err) {
      setError(errorMessage(err, 'Could not create your account'));
    } finally {
      setBusy(false);
    }
  };

  return (
    <AuthShell
      title="Create your account"
      subtitle="Free forever. Paid courses are optional."
      footer={<>Already have an account? <Link to="/login">Log in</Link></>}
    >
      {error && <div className="alert alert-error" role="alert">{error}</div>}
      <form onSubmit={submit} noValidate>
        <label className="field">
          <span>Full name</span>
          <input className="input" autoComplete="name" required maxLength={100} value={form.fullName} onChange={set('fullName')} />
          <span className="hint">This is the name printed on your certificates.</span>
        </label>
        <label className="field">
          <span>Email</span>
          <input className="input" type="email" autoComplete="email" required maxLength={150} value={form.email} onChange={set('email')} />
        </label>
        <label className="field">
          <span>Password</span>
          <input className="input" type="password" autoComplete="new-password" required maxLength={72} value={form.password} onChange={set('password')} />
          <span className={`hint ${form.password && !passwordOk ? 'text-red' : ''}`}>At least 8 characters, with a letter and a number.</span>
        </label>
        <label className="field">
          <span>Confirm password</span>
          <input className="input" type="password" autoComplete="new-password" required maxLength={72} value={form.confirm} onChange={set('confirm')} />
        </label>
        <button className="btn btn-primary btn-block btn-lg" disabled={busy}>
          {busy ? <span className="spinner spinner-sm" /> : 'Create account'}
        </button>
      </form>
    </AuthShell>
  );
}

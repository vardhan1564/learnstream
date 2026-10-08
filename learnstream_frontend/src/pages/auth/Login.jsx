import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { FiMail, FiLock } from 'react-icons/fi';
import { useAuth } from '../../context/AuthContext';
import { errorMessage } from '../../api/client';
import { usePageTitle } from '../../components/Common';
import AuthShell from './AuthShell';

export default function Login() {
  usePageTitle('Log in');
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ email: location.state?.email || '', password: '' });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const notice = location.state?.notice;

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    setBusy(true);
    try {
      const user = await login(form.email.trim(), form.password);
      const from = location.state?.from;
      navigate(from || (user.role === 'ROLE_ADMIN' ? '/admin' : '/dashboard'), { replace: true });
    } catch (err) {
      if (err.response?.data?.code === 'EMAIL_NOT_VERIFIED') {
        navigate(`/verify-email?email=${encodeURIComponent(form.email.trim())}`, {
          state: { notice: err.response.data.message },
        });
        return;
      }
      setError(errorMessage(err, 'Could not log in'));
    } finally {
      setBusy(false);
    }
  };

  return (
    <AuthShell
      title="Welcome back"
      subtitle="Log in to continue learning."
      footer={<>New to LearnStream? <Link to="/register">Create an account</Link></>}
    >
      {notice && <div className="alert alert-success">{notice}</div>}
      {error && <div className="alert alert-error" role="alert">{error}</div>}
      <form onSubmit={submit} noValidate>
        <label className="field">
          <span>Email</span>
          <div className="input-icon">
            <FiMail />
            <input className="input" type="email" autoComplete="email" required value={form.email}
                   onChange={(e) => setForm({ ...form, email: e.target.value })} />
          </div>
        </label>
        <label className="field">
          <span className="row">Password <span className="spacer" /><Link to="/forgot-password" className="small">Forgot password?</Link></span>
          <div className="input-icon">
            <FiLock />
            <input className="input" type="password" autoComplete="current-password" required value={form.password}
                   onChange={(e) => setForm({ ...form, password: e.target.value })} />
          </div>
        </label>
        <button className="btn btn-primary btn-block btn-lg" disabled={busy || !form.email || !form.password}>
          {busy ? <span className="spinner spinner-sm" /> : 'Log in'}
        </button>
      </form>
    </AuthShell>
  );
}

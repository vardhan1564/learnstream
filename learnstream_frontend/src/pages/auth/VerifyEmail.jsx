import { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import api, { errorMessage } from '../../api/client';
import { usePageTitle } from '../../components/Common';
import AuthShell from './AuthShell';

export default function VerifyEmail() {
  usePageTitle('Verify email');
  const [params] = useSearchParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [email, setEmail] = useState(params.get('email') || '');
  const [otp, setOtp] = useState('');
  const [error, setError] = useState('');
  const [info, setInfo] = useState(location.state?.notice || '');
  const [busy, setBusy] = useState(false);
  const [cooldown, setCooldown] = useState(location.state?.notice ? 60 : 0);

  useEffect(() => {
    if (cooldown <= 0) return undefined;
    const t = setTimeout(() => setCooldown((c) => c - 1), 1000);
    return () => clearTimeout(t);
  }, [cooldown]);

  const verify = async (e) => {
    e.preventDefault();
    setError('');
    setBusy(true);
    try {
      const { data } = await api.post('/api/auth/verify-otp', { email: email.trim(), otp });
      navigate('/login', { replace: true, state: { email: email.trim(), notice: data.message } });
    } catch (err) {
      setError(errorMessage(err, 'Verification failed'));
    } finally {
      setBusy(false);
    }
  };

  const resend = async () => {
    setError('');
    try {
      const { data } = await api.post('/api/auth/resend-otp', { email: email.trim() });
      setInfo(data.message);
      setCooldown(60);
    } catch (err) {
      setError(errorMessage(err, 'Could not resend the code'));
    }
  };

  return (
    <AuthShell
      title="Check your email"
      subtitle="Enter the 6-digit code we sent you. It expires in 10 minutes."
      footer={<>Wrong account? <Link to="/register">Sign up again</Link></>}
    >
      {info && <div className="alert alert-info">{info}</div>}
      {error && <div className="alert alert-error" role="alert">{error}</div>}
      <form onSubmit={verify} noValidate>
        <label className="field">
          <span>Email</span>
          <input className="input" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>
        <label className="field">
          <span>Verification code</span>
          <input className="input otp-input" inputMode="numeric" autoComplete="one-time-code" maxLength={6}
                 value={otp} onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))} autoFocus />
        </label>
        <button className="btn btn-primary btn-block btn-lg" disabled={busy || otp.length !== 6 || !email}>
          {busy ? <span className="spinner spinner-sm" /> : 'Verify email'}
        </button>
      </form>
      <p className="center small" style={{ marginTop: 16 }}>
        Didn't get it? Check spam, or{' '}
        <button className="link-btn" onClick={resend} disabled={cooldown > 0 || !email}>
          {cooldown > 0 ? `resend in ${cooldown}s` : 'send a new code'}
        </button>
      </p>
    </AuthShell>
  );
}

import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api, { errorMessage } from '../../api/client';
import { usePageTitle } from '../../components/Common';
import AuthShell from './AuthShell';

const PASSWORD_RULE = /^(?=.*[A-Za-z])(?=.*\d).{8,72}$/;

export default function ForgotPassword() {
  usePageTitle('Reset password');
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [info, setInfo] = useState('');
  const [busy, setBusy] = useState(false);

  const requestCode = async (e) => {
    e.preventDefault();
    setError('');
    setBusy(true);
    try {
      const { data } = await api.post('/api/auth/forgot-password', { email: email.trim() });
      setInfo(data.message);
      setStep(2);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  const reset = async (e) => {
    e.preventDefault();
    setError('');
    if (!PASSWORD_RULE.test(password)) return setError('Password must be at least 8 characters with a letter and a number.');
    setBusy(true);
    try {
      const { data } = await api.post('/api/auth/reset-password', { email: email.trim(), otp, newPassword: password });
      navigate('/login', { replace: true, state: { email: email.trim(), notice: data.message } });
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <AuthShell
      title="Reset your password"
      subtitle={step === 1 ? "We'll email you a code to set a new password." : 'Enter the code from your email and choose a new password.'}
      footer={<>Remembered it? <Link to="/login">Back to log in</Link></>}
    >
      {info && <div className="alert alert-info">{info}</div>}
      {error && <div className="alert alert-error" role="alert">{error}</div>}
      {step === 1 ? (
        <form onSubmit={requestCode} noValidate>
          <label className="field">
            <span>Email</span>
            <input className="input" type="email" autoComplete="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
          </label>
          <button className="btn btn-primary btn-block btn-lg" disabled={busy || !email}>
            {busy ? <span className="spinner spinner-sm" /> : 'Send reset code'}
          </button>
        </form>
      ) : (
        <form onSubmit={reset} noValidate>
          <label className="field">
            <span>Reset code</span>
            <input className="input otp-input" inputMode="numeric" maxLength={6} value={otp}
                   onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))} autoFocus />
          </label>
          <label className="field">
            <span>New password</span>
            <input className="input" type="password" autoComplete="new-password" maxLength={72} value={password} onChange={(e) => setPassword(e.target.value)} />
            <span className="hint">At least 8 characters, with a letter and a number.</span>
          </label>
          <button className="btn btn-primary btn-block btn-lg" disabled={busy || otp.length !== 6 || !password}>
            {busy ? <span className="spinner spinner-sm" /> : 'Set new password'}
          </button>
          <button type="button" className="btn btn-ghost btn-block" style={{ marginTop: 8 }} onClick={() => setStep(1)}>Use a different email</button>
        </form>
      )}
    </AuthShell>
  );
}

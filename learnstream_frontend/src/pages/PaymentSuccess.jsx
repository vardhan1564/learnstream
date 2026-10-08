import { useEffect, useRef, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { FiCheckCircle, FiAlertCircle } from 'react-icons/fi';
import api, { errorMessage } from '../api/client';
import { Loader, usePageTitle } from '../components/Common';

/** Stripe sends the student here; we ask the backend to confirm the payment with Stripe before unlocking. */
export default function PaymentSuccess() {
  usePageTitle('Payment');
  const [params] = useSearchParams();
  const sessionId = params.get('session_id');
  const [state, setState] = useState({ status: sessionId ? 'checking' : 'error', message: sessionId ? '' : 'Missing payment reference.' });
  const tries = useRef(0);

  useEffect(() => {
    if (!sessionId) return undefined;
    let timer;
    let cancelled = false;
    const verify = async () => {
      try {
        const { data } = await api.post('/api/payments/verify', { sessionId });
        if (!cancelled) setState({ status: 'ok', course: data });
      } catch (e) {
        // Payment can take a few seconds to settle - retry a handful of times on 402
        if (e.response?.status === 402 && tries.current < 5 && !cancelled) {
          tries.current += 1;
          timer = setTimeout(verify, 2500);
          return;
        }
        if (!cancelled) setState({ status: 'error', message: errorMessage(e, 'We could not confirm your payment.') });
      }
    };
    verify();
    return () => { cancelled = true; clearTimeout(timer); };
  }, [sessionId]);

  return (
    <div className="wrap page">
      <div className="panel center" style={{ maxWidth: 520, margin: '40px auto', padding: 40 }}>
        {state.status === 'checking' && (<><Loader /><h2>Confirming your payment</h2><p className="muted">This usually takes a couple of seconds.</p></>)}
        {state.status === 'ok' && (
          <>
            <FiCheckCircle size={56} className="text-green" />
            <h2 style={{ marginTop: 16 }}>You're enrolled!</h2>
            <p className="muted">Payment confirmed. <strong>{state.course.courseTitle}</strong> is now unlocked.</p>
            <Link to={`/learn/${state.course.courseId}`} className="btn btn-primary btn-lg">Start learning</Link>
          </>
        )}
        {state.status === 'error' && (
          <>
            <FiAlertCircle size={56} className="text-red" />
            <h2 style={{ marginTop: 16 }}>Payment not confirmed</h2>
            <p className="muted">{state.message} If money was deducted, it will be refunded automatically or you can contact support with your payment receipt.</p>
            <Link to="/dashboard" className="btn btn-outline">Go to my learning</Link>
          </>
        )}
      </div>
    </div>
  );
}

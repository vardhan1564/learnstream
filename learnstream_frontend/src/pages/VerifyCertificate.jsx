import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { FiAward, FiCheckCircle, FiXCircle } from 'react-icons/fi';
import useFetch from '../api/useFetch';
import { Loader, usePageTitle } from '../components/Common';
import { formatDate } from '../utils/format';

export default function VerifyCertificate() {
  usePageTitle('Verify certificate');
  const { serial } = useParams();
  const navigate = useNavigate();
  const [input, setInput] = useState(serial || '');
  const { data: result, error, loading } = useFetch(serial ? `/api/certificates/verify/${encodeURIComponent(serial)}` : null);

  const submit = (e) => {
    e.preventDefault();
    if (input.trim()) navigate(`/verify/${encodeURIComponent(input.trim().toUpperCase())}`);
  };

  return (
    <div className="wrap page">
      <div className="panel" style={{ maxWidth: 560, margin: '0 auto', padding: 32 }}>
        <FiAward size={36} className="text-amber" />
        <h1 style={{ marginTop: 12 }}>Verify a certificate</h1>
        <p className="muted">Enter the certificate ID printed at the bottom of a LearnStream certificate.</p>
        <form onSubmit={submit} className="row" style={{ flexWrap: 'nowrap' }}>
          <input className="input" placeholder="LS-20260101-ABCD2345" value={input} onChange={(e) => setInput(e.target.value)} aria-label="Certificate ID" />
          <button className="btn btn-primary">Verify</button>
        </form>
        {loading && <Loader />}
        {error && <div className="alert alert-error" style={{ marginTop: 16 }}>{error}</div>}
        {result && !loading && (result.valid ? (
          <div className="alert alert-success" style={{ marginTop: 20 }}>
            <p style={{ margin: 0 }}><FiCheckCircle /> <strong>Valid certificate</strong></p>
            <p style={{ margin: '8px 0 0' }}>
              Awarded to <strong>{result.studentName}</strong> for completing <strong>{result.courseTitle}</strong> on {formatDate(result.issuedAt)}.
            </p>
          </div>
        ) : (
          <div className="alert alert-error" style={{ marginTop: 20 }}>
            <FiXCircle /> No certificate found with ID <strong>{result.serialNumber}</strong>. Check the ID and try again.
          </div>
        ))}
      </div>
    </div>
  );
}

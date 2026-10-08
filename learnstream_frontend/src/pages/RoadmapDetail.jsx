import { useEffect, useState } from 'react';
import { Link, useLocation, useParams } from 'react-router-dom';
import { toast } from 'react-toastify';
import { FiCheck, FiChevronLeft, FiExternalLink, FiBookOpen } from 'react-icons/fi';
import api, { errorMessage } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { ErrorState, Loader, ProgressBar, usePageTitle } from '../components/Common';
import './learn.css';

export default function RoadmapDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const location = useLocation();
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(null);
  usePageTitle(data?.roadmap.title || 'Roadmap');

  useEffect(() => {
    api.get(`/api/roadmaps/${id}`).then((r) => setData(r.data)).catch((e) => setError(errorMessage(e)));
  }, [id]);

  const toggle = async (stepId) => {
    setBusy(stepId);
    try {
      const { data: next } = await api.post(`/api/roadmaps/steps/${stepId}/toggle`);
      setData(next);
    } catch (e) {
      toast.error(errorMessage(e));
    } finally {
      setBusy(null);
    }
  };

  if (error) return <div className="wrap page"><ErrorState message={error} /></div>;
  if (!data) return <Loader />;
  const { roadmap, steps } = data;
  const pct = roadmap.stepCount ? (roadmap.completedCount / roadmap.stepCount) * 100 : 0;

  return (
    <div className="wrap page roadmap-page">
      <Link to="/roadmaps" className="crumb"><FiChevronLeft /> Roadmaps</Link>
      <div className="page-head" style={{ marginTop: 10 }}>
        <h1>{roadmap.title}</h1>
        {roadmap.description && <p>{roadmap.description}</p>}
        <div className="row" style={{ marginTop: 12 }}>
          {roadmap.level && <span className="tag tag-grey">{roadmap.level}</span>}
          {roadmap.duration && <span className="muted small">About {roadmap.duration}</span>}
        </div>
      </div>

      {user ? (
        <div className="panel panel-tight roadmap-progress">
          <div className="row small" style={{ marginBottom: 6 }}>
            <strong>{roadmap.completedCount} of {roadmap.stepCount} steps complete</strong>
            <span className="spacer" /><strong>{Math.round(pct)}%</strong>
          </div>
          <ProgressBar value={pct} label="Roadmap progress" />
        </div>
      ) : (
        <div className="alert alert-info"><Link to="/login" state={{ from: location.pathname }}>Log in</Link> to track your progress on this roadmap.</div>
      )}

      <ol className="road">
        {steps.map((s, i) => (
          <li key={s.id} className={s.completed ? 'done' : ''}>
            <button className="road-dot" onClick={() => user && toggle(s.id)} disabled={!user || busy === s.id}
                    aria-label={s.completed ? `Mark step ${i + 1} as not done` : `Mark step ${i + 1} as done`}>
              {s.completed ? <FiCheck /> : i + 1}
            </button>
            <div className="road-body panel panel-tight">
              <h3>{s.title}</h3>
              {s.description && <p className="muted">{s.description}</p>}
              <div className="row">
                {s.courseId && <Link to={`/courses/${s.courseId}`} className="btn btn-outline btn-sm"><FiBookOpen /> {s.courseTitle}</Link>}
                {s.resourceUrl && <a href={s.resourceUrl} target="_blank" rel="noreferrer" className="btn btn-ghost btn-sm"><FiExternalLink /> Resource</a>}
                <span className="spacer" />
                {user && (
                  <button className={`btn btn-sm ${s.completed ? 'btn-ghost' : 'btn-outline'}`} onClick={() => toggle(s.id)} disabled={busy === s.id}>
                    {s.completed ? 'Mark as not done' : 'Mark as done'}
                  </button>
                )}
              </div>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}

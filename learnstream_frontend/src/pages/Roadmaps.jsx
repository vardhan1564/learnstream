import { Link } from 'react-router-dom';
import { FiMap } from 'react-icons/fi';
import useFetch from '../api/useFetch';
import { EmptyState, ErrorState, Loader, ProgressBar, usePageTitle } from '../components/Common';
import './learn.css';

export default function Roadmaps() {
  usePageTitle('Roadmaps');
  const { data: roadmaps, error, reload: load } = useFetch('/api/roadmaps');

  return (
    <div className="wrap page">
      <div className="page-head">
        <h1>Roadmaps</h1>
        <p>Step-by-step learning paths. Tick off each step as you go and we'll remember where you are.</p>
      </div>
      {error ? <ErrorState message={error} onRetry={load} />
        : roadmaps === null ? <Loader />
        : roadmaps.length === 0 ? <EmptyState icon={FiMap} title="No roadmaps yet">Learning paths will appear here soon.</EmptyState>
        : (
          <div className="grid grid-3">
            {roadmaps.map((r) => (
              <Link key={r.id} to={`/roadmaps/${r.id}`} className="roadmap-card panel">
                <div className="row">
                  {r.level && <span className="tag tag-grey">{r.level}</span>}
                  {r.duration && <span className="muted small">{r.duration}</span>}
                </div>
                <h3>{r.title}</h3>
                {r.description && <p className="muted small">{r.description}</p>}
                <div className="roadmap-card-foot">
                  <span className="small"><strong>{r.completedCount}</strong> of {r.stepCount} steps done</span>
                  <ProgressBar value={r.stepCount ? (r.completedCount / r.stepCount) * 100 : 0} label="Roadmap progress" />
                </div>
              </Link>
            ))}
          </div>
        )}
    </div>
  );
}

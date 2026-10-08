import { useState } from 'react';
import { Link } from 'react-router-dom';
import { FiSearch, FiCheckCircle, FiCode, FiGift } from 'react-icons/fi';
import useFetch from '../api/useFetch';
import { useAuth } from '../context/AuthContext';
import { EmptyState, ErrorState, Loader, ProgressBar, usePageTitle } from '../components/Common';
import { difficultyClass, difficultyLabel } from '../utils/format';
import './problems.css';

export default function Problems() {
  usePageTitle('Practice problems');
  const { user } = useAuth();
  const { data: problems, error, reload: load } = useFetch('/api/problems');
  const { data: rewards } = useFetch(user ? '/api/users/me/rewards' : null);
  const [query, setQuery] = useState('');
  const [difficulty, setDifficulty] = useState('ALL');
  const [status, setStatus] = useState('all');


  const filtered = (problems || []).filter((p) => {
    const q = query.trim().toLowerCase();
    if (q && !`${p.title} ${p.tags || ''}`.toLowerCase().includes(q)) return false;
    if (difficulty !== 'ALL' && p.difficulty !== difficulty) return false;
    if (status === 'solved' && !p.solved) return false;
    if (status === 'todo' && p.solved) return false;
    return true;
  });

  const per = rewards?.problemsPerFreeCourse || 5;
  const towards = rewards ? per - rewards.problemsToNextCredit : 0;

  return (
    <div className="wrap page">
      <div className="page-head-row page-head">
        <div>
          <h1>Practice problems</h1>
          <p>Read input, print output, and your code is checked against sample and hidden test cases.</p>
        </div>
      </div>

      <div className="reward-strip panel panel-tight">
        <FiGift size={26} className="text-amber" />
        {user && rewards ? (
          <div className="reward-strip-body">
            <div className="row small">
              <strong>{towards} of {per} problems towards your next free course</strong>
              <span className="spacer" />
              {rewards.creditsAvailable > 0 && (
                <Link to="/courses" className="tag tag-amber">{rewards.creditsAvailable} free course credit{rewards.creditsAvailable > 1 ? 's' : ''} ready</Link>
              )}
            </div>
            <ProgressBar value={(towards / per) * 100} gold label="Progress to next free course" />
          </div>
        ) : (
          <div className="reward-strip-body">
            <strong>Solve 5 problems, unlock any course for free.</strong>{' '}
            <Link to="/register">Create an account</Link> to start earning credits.
          </div>
        )}
      </div>

      <div className="toolbar">
        <div className="input-icon toolbar-search">
          <FiSearch />
          <input className="input" placeholder="Search by title or topic" value={query} onChange={(e) => setQuery(e.target.value)} aria-label="Search problems" />
        </div>
        <div className="segmented" role="group" aria-label="Difficulty">
          {['ALL', 'EASY', 'MEDIUM', 'HARD'].map((d) => (
            <button key={d} className={difficulty === d ? 'active' : ''} onClick={() => setDifficulty(d)}>
              {d === 'ALL' ? 'All' : difficultyLabel(d)}
            </button>
          ))}
        </div>
        {user && (
          <div className="segmented" role="group" aria-label="Status">
            {[['all', 'Any status'], ['todo', 'To do'], ['solved', 'Solved']].map(([k, l]) => (
              <button key={k} className={status === k ? 'active' : ''} onClick={() => setStatus(k)}>{l}</button>
            ))}
          </div>
        )}
      </div>

      {error ? <ErrorState message={error} onRetry={load} />
        : problems === null ? <Loader />
        : filtered.length === 0 ? (
          <EmptyState icon={FiCode} title={problems.length ? 'No problems match your filters' : 'No problems yet'}>
            {problems.length ? 'Try another difficulty or search term.' : 'Problems will appear here once they are published.'}
          </EmptyState>
        ) : (
          <div className="table-wrap">
            <table className="table problem-table">
              <thead>
                <tr><th style={{ width: 48 }}><span className="sr-only">Status</span></th><th>Problem</th><th>Topics</th><th>Difficulty</th></tr>
              </thead>
              <tbody>
                {filtered.map((p) => (
                  <tr key={p.id}>
                    <td>{p.solved ? <FiCheckCircle className="text-green" aria-label="Solved" /> : null}</td>
                    <td><Link to={`/problems/${p.id}`} className="problem-link">{p.title}</Link></td>
                    <td className="muted small">{(p.tags || '').split(',').filter(Boolean).join(', ')}</td>
                    <td><span className={difficultyClass(p.difficulty)}>{difficultyLabel(p.difficulty)}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
    </div>
  );
}

import { FiAward } from 'react-icons/fi';
import useFetch from '../api/useFetch';
import { EmptyState, ErrorState, Loader, usePageTitle } from '../components/Common';
import { initials } from '../utils/format';
import './learn.css';

export function LeaderboardTable({ rows, showEmail }) {
  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr>
            <th style={{ width: 70 }}>Rank</th>
            <th>Student</th>
            <th>Problems solved</th>
            <th>Hard</th>
            <th>Quiz points</th>
            <th>Total points</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.userId} className={r.me ? 'me' : ''}>
              <td><span className={`rank rank-${r.rank <= 3 ? r.rank : 'n'}`}>{r.rank}</span></td>
              <td>
                <div className="row" style={{ gap: 10, flexWrap: 'nowrap' }}>
                  <span className="avatar">{initials(r.fullName)}</span>
                  <div>
                    <strong>{r.fullName}{r.me ? ' (you)' : ''}</strong>
                    {showEmail && r.email && <div className="muted small">{r.email}</div>}
                  </div>
                </div>
              </td>
              <td>{r.problemsSolved}</td>
              <td>{r.hardSolved}</td>
              <td>{r.quizPoints}</td>
              <td><strong>{r.points}</strong></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function Leaderboard() {
  usePageTitle('Leaderboard');
  const { data: rows, error, reload: load } = useFetch('/api/leaderboard');

  return (
    <div className="wrap page">
      <div className="page-head">
        <h1>Leaderboard</h1>
        <p>Points come from solved problems (Easy 10, Medium 20, Hard 40) and your best quiz scores (2 per correct answer).</p>
      </div>
      {error ? <ErrorState message={error} onRetry={load} />
        : rows === null ? <Loader />
        : rows.length === 0 ? <EmptyState icon={FiAward} title="No one on the board yet">Solve a problem or pass a quiz to claim the top spot.</EmptyState>
        : <LeaderboardTable rows={rows} />}
    </div>
  );
}

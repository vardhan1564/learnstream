import { FiAward } from 'react-icons/fi';
import useFetch from '../../api/useFetch';
import { EmptyState, ErrorState, Loader } from '../../components/Common';
import { LeaderboardTable } from '../Leaderboard';
import '../learn.css';

export default function AdminLeaderboard() {
  const { data: rows, error, reload: load } = useFetch('/api/admin/leaderboard?limit=200');
  return (
    <>
      <div className="admin-head">
        <div>
          <h1>Leaderboard</h1>
          <p className="muted">Easy 10, Medium 20, Hard 40 points per solved problem, plus 2 points per correct answer in each quiz's best attempt.</p>
        </div>
      </div>
      {error ? <ErrorState message={error} onRetry={load} />
        : rows === null ? <Loader />
        : rows.length === 0 ? <EmptyState icon={FiAward} title="No activity yet">Students appear here after solving a problem or taking a quiz.</EmptyState>
        : <LeaderboardTable rows={rows} showEmail />}
    </>
  );
}

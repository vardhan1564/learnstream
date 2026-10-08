import { Link } from 'react-router-dom';
import { FiUsers, FiBookOpen, FiCode, FiHelpCircle, FiMap, FiAward, FiCheckCircle, FiTrendingUp } from 'react-icons/fi';
import useFetch from '../../api/useFetch';
import { ErrorState, Loader } from '../../components/Common';
import { formatDateTime, formatMoney } from '../../utils/format';

export default function AdminOverview() {
  const { data: stats, error, reload: load } = useFetch('/api/admin/stats');
  const payments = useFetch('/api/admin/payments?limit=10').data || [];

  if (error) return <ErrorState message={error} onRetry={load} />;
  if (!stats) return <Loader />;

  const cards = [
    { label: 'Students', value: stats.totalStudents, icon: FiUsers, to: '/admin/students' },
    { label: 'Courses', value: stats.totalCourses, icon: FiBookOpen, to: '/admin/courses' },
    { label: 'Enrollments', value: stats.totalEnrollments, icon: FiTrendingUp },
    { label: 'Coding problems', value: stats.totalProblems, icon: FiCode, to: '/admin/problems' },
    { label: 'Quizzes', value: stats.totalQuizzes, icon: FiHelpCircle, to: '/admin/quizzes' },
    { label: 'Roadmaps', value: stats.totalRoadmaps, icon: FiMap, to: '/admin/roadmaps' },
    { label: 'Accepted submissions', value: stats.acceptedSubmissions, icon: FiCheckCircle },
    { label: 'Certificates issued', value: stats.certificatesIssued, icon: FiAward },
  ];

  return (
    <>
      <div className="admin-head">
        <div>
          <h1>Overview</h1>
          <p className="muted">Revenue so far: <strong className="text-ink">{formatMoney(stats.revenue)}</strong></p>
        </div>
        <div className="row">
          <Link to="/admin/courses/new" className="btn btn-primary">New course</Link>
          <Link to="/admin/problems/new" className="btn btn-outline">New problem</Link>
          <Link to="/admin/quizzes/new" className="btn btn-outline">New quiz</Link>
        </div>
      </div>
      <div className="stat-grid">
        {cards.map(({ label, value, icon: Icon, to }) => {
          const inner = (<><Icon /><strong>{value}</strong><span>{label}</span></>);
          return to ? <Link key={label} to={to} className="admin-stat">{inner}</Link> : <div key={label} className="admin-stat">{inner}</div>;
        })}
      </div>

      <h2 className="admin-section-title">Recent payments</h2>
      {payments.length === 0 ? (
        <p className="muted">No paid enrollments yet.</p>
      ) : (
        <div className="table-wrap">
          <table className="table">
            <thead><tr><th>Student</th><th>Course</th><th>Amount</th><th>Paid</th></tr></thead>
            <tbody>
              {payments.map((p) => (
                <tr key={p.id}>
                  <td><strong>{p.studentName}</strong><div className="muted small">{p.studentEmail}</div></td>
                  <td>{p.courseTitle}</td>
                  <td>{formatMoney(p.amount)}</td>
                  <td className="muted small">{formatDateTime(p.paidAt)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

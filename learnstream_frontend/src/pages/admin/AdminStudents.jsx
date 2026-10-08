import { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import { FiSearch, FiUsers } from 'react-icons/fi';
import api, { errorMessage } from '../../api/client';
import useFetch from '../../api/useFetch';
import { useAuth } from '../../context/AuthContext';
import { ConfirmDialog, EmptyState, ErrorState, Loader } from '../../components/Common';
import { formatDate } from '../../utils/format';

export default function AdminStudents() {
  const { user } = useAuth();
  const [query, setQuery] = useState('');
  const [search, setSearch] = useState('');
  const usersFetch = useFetch(`/api/admin/users${search ? `?query=${encodeURIComponent(search)}` : ''}`);
  const users = usersFetch.data;
  const error = usersFetch.error;
  const load = usersFetch.reload;
  const courses = (useFetch('/api/admin/courses').data || []).map((c) => c.course);
  const [grant, setGrant] = useState(null); // { user, courseId }
  const [roleChange, setRoleChange] = useState(null);
  const [busy, setBusy] = useState(false);

  // Debounced search
  useEffect(() => {
    const t = setTimeout(() => setSearch(query.trim()), 350);
    return () => clearTimeout(t);
  }, [query]);

  const doGrant = async () => {
    setBusy(true);
    try {
      await api.post(`/api/admin/users/${grant.user.id}/enroll/${grant.courseId}`);
      toast.success('Course access granted');
      setGrant(null);
      load();
    } catch (e) {
      toast.error(errorMessage(e));
    } finally {
      setBusy(false);
    }
  };

  const doRole = async () => {
    setBusy(true);
    try {
      await api.put(`/api/admin/users/${roleChange.id}/role`, { role: roleChange.role === 'ROLE_ADMIN' ? 'ROLE_STUDENT' : 'ROLE_ADMIN' });
      toast.success('Role updated');
      setRoleChange(null);
      load();
    } catch (e) {
      toast.error(errorMessage(e));
      setRoleChange(null);
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <div className="admin-head">
        <div>
          <h1>Students</h1>
          <p className="muted">Search users, see their courses, grant access manually or make someone an admin.</p>
        </div>
      </div>
      <div className="input-icon" style={{ maxWidth: 420, marginBottom: 20 }}>
        <FiSearch />
        <input className="input" placeholder="Search by name or email" value={query} onChange={(e) => setQuery(e.target.value)} aria-label="Search users" />
      </div>
      {error ? <ErrorState message={error} onRetry={() => load()} />
        : users === null ? <Loader />
        : users.length === 0 ? <EmptyState icon={FiUsers} title="No users found">Try a different name or email.</EmptyState>
        : (
          <div className="table-wrap">
            <table className="table">
              <thead><tr><th>User</th><th>Role</th><th>Courses</th><th>Solved</th><th>Joined</th><th>Actions</th></tr></thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id}>
                    <td><strong>{u.fullName}</strong><div className="muted small">{u.email}</div>{!u.verified && <span className="tag tag-amber">Email not verified</span>}</td>
                    <td>{u.role === 'ROLE_ADMIN' ? <span className="tag">Admin</span> : <span className="tag tag-grey">Student</span>}</td>
                    <td className="small">{u.enrolledCourses.length ? u.enrolledCourses.join(', ') : <span className="muted">None</span>}</td>
                    <td>{u.problemsSolved}</td>
                    <td className="small muted">{formatDate(u.createdAt)}</td>
                    <td>
                      <div className="row" style={{ flexWrap: 'nowrap' }}>
                        <select className="select" style={{ minHeight: 34, padding: '4px 8px', width: 150 }} value=""
                                onChange={(e) => e.target.value && setGrant({ user: u, courseId: e.target.value })} aria-label={`Grant course to ${u.fullName}`}>
                          <option value="">Grant course...</option>
                          {courses.filter((c) => !u.enrolledCourses.includes(c.title)).map((c) => <option key={c.id} value={c.id}>{c.title}</option>)}
                        </select>
                        {u.id !== user.id && u.verified && (
                          <button className="btn btn-ghost btn-sm" onClick={() => setRoleChange(u)}>
                            {u.role === 'ROLE_ADMIN' ? 'Remove admin' : 'Make admin'}
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

      {grant && (
        <ConfirmDialog title="Grant course access?"
                       message={`${grant.user.fullName} will get free access to "${courses.find((c) => String(c.id) === String(grant.courseId))?.title}".`}
                       confirmLabel="Grant access" busy={busy} onConfirm={doGrant} onCancel={() => setGrant(null)} />
      )}
      {roleChange && (
        <ConfirmDialog title={roleChange.role === 'ROLE_ADMIN' ? 'Remove admin access?' : 'Make this user an admin?'}
                       message={roleChange.role === 'ROLE_ADMIN'
                         ? `${roleChange.fullName} will become a regular student.`
                         : `${roleChange.fullName} will be able to add, edit and delete courses, quizzes and problems.`}
                       confirmLabel="Confirm" danger={roleChange.role !== 'ROLE_ADMIN'} busy={busy} onConfirm={doRole} onCancel={() => setRoleChange(null)} />
      )}
    </>
  );
}

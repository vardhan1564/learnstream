import { useState } from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import { FiAward, FiBookOpen, FiCode, FiDownload, FiGift, FiHelpCircle, FiStar } from 'react-icons/fi';
import api, { blobErrorMessage, downloadFile, errorMessage, storage } from '../api/client';
import useFetch from '../api/useFetch';
import { useAuth } from '../context/AuthContext';
import { CourseArt } from '../components/CourseCard';
import { EmptyState, ErrorState, Loader, ProgressBar, usePageTitle } from '../components/Common';
import { formatDate } from '../utils/format';
import './learn.css';

export default function Dashboard() {
  usePageTitle('My learning');
  const { user, updateUser } = useAuth();
  const me = useFetch('/api/users/me');
  const myCourses = useFetch('/api/users/me/courses');
  const myCerts = useFetch('/api/users/me/certificates');
  const [tab, setTab] = useState('courses');
  const profile = me.data;
  const setProfile = me.setData;
  const courses = myCourses.data;
  const certs = myCerts.data || [];
  const error = me.error || myCourses.error || myCerts.error;
  const load = () => { me.reload(); myCourses.reload(); myCerts.reload(); };

  if (error) return <div className="wrap page"><ErrorState message={error} onRetry={load} /></div>;
  if (!profile || !courses) return <Loader />;

  const r = profile.rewards;
  const towards = r.problemsPerFreeCourse - r.problemsToNextCredit;
  const firstName = (user?.fullName || profile.fullName).split(' ')[0];

  return (
    <div className="wrap page">
      <div className="page-head">
        <h1>Hi {firstName}, keep the streak going</h1>
        <p>Member since {formatDate(profile.memberSince)}</p>
      </div>

      <div className="stat-row">
        <Stat icon={FiBookOpen} label="Courses enrolled" value={profile.coursesEnrolled} />
        <Stat icon={FiCode} label="Problems solved" value={profile.problemsSolved} />
        <Stat icon={FiHelpCircle} label="Quizzes passed" value={profile.quizzesPassed} />
        <Stat icon={FiAward} label="Certificates" value={profile.certificates} />
        <Stat icon={FiStar} label="Leaderboard points" value={profile.points} />
      </div>

      <div className="panel reward-panel">
        <FiGift size={30} />
        <div className="reward-panel-body">
          <h3>{r.creditsAvailable > 0 ? `You have ${r.creditsAvailable} free course credit${r.creditsAvailable > 1 ? 's' : ''}` : 'Free course progress'}</h3>
          <p className="small">
            {r.creditsAvailable > 0
              ? 'Open any paid course and choose "Unlock free with a credit".'
              : `Solve ${r.problemsToNextCredit} more problem${r.problemsToNextCredit === 1 ? '' : 's'} to unlock any course for free.`}
          </p>
          <ProgressBar value={(towards / r.problemsPerFreeCourse) * 100} gold label="Progress to next free course" />
        </div>
        <Link to={r.creditsAvailable > 0 ? '/courses' : '/problems'} className="btn btn-gold">
          {r.creditsAvailable > 0 ? 'Choose a course' : 'Solve problems'}
        </Link>
      </div>

      <div className="tabs" role="tablist">
        <button className={`tab ${tab === 'courses' ? 'active' : ''}`} onClick={() => setTab('courses')}>My courses</button>
        <button className={`tab ${tab === 'certs' ? 'active' : ''}`} onClick={() => setTab('certs')}>Certificates ({certs.length})</button>
        <button className={`tab ${tab === 'account' ? 'active' : ''}`} onClick={() => setTab('account')}>Account</button>
      </div>

      {tab === 'courses' && (courses.length === 0 ? (
        <EmptyState icon={FiBookOpen} title="You haven't enrolled in a course yet" action={<Link to="/courses" className="btn btn-primary">Browse courses</Link>}>
          Start with a free course or use a reward credit.
        </EmptyState>
      ) : (
        <div className="my-courses">
          {courses.map(({ course, progress }) => (
            <div key={course.id} className="my-course panel panel-tight">
              <CourseArt course={course} className="my-course-art" />
              <div className="my-course-body">
                <h3>{course.title}</h3>
                <div className="row small muted" style={{ marginBottom: 6 }}>
                  <span>
                    {progress.completedCount} of {progress.totalCount} lessons
                    {progress.quizzesTotal > 0 ? `, quiz ${progress.quizzesPassed}/${progress.quizzesTotal} passed` : ''}
                  </span>
                  <span className="spacer" /><strong className="text-ink">{progress.percentage}%</strong>
                </div>
                <ProgressBar value={progress.percentage} label={`${course.title} progress`} />
              </div>
              <div className="my-course-actions">
                {progress.certificateEligible ? (
                  <CertButton courseId={course.id} onDone={load} />
                ) : (
                  <Link to={`/learn/${course.id}`} className="btn btn-primary btn-sm">{progress.completedCount ? 'Continue' : 'Start'}</Link>
                )}
              </div>
            </div>
          ))}
        </div>
      ))}

      {tab === 'certs' && (certs.length === 0 ? (
        <EmptyState icon={FiAward} title="No certificates yet">Finish all lessons in a course and pass its quiz to earn one.</EmptyState>
      ) : (
        <div className="grid grid-3">
          {certs.map((c) => (
            <div key={c.serialNumber} className="panel cert-card">
              <FiAward size={28} className="text-amber" />
              <h3>{c.courseTitle}</h3>
              <p className="muted small">Issued {formatDate(c.issuedAt)}<br />ID {c.serialNumber}</p>
              <div className="row">
                <CertButton courseId={c.courseId} />
                <Link to={`/verify/${c.serialNumber}`} className="btn btn-ghost btn-sm">Share link</Link>
              </div>
            </div>
          ))}
        </div>
      ))}

      {tab === 'account' && <AccountSettings profile={profile} onSaved={(u) => { updateUser(u); setProfile((p) => ({ ...p, fullName: u.fullName })); }} />}
    </div>
  );
}

function Stat({ icon: Icon, label, value }) {
  return (
    <div className="stat">
      <Icon />
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}

function CertButton({ courseId, onDone }) {
  const [busy, setBusy] = useState(false);
  const click = async () => {
    setBusy(true);
    try {
      await downloadFile(`/api/certificates/course/${courseId}/download`, 'LearnStream_Certificate.pdf');
      onDone?.();
    } catch (e) {
      toast.error(await blobErrorMessage(e, 'Could not download the certificate'));
    } finally {
      setBusy(false);
    }
  };
  return (
    <button className="btn btn-gold btn-sm" onClick={click} disabled={busy}>
      <FiDownload /> {busy ? 'Preparing...' : 'Certificate'}
    </button>
  );
}

function AccountSettings({ profile, onSaved }) {
  const [name, setName] = useState(profile.fullName);
  const [pw, setPw] = useState({ currentPassword: '', newPassword: '', confirm: '' });
  const [busy, setBusy] = useState('');

  const saveName = async (e) => {
    e.preventDefault();
    setBusy('name');
    try {
      const { data } = await api.put('/api/users/me', { fullName: name.trim() });
      onSaved(data);
      toast.success('Name updated');
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setBusy('');
    }
  };

  const savePassword = async (e) => {
    e.preventDefault();
    if (pw.newPassword !== pw.confirm) return toast.error("New passwords don't match");
    setBusy('pw');
    try {
      const { data } = await api.put('/api/users/me/password', { currentPassword: pw.currentPassword, newPassword: pw.newPassword });
      storage.save(data.token, data.user); // new token; other devices are signed out
      setPw({ currentPassword: '', newPassword: '', confirm: '' });
      toast.success('Password changed. Other devices have been signed out.');
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setBusy('');
    }
  };

  return (
    <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))' }}>
      <form className="panel" onSubmit={saveName}>
        <h3>Profile</h3>
        <label className="field">
          <span>Full name</span>
          <input className="input" value={name} maxLength={100} onChange={(e) => setName(e.target.value)} />
          <span className="hint">Certificates always show your current name.</span>
        </label>
        <label className="field">
          <span>Email</span>
          <input className="input" value={profile.email} disabled />
        </label>
        <button className="btn btn-primary" disabled={busy === 'name' || name.trim().length < 2 || name.trim() === profile.fullName}>Save name</button>
      </form>
      <form className="panel" onSubmit={savePassword}>
        <h3>Change password</h3>
        <label className="field"><span>Current password</span>
          <input className="input" type="password" autoComplete="current-password" value={pw.currentPassword} onChange={(e) => setPw({ ...pw, currentPassword: e.target.value })} />
        </label>
        <label className="field"><span>New password</span>
          <input className="input" type="password" autoComplete="new-password" value={pw.newPassword} onChange={(e) => setPw({ ...pw, newPassword: e.target.value })} />
          <span className="hint">At least 8 characters, with a letter and a number.</span>
        </label>
        <label className="field"><span>Confirm new password</span>
          <input className="input" type="password" autoComplete="new-password" value={pw.confirm} onChange={(e) => setPw({ ...pw, confirm: e.target.value })} />
        </label>
        <button className="btn btn-primary" disabled={busy === 'pw' || !pw.currentPassword || !pw.newPassword}>Change password</button>
      </form>
    </div>
  );
}

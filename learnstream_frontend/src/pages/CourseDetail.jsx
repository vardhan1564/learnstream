import { useState } from 'react';
import { Link, useLocation, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { toast } from 'react-toastify';
import { FiLock, FiPlayCircle, FiCheckCircle, FiClock, FiUser, FiBarChart2, FiGift, FiHelpCircle } from 'react-icons/fi';
import api, { errorMessage } from '../api/client';
import useFetch from '../api/useFetch';
import { useAuth } from '../context/AuthContext';
import { CourseArt } from '../components/CourseCard';
import { ErrorState, Loader, ProgressBar, usePageTitle } from '../components/Common';
import VideoPlayer from '../components/VideoPlayer';
import { formatMinutes, formatPrice } from '../utils/format';
import './course.css';

export default function CourseDetail() {
  const { id } = useParams();
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { user, isAdmin } = useAuth();
  const { data, error, reload: load } = useFetch(`/api/courses/${id}`);
  const { data: rewards } = useFetch(user ? '/api/users/me/rewards' : null);
  const [busy, setBusy] = useState('');
  const [preview, setPreview] = useState(null);
  usePageTitle(data?.course.title || 'Course');


  const requireLogin = () => navigate('/login', { state: { from: location.pathname } });

  const enrollFree = async () => {
    if (!user) return requireLogin();
    setBusy('free');
    try {
      const { data: res } = await api.post(`/api/courses/${id}/enroll-free`);
      toast.success(res.message);
      navigate(`/learn/${id}`);
    } catch (e) {
      toast.error(errorMessage(e));
    } finally {
      setBusy('');
    }
  };

  const buy = async () => {
    if (!user) return requireLogin();
    setBusy('buy');
    try {
      const { data: res } = await api.post(`/api/courses/${id}/checkout`);
      window.location.assign(res.url);
    } catch (e) {
      toast.error(errorMessage(e));
      setBusy('');
    }
  };

  const claim = async () => {
    setBusy('claim');
    try {
      const { data: res } = await api.post(`/api/courses/${id}/claim-reward`);
      toast.success(res.message);
      navigate(`/learn/${id}`);
    } catch (e) {
      toast.error(errorMessage(e));
    } finally {
      setBusy('');
    }
  };

  if (error) return <div className="wrap page"><ErrorState message={error} onRetry={load} /></div>;
  if (!data) return <Loader />;

  const { course, lessons, quizzes, progress } = data;
  const free = !(course.price > 0);
  const firstPreview = lessons.find((l) => !l.locked);

  return (
    <div className="course-page">
      <section className="course-hero">
        <div className="wrap course-hero-grid">
          <div>
            <Link to="/courses" className="crumb">Courses</Link>
            <h1>{course.title}</h1>
            {course.description && <p className="course-desc">{course.description}</p>}
            <ul className="course-facts">
              {course.level && <li><FiBarChart2 /> {course.level}</li>}
              {course.instructor && <li><FiUser /> {course.instructor}</li>}
              <li><FiPlayCircle /> {course.lessonCount} {course.lessonCount === 1 ? "lesson" : "lessons"}</li>
              {course.totalMinutes > 0 && <li><FiClock /> {formatMinutes(course.totalMinutes)}</li>}
              {quizzes.length > 0 && <li><FiHelpCircle /> {quizzes.length} quiz{quizzes.length > 1 ? 'zes' : ''}</li>}
            </ul>
          </div>
        </div>
      </section>

      <div className="wrap course-body">
        <div className="course-main">
          {params.get('payment') === 'cancelled' && (
            <div className="alert alert-warn">Payment was cancelled. You haven't been charged.</div>
          )}

          {preview && (
            <div className="panel panel-tight preview-panel">
              <VideoPlayer url={preview.videoUrl} type={preview.videoType} title={preview.title} onExpired={load} />
              <div className="row" style={{ marginTop: 12 }}>
                <strong>Preview: {preview.title}</strong>
                <span className="spacer" />
                <button className="btn btn-ghost btn-sm" onClick={() => setPreview(null)}>Close preview</button>
              </div>
            </div>
          )}

          <h2>Course content</h2>
          {lessons.length === 0 ? (
            <p className="muted">Lessons are being added to this course.</p>
          ) : (
            <ol className="curriculum">
              {lessons.map((l, i) => (
                <li key={l.id} className={l.locked ? 'locked' : ''}>
                  <span className="curriculum-index">{l.completed ? <FiCheckCircle className="text-green" /> : i + 1}</span>
                  <div className="curriculum-text">
                    <strong>{l.title}</strong>
                    {l.description && <span>{l.description}</span>}
                  </div>
                  {l.durationMinutes ? <span className="muted small">{formatMinutes(l.durationMinutes)}</span> : null}
                  {l.locked ? (
                    <FiLock className="muted" aria-label="Locked" />
                  ) : course.enrolled || isAdmin ? (
                    <Link to={`/learn/${course.id}?lesson=${l.id}`} className="btn btn-ghost btn-sm">Watch</Link>
                  ) : (
                    <button className="btn btn-ghost btn-sm" onClick={() => { setPreview(l); window.scrollTo({ top: 0, behavior: 'smooth' }); }}>Preview</button>
                  )}
                </li>
              ))}
            </ol>
          )}

          {quizzes.length > 0 && (
            <>
              <h2 style={{ marginTop: 36 }}>Assessment</h2>
              <p className="muted">Pass {quizzes.length > 1 ? 'these quizzes' : 'this quiz'} after the lessons to unlock your certificate.</p>
              <ul className="quiz-mini-list">
                {quizzes.map((q) => (
                  <li key={q.id}>
                    <FiHelpCircle />
                    <span>{q.title}</span>
                    <span className="muted small">{q.questionCount} questions, pass mark {q.passPercentage}%</span>
                    {q.passed && <span className="tag tag-green">Passed</span>}
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>

        <aside className="buy-box panel">
          <CourseArt course={course} className="buy-art" />
          {course.enrolled ? (
            <>
              <p className="buy-state"><FiCheckCircle className="text-green" /> You're enrolled</p>
              {progress && (
                <div style={{ marginBottom: 16 }}>
                  <div className="row small" style={{ marginBottom: 6 }}>
                    <span>{progress.completedCount} of {progress.totalCount} lessons</span>
                    <span className="spacer" /><strong>{progress.percentage}%</strong>
                  </div>
                  <ProgressBar value={progress.percentage} label="Course progress" />
                </div>
              )}
              <Link to={`/learn/${course.id}`} className="btn btn-primary btn-block btn-lg">
                {progress?.completedCount ? 'Continue learning' : 'Start learning'}
              </Link>
            </>
          ) : isAdmin ? (
            <>
              <p className="buy-price">{formatPrice(course.price)}</p>
              <Link to={`/learn/${course.id}`} className="btn btn-dark btn-block btn-lg">Open course player</Link>
              <p className="muted small" style={{ marginTop: 10 }}>Admins can view every lesson without enrolling.</p>
            </>
          ) : (
            <>
              <p className="buy-price">{formatPrice(course.price)}</p>
              {free ? (
                <button className="btn btn-primary btn-block btn-lg" onClick={enrollFree} disabled={!!busy}>
                  {busy === 'free' ? 'Enrolling...' : 'Enroll for free'}
                </button>
              ) : (
                <>
                  <button className="btn btn-primary btn-block btn-lg" onClick={buy} disabled={!!busy}>
                    {busy === 'buy' ? 'Opening checkout...' : 'Buy now'}
                  </button>
                  {rewards?.creditsAvailable > 0 && (
                    <button className="btn btn-gold btn-block" style={{ marginTop: 10 }} onClick={claim} disabled={!!busy}>
                      <FiGift /> {busy === 'claim' ? 'Unlocking...' : `Unlock free with a credit (${rewards.creditsAvailable} left)`}
                    </button>
                  )}
                  {user && rewards && rewards.creditsAvailable === 0 && (
                    <p className="muted small" style={{ marginTop: 12 }}>
                      <FiGift /> Solve {rewards.problemsToNextCredit} more problem{rewards.problemsToNextCredit === 1 ? '' : 's'} to unlock any course for free.{' '}
                      <Link to="/problems">Practice now</Link>
                    </p>
                  )}
                </>
              )}
              {firstPreview && !preview && (
                <button className="btn btn-outline btn-block" style={{ marginTop: 10 }} onClick={() => setPreview(firstPreview)}>
                  <FiPlayCircle /> Watch a free preview
                </button>
              )}
              {!user && <p className="muted small center" style={{ marginTop: 12 }}>You'll be asked to log in first.</p>}
            </>
          )}
        </aside>
      </div>
    </div>
  );
}

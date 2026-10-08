import { useMemo, useState } from 'react';
import { Link, Navigate, useParams, useSearchParams } from 'react-router-dom';
import { toast } from 'react-toastify';
import { FiCheck, FiCheckCircle, FiChevronLeft, FiChevronRight, FiAward, FiHelpCircle, FiDownload, FiLock } from 'react-icons/fi';
import api, { blobErrorMessage, downloadFile, errorMessage } from '../api/client';
import useFetch from '../api/useFetch';
import { useAuth } from '../context/AuthContext';
import { ErrorState, Loader, ProgressBar, usePageTitle } from '../components/Common';
import VideoPlayer from '../components/VideoPlayer';
import { formatMinutes } from '../utils/format';
import './course.css';

export default function CoursePlayer() {
  const { id } = useParams();
  const [params, setParams] = useSearchParams();
  const { isAdmin } = useAuth();
  const { data, error, reload: load, setData } = useFetch(`/api/courses/${id}`);
  const [marking, setMarking] = useState(false);
  const [downloading, setDownloading] = useState(false);
  usePageTitle(data?.course.title || 'Course');


  const lessons = useMemo(() => data?.lessons || [], [data]);
  const lessonParam = Number(params.get('lesson'));
  const completedIds = useMemo(() => new Set(data?.progress?.completedLessonIds || []), [data]);
  const current = lessons.find((l) => l.id === lessonParam)
    || lessons.find((l) => !completedIds.has(l.id))
    || lessons[0];
  const index = current ? lessons.indexOf(current) : -1;

  const go = (lesson) => {
    setParams({ lesson: String(lesson.id) });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const markComplete = async () => {
    if (!current) return;
    setMarking(true);
    try {
      const { data: progress } = await api.post(`/api/courses/lessons/${current.id}/complete`);
      setData((d) => ({ ...d, progress }));
      if (progress.certificateEligible && !data.progress?.certificateEligible) {
        toast.success('Course complete! Your certificate is ready.');
      } else if (index < lessons.length - 1) {
        go(lessons[index + 1]);
      }
    } catch (e) {
      toast.error(errorMessage(e));
    } finally {
      setMarking(false);
    }
  };

  const downloadCertificate = async () => {
    setDownloading(true);
    try {
      await downloadFile(`/api/certificates/course/${id}/download`, 'LearnStream_Certificate.pdf');
      load();
    } catch (e) {
      toast.error(await blobErrorMessage(e, 'Could not download the certificate'));
    } finally {
      setDownloading(false);
    }
  };

  if (error) return <div className="wrap page"><ErrorState message={error} onRetry={load} /></div>;
  if (!data) return <Loader />;
  if (!data.course.enrolled && !isAdmin) return <Navigate to={`/courses/${id}`} replace />;

  const { course, quizzes, progress } = data;
  const isDone = current && completedIds.has(current.id);

  return (
    <div className="wrap page player">
      <div className="player-main">
        <Link to={`/courses/${course.id}`} className="crumb"><FiChevronLeft /> {course.title}</Link>
        {current ? (
          <>
            {current.locked ? (
              <div className="video-frame video-empty"><FiLock size={28} /><p>This lesson is locked.</p></div>
            ) : (
              <VideoPlayer
                url={current.videoUrl}
                type={current.videoType}
                title={current.title}
                onEnded={() => { if (progress && !isDone && !marking) markComplete(); }}
                onExpired={load}
              />
            )}
            <div className="player-head">
              <div>
                <span className="muted small">Lesson {index + 1} of {lessons.length}{current.durationMinutes ? `, ${formatMinutes(current.durationMinutes)}` : ''}</span>
                <h1 className="player-title">{current.title}</h1>
              </div>
              {progress && (
                isDone ? (
                  <span className="tag tag-green player-done"><FiCheck /> Completed</span>
                ) : (
                  <button className="btn btn-success" onClick={markComplete} disabled={marking}>
                    <FiCheckCircle /> {marking ? 'Saving...' : 'Mark as complete'}
                  </button>
                )
              )}
            </div>
            {current.description && <p className="player-desc">{current.description}</p>}
            <div className="row player-nav">
              <button className="btn btn-outline" disabled={index <= 0} onClick={() => go(lessons[index - 1])}><FiChevronLeft /> Previous</button>
              <span className="spacer" />
              <button className="btn btn-outline" disabled={index >= lessons.length - 1} onClick={() => go(lessons[index + 1])}>Next <FiChevronRight /></button>
            </div>
          </>
        ) : (
          <div className="video-frame video-empty"><p>No lessons in this course yet.</p></div>
        )}
      </div>

      <aside className="player-side">
        {progress && (
          <div className="panel panel-tight">
            <div className="row small" style={{ marginBottom: 8 }}>
              <strong>Your progress</strong><span className="spacer" /><strong>{progress.percentage}%</strong>
            </div>
            <ProgressBar value={progress.percentage} label="Course progress" />
            <p className="muted small" style={{ margin: '8px 0 0' }}>{progress.completedCount} of {progress.totalCount} lessons complete</p>
          </div>
        )}

        <div className="panel panel-tight">
          <h4 style={{ marginBottom: 12 }}>Lessons</h4>
          <ol className="stream-list">
            {lessons.map((l, i) => {
              const done = completedIds.has(l.id);
              return (
                <li key={l.id} className={`${done ? 'done' : ''} ${l.id === current?.id ? 'current' : ''}`}>
                  <button onClick={() => go(l)}>
                    <span className="stream-dot">{done ? <FiCheck /> : i + 1}</span>
                    <span className="stream-text">{l.title}</span>
                  </button>
                </li>
              );
            })}
          </ol>
        </div>

        {quizzes.length > 0 && (
          <div className="panel panel-tight">
            <h4 style={{ marginBottom: 10 }}>Course quiz</h4>
            {quizzes.map((q) => (
              <div key={q.id} className="quiz-row">
                <FiHelpCircle />
                <span className="quiz-row-title">{q.title}</span>
                {q.passed ? <span className="tag tag-green">Passed</span>
                  : <Link to={`/quizzes/${q.id}`} className="btn btn-outline btn-sm">Take quiz</Link>}
              </div>
            ))}
          </div>
        )}

        {progress && (
          <div className={`panel panel-tight cert-box ${progress.certificateEligible ? 'ready' : ''}`}>
            <FiAward size={26} />
            {progress.certificateEligible ? (
              <>
                <h4>Your certificate is ready</h4>
                <button className="btn btn-gold btn-block" onClick={downloadCertificate} disabled={downloading}>
                  <FiDownload /> {downloading ? 'Preparing PDF...' : 'Download certificate'}
                </button>
                {progress.certificateSerial && <p className="small muted" style={{ margin: '8px 0 0' }}>ID: {progress.certificateSerial}</p>}
              </>
            ) : (
              <>
                <h4>Certificate</h4>
                <p className="small muted" style={{ margin: 0 }}>
                  Complete all lessons{progress.quizzesTotal > 0 ? ` and pass the quiz (${progress.quizzesPassed}/${progress.quizzesTotal} passed)` : ''} to unlock it.
                </p>
              </>
            )}
          </div>
        )}
      </aside>
    </div>
  );
}

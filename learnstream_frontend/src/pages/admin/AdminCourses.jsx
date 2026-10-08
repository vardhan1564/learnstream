import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { toast } from 'react-toastify';
import { FiPlus, FiEdit2, FiExternalLink, FiBookOpen } from 'react-icons/fi';
import api, { errorMessage } from '../../api/client';
import useFetch from '../../api/useFetch';
import { EmptyState, ErrorState, Loader } from '../../components/Common';
import { CourseArt } from '../../components/CourseCard';
import { formatPrice } from '../../utils/format';
import { toPlayable } from '../../utils/video';
import { DeleteButton, PublishedTag, RowControls, moveItem } from './shared';
import VideoUpload from './VideoUpload';

export function CourseList() {
  const { data: courses, error, reload: load } = useFetch('/api/admin/courses');

  return (
    <>
      <div className="admin-head">
        <div>
          <h1>Courses & videos</h1>
          <p className="muted">Create courses and add video lessons. Only admins can do this.</p>
        </div>
        <Link to="/admin/courses/new" className="btn btn-primary"><FiPlus /> New course</Link>
      </div>
      {error ? <ErrorState message={error} onRetry={load} />
        : courses === null ? <Loader />
        : courses.length === 0 ? (
          <EmptyState icon={FiBookOpen} title="No courses yet" action={<Link to="/admin/courses/new" className="btn btn-primary">Create your first course</Link>}>
            Add a title, price and YouTube video links for each lesson.
          </EmptyState>
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead><tr><th>Course</th><th>Price</th><th>Lessons</th><th>Students</th><th>Status</th><th /></tr></thead>
              <tbody>
                {courses.map(({ course, enrollments }) => (
                  <tr key={course.id}>
                    <td>
                      <div className="row" style={{ flexWrap: 'nowrap' }}>
                        <CourseArt course={course} className="admin-thumb" />
                        <div><strong>{course.title}</strong><div className="muted small">{course.category || 'No category'}</div></div>
                      </div>
                    </td>
                    <td>{formatPrice(course.price)}</td>
                    <td>{course.lessonCount}</td>
                    <td>{enrollments}</td>
                    <td><PublishedTag published={course.published} /></td>
                    <td>
                      <div className="row-controls">
                        <Link to={`/courses/${course.id}`} className="icon-btn" title="View as student" aria-label="View course"><FiExternalLink /></Link>
                        <Link to={`/admin/courses/${course.id}`} className="icon-btn" title="Edit" aria-label="Edit course"><FiEdit2 /></Link>
                        <DeleteButton path={`/api/admin/courses/${course.id}`} what="Course" onDeleted={load}
                                      warning={enrollments > 0 ? `${enrollments} students are enrolled, so the server will refuse. Unpublish it instead.` : 'The course and all its lessons will be removed permanently.'} />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
    </>
  );
}

const emptyLesson = () => ({ key: crypto.randomUUID(), id: null, title: '', description: '', source: 'LINK', videoUrl: '', videoFileKey: '', videoFileName: '', durationMinutes: '', preview: false });

export function CourseEditor() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isNew = !id;
  const [form, setForm] = useState(isNew ? {
    title: '', description: '', price: '0', thumbnail: '', category: '', level: 'Beginner', instructor: '', published: true,
  } : null);
  const [lessons, setLessons] = useState(isNew ? [emptyLesson()] : []);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (isNew) return;
    api.get(`/api/admin/courses/${id}`).then(({ data }) => {
      const c = data.course;
      setForm({
        title: c.title || '', description: c.description || '', price: String(c.price ?? 0), thumbnail: c.thumbnail || '',
        category: c.category || '', level: c.level || '', instructor: c.instructor || '', published: c.published,
      });
      setLessons(data.lessons.map((l) => ({
        key: String(l.id), id: l.id, title: l.title, description: l.description || '',
        source: l.videoType === 'UPLOAD' ? 'UPLOAD' : 'LINK',
        videoUrl: l.videoType === 'UPLOAD' ? '' : (l.videoUrl || ''),
        videoFileKey: l.videoFileKey || '', videoFileName: l.videoFileName || '',
        durationMinutes: l.durationMinutes ?? '', preview: l.preview,
      })));
    }).catch((e) => setError(errorMessage(e)));
  }, [id, isNew]);

  if (!form) return error ? <ErrorState message={error} /> : <Loader />;

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.type === 'checkbox' ? e.target.checked : e.target.value });
  const setLesson = (i, k, v) => setLessons(lessons.map((l, j) => (j === i ? { ...l, [k]: v } : l)));

  const save = async (e) => {
    e.preventDefault();
    setError('');
    const price = Number(form.price);
    if (!form.title.trim()) return setError('Course title is required.');
    if (Number.isNaN(price) || price < 0) return setError('Price must be 0 (free) or more.');
    for (const [i, l] of lessons.entries()) {
      if (!l.title.trim()) return setError(`Lesson ${i + 1} needs a title.`);
      if (l.source === 'UPLOAD' && !l.videoFileKey) return setError(`Lesson ${i + 1}: upload a video or switch to "Video link".`);
      if (l.source === 'LINK' && !/^https?:\/\//.test(l.videoUrl.trim())) return setError(`Lesson ${i + 1} needs a video link starting with https://`);
    }
    setSaving(true);
    try {
      const body = {
        ...form,
        title: form.title.trim(),
        price,
        lessons: lessons.map((l) => ({
          id: l.id, title: l.title.trim(), description: l.description,
          videoUrl: l.source === 'LINK' ? l.videoUrl.trim() : '',
          videoFileKey: l.source === 'UPLOAD' ? l.videoFileKey : '',
          videoFileName: l.source === 'UPLOAD' ? l.videoFileName : '',
          durationMinutes: l.durationMinutes === '' ? null : Number(l.durationMinutes), preview: l.preview,
        })),
      };
      if (isNew) await api.post('/api/admin/courses', body);
      else await api.put(`/api/admin/courses/${id}`, body);
      toast.success(isNew ? 'Course created' : 'Course saved');
      navigate('/admin/courses');
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={save} noValidate>
      <div className="admin-head">
        <div>
          <Link to="/admin/courses" className="crumb">Courses</Link>
          <h1>{isNew ? 'New course' : 'Edit course'}</h1>
        </div>
        <div className="row">
          <label className="check"><input type="checkbox" checked={form.published} onChange={set('published')} /> Published</label>
          <button className="btn btn-primary" disabled={saving}>{saving ? 'Saving...' : isNew ? 'Create course' : 'Save changes'}</button>
        </div>
      </div>
      {error && <div className="alert alert-error" role="alert">{error}</div>}

      <div className="panel editor-section">
        <h3>Details</h3>
        <label className="field"><span>Title</span><input className="input" value={form.title} onChange={set('title')} maxLength={200} required /></label>
        <label className="field"><span>Description</span><textarea className="textarea" rows={4} value={form.description} onChange={set('description')} maxLength={10000} /></label>
        <div className="form-grid">
          <label className="field"><span>Price (₹)</span><input className="input" type="number" min="0" step="1" value={form.price} onChange={set('price')} />
            <span className="hint">0 makes the course free.</span></label>
          <label className="field"><span>Category</span><input className="input" value={form.category} onChange={set('category')} placeholder="Java, Web Development..." maxLength={60} /></label>
          <label className="field"><span>Level</span>
            <select className="select" value={form.level} onChange={set('level')}>
              <option value="">Not set</option><option>Beginner</option><option>Intermediate</option><option>Advanced</option>
            </select>
          </label>
          <label className="field"><span>Instructor</span><input className="input" value={form.instructor} onChange={set('instructor')} maxLength={100} /></label>
        </div>
        <label className="field"><span>Thumbnail image URL (optional)</span>
          <input className="input" value={form.thumbnail} onChange={set('thumbnail')} placeholder="https://..." maxLength={1000} />
          <span className="hint">Leave empty to use generated cover art.</span>
        </label>
      </div>

      <div className="panel editor-section">
        <div className="panel-title">
          <h3>Lessons ({lessons.length})</h3>
          <button type="button" className="btn btn-outline btn-sm" onClick={() => setLessons([...lessons, emptyLesson()])}><FiPlus /> Add lesson</button>
        </div>
        <p className="muted small">For each lesson, either paste a link (YouTube, Vimeo, Google Drive, .mp4) or upload a video file. Uploaded videos are stored outside the database and students only get short-lived links, so a copied link stops working. Tick "Free preview" to let anyone watch a lesson before buying. Students keep their progress on lessons you don't remove.</p>
        {lessons.length === 0 && <p className="muted">No lessons yet.</p>}
        {lessons.map((l, i) => {
          const bad = l.source === 'LINK' && l.videoUrl && !toPlayable(l.videoUrl);
          return (
            <div key={l.key} className="repeat-row">
              <div className="repeat-index">{i + 1}</div>
              <div className="repeat-body">
                <label className="field"><span>Lesson title</span><input className="input" value={l.title} onChange={(e) => setLesson(i, 'title', e.target.value)} maxLength={200} /></label>
                <div className="field">
                  <div className="row" style={{ marginBottom: 8 }}>
                    <span className="label" style={{ margin: 0 }}>Video</span>
                    <div className="segmented" role="group" aria-label="Video source">
                      <button type="button" className={l.source === 'LINK' ? 'active' : ''} onClick={() => setLesson(i, 'source', 'LINK')}>Video link</button>
                      <button type="button" className={l.source === 'UPLOAD' ? 'active' : ''} onClick={() => setLesson(i, 'source', 'UPLOAD')}>Upload file</button>
                    </div>
                  </div>
                  {l.source === 'LINK' ? (
                    <>
                      <input className="input" value={l.videoUrl} onChange={(e) => setLesson(i, 'videoUrl', e.target.value)} placeholder="https://www.youtube.com/watch?v=..." maxLength={1000} aria-label="Video link" />
                      {bad && <span className="hint text-red">This link doesn't look playable.</span>}
                    </>
                  ) : (
                    <VideoUpload
                      fileKey={l.videoFileKey}
                      fileName={l.videoFileName}
                      onClear={() => setLessons((prev) => prev.map((x, j) => (j === i ? { ...x, videoFileKey: '', videoFileName: '' } : x)))}
                      onUploaded={({ key, fileName, durationMinutes }) => setLessons((prev) => prev.map((x, j) => (j === i ? {
                        ...x, videoFileKey: key, videoFileName: fileName,
                        durationMinutes: x.durationMinutes === '' && durationMinutes ? durationMinutes : x.durationMinutes,
                      } : x)))}
                    />
                  )}
                </div>
                <label className="field"><span>Description (optional)</span><input className="input" value={l.description} onChange={(e) => setLesson(i, 'description', e.target.value)} maxLength={5000} /></label>
                <div className="row">
                  <label className="field" style={{ marginBottom: 0, width: 160 }}><span>Duration (min)</span>
                    <input className="input" type="number" min="0" value={l.durationMinutes} onChange={(e) => setLesson(i, 'durationMinutes', e.target.value)} /></label>
                  <label className="check" style={{ marginTop: 22 }}><input type="checkbox" checked={l.preview} onChange={(e) => setLesson(i, 'preview', e.target.checked)} /> Free preview</label>
                </div>
              </div>
              <RowControls index={i} count={lessons.length} label="lesson"
                           onMove={(idx, dir) => setLessons(moveItem(lessons, idx, dir))}
                           onRemove={(idx) => setLessons(lessons.filter((_, j) => j !== idx))} />
            </div>
          );
        })}
        {lessons.length > 0 && (
          <button type="button" className="btn btn-outline btn-sm" onClick={() => setLessons([...lessons, emptyLesson()])}><FiPlus /> Add lesson</button>
        )}
      </div>
      <div className="row" style={{ justifyContent: 'flex-end' }}>
        <Link to="/admin/courses" className="btn btn-ghost">Cancel</Link>
        <button className="btn btn-primary" disabled={saving}>{saving ? 'Saving...' : isNew ? 'Create course' : 'Save changes'}</button>
      </div>
    </form>
  );
}

import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { toast } from 'react-toastify';
import { FiPlus, FiEdit2, FiMap, FiExternalLink } from 'react-icons/fi';
import api, { errorMessage } from '../../api/client';
import useFetch from '../../api/useFetch';
import { EmptyState, ErrorState, Loader } from '../../components/Common';
import { DeleteButton, PublishedTag, RowControls, moveItem } from './shared';

export function RoadmapList() {
  const { data: roadmaps, error, reload: load } = useFetch('/api/admin/roadmaps');
  return (
    <>
      <div className="admin-head">
        <div>
          <h1>Roadmaps</h1>
          <p className="muted">Guided learning paths. Link steps to your courses or to outside resources.</p>
        </div>
        <Link to="/admin/roadmaps/new" className="btn btn-primary"><FiPlus /> New roadmap</Link>
      </div>
      {error ? <ErrorState message={error} onRetry={load} />
        : roadmaps === null ? <Loader />
        : roadmaps.length === 0 ? (
          <EmptyState icon={FiMap} title="No roadmaps yet" action={<Link to="/admin/roadmaps/new" className="btn btn-primary">Create a roadmap</Link>}>
            For example: "Java Backend Developer" with 6 steps.
          </EmptyState>
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead><tr><th>Roadmap</th><th>Level</th><th>Steps</th><th>Status</th><th /></tr></thead>
              <tbody>
                {roadmaps.map(({ roadmap: r }) => (
                  <tr key={r.id}>
                    <td><strong>{r.title}</strong><div className="muted small">{r.duration || ''}</div></td>
                    <td>{r.level || '-'}</td>
                    <td>{r.stepCount}</td>
                    <td><PublishedTag published={r.published} /></td>
                    <td>
                      <div className="row-controls">
                        <Link to={`/roadmaps/${r.id}`} className="icon-btn" aria-label="View roadmap" title="View"><FiExternalLink /></Link>
                        <Link to={`/admin/roadmaps/${r.id}`} className="icon-btn" aria-label="Edit roadmap" title="Edit"><FiEdit2 /></Link>
                        <DeleteButton path={`/api/admin/roadmaps/${r.id}`} what="Roadmap" onDeleted={load} warning="Students' progress on this roadmap will be removed." />
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

const emptyStep = () => ({ key: crypto.randomUUID(), id: null, title: '', description: '', resourceUrl: '', courseId: '' });

export function RoadmapEditor() {
  const { id } = useParams();
  const isNew = !id;
  const navigate = useNavigate();
  const [courses, setCourses] = useState([]);
  const [form, setForm] = useState(isNew ? { title: '', description: '', level: 'Beginner', duration: '', published: true } : null);
  const [steps, setSteps] = useState(isNew ? [emptyStep()] : []);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.get('/api/admin/courses').then((r) => setCourses(r.data.map((c) => c.course))).catch(() => {});
    if (isNew) return;
    api.get('/api/admin/roadmaps').then(({ data }) => {
      const found = data.find((d) => String(d.roadmap.id) === String(id));
      if (!found) { setError('Roadmap not found'); return; }
      const r = found.roadmap;
      setForm({ title: r.title, description: r.description || '', level: r.level || '', duration: r.duration || '', published: r.published });
      setSteps(found.steps.map((s) => ({ key: String(s.id), id: s.id, title: s.title, description: s.description || '', resourceUrl: s.resourceUrl || '', courseId: s.courseId ? String(s.courseId) : '' })));
    }).catch((e) => setError(errorMessage(e)));
  }, [id, isNew]);

  if (!form) return error ? <ErrorState message={error} /> : <Loader />;

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.type === 'checkbox' ? e.target.checked : e.target.value });
  const setS = (i, k, v) => setSteps(steps.map((s, j) => (j === i ? { ...s, [k]: v } : s)));

  const save = async (e) => {
    e.preventDefault();
    setError('');
    if (!form.title.trim()) return setError('Title is required.');
    if (steps.length === 0) return setError('Add at least one step.');
    for (const [i, s] of steps.entries()) {
      if (!s.title.trim()) return setError(`Step ${i + 1} needs a title.`);
      if (s.resourceUrl && !/^https?:\/\//.test(s.resourceUrl.trim())) return setError(`Step ${i + 1}: resource URL must start with https://`);
    }
    setSaving(true);
    try {
      const body = {
        ...form,
        title: form.title.trim(),
        steps: steps.map((s) => ({ id: s.id, title: s.title.trim(), description: s.description, resourceUrl: s.resourceUrl.trim(), courseId: s.courseId ? Number(s.courseId) : null })),
      };
      if (isNew) await api.post('/api/admin/roadmaps', body);
      else await api.put(`/api/admin/roadmaps/${id}`, body);
      toast.success(isNew ? 'Roadmap created' : 'Roadmap saved');
      navigate('/admin/roadmaps');
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
          <Link to="/admin/roadmaps" className="crumb">Roadmaps</Link>
          <h1>{isNew ? 'New roadmap' : 'Edit roadmap'}</h1>
        </div>
        <div className="row">
          <label className="check"><input type="checkbox" checked={form.published} onChange={set('published')} /> Published</label>
          <button className="btn btn-primary" disabled={saving}>{saving ? 'Saving...' : isNew ? 'Create roadmap' : 'Save changes'}</button>
        </div>
      </div>
      {error && <div className="alert alert-error" role="alert">{error}</div>}
      <div className="panel editor-section">
        <h3>Details</h3>
        <label className="field"><span>Title</span><input className="input" value={form.title} onChange={set('title')} maxLength={200} /></label>
        <label className="field"><span>Description</span><textarea className="textarea" rows={3} value={form.description} onChange={set('description')} maxLength={5000} /></label>
        <div className="form-grid">
          <label className="field"><span>Level</span>
            <select className="select" value={form.level} onChange={set('level')}>
              <option value="">Not set</option><option>Beginner</option><option>Intermediate</option><option>Advanced</option>
            </select>
          </label>
          <label className="field"><span>Duration</span><input className="input" value={form.duration} onChange={set('duration')} placeholder="3 months" maxLength={50} /></label>
        </div>
      </div>
      <div className="panel editor-section">
        <div className="panel-title"><h3>Steps ({steps.length})</h3></div>
        {steps.map((s, i) => (
          <div key={s.key} className="repeat-row">
            <div className="repeat-index">{i + 1}</div>
            <div className="repeat-body">
              <label className="field"><span>Step title</span><input className="input" value={s.title} onChange={(e) => setS(i, 'title', e.target.value)} maxLength={200} /></label>
              <label className="field"><span>What to learn</span><textarea className="textarea" rows={2} value={s.description} onChange={(e) => setS(i, 'description', e.target.value)} maxLength={5000} /></label>
              <div className="form-grid">
                <label className="field"><span>Linked course (optional)</span>
                  <select className="select" value={s.courseId} onChange={(e) => setS(i, 'courseId', e.target.value)}>
                    <option value="">None</option>
                    {courses.map((c) => <option key={c.id} value={c.id}>{c.title}</option>)}
                  </select>
                </label>
                <label className="field"><span>Resource URL (optional)</span><input className="input" value={s.resourceUrl} onChange={(e) => setS(i, 'resourceUrl', e.target.value)} placeholder="https://..." maxLength={1000} /></label>
              </div>
            </div>
            <RowControls index={i} count={steps.length} label="step"
                         onMove={(idx, dir) => setSteps(moveItem(steps, idx, dir))}
                         onRemove={(idx) => setSteps(steps.filter((_, j) => j !== idx))} />
          </div>
        ))}
        <button type="button" className="btn btn-outline btn-sm" onClick={() => setSteps([...steps, emptyStep()])}><FiPlus /> Add step</button>
      </div>
      <div className="row" style={{ justifyContent: 'flex-end' }}>
        <Link to="/admin/roadmaps" className="btn btn-ghost">Cancel</Link>
        <button className="btn btn-primary" disabled={saving}>{saving ? 'Saving...' : isNew ? 'Create roadmap' : 'Save changes'}</button>
      </div>
    </form>
  );
}

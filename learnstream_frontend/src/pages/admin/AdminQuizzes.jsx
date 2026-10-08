import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { toast } from 'react-toastify';
import { FiPlus, FiEdit2, FiHelpCircle, FiShield } from 'react-icons/fi';
import api, { errorMessage } from '../../api/client';
import useFetch from '../../api/useFetch';
import { EmptyState, ErrorState, Loader } from '../../components/Common';
import { DeleteButton, PublishedTag, RowControls, moveItem } from './shared';

export function QuizList() {
  const { data: quizzes, error, reload: load } = useFetch('/api/admin/quizzes');

  return (
    <>
      <div className="admin-head">
        <div>
          <h1>Quizzes (MCQ)</h1>
          <p className="muted">Correct answers stay on the server: students never receive them, not even in the browser's developer tools.</p>
        </div>
        <Link to="/admin/quizzes/new" className="btn btn-primary"><FiPlus /> New quiz</Link>
      </div>
      {error ? <ErrorState message={error} onRetry={load} />
        : quizzes === null ? <Loader />
        : quizzes.length === 0 ? (
          <EmptyState icon={FiHelpCircle} title="No quizzes yet" action={<Link to="/admin/quizzes/new" className="btn btn-primary">Create a quiz</Link>}>
            Attach a quiz to a course to make passing it a certificate requirement.
          </EmptyState>
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead><tr><th>Quiz</th><th>Course</th><th>Questions</th><th>Pass mark</th><th>Attempts</th><th>Status</th><th /></tr></thead>
              <tbody>
                {quizzes.map((q) => (
                  <tr key={q.id}>
                    <td><strong>{q.title}</strong><div className="muted small">{q.category || 'No category'}</div></td>
                    <td>{q.courseTitle || <span className="muted">Standalone</span>}</td>
                    <td>{q.questionCount}</td>
                    <td>{q.passPercentage}%</td>
                    <td>{q.maxAttempts === 0 ? 'Unlimited' : q.maxAttempts}</td>
                    <td><PublishedTag published={q.published} /></td>
                    <td>
                      <div className="row-controls">
                        <Link to={`/admin/quizzes/${q.id}`} className="icon-btn" aria-label="Edit quiz" title="Edit"><FiEdit2 /></Link>
                        <DeleteButton path={`/api/admin/quizzes/${q.id}`} what="Quiz" onDeleted={load}
                                      warning="All student attempts for this quiz will be deleted too. Leaderboard points from it are removed." />
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

const emptyQuestion = () => ({ key: crypto.randomUUID(), id: null, questionText: '', optionA: '', optionB: '', optionC: '', optionD: '', correctOption: '' });

export function QuizEditor() {
  const { id } = useParams();
  const isNew = !id;
  const navigate = useNavigate();
  const [courses, setCourses] = useState([]);
  const [form, setForm] = useState(isNew ? { title: '', description: '', category: '', courseId: '', passPercentage: 60, maxAttempts: 3, published: true } : null);
  const [questions, setQuestions] = useState(isNew ? [emptyQuestion()] : []);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.get('/api/admin/courses').then((r) => setCourses(r.data.map((c) => c.course))).catch(() => {});
    if (isNew) return;
    api.get(`/api/admin/quizzes/${id}`).then(({ data }) => {
      const q = data.quiz;
      setForm({
        title: q.title, description: q.description || '', category: q.category || '', courseId: q.courseId ? String(q.courseId) : '',
        passPercentage: q.passPercentage, maxAttempts: q.maxAttempts, published: q.published,
      });
      setQuestions(data.questions.map((x) => ({
        key: String(x.id), id: x.id, questionText: x.questionText, optionA: x.optionA, optionB: x.optionB,
        optionC: x.optionC || '', optionD: x.optionD || '', correctOption: x.correctOption,
      })));
    }).catch((e) => setError(errorMessage(e)));
  }, [id, isNew]);

  if (!form) return error ? <ErrorState message={error} /> : <Loader />;

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.type === 'checkbox' ? e.target.checked : e.target.value });
  const setQ = (i, k, v) => setQuestions(questions.map((q, j) => (j === i ? { ...q, [k]: v } : q)));

  const save = async (e) => {
    e.preventDefault();
    setError('');
    if (!form.title.trim()) return setError('Quiz title is required.');
    if (questions.length === 0) return setError('Add at least one question.');
    for (const [i, q] of questions.entries()) {
      if (!q.questionText.trim()) return setError(`Question ${i + 1}: enter the question text.`);
      if (!q.optionA.trim() || !q.optionB.trim()) return setError(`Question ${i + 1}: options A and B are required.`);
      if (!q.correctOption) return setError(`Question ${i + 1}: choose the correct answer.`);
      if (!q[`option${q.correctOption}`]?.trim()) return setError(`Question ${i + 1}: the correct answer points to an empty option.`);
    }
    setSaving(true);
    try {
      const body = {
        ...form,
        title: form.title.trim(),
        courseId: form.courseId ? Number(form.courseId) : null,
        passPercentage: Number(form.passPercentage),
        maxAttempts: Number(form.maxAttempts),
        questions: questions.map(({ key: _key, ...q }) => q),
      };
      if (isNew) await api.post('/api/admin/quizzes', body);
      else await api.put(`/api/admin/quizzes/${id}`, body);
      toast.success(isNew ? 'Quiz created' : 'Quiz saved');
      navigate('/admin/quizzes');
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
          <Link to="/admin/quizzes" className="crumb">Quizzes</Link>
          <h1>{isNew ? 'New quiz' : 'Edit quiz'}</h1>
        </div>
        <div className="row">
          <label className="check"><input type="checkbox" checked={form.published} onChange={set('published')} /> Published</label>
          <button className="btn btn-primary" disabled={saving}>{saving ? 'Saving...' : isNew ? 'Create quiz' : 'Save changes'}</button>
        </div>
      </div>
      {error && <div className="alert alert-error" role="alert">{error}</div>}

      <div className="panel editor-section">
        <h3>Settings</h3>
        <label className="field"><span>Title</span><input className="input" value={form.title} onChange={set('title')} maxLength={200} /></label>
        <label className="field"><span>Description</span><textarea className="textarea" rows={2} value={form.description} onChange={set('description')} maxLength={5000} /></label>
        <div className="form-grid">
          <label className="field"><span>Category</span><input className="input" value={form.category} onChange={set('category')} placeholder="Java, DSA..." maxLength={60} /></label>
          <label className="field"><span>Attach to course (optional)</span>
            <select className="select" value={form.courseId} onChange={set('courseId')}>
              <option value="">Standalone practice quiz</option>
              {courses.map((c) => <option key={c.id} value={c.id}>{c.title}</option>)}
            </select>
            <span className="hint">Course quizzes must be passed to get the certificate, and only enrolled students can take them.</span>
          </label>
          <label className="field"><span>Pass mark (%)</span><input className="input" type="number" min="1" max="100" value={form.passPercentage} onChange={set('passPercentage')} /></label>
          <label className="field"><span>Max attempts</span><input className="input" type="number" min="0" max="100" value={form.maxAttempts} onChange={set('maxAttempts')} />
            <span className="hint">0 = unlimited.</span></label>
        </div>
      </div>

      <div className="panel editor-section">
        <div className="panel-title">
          <h3>Questions ({questions.length})</h3>
          <span className="tag"><FiShield /> Answers are never sent to students</span>
        </div>
        {questions.map((q, i) => (
          <div key={q.key} className="repeat-row">
            <div className="repeat-index">{i + 1}</div>
            <div className="repeat-body">
              <label className="field"><span>Question</span><textarea className="textarea" rows={2} value={q.questionText} onChange={(e) => setQ(i, 'questionText', e.target.value)} maxLength={5000} /></label>
              <fieldset className="mcq-options">
                <legend className="label">Options (select the correct one)</legend>
                {['A', 'B', 'C', 'D'].map((k) => (
                  <div key={k} className={`mcq-option ${q.correctOption === k ? 'correct' : ''}`}>
                    <input type="radio" name={`correct-${q.key}`} checked={q.correctOption === k} onChange={() => setQ(i, 'correctOption', k)} aria-label={`Option ${k} is correct`} />
                    <span className="option-key">{k}</span>
                    <input className="input" value={q[`option${k}`]} onChange={(e) => setQ(i, `option${k}`, e.target.value)}
                           placeholder={k === 'A' || k === 'B' ? `Option ${k} (required)` : `Option ${k} (optional)`} maxLength={500} />
                  </div>
                ))}
              </fieldset>
            </div>
            <RowControls index={i} count={questions.length} label="question"
                         onMove={(idx, dir) => setQuestions(moveItem(questions, idx, dir))}
                         onRemove={(idx) => setQuestions(questions.filter((_, j) => j !== idx))} />
          </div>
        ))}
        <button type="button" className="btn btn-outline btn-sm" onClick={() => setQuestions([...questions, emptyQuestion()])}><FiPlus /> Add question</button>
      </div>
      <div className="row" style={{ justifyContent: 'flex-end' }}>
        <Link to="/admin/quizzes" className="btn btn-ghost">Cancel</Link>
        <button className="btn btn-primary" disabled={saving}>{saving ? 'Saving...' : isNew ? 'Create quiz' : 'Save changes'}</button>
      </div>
    </form>
  );
}

import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { toast } from 'react-toastify';
import { FiPlus, FiEdit2, FiCode, FiExternalLink, FiLock, FiEye } from 'react-icons/fi';
import api, { errorMessage } from '../../api/client';
import useFetch from '../../api/useFetch';
import { EmptyState, ErrorState, Loader } from '../../components/Common';
import { difficultyClass, difficultyLabel } from '../../utils/format';
import { DeleteButton, PublishedTag, RowControls, moveItem } from './shared';

const LANGS = [
  ['starterJava', 'Java'],
  ['starterPython', 'Python'],
  ['starterCpp', 'C++'],
  ['starterJavascript', 'JavaScript'],
];

export function ProblemList() {
  const { data: problems, error, reload: load } = useFetch('/api/admin/problems');

  return (
    <>
      <div className="admin-head">
        <div>
          <h1>Coding problems</h1>
          <p className="muted">Students read from standard input and print to standard output. Hidden test cases are never shown to them.</p>
        </div>
        <Link to="/admin/problems/new" className="btn btn-primary"><FiPlus /> New problem</Link>
      </div>
      {error ? <ErrorState message={error} onRetry={load} />
        : problems === null ? <Loader />
        : problems.length === 0 ? (
          <EmptyState icon={FiCode} title="No problems yet" action={<Link to="/admin/problems/new" className="btn btn-primary">Create a problem</Link>}>
            Add a description and some test cases. Every 5 solved problems earns a student a free course.
          </EmptyState>
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead><tr><th>Problem</th><th>Difficulty</th><th>Tests</th><th>Status</th><th /></tr></thead>
              <tbody>
                {problems.map((p) => {
                  const samples = p.testCases.filter((t) => t.sample).length;
                  return (
                    <tr key={p.id}>
                      <td><strong>{p.title}</strong><div className="muted small">{p.tags || 'No tags'}</div></td>
                      <td><span className={difficultyClass(p.difficulty)}>{difficultyLabel(p.difficulty)}</span></td>
                      <td className="small">{samples} sample, {p.testCases.length - samples} hidden</td>
                      <td><PublishedTag published={p.published} /></td>
                      <td>
                        <div className="row-controls">
                          <Link to={`/problems/${p.id}`} className="icon-btn" title="Try it in the editor" aria-label="Open problem"><FiExternalLink /></Link>
                          <Link to={`/admin/problems/${p.id}`} className="icon-btn" title="Edit" aria-label="Edit problem"><FiEdit2 /></Link>
                          <DeleteButton path={`/api/admin/problems/${p.id}`} what="Problem" onDeleted={load}
                                        warning="All submissions for this problem will be deleted, and students lose the points and reward progress from it." />
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
    </>
  );
}

const emptyTest = (sample = false) => ({ key: crypto.randomUUID(), input: '', expectedOutput: '', sample });

export function ProblemEditor() {
  const { id } = useParams();
  const isNew = !id;
  const navigate = useNavigate();
  const [form, setForm] = useState(isNew ? {
    title: '', description: '', difficulty: 'EASY', inputFormat: '', outputFormat: '', constraintsText: '', tags: '',
    starterJava: '', starterPython: '', starterCpp: '', starterJavascript: '', published: true,
  } : null);
  const [tests, setTests] = useState(isNew ? [emptyTest(true), emptyTest(false)] : []);
  const [starterTab, setStarterTab] = useState('starterJava');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (isNew) return;
    api.get(`/api/admin/problems/${id}`).then(({ data }) => {
      setForm({
        title: data.title, description: data.description, difficulty: data.difficulty,
        inputFormat: data.inputFormat || '', outputFormat: data.outputFormat || '', constraintsText: data.constraintsText || '',
        tags: data.tags || '', starterJava: data.starterJava || '', starterPython: data.starterPython || '',
        starterCpp: data.starterCpp || '', starterJavascript: data.starterJavascript || '', published: data.published,
      });
      setTests(data.testCases.map((t) => ({ key: String(t.id), input: t.input || '', expectedOutput: t.expectedOutput, sample: t.sample })));
    }).catch((e) => setError(errorMessage(e)));
  }, [id, isNew]);

  if (!form) return error ? <ErrorState message={error} /> : <Loader />;

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.type === 'checkbox' ? e.target.checked : e.target.value });
  const setT = (i, k, v) => setTests(tests.map((t, j) => (j === i ? { ...t, [k]: v } : t)));

  const save = async (e) => {
    e.preventDefault();
    setError('');
    if (!form.title.trim() || !form.description.trim()) return setError('Title and description are required.');
    if (tests.length === 0) return setError('Add at least one test case.');
    if (!tests.some((t) => t.sample)) return setError('Mark at least one test case as a visible example.');
    if (tests.some((t) => t.expectedOutput.trim() === '')) return setError('Every test case needs an expected output.');
    if (form.starterJava.trim() && !/\bclass\s+Main\b/.test(form.starterJava)) return setError('Java starter code must contain "public class Main".');
    setSaving(true);
    try {
      const body = { ...form, title: form.title.trim(), testCases: tests.map(({ key: _key, ...t }) => t) };
      if (isNew) await api.post('/api/admin/problems', body);
      else await api.put(`/api/admin/problems/${id}`, body);
      toast.success(isNew ? 'Problem created' : 'Problem saved');
      navigate('/admin/problems');
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
          <Link to="/admin/problems" className="crumb">Coding problems</Link>
          <h1>{isNew ? 'New problem' : 'Edit problem'}</h1>
        </div>
        <div className="row">
          <label className="check"><input type="checkbox" checked={form.published} onChange={set('published')} /> Published</label>
          <button className="btn btn-primary" disabled={saving}>{saving ? 'Saving...' : isNew ? 'Create problem' : 'Save changes'}</button>
        </div>
      </div>
      {error && <div className="alert alert-error" role="alert">{error}</div>}
      <div className="alert alert-info">Tip: save it as a draft (untick Published), open it from the list and solve it yourself to check the test cases before students see it.</div>

      <div className="panel editor-section">
        <h3>Problem statement</h3>
        <div className="form-grid">
          <label className="field"><span>Title</span><input className="input" value={form.title} onChange={set('title')} maxLength={200} /></label>
          <label className="field"><span>Difficulty</span>
            <select className="select" value={form.difficulty} onChange={set('difficulty')}>
              <option value="EASY">Easy</option><option value="MEDIUM">Medium</option><option value="HARD">Hard</option>
            </select>
          </label>
          <label className="field"><span>Topics</span><input className="input" value={form.tags} onChange={set('tags')} placeholder="Arrays,Hashing" maxLength={255} />
            <span className="hint">Comma separated.</span></label>
        </div>
        <label className="field"><span>Description</span><textarea className="textarea" rows={6} value={form.description} onChange={set('description')} maxLength={20000} /></label>
        <div className="form-grid">
          <label className="field"><span>Input format</span><textarea className="textarea" rows={3} value={form.inputFormat} onChange={set('inputFormat')} /></label>
          <label className="field"><span>Output format</span><textarea className="textarea" rows={3} value={form.outputFormat} onChange={set('outputFormat')} /></label>
          <label className="field"><span>Constraints</span><textarea className="textarea" rows={3} value={form.constraintsText} onChange={set('constraintsText')} /></label>
        </div>
      </div>

      <div className="panel editor-section">
        <h3>Starter code (optional)</h3>
        <p className="muted small">Leave a language empty to use the default template that reads from standard input. Java code must use <code>public class Main</code>.</p>
        <div className="tabs" style={{ marginBottom: 12 }}>
          {LANGS.map(([k, label]) => (
            <button type="button" key={k} className={`tab ${starterTab === k ? 'active' : ''}`} onClick={() => setStarterTab(k)}>
              {label}{form[k].trim() ? ' (custom)' : ''}
            </button>
          ))}
        </div>
        <textarea className="textarea code" rows={10} value={form[starterTab]} onChange={set(starterTab)} spellCheck={false}
                  placeholder="Leave empty for the default template" aria-label="Starter code" />
      </div>

      <div className="panel editor-section">
        <div className="panel-title">
          <h3>Test cases ({tests.length})</h3>
          <button type="button" className="btn btn-outline btn-sm" onClick={() => setTests([...tests, emptyTest(false)])}><FiPlus /> Add test case</button>
        </div>
        <p className="muted small">Output is compared line by line, ignoring trailing spaces and blank lines at the end. Maximum 30 tests.</p>
        {tests.map((t, i) => (
          <div key={t.key} className="repeat-row">
            <div className="repeat-index">{i + 1}</div>
            <div className="repeat-body">
              <div className="form-grid">
                <label className="field"><span>Input (stdin)</span><textarea className="textarea code" rows={3} value={t.input} onChange={(e) => setT(i, 'input', e.target.value)} spellCheck={false} /></label>
                <label className="field"><span>Expected output</span><textarea className="textarea code" rows={3} value={t.expectedOutput} onChange={(e) => setT(i, 'expectedOutput', e.target.value)} spellCheck={false} /></label>
              </div>
              <label className="check small">
                <input type="checkbox" checked={t.sample} onChange={(e) => setT(i, 'sample', e.target.checked)} />
                {t.sample ? <><FiEye /> Visible example</> : <><FiLock /> Hidden test</>}
              </label>
            </div>
            <RowControls index={i} count={tests.length} label="test case"
                         onMove={(idx, dir) => setTests(moveItem(tests, idx, dir))}
                         onRemove={(idx) => setTests(tests.filter((_, j) => j !== idx))} />
          </div>
        ))}
        {tests.length < 30 && <button type="button" className="btn btn-outline btn-sm" onClick={() => setTests([...tests, emptyTest(false)])}><FiPlus /> Add test case</button>}
      </div>
      <div className="row" style={{ justifyContent: 'flex-end' }}>
        <Link to="/admin/problems" className="btn btn-ghost">Cancel</Link>
        <button className="btn btn-primary" disabled={saving}>{saving ? 'Saving...' : isNew ? 'Create problem' : 'Save changes'}</button>
      </div>
    </form>
  );
}

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom';
import CodeMirror from '@uiw/react-codemirror';
import { java } from '@codemirror/lang-java';
import { python } from '@codemirror/lang-python';
import { cpp } from '@codemirror/lang-cpp';
import { javascript } from '@codemirror/lang-javascript';
import { toast } from 'react-toastify';
import { FiPlay, FiSend, FiRotateCcw, FiCheckCircle, FiXCircle, FiChevronLeft, FiLock } from 'react-icons/fi';
import api, { errorMessage } from '../api/client';
import useFetch from '../api/useFetch';
import { useAuth } from '../context/AuthContext';
import { ErrorState, Loader, usePageTitle } from '../components/Common';
import { difficultyClass, difficultyLabel, formatDateTime, verdictLabel } from '../utils/format';
import './problems.css';

const LANGS = [
  { id: 'java', name: 'Java', ext: () => java() },
  { id: 'python', name: 'Python 3', ext: () => python() },
  { id: 'cpp', name: 'C++', ext: () => cpp() },
  { id: 'javascript', name: 'JavaScript', ext: () => javascript() },
];

const draftKey = (id, lang) => `ls_draft_${id}_${lang}`;
const readDraft = (id, lang) => { try { return localStorage.getItem(draftKey(id, lang)); } catch { return null; } };
const writeDraft = (id, lang, code) => { try { localStorage.setItem(draftKey(id, lang), code); } catch { /* ignore */ } };
const clearDraft = (id, lang) => { try { localStorage.removeItem(draftKey(id, lang)); } catch { /* ignore */ } };

export default function ProblemWorkspace() {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();
  const { data: problem, error, setData: setProblem } = useFetch(`/api/problems/${id}`);
  const [lang, setLang] = useState(() => { try { return localStorage.getItem('ls_lang') || 'java'; } catch { return 'java'; } });
  const [code, setCode] = useState('');
  const [leftTab, setLeftTab] = useState('description');
  const [useCustom, setUseCustom] = useState(false);
  const [customInput, setCustomInput] = useState('');
  const [running, setRunning] = useState('');
  const [result, setResult] = useState(null);
  const [selectedTest, setSelectedTest] = useState(0);
  const [historyState, setHistory] = useState({ pid: null, list: null });
  const history = historyState.pid === id ? historyState.list : null;
  const saveTimer = useRef(null);
  usePageTitle(problem?.title || 'Problem');

  // Load the saved draft (or starter code) whenever the problem or language changes.
  // Done during render (not in an effect) so the editor never flashes the wrong code.
  const [codeKey, setCodeKey] = useState(null);
  const wantedKey = problem ? `${problem.id}:${lang}` : null;
  if (wantedKey && wantedKey !== codeKey) {
    setCodeKey(wantedKey);
    setCode(readDraft(id, lang) ?? problem.starterCode?.[lang] ?? '');
    if (codeKey && !codeKey.startsWith(`${problem.id}:`)) setResult(null);
  }

  const loadHistory = useCallback(() => {
    if (!user) return;
    api.get(`/api/problems/${id}/submissions`)
      .then((r) => setHistory({ pid: id, list: r.data }))
      .catch(() => setHistory({ pid: id, list: [] }));
  }, [id, user]);
  useEffect(() => { if (leftTab === 'submissions') loadHistory(); }, [leftTab, loadHistory]);

  const onCodeChange = (value) => {
    setCode(value);
    clearTimeout(saveTimer.current);
    saveTimer.current = setTimeout(() => writeDraft(id, lang, value), 400);
  };

  const changeLang = (next) => {
    writeDraft(id, lang, code);
    setLang(next);
    try { localStorage.setItem('ls_lang', next); } catch { /* ignore */ }
  };

  const resetCode = () => {
    clearDraft(id, lang);
    setCode(problem.starterCode?.[lang] ?? '');
  };

  const execute = async (kind) => {
    if (!user) {
      navigate('/login', { state: { from: location.pathname } });
      return;
    }
    if (!code.trim()) {
      toast.error('Write some code first.');
      return;
    }
    setRunning(kind);
    setResult(null);
    try {
      const body = { language: lang, code };
      if (kind === 'run' && useCustom) body.customInput = customInput;
      const { data } = await api.post(`/api/problems/${id}/${kind}`, body, { timeout: 120000 });
      setResult({ ...data, kind });
      const firstFail = data.results.findIndex((r) => !r.passed);
      setSelectedTest(firstFail >= 0 ? firstFail : 0);
      if (kind === 'submit') {
        if (data.status === 'ACCEPTED') {
          setProblem((p) => ({ ...p, solved: true }));
          if (data.firstSolve) {
            const r = data.rewards;
            if (r && r.problemsSolved > 0 && r.problemsSolved % r.problemsPerFreeCourse === 0) {
              toast.success('You earned a free course credit! Use it on any paid course.', { autoClose: 8000 });
            } else {
              toast.success(`Accepted! ${r ? `${r.problemsToNextCredit} more to your next free course.` : ''}`);
            }
          } else {
            toast.success('Accepted!');
          }
        }
        if (leftTab === 'submissions') loadHistory();
      }
    } catch (e) {
      toast.error(errorMessage(e, 'Could not run your code'));
    } finally {
      setRunning('');
    }
  };

  const extensions = useMemo(() => [LANGS.find((l) => l.id === lang)?.ext() || java()], [lang]);

  if (error) return <div className="wrap page"><ErrorState message={error} /></div>;
  if (!problem) return <Loader />;

  const test = result?.results?.[selectedTest];

  return (
    <div className="workspace">
      <section className="ws-left">
        <div className="ws-left-head">
          <Link to="/problems" className="crumb"><FiChevronLeft /> Problems</Link>
          <div className="tabs ws-tabs">
            <button className={`tab ${leftTab === 'description' ? 'active' : ''}`} onClick={() => setLeftTab('description')}>Description</button>
            <button className={`tab ${leftTab === 'submissions' ? 'active' : ''}`} onClick={() => setLeftTab('submissions')}>My submissions</button>
          </div>
        </div>

        <div className="ws-left-body">
          {leftTab === 'description' ? (
            <article className="problem-statement">
              <h1>{problem.title}</h1>
              <div className="row" style={{ marginBottom: 18 }}>
                <span className={difficultyClass(problem.difficulty)}>{difficultyLabel(problem.difficulty)}</span>
                {(problem.tags || '').split(',').filter(Boolean).map((t) => <span key={t} className="tag tag-grey">{t.trim()}</span>)}
                {problem.solved && <span className="tag tag-green"><FiCheckCircle /> Solved</span>}
              </div>
              <p className="pre-wrap">{problem.description}</p>
              {problem.inputFormat && (<><h4>Input</h4><p className="pre-wrap">{problem.inputFormat}</p></>)}
              {problem.outputFormat && (<><h4>Output</h4><p className="pre-wrap">{problem.outputFormat}</p></>)}
              {problem.constraintsText && (<><h4>Constraints</h4><p className="pre-wrap">{problem.constraintsText}</p></>)}
              {problem.samples.map((s, i) => (
                <div key={i} className="sample">
                  <h4>Example {i + 1}</h4>
                  <div className="sample-grid">
                    <div><span className="label">Input</span><pre>{s.input || '(empty)'}</pre></div>
                    <div><span className="label">Output</span><pre>{s.expectedOutput}</pre></div>
                  </div>
                </div>
              ))}
              {problem.hiddenTestCount > 0 && (
                <p className="muted small"><FiLock /> Plus {problem.hiddenTestCount} hidden test case{problem.hiddenTestCount > 1 ? 's' : ''} checked when you submit.</p>
              )}
            </article>
          ) : !user ? (
            <p className="muted"><Link to="/login" state={{ from: location.pathname }}>Log in</Link> to see your submissions.</p>
          ) : history === null ? <Loader /> : history.length === 0 ? (
            <p className="muted">No submissions yet. Press Submit when your solution passes the examples.</p>
          ) : (
            <ul className="history">
              {history.map((h) => (
                <li key={h.id}>
                  <span className={`verdict ${h.status === 'ACCEPTED' ? 'ok' : 'bad'}`}>{verdictLabel(h.status)}</span>
                  <span className="muted small">{LANGS.find((l) => l.id === h.language)?.name || h.language}, {h.passedCount}/{h.totalCount} tests</span>
                  <span className="spacer" />
                  <span className="muted small">{formatDateTime(h.submittedAt)}</span>
                  <button className="btn btn-ghost btn-sm" onClick={() => { changeLang(h.language); setTimeout(() => setCode(h.code), 0); }}>Load code</button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>

      <section className="ws-right">
        <div className="ws-toolbar">
          <select className="select ws-lang" value={lang} onChange={(e) => changeLang(e.target.value)} aria-label="Language">
            {LANGS.map((l) => <option key={l.id} value={l.id}>{l.name}</option>)}
          </select>
          {lang === 'java' && <span className="muted small ws-hint">Class must be named Main</span>}
          <span className="spacer" />
          <button className="btn btn-ghost btn-sm" onClick={resetCode} title="Reset to starter code"><FiRotateCcw /> Reset</button>
        </div>

        <div className="ws-editor">
          <CodeMirror value={code} height="100%" extensions={extensions} onChange={onCodeChange}
                      basicSetup={{ tabSize: 4, foldGutter: false }} aria-label="Code editor" />
        </div>

        <div className="ws-console">
          <div className="ws-console-head">
            <label className="check small">
              <input type="checkbox" checked={useCustom} onChange={(e) => setUseCustom(e.target.checked)} />
              Run with custom input
            </label>
            <span className="spacer" />
            <button className="btn btn-outline" onClick={() => execute('run')} disabled={!!running}>
              {running === 'run' ? <span className="spinner spinner-sm dark" /> : <FiPlay />} Run
            </button>
            <button className="btn btn-success" onClick={() => execute('submit')} disabled={!!running}>
              {running === 'submit' ? <span className="spinner spinner-sm" /> : <FiSend />} Submit
            </button>
          </div>

          <div className="ws-console-body">
            {useCustom && (
              <textarea className="textarea code ws-custom" placeholder="Type the input your program should read" value={customInput}
                        onChange={(e) => setCustomInput(e.target.value)} />
            )}
            {running && <p className="muted">{running === 'submit' ? 'Running all test cases...' : 'Running your code...'}</p>}
            {!running && !result && !useCustom && <p className="muted">Run checks the examples. Submit checks every test, including hidden ones.</p>}
            {result && !running && (
              <div className="result">
                <div className={`result-banner ${result.status === 'ACCEPTED' || result.status === 'EXECUTED' ? 'ok' : 'bad'}`}>
                  {result.status === 'ACCEPTED' || result.status === 'EXECUTED' ? <FiCheckCircle /> : <FiXCircle />}
                  <strong>{verdictLabel(result.status)}</strong>
                  {result.status !== 'EXECUTED' && <span>{result.passedCount} / {result.totalCount} tests passed</span>}
                </div>
                {result.compileOutput && <pre className="out out-error">{result.compileOutput}</pre>}
                {!result.compileOutput && result.stderr && <pre className="out out-error">{result.stderr}</pre>}

                {result.results.length > 1 && (
                  <div className="test-chips">
                    {result.results.map((r, i) => (
                      <button key={i} className={`test-chip ${r.passed ? 'ok' : 'bad'} ${i === selectedTest ? 'active' : ''}`} onClick={() => setSelectedTest(i)}>
                        {r.passed ? <FiCheckCircle /> : <FiXCircle />} Test {r.index}{r.hidden ? ' (hidden)' : ''}
                      </button>
                    ))}
                  </div>
                )}
                {test && (test.hidden ? (
                  <p className="muted small"><FiLock /> Hidden test: {verdictLabel(test.status)}. Its input isn't shown, so think about edge cases (empty input, large numbers, negatives).</p>
                ) : (
                  <div className="io-grid">
                    {test.input !== null && <div><span className="label">Input</span><pre className="out">{test.input || '(empty)'}</pre></div>}
                    {test.expectedOutput !== null && <div><span className="label">Expected</span><pre className="out">{test.expectedOutput}</pre></div>}
                    <div><span className="label">Your output</span><pre className="out">{test.actualOutput || '(no output)'}</pre></div>
                  </div>
                ))}
                {test?.time && <p className="muted small" style={{ margin: 0 }}>Time {test.time}s{test.memory ? `, memory ${Math.round(test.memory / 1024 * 10) / 10} MB` : ''}</p>}
              </div>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}

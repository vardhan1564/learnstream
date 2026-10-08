import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { toast } from 'react-toastify';
import { FiChevronLeft, FiChevronRight, FiCheckCircle, FiXCircle } from 'react-icons/fi';
import api, { errorMessage } from '../api/client';
import { ConfirmDialog, ErrorState, Loader, ProgressBar, usePageTitle } from '../components/Common';
import './learn.css';

export default function QuizTake() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [answers, setAnswers] = useState({});
  const [index, setIndex] = useState(0);
  const [result, setResult] = useState(null);
  const [confirm, setConfirm] = useState(false);
  const [busy, setBusy] = useState(false);
  usePageTitle(data?.quiz.title || 'Quiz');

  useEffect(() => {
    api.get(`/api/quizzes/${id}`).then((r) => setData(r.data)).catch((e) => setError(errorMessage(e)));
  }, [id]);

  // Warn before leaving mid-quiz
  useEffect(() => {
    if (result || Object.keys(answers).length === 0) return undefined;
    const handler = (e) => { e.preventDefault(); e.returnValue = ''; };
    window.addEventListener('beforeunload', handler);
    return () => window.removeEventListener('beforeunload', handler);
  }, [answers, result]);

  const submit = async () => {
    setBusy(true);
    try {
      const { data: res } = await api.post(`/api/quizzes/${id}/submit`, { answers });
      setResult(res);
      setConfirm(false);
      window.scrollTo({ top: 0 });
    } catch (e) {
      toast.error(errorMessage(e));
      setConfirm(false);
    } finally {
      setBusy(false);
    }
  };

  if (error) return <div className="wrap page"><ErrorState message={error} /></div>;
  if (!data) return <Loader />;

  const { quiz, questions } = data;
  const left = quiz.maxAttempts > 0 ? quiz.maxAttempts - quiz.attemptsUsed : null;

  if (result) {
    const attemptsLeft = result.maxAttempts > 0 ? result.maxAttempts - result.attemptsUsed : null;
    return (
      <div className="wrap page">
        <div className="panel quiz-result">
          {result.passed ? <FiCheckCircle size={56} className="text-green" /> : <FiXCircle size={56} className="text-red" />}
          <h1>{result.passed ? 'You passed!' : 'Not quite there yet'}</h1>
          <p className="quiz-score">{result.score} / {result.total}</p>
          <p className="muted">You scored {result.percentage}%. The pass mark is {result.passPercentage}%.</p>
          {attemptsLeft !== null && !result.passed && (
            <p className="muted small">{attemptsLeft > 0 ? `${attemptsLeft} attempt${attemptsLeft > 1 ? 's' : ''} left.` : 'No attempts left for this quiz.'}</p>
          )}
          <div className="row" style={{ justifyContent: 'center', marginTop: 12 }}>
            {quiz.courseId && <Link to={`/learn/${quiz.courseId}`} className="btn btn-primary">Back to course</Link>}
            <Link to="/quizzes" className="btn btn-outline">All quizzes</Link>
            {!result.passed && (attemptsLeft === null || attemptsLeft > 0) && (
              <button className="btn btn-ghost" onClick={() => { setResult(null); setAnswers({}); setIndex(0); setData((d) => ({ ...d, quiz: { ...d.quiz, attemptsUsed: result.attemptsUsed } })); }}>Try again</button>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (left !== null && left <= 0) {
    return (
      <div className="wrap page">
        <div className="panel quiz-result">
          <h1>No attempts left</h1>
          <p className="muted">You've used all {quiz.maxAttempts} attempts for this quiz{quiz.bestPercentage != null ? `. Your best score was ${quiz.bestPercentage}%` : ''}.</p>
          <button className="btn btn-outline" onClick={() => navigate('/quizzes')}>Back to quizzes</button>
        </div>
      </div>
    );
  }

  const q = questions[index];
  const answered = Object.keys(answers).length;

  return (
    <div className="wrap page quiz-take">
      <Link to="/quizzes" className="crumb"><FiChevronLeft /> Quizzes</Link>
      <div className="quiz-head">
        <h1>{quiz.title}</h1>
        <p className="muted">{questions.length} questions, pass mark {quiz.passPercentage}%{left !== null ? `, attempt ${quiz.attemptsUsed + 1} of ${quiz.maxAttempts}` : ''}</p>
        <ProgressBar value={(answered / questions.length) * 100} label="Questions answered" />
      </div>

      <div className="quiz-layout">
        <div className="panel">
          <p className="muted small">Question {index + 1} of {questions.length}</p>
          <h2 className="quiz-question">{q.questionText}</h2>
          <div className="options" role="radiogroup" aria-label={`Question ${index + 1}`}>
            {q.options.map((o) => (
              <label key={o.key} className={`option ${answers[q.id] === o.key ? 'selected' : ''}`}>
                <input type="radio" name={`q-${q.id}`} value={o.key} checked={answers[q.id] === o.key}
                       onChange={() => setAnswers({ ...answers, [q.id]: o.key })} />
                <span className="option-key">{o.key}</span>
                <span>{o.text}</span>
              </label>
            ))}
          </div>
          <div className="row" style={{ marginTop: 24 }}>
            <button className="btn btn-outline" disabled={index === 0} onClick={() => setIndex(index - 1)}><FiChevronLeft /> Previous</button>
            <span className="spacer" />
            {index < questions.length - 1 ? (
              <button className="btn btn-primary" onClick={() => setIndex(index + 1)}>Next <FiChevronRight /></button>
            ) : (
              <button className="btn btn-success" onClick={() => setConfirm(true)}>Submit answers</button>
            )}
          </div>
        </div>

        <aside className="panel panel-tight">
          <h4>Questions</h4>
          <div className="q-grid">
            {questions.map((qq, i) => (
              <button key={qq.id} className={`q-dot ${answers[qq.id] ? 'answered' : ''} ${i === index ? 'current' : ''}`}
                      onClick={() => setIndex(i)} aria-label={`Question ${i + 1}${answers[qq.id] ? ', answered' : ''}`}>{i + 1}</button>
            ))}
          </div>
          <p className="muted small">{answered} of {questions.length} answered</p>
          <button className="btn btn-success btn-block" onClick={() => setConfirm(true)}>Submit answers</button>
        </aside>
      </div>

      {confirm && (
        <ConfirmDialog
          title="Submit your answers?"
          message={answered < questions.length
            ? `You've answered ${answered} of ${questions.length} questions. Unanswered questions count as wrong.`
            : 'You can’t change your answers after submitting.'}
          confirmLabel="Submit"
          busy={busy}
          onConfirm={submit}
          onCancel={() => setConfirm(false)}
        />
      )}
    </div>
  );
}

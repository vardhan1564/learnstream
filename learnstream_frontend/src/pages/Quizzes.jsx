import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { FiHelpCircle, FiCheckCircle, FiLock } from 'react-icons/fi';
import useFetch from '../api/useFetch';
import { EmptyState, ErrorState, Loader, usePageTitle } from '../components/Common';
import './learn.css';

export default function Quizzes() {
  usePageTitle('Quizzes');
  const { data: quizzes, error, reload: load } = useFetch('/api/quizzes');
  const [category, setCategory] = useState('All');


  const categories = useMemo(() => ['All', ...new Set((quizzes || []).map((q) => q.category).filter(Boolean))], [quizzes]);
  const list = (quizzes || []).filter((q) => category === 'All' || q.category === category);

  return (
    <div className="wrap page">
      <div className="page-head">
        <h1>Quizzes</h1>
        <p>Test what you've learned. Answers are checked on the server and you see your score right away.</p>
      </div>
      {categories.length > 2 && (
        <div className="segmented" style={{ marginBottom: 24 }} role="group" aria-label="Category">
          {categories.map((c) => <button key={c} className={category === c ? 'active' : ''} onClick={() => setCategory(c)}>{c}</button>)}
        </div>
      )}
      {error ? <ErrorState message={error} onRetry={load} />
        : quizzes === null ? <Loader />
        : list.length === 0 ? <EmptyState icon={FiHelpCircle} title="No quizzes yet">Quizzes will show up here once they're published.</EmptyState>
        : (
          <div className="grid grid-3">
            {list.map((q) => {
              const left = q.maxAttempts > 0 ? Math.max(0, q.maxAttempts - q.attemptsUsed) : null;
              const out = left === 0 && !q.passed;
              return (
                <div key={q.id} className="quiz-card panel">
                  <div className="row">
                    {q.category && <span className="tag tag-grey">{q.category}</span>}
                    {q.passed && <span className="tag tag-green"><FiCheckCircle /> Passed</span>}
                  </div>
                  <h3>{q.title}</h3>
                  {q.description && <p className="muted small">{q.description}</p>}
                  {q.courseTitle && <p className="small">Part of <strong>{q.courseTitle}</strong></p>}
                  <dl className="quiz-facts">
                    <div><dt>Questions</dt><dd>{q.questionCount}</dd></div>
                    <div><dt>Pass mark</dt><dd>{q.passPercentage}%</dd></div>
                    <div><dt>Attempts left</dt><dd>{left === null ? 'Unlimited' : left}</dd></div>
                    {q.bestPercentage != null && <div><dt>Best score</dt><dd>{q.bestPercentage}%</dd></div>}
                  </dl>
                  {out ? (
                    <button className="btn btn-outline btn-block" disabled><FiLock /> No attempts left</button>
                  ) : (
                    <Link to={`/quizzes/${q.id}`} className={`btn btn-block ${q.attemptsUsed ? 'btn-outline' : 'btn-primary'}`}>
                      {q.attemptsUsed ? 'Try again' : 'Start quiz'}
                    </Link>
                  )}
                </div>
              );
            })}
          </div>
        )}
    </div>
  );
}

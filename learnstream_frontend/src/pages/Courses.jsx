import { useMemo, useState } from 'react';
import { FiSearch, FiBookOpen } from 'react-icons/fi';
import useFetch from '../api/useFetch';
import CourseCard from '../components/CourseCard';
import { EmptyState, ErrorState, Loader, usePageTitle } from '../components/Common';

export default function Courses() {
  usePageTitle('Courses');
  const { data: courses, error, reload: load } = useFetch('/api/courses');
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('All');
  const [price, setPrice] = useState('all');

  const categories = useMemo(
    () => ['All', ...new Set((courses || []).map((c) => c.category).filter(Boolean))],
    [courses]
  );

  const filtered = (courses || []).filter((c) => {
    const q = query.trim().toLowerCase();
    if (q && !`${c.title} ${c.description || ''} ${c.category || ''}`.toLowerCase().includes(q)) return false;
    if (category !== 'All' && c.category !== category) return false;
    if (price === 'free' && c.price > 0) return false;
    if (price === 'paid' && !(c.price > 0)) return false;
    return true;
  });

  return (
    <div className="wrap page">
      <div className="page-head">
        <h1>Courses</h1>
        <p>Every course has free preview lessons. Enroll to track progress, take the quiz and earn a certificate.</p>
      </div>

      <div className="toolbar">
        <div className="input-icon toolbar-search">
          <FiSearch />
          <input className="input" placeholder="Search courses" value={query} onChange={(e) => setQuery(e.target.value)} aria-label="Search courses" />
        </div>
        <select className="select toolbar-select" value={category} onChange={(e) => setCategory(e.target.value)} aria-label="Category">
          {categories.map((c) => <option key={c} value={c}>{c === 'All' ? 'All categories' : c}</option>)}
        </select>
        <div className="segmented" role="group" aria-label="Price">
          {[['all', 'All'], ['free', 'Free'], ['paid', 'Paid']].map(([k, label]) => (
            <button key={k} className={price === k ? 'active' : ''} onClick={() => setPrice(k)}>{label}</button>
          ))}
        </div>
      </div>

      {error ? <ErrorState message={error} onRetry={load} />
        : courses === null ? <Loader />
        : filtered.length === 0 ? (
          <EmptyState icon={FiBookOpen} title={courses.length === 0 ? 'No courses yet' : 'No courses match your filters'}>
            {courses.length === 0 ? 'New courses are on the way. Check back soon.' : 'Try a different search or clear the filters.'}
          </EmptyState>
        ) : (
          <div className="grid grid-3">
            {filtered.map((c) => <CourseCard key={c.id} course={c} />)}
          </div>
        )}
    </div>
  );
}

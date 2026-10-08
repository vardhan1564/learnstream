import { Link } from 'react-router-dom';
import { FiPlayCircle, FiClock } from 'react-icons/fi';
import { formatMinutes, formatPrice } from '../utils/format';

const PALETTES = [
  ['#0b2e6b', '#1b5bd0'],
  ['#0c4a6e', '#12a0d6'],
  ['#1e3a8a', '#6366f1'],
  ['#064e3b', '#10b981'],
  ['#7c2d12', '#ea8a2e'],
  ['#4c1d95', '#a855f7'],
];

function hash(str = '') {
  let h = 0;
  for (let i = 0; i < str.length; i++) h = (h * 31 + str.charCodeAt(i)) | 0;
  return Math.abs(h);
}

/** Thumbnail, or generated cover art when the admin didn't upload one. */
export function CourseArt({ course, className = '' }) {
  if (course.thumbnail) {
    return (
      <div className={`course-art ${className}`}>
        <img src={course.thumbnail} alt="" loading="lazy" onError={(e) => { e.currentTarget.style.display = 'none'; }} />
      </div>
    );
  }
  const [a, b] = PALETTES[hash(course.category || course.title) % PALETTES.length];
  const label = (course.category || course.title || '').slice(0, 14);
  return (
    <div className={`course-art generated ${className}`} style={{ background: `linear-gradient(135deg, ${a}, ${b})` }} aria-hidden="true">
      <svg viewBox="0 0 400 200" preserveAspectRatio="none">
        <path d="M-10 150 C 80 90, 160 190, 250 120 S 380 60, 420 90" fill="none" stroke="rgba(255,255,255,.22)" strokeWidth="18" strokeLinecap="round" />
        <path d="M-10 175 C 90 120, 170 210, 260 150 S 380 95, 420 120" fill="none" stroke="rgba(255,255,255,.12)" strokeWidth="10" strokeLinecap="round" />
      </svg>
      <span>{label}</span>
    </div>
  );
}

export default function CourseCard({ course }) {
  const minutes = formatMinutes(course.totalMinutes);
  return (
    <Link to={`/courses/${course.id}`} className="course-card">
      <CourseArt course={course} />
      <div className="course-card-body">
        <div className="row course-card-tags">
          {course.level && <span className="tag tag-grey">{course.level}</span>}
          {course.enrolled && <span className="tag tag-green">Enrolled</span>}
        </div>
        <h3>{course.title}</h3>
        {course.instructor && <p className="muted small course-card-by">{course.instructor}</p>}
        <div className="course-card-foot">
          <span className="course-card-meta">
            <FiPlayCircle /> {course.lessonCount} {course.lessonCount === 1 ? 'lesson' : 'lessons'}
            {minutes && <><FiClock /> {minutes}</>}
          </span>
          <strong className={course.price > 0 ? 'price' : 'price free'}>{course.enrolled ? 'Owned' : formatPrice(course.price)}</strong>
        </div>
      </div>
    </Link>
  );
}

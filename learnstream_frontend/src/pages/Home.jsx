import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { FiPlay, FiCode, FiAward, FiCheck, FiMap, FiGift } from 'react-icons/fi';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import CourseCard from '../components/CourseCard';
import { usePageTitle } from '../components/Common';
import './home.css';

export default function Home() {
  usePageTitle(null);
  const { user } = useAuth();
  const [courses, setCourses] = useState([]);
  const [roadmaps, setRoadmaps] = useState([]);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    api.get('/api/courses').then((r) => setCourses(r.data.slice(0, 3))).catch(() => {});
    api.get('/api/roadmaps').then((r) => setRoadmaps(r.data.slice(0, 2))).catch(() => {});
    api.get('/api/stats/public').then((r) => setStats(r.data)).catch(() => {});
  }, []);

  return (
    <>
      <section className="hero">
        <div className="wrap hero-grid">
          <div className="hero-copy">
            <h1 className="hero-title">Learn.<br />Code.<br />Succeed.</h1>
            <p className="hero-lead">
              Video courses, hands-on coding problems and quizzes in one place. Finish a course,
              pass its quiz and download a certificate anyone can verify.
            </p>
            <div className="row hero-ctas">
              <Link to="/courses" className="btn btn-primary btn-lg">Browse courses</Link>
              <Link to="/problems" className="btn btn-outline btn-lg">Start practicing</Link>
            </div>
            {stats && (
              <p className="hero-stats">
                {stats.courses} courses, {stats.problems} practice problems and {stats.quizzes} quizzes
                {stats.students > 0 ? `, with ${stats.students} learners and counting` : ''}.
              </p>
            )}
          </div>

          <div className="hero-visual" aria-hidden="true">
            <svg className="hero-ribbon" viewBox="0 0 520 560" preserveAspectRatio="none">
              <defs>
                <linearGradient id="ribbon" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0" stopColor="#0b2e6b" />
                  <stop offset=".55" stopColor="#1b5bd0" />
                  <stop offset="1" stopColor="#12a0d6" />
                </linearGradient>
              </defs>
              <path d="M40 20 C 40 140, 470 120, 460 260 S 60 380, 90 540" fill="none" stroke="url(#ribbon)" strokeWidth="26" strokeLinecap="round" opacity=".16" />
              <path className="hero-ribbon-line" d="M40 20 C 40 140, 470 120, 460 260 S 60 380, 90 540" fill="none" stroke="url(#ribbon)" strokeWidth="4" strokeLinecap="round" />
            </svg>

            <div className="hero-node node-1">
              <span className="node-icon"><FiPlay /></span>
              <div>
                <strong>Watch the lesson</strong>
                <span>Two Pointers, lesson 4 of 12</span>
              </div>
            </div>

            <div className="hero-node node-2 hero-code">
              <div className="hero-code-head">
                <span>Palindrome Check</span>
                <span className="tag tag-green"><FiCheck /> Accepted</span>
              </div>
              <pre>{`int i = 0, j = s.length() - 1;
while (i < j) {
  if (s.charAt(i++) != s.charAt(j--))
    return "NO";
}
return "YES";`}</pre>
              <div className="hero-code-foot">6 / 6 tests passed</div>
            </div>

            <div className="hero-node node-3">
              <span className="node-icon gold"><FiAward /></span>
              <div>
                <strong>Earn the certificate</strong>
                <span>Verifiable with a unique ID</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="wrap">
          <h2>How it works</h2>
          <ol className="steps">
            <li>
              <FiPlay className="step-icon" />
              <h3>Learn from video lessons</h3>
              <p>Short, structured lessons. Your progress is saved, so you can pick up exactly where you stopped.</p>
            </li>
            <li>
              <FiCode className="step-icon" />
              <h3>Practice in the browser</h3>
              <p>Write code in Java, Python, C++ or JavaScript and run it against real test cases instantly.</p>
            </li>
            <li>
              <FiAward className="step-icon" />
              <h3>Pass the quiz, get certified</h3>
              <p>Complete every lesson and pass the course quiz to download your certificate.</p>
            </li>
          </ol>
        </div>
      </section>

      {courses.length > 0 && (
        <section className="section section-white">
          <div className="wrap">
            <div className="page-head-row" style={{ marginBottom: 24 }}>
              <h2 style={{ margin: 0 }}>Popular courses</h2>
              <Link to="/courses" className="btn btn-outline btn-sm">See all courses</Link>
            </div>
            <div className="grid grid-3">
              {courses.map((c) => <CourseCard key={c.id} course={c} />)}
            </div>
          </div>
        </section>
      )}

      <section className="section">
        <div className="wrap reward-band">
          <FiGift className="reward-band-icon" />
          <div>
            <h2>Solve 5 problems, unlock a course for free</h2>
            <p>
              Every 5 practice problems you solve earns you one free-course credit. Spend it on any paid
              course. No coupon codes, no catch.
            </p>
          </div>
          <Link to="/problems" className="btn btn-gold btn-lg">Solve your first problem</Link>
        </div>
      </section>

      {roadmaps.length > 0 && (
        <section className="section section-white">
          <div className="wrap">
            <div className="page-head-row" style={{ marginBottom: 24 }}>
              <div>
                <h2 style={{ margin: 0 }}>Not sure where to start?</h2>
                <p className="muted" style={{ margin: '6px 0 0' }}>Follow a roadmap: a step-by-step path from beginner to job-ready.</p>
              </div>
              <Link to="/roadmaps" className="btn btn-outline btn-sm">All roadmaps</Link>
            </div>
            <div className="grid grid-3">
              {roadmaps.map((r) => (
                <Link key={r.id} to={`/roadmaps/${r.id}`} className="roadmap-tile">
                  <FiMap size={22} />
                  <h3>{r.title}</h3>
                  <p className="muted small">{r.description}</p>
                  <span className="small"><strong>{r.stepCount} steps</strong>{r.duration ? `, about ${r.duration}` : ''}</span>
                </Link>
              ))}
            </div>
          </div>
        </section>
      )}

      {!user && (
        <section className="section">
          <div className="wrap final-cta">
            <h2>Your first lesson is free</h2>
            <p>Create an account in under a minute and start learning today.</p>
            <Link to="/register" className="btn btn-primary btn-lg">Create free account</Link>
          </div>
        </section>
      )}
    </>
  );
}

import { Link } from 'react-router-dom';
import mark from '../../assets/logo-mark.png';

/** Two-column layout shared by all auth screens. */
export default function AuthShell({ title, subtitle, children, footer }) {
  return (
    <div className="auth">
      <aside className="auth-side" aria-hidden="true">
        <img src={mark} alt="" className="auth-mark" />
        <p className="auth-quote">Watch a lesson, solve a problem, pass the quiz. Every day you show up moves you further down the stream.</p>
        <ul className="auth-points">
          <li>Video courses with progress tracking</li>
          <li>Practice problems in Java, Python, C++ and JavaScript</li>
          <li>Solve 5 problems, unlock a course for free</li>
          <li>Verifiable certificates when you finish</li>
        </ul>
      </aside>
      <section className="auth-main">
        <div className="auth-card">
          <Link to="/" className="auth-back">LearnStream</Link>
          <h1>{title}</h1>
          {subtitle && <p className="muted">{subtitle}</p>}
          {children}
          {footer && <div className="auth-footer">{footer}</div>}
        </div>
      </section>
    </div>
  );
}

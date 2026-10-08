import { Link } from 'react-router-dom';
import mark from '../assets/logo-mark.png';

export default function Footer() {
  return (
    <footer className="footer">
      <div className="wrap footer-inner">
        <div className="footer-brand">
          <img src={mark} alt="" width="44" height="34" />
          <div>
            <strong>LearnStream</strong>
            <span>Learn. Code. Succeed.</span>
          </div>
        </div>
        <nav className="footer-links" aria-label="Footer">
          <Link to="/courses">Courses</Link>
          <Link to="/problems">Practice problems</Link>
          <Link to="/roadmaps">Roadmaps</Link>
          <Link to="/verify">Verify a certificate</Link>
        </nav>
        <p className="footer-copy">© {new Date().getFullYear()} LearnStream. Built for learners.</p>
      </div>
    </footer>
  );
}

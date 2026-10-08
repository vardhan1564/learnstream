import { useEffect, useRef, useState } from 'react';
import { Link, NavLink, useLocation, useNavigate } from 'react-router-dom';
import { FiMenu, FiX, FiChevronDown, FiLogOut, FiGrid, FiShield } from 'react-icons/fi';
import { useAuth } from '../context/AuthContext';
import { initials } from '../utils/format';
import logo from '../assets/logo.png';
import './navbar.css';

export default function Navbar() {
  const { user, isAdmin, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const [menu, setMenu] = useState(false);
  const menuRef = useRef(null);
  const location = useLocation();
  const navigate = useNavigate();

  // Close menus on navigation (adjusting state during render, as React recommends)
  const [path, setPath] = useState(location.pathname);
  if (path !== location.pathname) {
    setPath(location.pathname);
    setOpen(false);
    setMenu(false);
  }

  useEffect(() => {
    const onClick = (e) => { if (menuRef.current && !menuRef.current.contains(e.target)) setMenu(false); };
    const onKey = (e) => { if (e.key === 'Escape') { setMenu(false); setOpen(false); } };
    document.addEventListener('mousedown', onClick);
    document.addEventListener('keydown', onKey);
    return () => { document.removeEventListener('mousedown', onClick); document.removeEventListener('keydown', onKey); };
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const links = [
    { to: '/courses', label: 'Courses' },
    { to: '/problems', label: 'Practice' },
    { to: '/quizzes', label: 'Quizzes' },
    { to: '/roadmaps', label: 'Roadmaps' },
    ...(user ? [{ to: '/leaderboard', label: 'Leaderboard' }] : []),
  ];

  return (
    <header className="nav">
      <div className="wrap nav-inner">
        <Link to="/" className="nav-logo" aria-label="LearnStream home">
          <img src={logo} alt="LearnStream" />
        </Link>

        <nav className={`nav-links ${open ? 'open' : ''}`} aria-label="Main">
          {links.map((l) => (
            <NavLink key={l.to} to={l.to} className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              {l.label}
            </NavLink>
          ))}
          <div className="nav-mobile-auth">
            {user ? (
              <>
                <NavLink to="/dashboard" className="nav-link">My learning</NavLink>
                {isAdmin && <NavLink to="/admin" className="nav-link">Admin panel</NavLink>}
                <button className="nav-link as-button" onClick={handleLogout}>Log out</button>
              </>
            ) : (
              <>
                <NavLink to="/login" className="nav-link">Log in</NavLink>
                <Link to="/register" className="btn btn-primary btn-block">Sign up free</Link>
              </>
            )}
          </div>
        </nav>

        <div className="nav-right">
          {user ? (
            <>
              <Link to="/dashboard" className="btn btn-ghost btn-sm nav-hide-sm">My learning</Link>
              <div className="nav-user" ref={menuRef}>
                <button className="nav-user-btn" onClick={() => setMenu((m) => !m)} aria-expanded={menu} aria-haspopup="menu">
                  <span className="avatar">{initials(user.fullName)}</span>
                  <FiChevronDown />
                </button>
                {menu && (
                  <div className="nav-menu" role="menu">
                    <div className="nav-menu-head">
                      <strong>{user.fullName}</strong>
                      <span>{user.email}</span>
                    </div>
                    <Link to="/dashboard" role="menuitem"><FiGrid /> Dashboard</Link>
                    {isAdmin && <Link to="/admin" role="menuitem"><FiShield /> Admin panel</Link>}
                    <button onClick={handleLogout} role="menuitem"><FiLogOut /> Log out</button>
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="nav-hide-sm row">
              <Link to="/login" className="btn btn-ghost btn-sm">Log in</Link>
              <Link to="/register" className="btn btn-primary btn-sm">Sign up free</Link>
            </div>
          )}
          <button className="nav-burger" onClick={() => setOpen((o) => !o)} aria-label={open ? 'Close menu' : 'Open menu'} aria-expanded={open}>
            {open ? <FiX size={22} /> : <FiMenu size={22} />}
          </button>
        </div>
      </div>
    </header>
  );
}

import { NavLink, Route, Routes } from 'react-router-dom';
import { FiGrid, FiBookOpen, FiHelpCircle, FiCode, FiMap, FiUsers, FiAward } from 'react-icons/fi';
import { NotFound, usePageTitle } from '../../components/Common';
import AdminOverview from './AdminOverview';
import { CourseList, CourseEditor } from './AdminCourses';
import { QuizList, QuizEditor } from './AdminQuizzes';
import { ProblemList, ProblemEditor } from './AdminProblems';
import { RoadmapList, RoadmapEditor } from './AdminRoadmaps';
import AdminStudents from './AdminStudents';
import AdminLeaderboard from './AdminLeaderboard';
import './admin.css';

const NAV = [
  { to: '/admin', label: 'Overview', icon: FiGrid, end: true },
  { to: '/admin/courses', label: 'Courses & videos', icon: FiBookOpen },
  { to: '/admin/quizzes', label: 'Quizzes (MCQ)', icon: FiHelpCircle },
  { to: '/admin/problems', label: 'Coding problems', icon: FiCode },
  { to: '/admin/roadmaps', label: 'Roadmaps', icon: FiMap },
  { to: '/admin/students', label: 'Students', icon: FiUsers },
  { to: '/admin/leaderboard', label: 'Leaderboard', icon: FiAward },
];

export default function AdminLayout() {
  usePageTitle('Admin');
  return (
    <div className="admin">
      <aside className="admin-side">
        <p className="admin-side-title">Admin panel</p>
        <nav>
          {NAV.map(({ to, label, icon: Icon, end }) => (
            <NavLink key={to} to={to} end={end} className={({ isActive }) => `admin-link ${isActive ? 'active' : ''}`}>
              <Icon /> {label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <section className="admin-main">
        <Routes>
          <Route index element={<AdminOverview />} />
          <Route path="courses" element={<CourseList />} />
          <Route path="courses/new" element={<CourseEditor />} />
          <Route path="courses/:id" element={<CourseEditor />} />
          <Route path="quizzes" element={<QuizList />} />
          <Route path="quizzes/new" element={<QuizEditor />} />
          <Route path="quizzes/:id" element={<QuizEditor />} />
          <Route path="problems" element={<ProblemList />} />
          <Route path="problems/new" element={<ProblemEditor />} />
          <Route path="problems/:id" element={<ProblemEditor />} />
          <Route path="roadmaps" element={<RoadmapList />} />
          <Route path="roadmaps/new" element={<RoadmapEditor />} />
          <Route path="roadmaps/:id" element={<RoadmapEditor />} />
          <Route path="students" element={<AdminStudents />} />
          <Route path="leaderboard" element={<AdminLeaderboard />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </section>
    </div>
  );
}

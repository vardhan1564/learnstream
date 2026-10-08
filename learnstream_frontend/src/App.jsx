import { lazy, Suspense } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ProtectedRoute from './components/ProtectedRoute';
import ScrollToTop from './components/ScrollToTop';
import { Loader, NotFound } from './components/Common';

import Home from './pages/Home';
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import VerifyEmail from './pages/auth/VerifyEmail';
import ForgotPassword from './pages/auth/ForgotPassword';
import Courses from './pages/Courses';
import CourseDetail from './pages/CourseDetail';

// Heavier pages are loaded on demand
const CoursePlayer = lazy(() => import('./pages/CoursePlayer'));
const PaymentSuccess = lazy(() => import('./pages/PaymentSuccess'));
const Problems = lazy(() => import('./pages/Problems'));
const ProblemWorkspace = lazy(() => import('./pages/ProblemWorkspace'));
const Quizzes = lazy(() => import('./pages/Quizzes'));
const QuizTake = lazy(() => import('./pages/QuizTake'));
const Roadmaps = lazy(() => import('./pages/Roadmaps'));
const RoadmapDetail = lazy(() => import('./pages/RoadmapDetail'));
const Leaderboard = lazy(() => import('./pages/Leaderboard'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const VerifyCertificate = lazy(() => import('./pages/VerifyCertificate'));
const AdminLayout = lazy(() => import('./pages/admin/AdminLayout'));

const auth = (el) => <ProtectedRoute>{el}</ProtectedRoute>;

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <ScrollToTop />
        <div className="app">
          <Navbar />
          <main className="app-main">
            <Suspense fallback={<Loader />}>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/verify-email" element={<VerifyEmail />} />
                <Route path="/forgot-password" element={<ForgotPassword />} />

                <Route path="/courses" element={<Courses />} />
                <Route path="/courses/:id" element={<CourseDetail />} />
                <Route path="/learn/:id" element={auth(<CoursePlayer />)} />
                <Route path="/payment-success" element={auth(<PaymentSuccess />)} />

                <Route path="/problems" element={<Problems />} />
                <Route path="/problems/:id" element={<ProblemWorkspace />} />

                <Route path="/quizzes" element={auth(<Quizzes />)} />
                <Route path="/quizzes/:id" element={auth(<QuizTake />)} />

                <Route path="/roadmaps" element={<Roadmaps />} />
                <Route path="/roadmaps/:id" element={<RoadmapDetail />} />

                <Route path="/leaderboard" element={auth(<Leaderboard />)} />
                <Route path="/dashboard" element={auth(<Dashboard />)} />
                <Route path="/verify" element={<VerifyCertificate />} />
                <Route path="/verify/:serial" element={<VerifyCertificate />} />

                <Route path="/admin/*" element={<ProtectedRoute adminOnly><AdminLayout /></ProtectedRoute>} />
                <Route path="*" element={<NotFound />} />
              </Routes>
            </Suspense>
          </main>
          <Footer />
        </div>
        <ToastContainer position="bottom-right" autoClose={3500} newestOnTop />
      </BrowserRouter>
    </AuthProvider>
  );
}

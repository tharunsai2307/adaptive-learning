import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import ErrorBoundary from './components/ErrorBoundary';
import Login from './pages/Login';
import Profile from './pages/Profile';
import Subjects from './pages/Subjects';
import Dashboard from './pages/Dashboard';
import LearningPath from './pages/LearningPath';
import Learn from './pages/Learn';
import Quiz from './pages/Quiz';
import QLearning from './pages/QLearning';
import History from './pages/History';

function ProtectedRoute({ children }) {
  const { token, loading } = useAuth();
  if (loading) return <div className="min-h-screen bg-slate-900 flex items-center justify-center text-white">Loading...</div>;
  if (!token) return <Navigate to="/" replace />;
  return children;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
      <Route path="/subjects" element={<ProtectedRoute><Subjects /></ProtectedRoute>} />
      <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      <Route path="/learning-path" element={<ProtectedRoute><LearningPath /></ProtectedRoute>} />
      <Route path="/learn/:topicId" element={<ProtectedRoute><Learn /></ProtectedRoute>} />
      <Route path="/quiz/:topicId" element={<ProtectedRoute><Quiz /></ProtectedRoute>} />
      <Route path="/qlearning" element={<ProtectedRoute><QLearning /></ProtectedRoute>} />
      <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />
    </Routes>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </AuthProvider>
    </ErrorBoundary>
  );
}

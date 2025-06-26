import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Layout from './components/Layout';
import LoadingSpinner from './components/LoadingSpinner';

// 페이지 컴포넌트들
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import SessionListPage from './pages/SessionListPage';
import InterviewPage from './pages/InterviewPage';
import MyStoriesPage from './pages/MyStoriesPage';
import AutobiographyPage from './pages/AutobiographyPage';

// 인증이 필요한 라우트를 보호하는 컴포넌트
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <LoadingSpinner />;
  }
  
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

// 인증된 사용자는 접근할 수 없는 라우트 (로그인, 회원가입)
const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <LoadingSpinner />;
  }
  
  return !isAuthenticated ? children : <Navigate to="/sessions" replace />;
};

function App() {
  const { loading } = useAuth();

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="App">
      <Routes>
        {/* 공개 라우트 */}
        <Route path="/login" element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        } />
        <Route path="/register" element={
          <PublicRoute>
            <RegisterPage />
          </PublicRoute>
        } />

        {/* 보호된 라우트 */}
        <Route path="/" element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }>
          {/* 기본 경로는 세션 리스트로 리다이렉트 */}
          <Route index element={<Navigate to="/sessions" replace />} />
          
          {/* 메인 페이지들 */}
          <Route path="sessions" element={<SessionListPage />} />
          <Route path="sessions/:sessionId/interview" element={<InterviewPage />} />
          <Route path="my-stories" element={<MyStoriesPage />} />
          <Route path="autobiography" element={<AutobiographyPage />} />
        </Route>

        {/* 잘못된 경로 처리 */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}

export default App;
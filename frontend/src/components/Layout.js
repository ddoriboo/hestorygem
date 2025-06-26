import React from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Book, MessageSquare, User, LogOut, Home } from 'lucide-react';

const Layout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navigationItems = [
    {
      path: '/sessions',
      label: '세션 목록',
      icon: Home,
      description: '12개의 인생 이야기 세션'
    },
    {
      path: '/my-stories', 
      label: '내 이야기 보기',
      icon: MessageSquare,
      description: '지금까지의 대화 내용'
    },
    {
      path: '/autobiography',
      label: '자서전 초고',
      icon: Book,
      description: '나만의 자서전 만들기'
    }
  ];

  return (
    <div className="min-h-screen bg-secondary">
      {/* 헤더 */}
      <header className="bg-primary text-white shadow-lg">
        <div className="container">
          <div className="flex items-center justify-between py-lg">
            {/* 로고 및 제목 */}
            <div className="flex items-center gap-md">
              <Book size={32} />
              <div>
                <h1 className="text-2xl font-bold mb-0">He'story</h1>
                <p className="text-sm text-blue-100 mb-0">나의 이야기</p>
              </div>
            </div>

            {/* 사용자 정보 및 로그아웃 */}
            <div className="flex items-center gap-lg">
              <div className="text-right">
                <div className="flex items-center gap-sm">
                  <User size={20} />
                  <span className="font-semibold">{user?.full_name || user?.username}</span>
                </div>
                <p className="text-sm text-blue-100 mb-0">환영합니다!</p>
              </div>
              <button
                onClick={handleLogout}
                className="btn btn-secondary"
                style={{
                  backgroundColor: 'rgba(255,255,255,0.1)',
                  borderColor: 'rgba(255,255,255,0.3)',
                  color: 'white'
                }}
              >
                <LogOut size={18} />
                로그아웃
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* 네비게이션 */}
      <nav className="bg-white border-b-2 border-border-light">
        <div className="container">
          <div className="flex gap-md py-md">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname.startsWith(item.path);
              
              return (
                <button
                  key={item.path}
                  onClick={() => navigate(item.path)}
                  className={`flex items-center gap-sm p-lg rounded-lg transition-all ${
                    isActive 
                      ? 'bg-primary text-white' 
                      : 'bg-bg-tertiary text-text-secondary hover:bg-primary hover:text-white'
                  }`}
                  style={{ minHeight: '60px' }}
                >
                  <Icon size={24} />
                  <div className="text-left">
                    <div className="font-semibold text-lg">{item.label}</div>
                    <div className={`text-sm ${isActive ? 'text-blue-100' : 'text-text-muted'}`}>
                      {item.description}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      </nav>

      {/* 메인 컨텐츠 */}
      <main className="py-xl">
        <div className="container">
          <Outlet />
        </div>
      </main>

      {/* 푸터 */}
      <footer className="bg-white border-t border-border-light mt-2xl">
        <div className="container py-xl text-center">
          <p className="text-muted">
            © 2024 He'story. 시니어를 위한 AI 자서전 작성 서비스
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
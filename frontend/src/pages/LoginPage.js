import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Book, User, Lock, Eye, EyeOff } from 'lucide-react';

const LoginPage = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    // 입력 시 에러 메시지 초기화
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.username || !formData.password) {
      setError('아이디와 비밀번호를 모두 입력해주세요.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await login(formData.username, formData.password);
      
      if (result.success) {
        navigate('/sessions');
      } else {
        setError(result.error || '로그인에 실패했습니다.');
      }
    } catch (err) {
      setError('로그인 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-secondary flex items-center justify-center p-lg">
      <div className="w-full max-w-md">
        {/* 로고 및 제목 */}
        <div className="text-center mb-2xl">
          <div className="flex justify-center mb-lg">
            <div className="bg-primary text-white p-xl rounded-xl">
              <Book size={48} />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-primary mb-sm">He'story</h1>
          <p className="text-xl text-secondary">나의 소중한 이야기를 시작하세요</p>
        </div>

        {/* 로그인 폼 */}
        <div className="card">
          <form onSubmit={handleSubmit} className="space-y-lg">
            <div className="card-header text-center">
              <h2 className="card-title">로그인</h2>
              <p className="card-subtitle">아이디와 비밀번호를 입력해주세요</p>
            </div>

            {/* 에러 메시지 */}
            {error && (
              <div className="bg-red-50 border-2 border-red-200 rounded-lg p-lg">
                <p className="text-red-600 text-center font-semibold">{error}</p>
              </div>
            )}

            {/* 아이디 입력 */}
            <div>
              <label htmlFor="username" className="block text-lg font-semibold mb-md">
                <User size={20} className="inline mr-sm" />
                아이디
              </label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleChange}
                placeholder="아이디를 입력하세요"
                className="input focus-ring"
                disabled={loading}
                autoComplete="username"
              />
            </div>

            {/* 비밀번호 입력 */}
            <div>
              <label htmlFor="password" className="block text-lg font-semibold mb-md">
                <Lock size={20} className="inline mr-sm" />
                비밀번호
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="비밀번호를 입력하세요"
                  className="input focus-ring pr-16"
                  disabled={loading}
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-lg top-1/2 transform -translate-y-1/2 text-text-muted hover:text-text-primary"
                  disabled={loading}
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>

            {/* 로그인 버튼 */}
            <button
              type="submit"
              className="btn btn-primary btn-lg btn-full"
              disabled={loading}
            >
              {loading ? (
                <>
                  <div className="spinner" style={{ width: '20px', height: '20px', marginRight: '8px' }}></div>
                  로그인 중...
                </>
              ) : (
                '로그인'
              )}
            </button>

            {/* 회원가입 링크 */}
            <div className="text-center pt-lg border-t border-border-light">
              <p className="text-secondary mb-md">계정이 없으신가요?</p>
              <Link
                to="/register"
                className="btn btn-secondary btn-lg"
                style={{ textDecoration: 'none' }}
              >
                회원가입
              </Link>
            </div>
          </form>
        </div>

        {/* 도움말 */}
        <div className="text-center mt-xl">
          <p className="text-muted">
            He'story는 시니어를 위한 AI 기반 자서전 작성 서비스입니다.<br />
            어려움이 있으시면 가족분께 도움을 요청하세요.
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
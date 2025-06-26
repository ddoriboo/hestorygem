import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Book, User, Lock, Mail, Calendar, Eye, EyeOff } from 'lucide-react';

const RegisterPage = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: '',
    email: '',
    fullName: '',
    birthYear: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    // 입력 시 에러 메시지 초기화
    if (error) setError('');
  };

  const validateForm = () => {
    if (!formData.username) {
      setError('아이디를 입력해주세요.');
      return false;
    }

    if (formData.username.length < 3) {
      setError('아이디는 3글자 이상이어야 합니다.');
      return false;
    }

    if (!formData.password) {
      setError('비밀번호를 입력해주세요.');
      return false;
    }

    if (formData.password.length < 6) {
      setError('비밀번호는 6글자 이상이어야 합니다.');
      return false;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('비밀번호가 일치하지 않습니다.');
      return false;
    }

    if (!formData.email) {
      setError('이메일을 입력해주세요.');
      return false;
    }

    if (!formData.fullName) {
      setError('성명을 입력해주세요.');
      return false;
    }

    if (formData.birthYear && (formData.birthYear < 1900 || formData.birthYear > 2024)) {
      setError('올바른 출생년도를 입력해주세요.');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await register(
        formData.username,
        formData.password,
        formData.email,
        formData.fullName,
        formData.birthYear ? parseInt(formData.birthYear) : null
      );
      
      if (result.success) {
        navigate('/sessions');
      } else {
        setError(result.error || '회원가입에 실패했습니다.');
      }
    } catch (err) {
      setError('회원가입 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-secondary flex items-center justify-center p-lg">
      <div className="w-full max-w-md">
        {/* 로고 및 제목 */}
        <div className="text-center mb-xl">
          <div className="flex justify-center mb-lg">
            <div className="bg-primary text-white p-lg rounded-xl">
              <Book size={40} />
            </div>
          </div>
          <h1 className="text-3xl font-bold text-primary mb-sm">He'story 회원가입</h1>
          <p className="text-lg text-secondary">나만의 인생 이야기를 시작하세요</p>
        </div>

        {/* 회원가입 폼 */}
        <div className="card">
          <form onSubmit={handleSubmit} className="space-y-lg">
            <div className="card-header text-center">
              <h2 className="card-title">회원 정보 입력</h2>
              <p className="card-subtitle">간단한 정보만 입력하시면 됩니다</p>
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
                아이디 *
              </label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleChange}
                placeholder="영문, 숫자 3글자 이상"
                className="input focus-ring"
                disabled={loading}
                autoComplete="username"
              />
            </div>

            {/* 비밀번호 입력 */}
            <div>
              <label htmlFor="password" className="block text-lg font-semibold mb-md">
                <Lock size={20} className="inline mr-sm" />
                비밀번호 *
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="6글자 이상"
                  className="input focus-ring pr-16"
                  disabled={loading}
                  autoComplete="new-password"
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

            {/* 비밀번호 확인 */}
            <div>
              <label htmlFor="confirmPassword" className="block text-lg font-semibold mb-md">
                <Lock size={20} className="inline mr-sm" />
                비밀번호 확인 *
              </label>
              <div className="relative">
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  id="confirmPassword"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  placeholder="비밀번호를 다시 입력하세요"
                  className="input focus-ring pr-16"
                  disabled={loading}
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-lg top-1/2 transform -translate-y-1/2 text-text-muted hover:text-text-primary"
                  disabled={loading}
                >
                  {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>

            {/* 이메일 입력 */}
            <div>
              <label htmlFor="email" className="block text-lg font-semibold mb-md">
                <Mail size={20} className="inline mr-sm" />
                이메일 *
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="example@email.com"
                className="input focus-ring"
                disabled={loading}
                autoComplete="email"
              />
            </div>

            {/* 성명 입력 */}
            <div>
              <label htmlFor="fullName" className="block text-lg font-semibold mb-md">
                <User size={20} className="inline mr-sm" />
                성명 *
              </label>
              <input
                type="text"
                id="fullName"
                name="fullName"
                value={formData.fullName}
                onChange={handleChange}
                placeholder="홍길동"
                className="input focus-ring"
                disabled={loading}
                autoComplete="name"
              />
            </div>

            {/* 출생년도 입력 (선택사항) */}
            <div>
              <label htmlFor="birthYear" className="block text-lg font-semibold mb-md">
                <Calendar size={20} className="inline mr-sm" />
                출생년도 (선택사항)
              </label>
              <input
                type="number"
                id="birthYear"
                name="birthYear"
                value={formData.birthYear}
                onChange={handleChange}
                placeholder="1950"
                min="1900"
                max="2024"
                className="input focus-ring"
                disabled={loading}
              />
              <p className="text-sm text-muted mt-sm">
                * 출생년도는 자서전 작성에 도움이 됩니다
              </p>
            </div>

            {/* 회원가입 버튼 */}
            <button
              type="submit"
              className="btn btn-primary btn-lg btn-full"
              disabled={loading}
            >
              {loading ? (
                <>
                  <div className="spinner" style={{ width: '20px', height: '20px', marginRight: '8px' }}></div>
                  회원가입 중...
                </>
              ) : (
                '회원가입'
              )}
            </button>

            {/* 로그인 링크 */}
            <div className="text-center pt-lg border-t border-border-light">
              <p className="text-secondary mb-md">이미 계정이 있으신가요?</p>
              <Link
                to="/login"
                className="btn btn-secondary btn-lg"
                style={{ textDecoration: 'none' }}
              >
                로그인
              </Link>
            </div>
          </form>
        </div>

        {/* 도움말 */}
        <div className="text-center mt-xl">
          <p className="text-muted text-sm">
            * 표시된 항목은 필수 입력 사항입니다.<br />
            회원가입 후 바로 12개의 인생 이야기 세션이 준비됩니다.
          </p>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
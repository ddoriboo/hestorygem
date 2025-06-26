import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiService } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));

  // 토큰이 있으면 사용자 정보 가져오기
  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          apiService.setAuthToken(token);
          const userData = await apiService.getCurrentUser();
          setUser(userData);
        } catch (error) {
          console.error('Failed to load user:', error);
          // 토큰이 유효하지 않으면 제거
          localStorage.removeItem('token');
          setToken(null);
          apiService.setAuthToken(null);
        }
      }
      setLoading(false);
    };

    initAuth();
  }, [token]);

  const login = async (username, password) => {
    try {
      const { access_token } = await apiService.login(username, password);
      localStorage.setItem('token', access_token);
      setToken(access_token);
      apiService.setAuthToken(access_token);
      
      const userData = await apiService.getCurrentUser();
      setUser(userData);
      
      return { success: true };
    } catch (error) {
      console.error('Login error:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || '로그인에 실패했습니다.' 
      };
    }
  };

  const register = async (username, password, email, fullName, birthYear) => {
    try {
      await apiService.register({
        username,
        password,
        email,
        full_name: fullName,
        birth_year: birthYear
      });
      
      // 회원가입 후 자동 로그인
      return await login(username, password);
    } catch (error) {
      console.error('Register error:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || '회원가입에 실패했습니다.' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    apiService.setAuthToken(null);
  };

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
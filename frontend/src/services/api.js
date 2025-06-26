import axios from 'axios';

// API 기본 설정
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 요청 인터셉터: 토큰 자동 추가
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // 응답 인터셉터: 401 에러 시 로그아웃 처리
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  setAuthToken(token) {
    if (token) {
      this.api.defaults.headers.Authorization = `Bearer ${token}`;
    } else {
      delete this.api.defaults.headers.Authorization;
    }
  }

  // 인증 관련 API
  async login(username, password) {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await this.api.post('/api/auth/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  }

  async register(userData) {
    const response = await this.api.post('/api/auth/register', userData);
    return response.data;
  }

  async getCurrentUser() {
    const response = await this.api.get('/api/auth/me');
    return response.data;
  }

  // 세션 관련 API
  async getSessions() {
    const response = await this.api.get('/api/sessions/');
    return response.data;
  }

  async getSession(sessionId) {
    const response = await this.api.get(`/api/sessions/${sessionId}`);
    return response.data;
  }

  async updateSession(sessionId, updates) {
    const response = await this.api.patch(`/api/sessions/${sessionId}`, updates);
    return response.data;
  }

  async getSessionProgress(sessionId) {
    const response = await this.api.get(`/api/sessions/${sessionId}/progress`);
    return response.data;
  }

  async getSessionFlowStatus(sessionId) {
    const response = await this.api.get(`/api/sessions/${sessionId}/flow-status`);
    return response.data;
  }

  async initializeSessionFlow(sessionId) {
    const response = await this.api.post(`/api/sessions/${sessionId}/initialize-flow`);
    return response.data;
  }

  // 대화 관련 API
  async getSessionConversations(sessionId, skip = 0, limit = 100) {
    const response = await this.api.get(`/api/conversations/session/${sessionId}`, {
      params: { skip, limit }
    });
    return response.data;
  }

  async createInterview(sessionId, message, conversationType = 'text') {
    const response = await this.api.post('/api/conversations/interview', {
      session_id: sessionId,
      message,
      conversation_type: conversationType
    });
    return response.data;
  }

  async generateAutobiography() {
    const response = await this.api.post('/api/conversations/generate-autobiography');
    return response.data;
  }

  // 자서전 관련 API
  async generateAutobiographyDetailed(format = 'text') {
    const response = await this.api.post('/api/autobiography/generate', null, {
      params: { format }
    });
    return response.data;
  }

  async getAutobiographyPreview(sessionNumbers = null) {
    const params = sessionNumbers ? { session_numbers: sessionNumbers } : {};
    const response = await this.api.get('/api/autobiography/preview', { params });
    return response.data;
  }

  async getAutobiographyStatus() {
    const response = await this.api.get('/api/autobiography/status');
    return response.data;
  }

  // WebSocket 연결 (실시간 음성 인터뷰용)
  connectLiveInterview(sessionId, token) {
    const wsUrl = `${API_BASE_URL.replace('http', 'ws')}/api/conversations/live/${sessionId}`;
    const ws = new WebSocket(wsUrl);
    
    // 연결 시 인증 토큰 전송
    ws.onopen = () => {
      ws.send(JSON.stringify({ token }));
    };

    return ws;
  }

  // 헬스 체크
  async healthCheck() {
    const response = await this.api.get('/health');
    return response.data;
  }
}

export const apiService = new ApiService();
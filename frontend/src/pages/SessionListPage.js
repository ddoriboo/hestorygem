import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import { 
  Play, 
  CheckCircle, 
  Circle, 
  MessageSquare, 
  RotateCcw, 
  Trash2, 
  Plus,
  Clock,
  Award
} from 'lucide-react';

const SessionListPage = () => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionLoading, setActionLoading] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      setLoading(true);
      const data = await apiService.getSessions();
      setSessions(data.sessions || []);
    } catch (err) {
      setError('세션 목록을 불러오는데 실패했습니다.');
      console.error('Load sessions error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStartSession = (sessionId) => {
    navigate(`/sessions/${sessionId}/interview`);
  };

  const handleMarkComplete = async (sessionId, isCompleted) => {
    try {
      setActionLoading(prev => ({ ...prev, [sessionId]: true }));
      
      await apiService.updateSession(sessionId, { 
        is_completed: !isCompleted 
      });
      
      // 세션 목록 새로고침
      await loadSessions();
    } catch (err) {
      setError('세션 상태 변경에 실패했습니다.');
      console.error('Update session error:', err);
    } finally {
      setActionLoading(prev => ({ ...prev, [sessionId]: false }));
    }
  };

  const handleResetSession = async (sessionId) => {
    if (!window.confirm('이 세션의 모든 대화 내용이 삭제됩니다. 정말 다시 시작하시겠습니까?')) {
      return;
    }

    try {
      setActionLoading(prev => ({ ...prev, [sessionId]: true }));
      
      // 세션을 미완료로 변경
      await apiService.updateSession(sessionId, { 
        is_completed: false 
      });
      
      // TODO: 해당 세션의 대화 내용 삭제 API 호출
      // 현재는 상태만 변경
      
      await loadSessions();
      alert('세션이 초기화되었습니다.');
    } catch (err) {
      setError('세션 초기화에 실패했습니다.');
      console.error('Reset session error:', err);
    } finally {
      setActionLoading(prev => ({ ...prev, [sessionId]: false }));
    }
  };

  const getSessionIcon = (sessionNumber) => {
    // 세션 번호에 따른 아이콘 (간단한 예시)
    const icons = ['🌱', '🏠', '📚', '🎯', '💕', '👶', '💼', '🌳', '💭', '🙏', '💌', '📖'];
    return icons[sessionNumber] || '📝';
  };

  const getProgressColor = (conversationCount, isCompleted) => {
    if (isCompleted) return 'text-green-600';
    if (conversationCount >= 5) return 'text-blue-600';
    if (conversationCount >= 1) return 'text-yellow-600';
    return 'text-gray-400';
  };

  if (loading) {
    return <LoadingSpinner message="세션 목록을 불러오는 중..." />;
  }

  const completedSessions = sessions.filter(s => s.is_completed).length;
  const totalConversations = sessions.reduce((sum, s) => sum + (s.conversation_count || 0), 0);

  return (
    <div className="max-w-6xl mx-auto">
      {/* 페이지 헤더 */}
      <div className="text-center mb-2xl">
        <h1 className="text-4xl font-bold text-primary mb-md">나의 인생 이야기</h1>
        <p className="text-xl text-secondary mb-lg">
          12개의 세션을 통해 아름다운 자서전을 만들어보세요
        </p>
        
        {/* 진행 상황 요약 */}
        <div className="flex justify-center gap-xl">
          <div className="bg-white rounded-lg p-lg shadow-md">
            <div className="flex items-center gap-sm">
              <CheckCircle className="text-green-600" size={24} />
              <div>
                <div className="text-2xl font-bold text-green-600">{completedSessions}</div>
                <div className="text-sm text-muted">완료된 세션</div>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg p-lg shadow-md">
            <div className="flex items-center gap-sm">
              <MessageSquare className="text-blue-600" size={24} />
              <div>
                <div className="text-2xl font-bold text-blue-600">{totalConversations}</div>
                <div className="text-sm text-muted">총 대화 수</div>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg p-lg shadow-md">
            <div className="flex items-center gap-sm">
              <Award className="text-purple-600" size={24} />
              <div>
                <div className="text-2xl font-bold text-purple-600">
                  {Math.round((completedSessions / 12) * 100)}%
                </div>
                <div className="text-sm text-muted">전체 진행률</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 에러 메시지 */}
      {error && (
        <div className="bg-red-50 border-2 border-red-200 rounded-lg p-lg mb-xl">
          <p className="text-red-600 text-center font-semibold">{error}</p>
        </div>
      )}

      {/* 세션 목록 */}
      <div className="grid grid-2 gap-lg">
        {sessions.map((session) => (
          <div
            key={session.id}
            className={`card transition-all hover:shadow-lg ${
              session.is_completed ? 'border-green-200 bg-green-50' : ''
            }`}
          >
            {/* 세션 헤더 */}
            <div className="flex items-start gap-md mb-lg">
              <div className="text-3xl">{getSessionIcon(session.session_number)}</div>
              
              <div className="flex-1">
                <div className="flex items-center gap-sm mb-sm">
                  <h3 className="text-xl font-bold text-primary">{session.title}</h3>
                  {session.is_completed ? (
                    <CheckCircle className="text-green-600" size={20} />
                  ) : (
                    <Circle className="text-gray-400" size={20} />
                  )}
                </div>
                
                <p className="text-secondary mb-md">{session.description}</p>
                
                {/* 세션 통계 */}
                <div className="flex items-center gap-lg text-sm">
                  <div className="flex items-center gap-sm">
                    <MessageSquare size={16} className={getProgressColor(session.conversation_count, session.is_completed)} />
                    <span className="text-muted">
                      {session.conversation_count || 0}개 대화
                    </span>
                  </div>
                  
                  {session.is_completed && (
                    <div className="flex items-center gap-sm text-green-600">
                      <Award size={16} />
                      <span className="font-semibold">완료</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* 액션 버튼들 */}
            <div className="flex gap-md">
              {/* 대화 시작/계속하기 버튼 */}
              <button
                onClick={() => handleStartSession(session.id)}
                className="btn btn-primary flex-1"
                disabled={actionLoading[session.id]}
              >
                <Play size={18} />
                {session.conversation_count > 0 ? '대화 계속하기' : '대화 시작하기'}
              </button>

              {/* 완료 토글 버튼 */}
              <button
                onClick={() => handleMarkComplete(session.id, session.is_completed)}
                className={`btn ${session.is_completed ? 'btn-success' : 'btn-secondary'}`}
                disabled={actionLoading[session.id]}
                title={session.is_completed ? '미완료로 변경' : '완료로 표시'}
              >
                {actionLoading[session.id] ? (
                  <div className="spinner" style={{ width: '16px', height: '16px' }}></div>
                ) : session.is_completed ? (
                  <CheckCircle size={18} />
                ) : (
                  <Circle size={18} />
                )}
              </button>

              {/* 다시하기 버튼 */}
              {session.conversation_count > 0 && (
                <button
                  onClick={() => handleResetSession(session.id)}
                  className="btn btn-secondary"
                  disabled={actionLoading[session.id]}
                  title="세션 다시 시작"
                >
                  <RotateCcw size={18} />
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* 하단 액션 */}
      <div className="text-center mt-2xl">
        <div className="bg-white rounded-lg p-xl shadow-md max-w-md mx-auto">
          <h3 className="text-xl font-bold mb-md">다음 단계</h3>
          <p className="text-secondary mb-lg">
            {completedSessions >= 3 
              ? '충분한 이야기가 모였습니다! 자서전을 만들어보세요.' 
              : `최소 3개 세션 완료 후 자서전 생성이 가능합니다. (현재 ${completedSessions}개 완료)`
            }
          </p>
          
          <div className="flex gap-md">
            <button
              onClick={() => navigate('/my-stories')}
              className="btn btn-secondary flex-1"
            >
              <MessageSquare size={18} />
              내 이야기 보기
            </button>
            
            <button
              onClick={() => navigate('/autobiography')}
              className={`btn flex-1 ${
                completedSessions >= 3 ? 'btn-primary' : 'btn-secondary'
              }`}
              disabled={completedSessions < 3}
            >
              <Award size={18} />
              자서전 만들기
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SessionListPage;
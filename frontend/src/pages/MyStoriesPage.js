import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import { 
  MessageSquare, 
  Calendar, 
  Eye, 
  EyeOff, 
  ChevronDown, 
  ChevronUp,
  Download,
  RefreshCw,
  BookOpen
} from 'lucide-react';

const MyStoriesPage = () => {
  const [sessions, setSessions] = useState([]);
  const [sessionConversations, setSessionConversations] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expandedSessions, setExpandedSessions] = useState({});
  const [showRawData, setShowRawData] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    try {
      setLoading(true);
      
      // 모든 세션 목록 가져오기
      const sessionsData = await apiService.getSessions();
      const sessions = sessionsData.sessions || [];
      setSessions(sessions);
      
      // 각 세션의 대화 내용 가져오기
      const conversationsData = {};
      await Promise.all(
        sessions.map(async (session) => {
          try {
            const conversations = await apiService.getSessionConversations(session.id);
            conversationsData[session.id] = conversations.conversations || [];
          } catch (err) {
            console.error(`Failed to load conversations for session ${session.id}:`, err);
            conversationsData[session.id] = [];
          }
        })
      );
      
      setSessionConversations(conversationsData);
    } catch (err) {
      setError('데이터를 불러오는데 실패했습니다.');
      console.error('Load all data error:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleSessionExpansion = (sessionId) => {
    setExpandedSessions(prev => ({
      ...prev,
      [sessionId]: !prev[sessionId]
    }));
  };

  const toggleRawData = (sessionId) => {
    setShowRawData(prev => ({
      ...prev,
      [sessionId]: !prev[sessionId]
    }));
  };

  const generateSessionSummary = (conversations) => {
    if (!conversations || conversations.length === 0) {
      return '아직 대화가 없습니다.';
    }

    // 사용자 메시지들을 모아서 간단한 요약 생성
    const userMessages = conversations
      .filter(conv => conv.user_message && conv.user_message.trim())
      .map(conv => conv.user_message.trim());

    if (userMessages.length === 0) {
      return '대화가 시작되었지만 아직 충분한 내용이 없습니다.';
    }

    // 첫 번째와 마지막 메시지, 그리고 중간의 주요 내용 추출
    let summary = '';
    if (userMessages.length >= 1) {
      const firstMessage = userMessages[0];
      summary += firstMessage.length > 100 ? firstMessage.substring(0, 100) + '...' : firstMessage;
    }

    if (userMessages.length > 2) {
      summary += '\n\n...그리고 더 많은 이야기들...';
    }

    if (userMessages.length > 1) {
      const lastMessage = userMessages[userMessages.length - 1];
      summary += '\n\n' + (lastMessage.length > 100 ? lastMessage.substring(0, 100) + '...' : lastMessage);
    }

    return summary;
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const exportSessionData = (session, conversations) => {
    const data = {
      session: {
        title: session.title,
        description: session.description,
        completed: session.is_completed
      },
      conversations: conversations.map(conv => ({
        user_message: conv.user_message,
        ai_response: conv.ai_response,
        created_at: conv.created_at,
        type: conv.conversation_type
      }))
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { 
      type: 'application/json' 
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `hestory_${session.title.replace(/[^a-zA-Z0-9가-힣]/g, '_')}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return <LoadingSpinner message="내 이야기를 불러오는 중..." />;
  }

  const totalConversations = Object.values(sessionConversations)
    .reduce((sum, conversations) => sum + conversations.length, 0);
  
  const completedSessions = sessions.filter(s => s.is_completed).length;

  return (
    <div className="max-w-6xl mx-auto">
      {/* 페이지 헤더 */}
      <div className="text-center mb-2xl">
        <h1 className="text-4xl font-bold text-primary mb-md">내 이야기 보기</h1>
        <p className="text-xl text-secondary mb-lg">
          지금까지 나눈 모든 대화를 확인하고 관리하세요
        </p>
        
        {/* 통계 요약 */}
        <div className="flex justify-center gap-xl mb-xl">
          <div className="bg-white rounded-lg p-lg shadow-md">
            <div className="text-2xl font-bold text-blue-600">{sessions.length}</div>
            <div className="text-sm text-muted">전체 세션</div>
          </div>
          
          <div className="bg-white rounded-lg p-lg shadow-md">
            <div className="text-2xl font-bold text-green-600">{completedSessions}</div>
            <div className="text-sm text-muted">완료된 세션</div>
          </div>
          
          <div className="bg-white rounded-lg p-lg shadow-md">
            <div className="text-2xl font-bold text-purple-600">{totalConversations}</div>
            <div className="text-sm text-muted">총 대화 수</div>
          </div>
        </div>

        {/* 액션 버튼 */}
        <div className="flex justify-center gap-md">
          <button
            onClick={loadAllData}
            className="btn btn-secondary"
            disabled={loading}
          >
            <RefreshCw size={18} />
            새로고침
          </button>
          
          <button
            onClick={() => navigate('/autobiography')}
            className={`btn ${completedSessions >= 3 ? 'btn-primary' : 'btn-secondary'}`}
            disabled={completedSessions < 3}
          >
            <BookOpen size={18} />
            자서전 초고 만들기
          </button>
        </div>
      </div>

      {/* 에러 메시지 */}
      {error && (
        <div className="bg-red-50 border-2 border-red-200 rounded-lg p-lg mb-xl">
          <p className="text-red-600 text-center font-semibold">{error}</p>
        </div>
      )}

      {/* 세션별 이야기 목록 */}
      <div className="space-y-lg">
        {sessions.map((session) => {
          const conversations = sessionConversations[session.id] || [];
          const isExpanded = expandedSessions[session.id];
          const showRaw = showRawData[session.id];
          const latestDate = conversations.length > 0 
            ? new Date(Math.max(...conversations.map(c => new Date(c.created_at))))
            : null;

          return (
            <div key={session.id} className="card">
              {/* 세션 헤더 */}
              <div className="card-header">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-md">
                      <h3 className="card-title">{session.title}</h3>
                      {session.is_completed && (
                        <span className="bg-green-100 text-green-800 px-md py-sm rounded-full text-sm font-semibold">
                          완료
                        </span>
                      )}
                    </div>
                    
                    <div className="flex items-center gap-lg text-sm text-muted mt-sm">
                      <div className="flex items-center gap-sm">
                        <MessageSquare size={16} />
                        <span>{conversations.length}개 대화</span>
                      </div>
                      
                      {latestDate && (
                        <div className="flex items-center gap-sm">
                          <Calendar size={16} />
                          <span>최근 대화: {formatDate(latestDate)}</span>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-md">
                    {conversations.length > 0 && (
                      <button
                        onClick={() => exportSessionData(session, conversations)}
                        className="btn btn-secondary btn-sm"
                        title="세션 데이터 다운로드"
                      >
                        <Download size={16} />
                      </button>
                    )}
                    
                    <button
                      onClick={() => toggleSessionExpansion(session.id)}
                      className="btn btn-secondary btn-sm"
                    >
                      {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                      {isExpanded ? '접기' : '펼치기'}
                    </button>
                  </div>
                </div>
              </div>

              {/* 세션 내용 (확장된 경우) */}
              {isExpanded && (
                <div className="space-y-lg">
                  {conversations.length === 0 ? (
                    <div className="text-center py-xl">
                      <p className="text-lg text-muted mb-lg">아직 대화가 없습니다.</p>
                      <button
                        onClick={() => navigate(`/sessions/${session.id}/interview`)}
                        className="btn btn-primary"
                      >
                        <MessageSquare size={18} />
                        대화 시작하기
                      </button>
                    </div>
                  ) : (
                    <>
                      {/* 이야기 요약 */}
                      <div className="bg-blue-50 rounded-lg p-lg">
                        <h4 className="text-lg font-semibold text-blue-900 mb-md">📖 이야기 요약</h4>
                        <div className="text-blue-800 whitespace-pre-line">
                          {generateSessionSummary(conversations)}
                        </div>
                      </div>

                      {/* Raw Data 토글 */}
                      <div className="flex items-center justify-between">
                        <h4 className="text-lg font-semibold">상세 대화 내용</h4>
                        <button
                          onClick={() => toggleRawData(session.id)}
                          className="btn btn-secondary btn-sm"
                        >
                          {showRaw ? <EyeOff size={16} /> : <Eye size={16} />}
                          {showRaw ? '숨기기' : '전체 보기'}
                        </button>
                      </div>

                      {/* 대화 내용 */}
                      {showRaw && (
                        <div className="bg-gray-50 rounded-lg p-lg max-h-96 overflow-y-auto">
                          <div className="space-y-md">
                            {conversations.map((conversation, index) => (
                              <div key={index} className="bg-white rounded-lg p-md">
                                <div className="text-xs text-muted mb-sm">
                                  {formatDate(conversation.created_at)} | {conversation.conversation_type}
                                </div>
                                
                                {conversation.user_message && (
                                  <div className="mb-md">
                                    <div className="text-sm font-semibold text-blue-600 mb-sm">
                                      👤 사용자:
                                    </div>
                                    <div className="text-gray-800 pl-md">
                                      {conversation.user_message}
                                    </div>
                                  </div>
                                )}
                                
                                {conversation.ai_response && (
                                  <div>
                                    <div className="text-sm font-semibold text-green-600 mb-sm">
                                      🤖 기억의 안내자:
                                    </div>
                                    <div className="text-gray-800 pl-md">
                                      {conversation.ai_response}
                                    </div>
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* 세션 액션 */}
                      <div className="flex gap-md pt-lg border-t border-gray-200">
                        <button
                          onClick={() => navigate(`/sessions/${session.id}/interview`)}
                          className="btn btn-primary flex-1"
                        >
                          <MessageSquare size={18} />
                          대화 계속하기
                        </button>
                      </div>
                    </>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* 하단 안내 */}
      {sessions.length === 0 && (
        <div className="text-center py-2xl">
          <p className="text-xl text-muted mb-xl">아직 세션이 없습니다.</p>
          <button
            onClick={() => navigate('/sessions')}
            className="btn btn-primary btn-lg"
          >
            <MessageSquare size={18} />
            첫 번째 이야기 시작하기
          </button>
        </div>
      )}
      
      {totalConversations > 0 && (
        <div className="bg-white rounded-lg p-xl text-center mt-2xl">
          <h3 className="text-xl font-bold mb-md">🎉 멋진 이야기들이 모였네요!</h3>
          <p className="text-secondary mb-lg">
            {completedSessions >= 3 
              ? `${completedSessions}개 세션이 완료되었습니다. 이제 자서전을 만들어보세요!`
              : `${completedSessions}개 세션 완료. ${3 - completedSessions}개 더 완료하면 자서전 생성이 가능합니다.`
            }
          </p>
          
          <button
            onClick={() => navigate('/autobiography')}
            className={`btn btn-lg ${completedSessions >= 3 ? 'btn-primary' : 'btn-secondary'}`}
            disabled={completedSessions < 3}
          >
            <BookOpen size={18} />
            자서전 초고 만들기
          </button>
        </div>
      )}
    </div>
  );
};

export default MyStoriesPage;
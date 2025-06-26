import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import { 
  Play, 
  Pause, 
  Send, 
  Mic, 
  MicOff, 
  ArrowLeft, 
  MessageSquare,
  Volume2,
  VolumeX,
  RotateCcw
} from 'lucide-react';

const InterviewPage = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  
  // 상태 관리
  const [session, setSession] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // 인터뷰 상태
  const [isInterviewActive, setIsInterviewActive] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [textMessage, setTextMessage] = useState('');
  
  // 음성 관련
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [audioSupported, setAudioSupported] = useState(false);
  
  // 레퍼런스
  const chatContainerRef = useRef(null);
  const recognitionRef = useRef(null);
  const synthesisRef = useRef(null);

  useEffect(() => {
    loadSessionData();
    initializeAudio();
    
    return () => {
      cleanup();
    };
  }, [sessionId]);

  useEffect(() => {
    scrollToBottom();
  }, [conversations]);

  const loadSessionData = async () => {
    try {
      setLoading(true);
      
      // 세션 정보와 대화 내역을 동시에 로드
      const [sessionData, conversationsData] = await Promise.all([
        apiService.getSession(sessionId),
        apiService.getSessionConversations(sessionId)
      ]);
      
      setSession(sessionData);
      setConversations(conversationsData.conversations || []);
    } catch (err) {
      setError('세션 정보를 불러오는데 실패했습니다.');
      console.error('Load session data error:', err);
    } finally {
      setLoading(false);
    }
  };

  const initializeAudio = () => {
    // 웹 음성 인식 API 확인
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'ko-KR';
      
      recognitionRef.current.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }
        
        setTranscript(finalTranscript + interimTranscript);
        
        if (finalTranscript) {
          handleSpeechResult(finalTranscript);
        }
      };
      
      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        setIsRecording(false);
      };
      
      recognitionRef.current.onend = () => {
        setIsListening(false);
        setIsRecording(false);
      };
      
      setAudioSupported(true);
    }
    
    // 음성 합성 API 확인
    if ('speechSynthesis' in window) {
      synthesisRef.current = window.speechSynthesis;
    }
  };

  const cleanup = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    if (synthesisRef.current) {
      synthesisRef.current.cancel();
    }
  };

  const scrollToBottom = () => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  };

  const startInterview = async () => {
    try {
      setIsInterviewActive(true);
      
      // 세션 플로우 초기화 (첫 시작인 경우)
      if (conversations.length === 0) {
        const initResult = await apiService.initializeSessionFlow(sessionId);
        
        // AI의 첫 인사말 추가
        const newConversation = {
          id: Date.now(),
          user_message: '',
          ai_response: initResult.opening_message,
          created_at: new Date().toISOString(),
          conversation_type: 'text'
        };
        
        setConversations([newConversation]);
        
        // AI 음성으로 인사말 재생
        speakText(initResult.opening_message);
      }
    } catch (err) {
      setError('인터뷰 시작에 실패했습니다.');
      console.error('Start interview error:', err);
      setIsInterviewActive(false);
    }
  };

  const stopInterview = () => {
    setIsInterviewActive(false);
    setIsRecording(false);
    setIsListening(false);
    
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    if (synthesisRef.current) {
      synthesisRef.current.cancel();
    }
  };

  const startListening = () => {
    if (!audioSupported || !recognitionRef.current) {
      alert('음성 인식이 지원되지 않는 브라우저입니다.');
      return;
    }
    
    setIsRecording(true);
    setIsListening(true);
    setTranscript('');
    
    try {
      recognitionRef.current.start();
    } catch (err) {
      console.error('Start recognition error:', err);
      setIsRecording(false);
      setIsListening(false);
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsRecording(false);
    setIsListening(false);
  };

  const handleSpeechResult = async (speechText) => {
    if (speechText.trim()) {
      setTranscript('');
      await sendMessage(speechText.trim());
    }
  };

  const sendTextMessage = async () => {
    if (!textMessage.trim()) return;
    
    const message = textMessage.trim();
    setTextMessage('');
    await sendMessage(message);
  };

  const sendMessage = async (message) => {
    if (!message.trim() || isSending) return;
    
    try {
      setIsSending(true);
      
      // 사용자 메시지를 즉시 화면에 표시
      const userConversation = {
        id: Date.now(),
        user_message: message,
        ai_response: '',
        created_at: new Date().toISOString(),
        conversation_type: 'text',
        isLoading: true
      };
      
      setConversations(prev => [...prev, userConversation]);
      
      // API 호출
      const response = await apiService.createInterview(sessionId, message);
      
      // AI 응답으로 업데이트
      setConversations(prev => 
        prev.map(conv => 
          conv.id === userConversation.id
            ? { ...conv, ai_response: response.ai_response, isLoading: false }
            : conv
        )
      );
      
      // AI 응답을 음성으로 재생
      speakText(response.ai_response);
      
    } catch (err) {
      setError('메시지 전송에 실패했습니다.');
      console.error('Send message error:', err);
      
      // 실패한 메시지 제거
      setConversations(prev => 
        prev.filter(conv => conv.id !== userConversation?.id)
      );
    } finally {
      setIsSending(false);
    }
  };

  const speakText = (text) => {
    if (!synthesisRef.current || !text) return;
    
    // 기존 음성 중지
    synthesisRef.current.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'ko-KR';
    utterance.rate = 0.9; // 조금 느리게
    utterance.pitch = 1;
    utterance.volume = 1;
    
    synthesisRef.current.speak(utterance);
  };

  const stopSpeaking = () => {
    if (synthesisRef.current) {
      synthesisRef.current.cancel();
    }
  };

  if (loading) {
    return <LoadingSpinner message="세션을 불러오는 중..." />;
  }

  if (!session) {
    return (
      <div className="text-center py-2xl">
        <p className="text-xl text-secondary mb-xl">세션을 찾을 수 없습니다.</p>
        <button onClick={() => navigate('/sessions')} className="btn btn-primary">
          <ArrowLeft size={18} />
          세션 목록으로
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* 헤더 */}
      <div className="flex items-center justify-between mb-xl">
        <button
          onClick={() => navigate('/sessions')}
          className="btn btn-secondary"
        >
          <ArrowLeft size={18} />
          세션 목록
        </button>
        
        <div className="text-center flex-1 mx-lg">
          <h1 className="text-2xl font-bold text-primary mb-sm">{session.title}</h1>
          <p className="text-secondary">{session.description}</p>
        </div>
        
        <div className="flex items-center gap-md">
          <div className="text-right text-sm text-muted">
            <div>대화 수: {conversations.length}</div>
            <div className={session.is_completed ? 'text-green-600 font-semibold' : ''}>
              {session.is_completed ? '완료됨' : '진행 중'}
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

      {/* 대화창 */}
      <div className="card mb-xl" style={{ height: '500px', display: 'flex', flexDirection: 'column' }}>
        <div className="card-header">
          <h3 className="card-title flex items-center gap-sm">
            <MessageSquare size={24} />
            대화 내용
          </h3>
        </div>
        
        {/* 대화 목록 */}
        <div 
          ref={chatContainerRef}
          className="flex-1 overflow-y-auto p-lg space-y-lg"
          style={{ maxHeight: '400px' }}
        >
          {conversations.length === 0 ? (
            <div className="text-center py-xl">
              <p className="text-lg text-muted mb-lg">
                아직 대화가 시작되지 않았습니다.<br />
                아래 '대화 시작하기' 버튼을 눌러 인터뷰를 시작하세요.
              </p>
            </div>
          ) : (
            conversations.map((conversation, index) => (
              <div key={conversation.id || index} className="space-y-md">
                {/* 사용자 메시지 */}
                {conversation.user_message && (
                  <div className="flex justify-end">
                    <div className="bg-primary text-white p-lg rounded-lg max-w-xs lg:max-w-md">
                      <p className="mb-0">{conversation.user_message}</p>
                    </div>
                  </div>
                )}
                
                {/* AI 응답 */}
                {conversation.ai_response && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 p-lg rounded-lg max-w-xs lg:max-w-md">
                      <div className="flex items-start gap-sm">
                        <div className="bg-primary text-white rounded-full p-sm">
                          <MessageSquare size={16} />
                        </div>
                        <div className="flex-1">
                          <p className="text-sm text-muted mb-sm">기억의 안내자</p>
                          <p className="mb-0">{conversation.ai_response}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                
                {/* 로딩 상태 */}
                {conversation.isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 p-lg rounded-lg">
                      <div className="flex items-center gap-sm">
                        <div className="spinner" style={{ width: '16px', height: '16px' }}></div>
                        <span className="text-muted">답변을 생각하고 있습니다...</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
          
          {/* 실시간 음성 인식 텍스트 */}
          {transcript && (
            <div className="flex justify-end">
              <div className="bg-blue-100 border-2 border-blue-300 p-lg rounded-lg max-w-xs lg:max-w-md">
                <p className="text-sm text-blue-600 mb-sm">음성 인식 중...</p>
                <p className="mb-0 text-blue-800">{transcript}</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 인터뷰 컨트롤 */}
      <div className="space-y-lg">
        {/* 메인 컨트롤 버튼 */}
        <div className="text-center">
          {!isInterviewActive ? (
            <button
              onClick={startInterview}
              className="btn btn-primary btn-lg"
              style={{ minWidth: '200px', minHeight: '80px' }}
            >
              <Play size={24} />
              대화 시작하기
            </button>
          ) : (
            <button
              onClick={stopInterview}
              className="btn btn-danger btn-lg"
              style={{ minWidth: '200px', minHeight: '80px' }}
            >
              <Pause size={24} />
              대화 종료하기
            </button>
          )}
        </div>

        {/* 입력 컨트롤 (인터뷰가 활성화된 경우만) */}
        {isInterviewActive && (
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">메시지 입력</h3>
            </div>
            
            {/* 음성 입력 */}
            {audioSupported && (
              <div className="text-center mb-lg">
                <button
                  onClick={isRecording ? stopListening : startListening}
                  className={`btn btn-lg ${isRecording ? 'btn-danger' : 'btn-primary'}`}
                  style={{ minWidth: '180px', minHeight: '70px' }}
                  disabled={isSending}
                >
                  {isRecording ? <MicOff size={24} /> : <Mic size={24} />}
                  {isRecording ? '음성 입력 중지' : '음성으로 답변하기'}
                </button>
                
                {isListening && (
                  <p className="text-sm text-blue-600 mt-md">
                    🎤 음성을 듣고 있습니다... 편안하게 말씀해주세요.
                  </p>
                )}
              </div>
            )}
            
            {/* 텍스트 입력 */}
            <div className="flex gap-md">
              <input
                type="text"
                value={textMessage}
                onChange={(e) => setTextMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendTextMessage()}
                placeholder="또는 직접 타이핑해서 답변하세요..."
                className="input flex-1"
                disabled={isSending || isRecording}
              />
              <button
                onClick={sendTextMessage}
                className="btn btn-primary"
                disabled={!textMessage.trim() || isSending || isRecording}
              >
                <Send size={18} />
                전송
              </button>
            </div>
            
            {/* 음성 컨트롤 */}
            {synthesisRef.current && (
              <div className="flex justify-center gap-md mt-lg">
                <button
                  onClick={stopSpeaking}
                  className="btn btn-secondary btn-sm"
                >
                  <VolumeX size={16} />
                  음성 중지
                </button>
              </div>
            )}
            
            {!audioSupported && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-md mt-md">
                <p className="text-yellow-700 text-sm">
                  음성 기능이 지원되지 않는 브라우저입니다. Chrome 브라우저를 권장합니다.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default InterviewPage;
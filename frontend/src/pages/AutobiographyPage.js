import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import { 
  BookOpen, 
  Download, 
  Eye, 
  EyeOff, 
  Copy, 
  CheckCircle,
  AlertCircle,
  RefreshCw,
  FileText,
  Share2
} from 'lucide-react';

const AutobiographyPage = () => {
  const [autobiographyStatus, setAutobiographyStatus] = useState(null);
  const [generatedAutobiography, setGeneratedAutobiography] = useState('');
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');
  const [showPreview, setShowPreview] = useState(false);
  const [copied, setCopied] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    loadAutobiographyStatus();
  }, []);

  const loadAutobiographyStatus = async () => {
    try {
      setLoading(true);
      
      // 자서전 생성 가능 상태 확인
      const status = await apiService.getAutobiographyStatus();
      setAutobiographyStatus(status);
      
      // 미리보기 데이터 로드
      if (status.can_generate) {
        const previewData = await apiService.getAutobiographyPreview();
        setPreview(previewData);
      }
    } catch (err) {
      setError('상태 정보를 불러오는데 실패했습니다.');
      console.error('Load autobiography status error:', err);
    } finally {
      setLoading(false);
    }
  };

  const generateAutobiography = async () => {
    try {
      setGenerating(true);
      setError('');
      
      const result = await apiService.generateAutobiographyDetailed('text');
      setGeneratedAutobiography(result.autobiography);
      
      // 성공 메시지
      alert('자서전 초고가 성공적으로 생성되었습니다!');
    } catch (err) {
      const errorMessage = err.response?.data?.detail || '자서전 생성에 실패했습니다.';
      setError(errorMessage);
      console.error('Generate autobiography error:', err);
    } finally {
      setGenerating(false);
    }
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(generatedAutobiography);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      alert('클립보드 복사에 실패했습니다.');
    }
  };

  const downloadAsText = () => {
    const blob = new Blob([generatedAutobiography], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'hestory_autobiography.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const shareAutobiography = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'He\'story - 나의 자서전',
          text: generatedAutobiography.substring(0, 100) + '...',
          url: window.location.href
        });
      } catch (err) {
        console.log('Share cancelled or failed');
      }
    } else {
      // Fallback: copy to clipboard
      copyToClipboard();
      alert('클립보드에 복사되었습니다.');
    }
  };

  if (loading) {
    return <LoadingSpinner message="자서전 정보를 불러오는 중..." />;
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* 페이지 헤더 */}
      <div className="text-center mb-2xl">
        <h1 className="text-4xl font-bold text-primary mb-md">나만의 자서전</h1>
        <p className="text-xl text-secondary">
          지금까지의 모든 이야기를 하나의 아름다운 자서전으로 만들어보세요
        </p>
      </div>

      {/* 에러 메시지 */}
      {error && (
        <div className="bg-red-50 border-2 border-red-200 rounded-lg p-lg mb-xl">
          <div className="flex items-center gap-sm">
            <AlertCircle className="text-red-600" size={20} />
            <p className="text-red-600 font-semibold">{error}</p>
          </div>
        </div>
      )}

      {/* 자서전 생성 상태 */}
      {autobiographyStatus && (
        <div className="card mb-xl">
          <div className="card-header">
            <h2 className="card-title">자서전 생성 준비 상태</h2>
          </div>
          
          <div className="space-y-lg">
            {/* 요구사항 체크 */}
            <div className="grid grid-2 gap-lg">
              <div className="bg-gray-50 rounded-lg p-lg">
                <h3 className="font-semibold mb-md">완료된 세션</h3>
                <div className="flex items-center gap-sm">
                  {autobiographyStatus.requirements.current_sessions >= autobiographyStatus.requirements.min_sessions ? (
                    <CheckCircle className="text-green-600" size={20} />
                  ) : (
                    <AlertCircle className="text-yellow-600" size={20} />
                  )}
                  <span className="text-lg">
                    {autobiographyStatus.requirements.current_sessions} / {autobiographyStatus.requirements.min_sessions}
                  </span>
                </div>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-lg">
                <h3 className="font-semibold mb-md">총 대화 수</h3>
                <div className="flex items-center gap-sm">
                  {autobiographyStatus.requirements.current_conversations >= autobiographyStatus.requirements.min_conversations ? (
                    <CheckCircle className="text-green-600" size={20} />
                  ) : (
                    <AlertCircle className="text-yellow-600" size={20} />
                  )}
                  <span className="text-lg">
                    {autobiographyStatus.requirements.current_conversations} / {autobiographyStatus.requirements.min_conversations}
                  </span>
                </div>
              </div>
            </div>

            {/* 세션별 상태 */}
            <div>
              <h3 className="font-semibold mb-md">세션별 진행 상황</h3>
              <div className="grid grid-3 gap-md">
                {autobiographyStatus.session_stats.map((sessionStat) => (
                  <div
                    key={sessionStat.session_number}
                    className={`p-md rounded-lg border-2 ${
                      sessionStat.is_completed 
                        ? 'border-green-200 bg-green-50' 
                        : sessionStat.conversation_count > 0
                        ? 'border-yellow-200 bg-yellow-50'
                        : 'border-gray-200 bg-gray-50'
                    }`}
                  >
                    <div className="text-sm font-semibold mb-sm">
                      세션 {sessionStat.session_number + 1}
                    </div>
                    <div className="text-xs text-muted mb-sm">
                      {sessionStat.title}
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">
                        {sessionStat.conversation_count}개 대화
                      </span>
                      {sessionStat.is_completed && (
                        <CheckCircle className="text-green-600" size={16} />
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 생성 가능 여부 */}
            <div className={`p-lg rounded-lg ${
              autobiographyStatus.can_generate 
                ? 'bg-green-50 border-2 border-green-200' 
                : 'bg-yellow-50 border-2 border-yellow-200'
            }`}>
              <div className="flex items-center gap-sm mb-md">
                {autobiographyStatus.can_generate ? (
                  <CheckCircle className="text-green-600" size={24} />
                ) : (
                  <AlertCircle className="text-yellow-600" size={24} />
                )}
                <h3 className={`font-bold text-lg ${
                  autobiographyStatus.can_generate ? 'text-green-800' : 'text-yellow-800'
                }`}>
                  {autobiographyStatus.can_generate 
                    ? '자서전 생성 준비 완료!' 
                    : '조금 더 이야기가 필요해요'
                  }
                </h3>
              </div>
              
              <p className={autobiographyStatus.can_generate ? 'text-green-700' : 'text-yellow-700'}>
                {autobiographyStatus.can_generate 
                  ? '충분한 이야기가 모였습니다. 아래 버튼을 눌러 자서전을 생성하세요.'
                  : `최소 ${autobiographyStatus.requirements.min_sessions}개 세션과 ${autobiographyStatus.requirements.min_conversations}개 대화가 필요합니다. 더 많은 이야기를 나누어 주세요.`
                }
              </p>
            </div>
          </div>
        </div>
      )}

      {/* 미리보기 */}
      {preview && showPreview && (
        <div className="card mb-xl">
          <div className="card-header">
            <div className="flex items-center justify-between">
              <h2 className="card-title">이야기 미리보기</h2>
              <button
                onClick={() => setShowPreview(false)}
                className="btn btn-secondary btn-sm"
              >
                <EyeOff size={16} />
                숨기기
              </button>
            </div>
          </div>
          
          <div className="max-h-96 overflow-y-auto">
            {preview.preview.map((sessionPreview, index) => (
              <div key={index} className="mb-lg pb-lg border-b border-gray-200 last:border-b-0">
                <h3 className="font-semibold text-lg mb-md text-primary">
                  {sessionPreview.session_title}
                </h3>
                
                <div className="flex items-center gap-md mb-md">
                  <span className={`px-md py-sm rounded-full text-sm ${
                    sessionPreview.is_completed 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {sessionPreview.is_completed ? '완료' : '진행 중'}
                  </span>
                  <span className="text-sm text-muted">
                    {sessionPreview.sample_conversations.length}개 대화 샘플
                  </span>
                </div>
                
                <div className="space-y-sm">
                  {sessionPreview.sample_conversations.map((conv, convIndex) => (
                    <div key={convIndex} className="bg-gray-50 rounded p-md">
                      <div className="text-sm text-gray-600 mb-sm">
                        👤 <strong>사용자:</strong> {conv.user}
                      </div>
                      <div className="text-sm text-gray-600">
                        🤖 <strong>AI:</strong> {conv.ai}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 자서전 생성 액션 */}
      <div className="card mb-xl">
        <div className="card-header">
          <h2 className="card-title">자서전 초고 생성</h2>
        </div>
        
        <div className="text-center space-y-lg">
          {!generatedAutobiography ? (
            <>
              {preview && !showPreview && (
                <button
                  onClick={() => setShowPreview(true)}
                  className="btn btn-secondary mb-lg"
                >
                  <Eye size={18} />
                  이야기 미리보기
                </button>
              )}
              
              <div className="space-y-md">
                <p className="text-lg text-secondary">
                  {autobiographyStatus?.can_generate 
                    ? 'AI가 여러분의 소중한 이야기들을 하나의 완성된 자서전으로 엮어드립니다.'
                    : '더 많은 이야기를 나누신 후 자서전 생성이 가능합니다.'
                  }
                </p>
                
                <button
                  onClick={generateAutobiography}
                  className={`btn btn-lg ${
                    autobiographyStatus?.can_generate ? 'btn-primary' : 'btn-secondary'
                  }`}
                  disabled={!autobiographyStatus?.can_generate || generating}
                  style={{ minWidth: '250px', minHeight: '80px' }}
                >
                  {generating ? (
                    <>
                      <div className="spinner" style={{ width: '24px', height: '24px', marginRight: '8px' }}></div>
                      자서전 생성 중...
                    </>
                  ) : (
                    <>
                      <BookOpen size={24} />
                      자서전 초고 만들기
                    </>
                  )}
                </button>
                
                {generating && (
                  <p className="text-sm text-muted">
                    AI가 여러분의 이야기를 정리하고 있습니다. 잠시만 기다려주세요... (1-2분 소요)
                  </p>
                )}
              </div>
            </>
          ) : (
            <div className="text-left">
              <div className="flex items-center justify-between mb-lg">
                <h3 className="text-xl font-bold text-green-600">
                  🎉 자서전 초고가 완성되었습니다!
                </h3>
                
                <div className="flex gap-md">
                  <button
                    onClick={copyToClipboard}
                    className={`btn btn-secondary ${copied ? 'btn-success' : ''}`}
                  >
                    {copied ? <CheckCircle size={18} /> : <Copy size={18} />}
                    {copied ? '복사됨!' : '복사'}
                  </button>
                  
                  <button
                    onClick={downloadAsText}
                    className="btn btn-secondary"
                  >
                    <Download size={18} />
                    다운로드
                  </button>
                  
                  <button
                    onClick={shareAutobiography}
                    className="btn btn-secondary"
                  >
                    <Share2 size={18} />
                    공유
                  </button>
                </div>
              </div>
              
              {/* 자서전 내용 */}
              <div className="bg-white border-2 border-gray-200 rounded-lg p-xl">
                <div 
                  className="prose prose-lg max-w-none"
                  style={{
                    fontSize: '18px',
                    lineHeight: '1.8',
                    fontFamily: 'Noto Sans KR, sans-serif'
                  }}
                >
                  <div className="whitespace-pre-wrap">{generatedAutobiography}</div>
                </div>
              </div>
              
              {/* 하단 액션 */}
              <div className="flex justify-center gap-md mt-xl">
                <button
                  onClick={() => {
                    setGeneratedAutobiography('');
                    loadAutobiographyStatus();
                  }}
                  className="btn btn-secondary"
                >
                  <RefreshCw size={18} />
                  다시 생성하기
                </button>
                
                <button
                  onClick={() => navigate('/sessions')}
                  className="btn btn-primary"
                >
                  <FileText size={18} />
                  더 많은 이야기 추가하기
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 도움말 */}
      {!autobiographyStatus?.can_generate && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-lg text-center">
          <h3 className="text-lg font-bold text-blue-800 mb-md">💡 더 풍성한 자서전을 위한 팁</h3>
          <ul className="text-blue-700 text-left max-w-md mx-auto space-y-sm">
            <li>• 각 세션에서 5개 이상의 대화를 나누어보세요</li>
            <li>• 구체적인 에피소드와 감정을 자세히 표현해보세요</li>
            <li>• 최소 3개 세션을 완료해야 자서전 생성이 가능합니다</li>
            <li>• 더 많은 세션을 완료할수록 풍성한 자서전이 만들어집니다</li>
          </ul>
          
          <button
            onClick={() => navigate('/sessions')}
            className="btn btn-primary mt-lg"
          >
            <FileText size={18} />
            세션 이어가기
          </button>
        </div>
      )}
    </div>
  );
};

export default AutobiographyPage;
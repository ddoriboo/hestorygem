import React from 'react';

const LoadingSpinner = ({ message = '로딩 중...' }) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-white">
      <div className="spinner"></div>
      <p className="mt-lg text-lg text-muted">{message}</p>
    </div>
  );
};

export default LoadingSpinner;
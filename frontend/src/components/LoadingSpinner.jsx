import React from 'react';

/**
 * Loading spinner component
 */
const LoadingSpinner = ({ size = 'medium', text = 'Detecting...' }) => {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12',
  };

  return (
    <div className="flex flex-col items-center justify-center space-y-3">
      <div
        className={`${sizeClasses[size]} border-2 border-gray-200 border-t-blue-600 rounded-full animate-spin-slow`}
      ></div>
      {text && (
        <p className="text-gray-600 animate-pulse-slow">
          {text}
        </p>
      )}
    </div>
  );
};

export default LoadingSpinner;

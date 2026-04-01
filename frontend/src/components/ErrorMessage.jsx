import React from 'react';

/**
 * Component to display error messages
 */
const ErrorMessage = ({ error, onDismiss }) => {
  if (!error) return null;

  const getErrorIcon = () => {
    if (error.includes('connection') || error.includes('server') || error.includes('timeout')) {
      return '🔌';
    }
    if (error.includes('character') || error.includes('empty') || error.includes('minimum')) {
      return '📝';
    }
    if (error.includes('available') || error.includes('503')) {
      return '🤖';
    }
    return '⚠️';
  };

  const getErrorTitle = () => {
    if (error.includes('connection') || error.includes('server') || error.includes('timeout')) {
      return 'Connection Error';
    }
    if (error.includes('character') || error.includes('empty') || error.includes('minimum')) {
      return 'Input Validation Error';
    }
    if (error.includes('available') || error.includes('503')) {
      return 'Service Unavailable';
    }
    return 'Error';
  };

  return (
    <div className="error-card mt-6">
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <span className="text-2xl">{getErrorIcon()}</span>
        </div>
        <div className="ml-4 flex-1">
          <h3 className="text-lg font-medium text-red-800 mb-2">
            {getErrorTitle()}
          </h3>
          <div className="text-sm text-red-700">
            <p>{error}</p>
          </div>
          
          {/* Specific error solutions */}
          {error.includes('connection') && (
            <div className="mt-3 text-sm text-red-600">
              <p className="font-medium mb-2">Possible solutions:</p>
              <ul className="list-disc list-inside space-y-1">
                <li>Check if the backend server is running</li>
                <li>Verify the server is accessible at http://localhost:8000</li>
                <li>Try refreshing the page and detecting again</li>
                <li>Check your internet connection</li>
              </ul>
            </div>
          )}
          
          {error.includes('character') && (
            <div className="mt-3 text-sm text-red-600">
              <p className="font-medium mb-2">Please note:</p>
              <ul className="list-disc list-inside space-y-1">
                <li>Enter at least 3 characters for detection</li>
                <li>Use meaningful text for better accuracy</li>
                <li>Avoid using only punctuation or numbers</li>
              </ul>
            </div>
          )}
          
          {error.includes('available') && (
            <div className="mt-3 text-sm text-red-600">
              <p className="font-medium mb-2">Service issue:</p>
              <ul className="list-disc list-inside space-y-1">
                <li>The AI model is currently not loaded</li>
                <li>Please try again in a few moments</li>
                <li>Contact support if the issue persists</li>
              </ul>
            </div>
          )}
        </div>
        
        {onDismiss && (
          <div className="ml-auto pl-3">
            <button
              onClick={onDismiss}
              className="text-red-400 hover:text-red-600 transition-colors duration-200 p-1 rounded hover:bg-red-100"
              aria-label="Dismiss error"
            >
              <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ErrorMessage;

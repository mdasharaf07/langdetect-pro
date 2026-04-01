import React, { useState } from 'react';

/**
 * Component to display detection history
 */
const HistoryPanel = ({ history, clearHistory, removeFromHistory, onItemClick }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const truncateText = (text, maxLength = 50) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  const getTopPrediction = (predictions) => {
    return predictions && predictions.length > 0 ? predictions[0] : null;
  };

  if (!history || history.length === 0) {
    return null;
  }

  return (
    <div className="mt-8">
      <div className="flex items-center justify-between mb-4">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center space-x-2 text-gray-700 hover:text-gray-900 transition-colors duration-200"
        >
          <svg
            className={`w-5 h-5 transform transition-transform duration-200 ${isExpanded ? 'rotate-90' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
          <span className="font-semibold">
            Detection History ({history.length})
          </span>
        </button>
        
        {history.length > 0 && (
          <button
            onClick={clearHistory}
            className="text-sm text-red-600 hover:text-red-800 transition-colors duration-200"
          >
            Clear All
          </button>
        )}
      </div>

      {isExpanded && (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {history.map((item) => {
            const topPrediction = getTopPrediction(item.predictions);
            return (
              <div
                key={item.id}
                className="glass-morphism rounded-lg p-4 hover:shadow-md transition-all duration-200 cursor-pointer"
                onClick={() => onItemClick(item)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900 font-medium truncate mb-1">
                      {truncateText(item.text)}
                    </p>
                    <div className="flex items-center space-x-2 text-xs text-gray-500">
                      <span className="script-badge">
                        {item.script}
                      </span>
                      {topPrediction && (
                        <span className="font-medium text-blue-600">
                          {topPrediction.language} ({(topPrediction.confidence * 100).toFixed(1)}%)
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-gray-400 mt-1">
                      {formatTimestamp(item.timestamp)}
                    </p>
                  </div>
                  
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      removeFromHistory(item.id);
                    }}
                    className="ml-2 text-gray-400 hover:text-red-600 transition-colors duration-200 p-1"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default HistoryPanel;

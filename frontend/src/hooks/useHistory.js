import { useState, useEffect, useCallback } from 'react';

/**
 * Custom hook for managing detection history
 */
export const useHistory = () => {
  const [history, setHistory] = useState([]);

  // Load history from localStorage on mount
  useEffect(() => {
    try {
      const savedHistory = localStorage.getItem('languageDetectionHistory');
      if (savedHistory) {
        setHistory(JSON.parse(savedHistory));
      }
    } catch (error) {
      console.error('Error loading history from localStorage:', error);
    }
  }, []);

  // Save history to localStorage whenever it changes
  useEffect(() => {
    try {
      if (history.length > 0) {
        localStorage.setItem('languageDetectionHistory', JSON.stringify(history));
      }
    } catch (error) {
      console.error('Error saving history to localStorage:', error);
    }
  }, [history]);

  const addToHistory = useCallback((detection) => {
    const historyItem = {
      id: Date.now(),
      text: detection.input,
      script: detection.script,
      predictions: detection.predictions,
      status: detection.status,
      timestamp: detection.timestamp,
      processingTime: detection.processing_time_ms,
    };

    setHistory(prev => {
      // Keep only the last 50 items
      const newHistory = [historyItem, ...prev].slice(0, 50);
      return newHistory;
    });
  }, []);

  const clearHistory = useCallback(() => {
    setHistory([]);
    try {
      localStorage.removeItem('languageDetectionHistory');
    } catch (error) {
      console.error('Error clearing history from localStorage:', error);
    }
  }, []);

  const removeFromHistory = useCallback((id) => {
    setHistory(prev => prev.filter(item => item.id !== id));
  }, []);

  return {
    history,
    addToHistory,
    clearHistory,
    removeFromHistory,
  };
};

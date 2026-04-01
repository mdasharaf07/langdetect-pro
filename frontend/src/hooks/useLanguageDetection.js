import { useState, useCallback } from 'react';
import axios from 'axios'; // ✅ ADD THIS

/**
 * Custom hook for language detection
 */
export const useLanguageDetection = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const detect = useCallback(async (text) => {
    if (!text || text.trim().length < 3) {
      setError('Please enter at least 3 characters');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      // ✅ REAL API CALL
      const response = await axios.post('http://localhost:8000/predict', {
        text: text.trim(),
      });

      setResult(response.data);

    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Something went wrong');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setError(null);
    setResult(null);
  }, []);

  return {
    isLoading,
    error,
    result,
    detect,
    reset,
  };
};
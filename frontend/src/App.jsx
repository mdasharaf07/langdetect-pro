import React, { useState, useEffect } from 'react';
import { useLanguageDetection } from './hooks/useLanguageDetection';
import { useHistory } from './hooks/useHistory';
import LoadingSpinner from './components/LoadingSpinner.jsx';
import ResultDisplay from './components/ResultDisplay.jsx';
import ErrorMessage from './components/ErrorMessage.jsx';
import HistoryPanel from './components/HistoryPanel.jsx';

/**
 * Main App component
 */
function App() {
  const [text, setText] = useState('');
  const [sampleTexts, setSampleTexts] = useState({});
  const { isLoading, error, result, detect, reset } = useLanguageDetection();
  const { history, addToHistory, clearHistory, removeFromHistory } = useHistory();

  // Load sample texts on component mount
  useEffect(() => {
    const loadSampleTexts = async () => {
      try {
        // const samples = await getSampleTexts();
        // setSampleTexts(samples);
      } catch (error) {
        console.error('Failed to load sample texts:', error);
        setSampleTexts({
          English: [
            "Hello, how are you today? I hope you're having a wonderful day!",
            "The weather is beautiful this morning.",
            "I love programming and machine learning."
          ],
          French: [
            "Bonjour, comment allez-vous aujourd'hui?",
            "Le temps est magnifique ce matin.",
            "J'adore la programmation et l'apprentissage automatique."
          ],
          Tamil: [
            "வணக்கம், நீங்கள் இன்று எப்படி இருக்கிறீர்கள்?",
            "இன்று காலை வானிலை அழகாக உள்ளது.",
            "நான் நிரலாக்கம் மற்றும் இயந்திர கற்றலை விரும்புகிறேன்."
          ],
          Hindi: [
            "नमस्ते, आज आप कैसे हैं?",
            "आज सुबह का मौसम बहुत खूबसूरत है।",
            "मुझे प्रोग्रामिंग और मशीन लर्निंग पसंद है।"
          ]
        });
      }
    };

    loadSampleTexts();
  }, []);

  const handleDetect = () => {
    detect(text);
  };

  const handleReset = () => {
    setText('');
    reset();
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      e.preventDefault();
      handleDetect();
    }
  };

  const handleHistoryItemClick = (historyItem) => {
    setText(historyItem.text);
  };

  useEffect(() => {
    if (result) {
      addToHistory(result);
    }
  }, [result]);

  const trimmedText = text.trim();
  const isButtonDisabled = !trimmedText || trimmedText.length < 3 || isLoading;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">

        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-4">
            Language Detector
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-2">
            Advanced AI-powered language detection supporting 150+ languages
          </p>
          <p className="text-sm text-gray-500">
            Powered by FastText with script detection and confidence scoring
          </p>
        </div>

        {/* Main Content */}
        <div className="glass-morphism rounded-3xl p-8 shadow-2xl">

          {/* Input Section */}
          <div className="space-y-6">
            <div>
              <label htmlFor="text-input" className="block text-sm font-semibold text-gray-700 mb-3">
                Enter text to analyze
              </label>
              <textarea
                id="text-input"
                value={text}
                onChange={(e) => setText(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Type or paste your text here... (minimum 3 characters)"
                className="input-field"
                rows={6}
                disabled={isLoading}
              />
              <div className="mt-3 flex justify-between items-center">
                <span className="text-sm text-gray-500">
                  {text.length} characters
                </span>
                <span className="text-xs text-gray-400">
                  Ctrl + Enter to detect
                </span>
              </div>
            </div>

            {/* Buttons */}
            <div className="flex space-x-4">
              <button
                onClick={handleDetect}
                disabled={isButtonDisabled}
                className={`flex-1 ${isButtonDisabled ? 'btn-disabled' : 'btn-primary'}`}
              >
                {isLoading ? (
                  <div className="flex items-center justify-center space-x-2">
                    <LoadingSpinner size="small" text="" />
                    <span>Detecting...</span>
                  </div>
                ) : (
                  'Detect Language'
                )}
              </button>

              <button
                onClick={handleReset}
                disabled={isLoading}
                className="px-8 py-3 border-2 border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 transition-all duration-200 disabled:opacity-50"
              >
                Clear
              </button>
            </div>
          </div>

          {/* Loading */}
          {isLoading && (
            <div className="mt-8 text-center py-8">
              <LoadingSpinner size="large" text="Analyzing text..." />
            </div>
          )}

          {/* Error */}
          <ErrorMessage error={error} onDismiss={reset} />

          {/* Result */}
          {!isLoading && !error && result && (
            <ResultDisplay result={result} />
          )}

          {/* Samples */}
          {!isLoading && !error && !result && Object.keys(sampleTexts).length > 0 && (
            <div className="mt-8 p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl border border-blue-200">
              <h3 className="text-lg font-semibold text-blue-800 mb-4">
                Try sample texts:
              </h3>
              {Object.entries(sampleTexts).map(([lang, texts]) => (
                <div key={lang} className="mb-3">
                  <p className="text-sm font-medium text-blue-700">{lang}</p>
                  {texts.map((t, i) => (
                    <button
                      key={i}
                      onClick={() => setText(t)}
                      className="block w-full text-left text-sm text-blue-600 hover:bg-blue-100 p-2 rounded"
                    >
                      {t}
                    </button>
                  ))}
                </div>
              ))}
            </div>
          )}

          {/* History */}
          <HistoryPanel
            history={history}
            clearHistory={clearHistory}
            removeFromHistory={removeFromHistory}
            onItemClick={handleHistoryItemClick}
          />
        </div>

        {/* Footer */}
        <div className="mt-12 text-center space-y-2">
          <p className="text-sm text-gray-500">
            FastText • 150+ languages • Script detection
          </p>
          <p className="text-xs text-gray-400">
            Confidence threshold: 60% • &lt;100ms response
          </p>
        </div>

      </div>
    </div>
  );
}

export default App;
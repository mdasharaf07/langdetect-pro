import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

/**
 * Component to display language detection results
 */
const ResultDisplay = ({ result }) => {
  if (!result || !result.predictions || result.predictions.length === 0) {
    return null;
  }

  const topPrediction = result.predictions[0];
  const confidence = topPrediction.confidence;
  const confidencePercentage = (confidence * 100).toFixed(1);

  const getConfidenceColor = (conf) => {
    if (conf >= 0.9) return 'bg-green-500';
    if (conf >= 0.7) return 'bg-yellow-500';
    if (conf >= 0.6) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getConfidenceTextColor = (conf) => {
    if (conf >= 0.9) return 'text-green-600';
    if (conf >= 0.7) return 'text-yellow-600';
    if (conf >= 0.6) return 'text-orange-600';
    return 'text-red-600';
  };

  const getStatusColor = (status) => {
    if (status === 'success') return 'status-success';
    if (status === 'uncertain') return 'status-uncertain';
    return 'status-uncertain';
  };

  // Prepare data for chart
  const chartData = result.predictions.map((pred, index) => ({
    name: pred.language,
    confidence: parseFloat((pred.confidence * 100).toFixed(1)),
    fill: index === 0 ? '#3B82F6' : '#93C5FD'
  }));

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className="result-card mt-8">
      {/* Header */}
      <div className="text-center mb-6">
        <h2 className="text-3xl font-bold text-gray-800 mb-4">Detection Result</h2>
        
        {/* Script Badge */}
        <div className="flex justify-center items-center space-x-2 mb-4">
          <span className="script-badge">
            Script: {result.script}
          </span>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(result.status)}`}>
            {result.status === 'success' ? 'High Confidence' : 'Low Confidence'}
          </span>
        </div>
        
        {/* Main Prediction */}
        <div className="flex items-center justify-center space-x-3 mb-4">
          <span className="text-4xl font-bold text-blue-600">
            {topPrediction.language}
          </span>
          <span className={`text-xl font-semibold ${getConfidenceTextColor(confidence)}`}>
            ({confidencePercentage}%)
          </span>
        </div>
        
        {/* Confidence Bar */}
        <div className="w-full max-w-md mx-auto mb-4">
          <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
            <div
              className={`confidence-bar ${getConfidenceColor(confidence)}`}
              style={{ width: `${confidencePercentage}%` }}
            ></div>
          </div>
        </div>

        {/* Processing Time */}
        {result.processing_time_ms && (
          <p className="text-sm text-gray-500">
            Processing time: {result.processing_time_ms.toFixed(2)}ms
          </p>
        )}

        {/* Timestamp */}
        {result.timestamp && (
          <p className="text-xs text-gray-400 mt-2">
            {formatTimestamp(result.timestamp)}
          </p>
        )}
      </div>

      {/* Confidence Chart */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-gray-700 mb-4 text-center">
          Confidence Distribution
        </h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="name" 
                angle={-45}
                textAnchor="end"
                height={80}
                interval={0}
              />
              <YAxis />
              <Tooltip 
                formatter={(value) => [`${value}%`, 'Confidence']}
                labelStyle={{ color: '#374151' }}
              />
              <Bar dataKey="confidence" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top Predictions List */}
      <div>
        <h3 className="text-lg font-semibold text-gray-700 mb-4 text-center">
          Top Predictions
        </h3>
        <div className="space-y-3">
          {result.predictions.map((prediction, index) => (
            <div
              key={index}
              className={`prediction-item ${
                index === 0 ? 'ring-2 ring-blue-400 bg-gradient-to-r from-blue-50 to-white' : ''
              }`}
            >
              <div className="flex items-center space-x-3">
                <span className="text-lg font-bold text-gray-600">
                  #{index + 1}
                </span>
                <span className="font-medium text-gray-800">
                  {prediction.language}
                </span>
              </div>
              <div className="flex items-center space-x-3">
                <span className={`font-semibold ${getConfidenceTextColor(prediction.confidence)}`}>
                  {(prediction.confidence * 100).toFixed(1)}%
                </span>
                <div className="w-24 bg-gray-200 rounded-full h-2 overflow-hidden">
                  <div
                    className={`confidence-bar ${getConfidenceColor(prediction.confidence)}`}
                    style={{ width: `${prediction.confidence * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Uncertain Message */}
      {result.status === 'uncertain' && (
        <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-xl">
          <p className="text-sm text-yellow-800 text-center">
            ⚠️ The prediction confidence is below 60%. The text might be too short or contain mixed languages.
          </p>
        </div>
      )}
    </div>
  );
};

export default ResultDisplay;

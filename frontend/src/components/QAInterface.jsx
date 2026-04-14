import React, { useState } from 'react';
import { Send, AlertCircle, ChevronDown, ChevronUp, Sparkles } from 'lucide-react';
import { apiClient } from '../api';

const QAInterface = ({ onResultsReceived, isLoading }) => {
  const [question, setQuestion] = useState('');
  const [topK, setTopK] = useState(3);
  const [threshold, setThreshold] = useState(0.65);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!question.trim()) {
      setError('Please enter a question');
      return;
    }

    try {
      setSearching(true);
      setError('');
      
      const response = await apiClient.askQuestionWithLLM(
        question,
        topK,
        threshold,
        'gemini-2.5-flash'
      );
      onResultsReceived(response.data);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Request failed. Please try again.';
      if (errorMsg.includes('Gemini')) {
        setError('Gemini API not configured. Please set GEMINI_API_KEY environment variable.');
      } else {
        setError(errorMsg);
      }
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="space-y-4">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="question" className="block text-sm font-medium text-gray-700 mb-2">
            Ask a Question
          </label>
          <div className="relative">
            <input
              id="question"
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="What would you like to know about your documents?"
              disabled={searching || isLoading}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500"
            />
            <button
              type="submit"
              disabled={searching || isLoading || !question.trim()}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-2 text-blue-500 hover:bg-blue-50 rounded-lg disabled:text-gray-400 disabled:bg-transparent"
            >
              <Send size={20} />
            </button>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="topK" className="block text-sm font-medium text-gray-700 mb-2">
              Number of Results (top_k)
            </label>
            <input
              id="topK"
              type="number"
              min="1"
              max="10"
              value={topK}
              onChange={(e) => setTopK(parseInt(e.target.value))}
              disabled={searching || isLoading}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50"
            />
          </div>

          <div>
            <label htmlFor="threshold" className="block text-sm font-medium text-gray-700 mb-2">
              Similarity Threshold
            </label>
            <div className="flex items-center gap-2">
              <input
                id="threshold"
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={threshold}
                onChange={(e) => setThreshold(parseFloat(e.target.value))}
                disabled={searching || isLoading}
                className="flex-1"
              />
              <span className="text-sm font-medium text-gray-700 w-12 text-right">
                {threshold.toFixed(2)}
              </span>
            </div>
          </div>
        </div>
      </form>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="text-red-500 flex-shrink-0 mt-0.5" size={20} />
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}
    </div>
  );
};

export const SearchResults = ({ results, question, isLoading }) => {
  const [expandedChunks, setExpandedChunks] = useState({});

  if (!results) {
    return null;
  }

  // Handle LLM response format
  if (results.answer) {
    return (
      <div className="space-y-6">
        {/* AI-Generated Answer */}
        <div className="border border-indigo-200 rounded-lg overflow-hidden bg-gradient-to-r from-indigo-50 to-blue-50">
          <div className="px-4 py-3 bg-gradient-to-r from-indigo-500 to-blue-500 text-white flex items-center gap-2">
            <Sparkles size={20} />
            <h3 className="font-semibold">AI Answer</h3>
          </div>
          <div className="px-4 py-4">
            <p className="text-gray-800 leading-relaxed whitespace-pre-wrap text-base">
              {results.answer}
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Handle regular search results format
  if (results.total_results === 0) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-yellow-800 text-sm">
          {results.message || 'No relevant chunks found. Try lowering the similarity threshold or rephrasing your question.'}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="mb-4">
        <p className="text-sm text-gray-600">
          Found <span className="font-semibold">{results.total_results}</span> relevant chunk{results.total_results !== 1 ? 's' : ''} for your question
        </p>
      </div>

      {results.results.map((chunk) => (
        <div
          key={chunk.chunk_id}
          className="border border-gray-200 rounded-lg overflow-hidden hover:border-blue-300 transition-colors"
        >
          <button
            onClick={() =>
              setExpandedChunks((prev) => ({
                ...prev,
                [chunk.chunk_id]: !prev[chunk.chunk_id],
              }))
            }
            className="w-full px-4 py-3 flex items-center justify-between bg-gray-50 hover:bg-gray-100 transition-colors"
          >
            <div className="text-left flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-sm font-semibold text-blue-600">#{chunk.rank}</span>
                <span className="text-sm font-medium text-gray-900">{chunk.document_name}</span>
              </div>
              <div className="text-xs text-gray-600">
                Chunk {chunk.chunk_index} • Similarity: {(chunk.similarity_score * 100).toFixed(1)}%
              </div>
            </div>
            {expandedChunks[chunk.chunk_id] ? (
              <ChevronUp className="text-gray-400" />
            ) : (
              <ChevronDown className="text-gray-400" />
            )}
          </button>

          {expandedChunks[chunk.chunk_id] && (
            <div className="px-4 py-3 bg-white border-t border-gray-200">
              <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                {chunk.text}
              </p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default QAInterface;

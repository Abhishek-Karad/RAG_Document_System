import React, { useState, useEffect } from 'react';
import { FileUp, MessageSquare, Loader } from 'lucide-react';
import DocumentUpload from './components/DocumentUpload';
import DocumentList from './components/DocumentList';
import QAInterface, { SearchResults } from './components/QAInterface';
import { apiClient } from './api';
import './index.css';

function App() {
  const [documents, setDocuments] = useState([]);
  const [results, setResults] = useState(null);
  const [lastQuestion, setLastQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('upload');

  // Fetch documents on mount
  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      setIsLoading(true);
      const response = await apiClient.getDocuments();
      setDocuments(response.data.documents);
      if (response.data.documents.length > 0 && activeTab === 'upload') {
        setActiveTab('ask');
      }
    } catch (err) {
      console.error('Failed to fetch documents:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUploadSuccess = (uploadData) => {
    setResults(null);
    setLastQuestion('');
    fetchDocuments();
  };

  const handleDelete = async (documentId) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      try {
        setIsLoading(true);
        await apiClient.deleteDocument(documentId);
        await fetchDocuments();
        setResults(null);
      } catch (err) {
        alert('Failed to delete document');
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleResultsReceived = (data) => {
    setResults(data);
    setLastQuestion(data.question);
  };

  const canAsk = documents.length > 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <MessageSquare className="text-blue-600" size={24} />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Document QA</h1>
                <p className="text-sm text-gray-600">Powered by FAISS Similarity Search</p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-xs font-medium px-3 py-1 rounded-full bg-green-100 text-green-800">
                ✓ System Ready
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Panel - Documents */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6 sticky top-8">
              <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <FileUp size={20} className="text-blue-600" />
                Your Documents
              </h2>

              {documents.length > 0 && (
                <div className="mb-4 p-3 bg-blue-50 rounded-lg">
                  <p className="text-sm text-blue-700">
                    <span className="font-semibold">{documents.length}</span> document{documents.length !== 1 ? 's' : ''} ready for Q&A
                  </p>
                </div>
              )}

              <DocumentList
                documents={documents}
                onDelete={handleDelete}
                isLoading={isLoading}
              />
            </div>
          </div>

          {/* Right Panel - Upload & QA */}
          <div className="lg:col-span-2 space-y-8">
            {/* Upload Section */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center gap-2 mb-6">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <FileUp className="text-blue-600" size={20} />
                </div>
                <h2 className="text-lg font-bold text-gray-900">Upload Document</h2>
              </div>

              <DocumentUpload
                onUploadSuccess={handleUploadSuccess}
                isLoading={isLoading}
              />

              <div className="mt-4 p-4 bg-blue-50 rounded-lg text-sm text-blue-700">
                <p className="font-medium mb-2">Supported formats:</p>
                <ul className="list-disc list-inside space-y-1">
                  <li>PDF documents</li>
                  <li>Plain text files (.txt)</li>
                  <li>Markdown files (.md)</li>
                </ul>
              </div>
            </div>

            {/* QA Section */}
            {canAsk ? (
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center gap-2 mb-6">
                  <div className="p-2 bg-indigo-100 rounded-lg">
                    <MessageSquare className="text-indigo-600" size={20} />
                  </div>
                  <h2 className="text-lg font-bold text-gray-900">Ask Questions</h2>
                </div>

                <QAInterface
                  onResultsReceived={handleResultsReceived}
                  isLoading={isLoading}
                />

                {results && (
                  <div className="mt-6 pt-6 border-t border-gray-200">
                    <h3 className="text-md font-semibold text-gray-900 mb-4">
                      Results for: "{lastQuestion}"
                    </h3>
                    <SearchResults
                      results={results}
                      question={lastQuestion}
                      isLoading={isLoading}
                    />
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-md p-8 text-center">
                <MessageSquare className="mx-auto h-12 w-12 text-gray-400 mb-3" />
                <p className="text-gray-600 mb-2">Upload documents first to start asking questions</p>
                <p className="text-sm text-gray-500">
                  Upload at least one document to enable the Q&A feature
                </p>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-12 border-t border-gray-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 text-center text-sm text-gray-600">
          <p>FAISS Document QA System © 2024 | Built with FastAPI & React</p>
        </div>
      </footer>
    </div>
  );
}

export default App;

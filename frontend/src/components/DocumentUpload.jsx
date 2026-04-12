import React, { useState } from 'react';
import { Upload, X, AlertCircle } from 'lucide-react';
import { apiClient } from '../api';

const DocumentUpload = ({ onUploadSuccess, isLoading }) => {
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState('');
  const [uploading, setUploading] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleFile = async (file) => {
    setError('');
    
    // Validate file type
    const allowedTypes = ['.pdf', '.txt', '.md'];
    const fileExt = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(fileExt)) {
      setError(`Invalid file type. Allowed: ${allowedTypes.join(', ')}`);
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB');
      return;
    }

    try {
      setUploading(true);
      const response = await apiClient.uploadDocument(file);
      setError('');
      onUploadSuccess(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      handleFile(files[0]);
    }
  };

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  return (
    <div className="w-full">
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-colors duration-200
          ${dragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 bg-gray-50 hover:border-gray-400'
          }
          ${uploading ? 'opacity-60 cursor-not-allowed' : ''}
        `}
      >
        <input
          type="file"
          onChange={handleChange}
          disabled={uploading || isLoading}
          className="hidden"
          id="file-input"
          accept=".pdf,.txt,.md"
        />

        <label htmlFor="file-input" className="cursor-pointer block">
          <Upload className="mx-auto h-12 w-12 text-gray-400 mb-2" />
          <p className="text-lg font-medium text-gray-700">
            {uploading ? 'Uploading...' : 'Drag and drop your document'}
          </p>
          <p className="text-sm text-gray-500 mt-1">
            or click to select (PDF, TXT, MD - max 10MB)
          </p>
        </label>
      </div>

      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="text-red-500 flex-shrink-0 mt-0.5" size={20} />
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}
    </div>
  );
};

export default DocumentUpload;

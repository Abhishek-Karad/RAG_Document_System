import React from 'react';
import { Trash2, FileText, Calendar } from 'lucide-react';

const DocumentList = ({ documents, onDelete, isLoading }) => {
  if (documents.length === 0) {
    return (
      <div className="text-center py-8">
        <FileText className="mx-auto h-12 w-12 text-gray-400 mb-2" />
        <p className="text-gray-500">No documents uploaded yet.</p>
        <p className="text-sm text-gray-400">Upload a document to get started</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {documents.map((doc) => (
        <div
          key={doc.document_id}
          className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200 hover:border-gray-300 transition-colors"
        >
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <FileText size={20} className="text-blue-500 flex-shrink-0" />
              <div>
                <p className="font-medium text-gray-900">{doc.name}</p>
                <div className="flex items-center gap-4 text-xs text-gray-500 mt-1">
                  <span>{doc.chunk_count} chunks</span>
                  <span>{doc.total_characters.toLocaleString()} characters</span>
                  <div className="flex items-center gap-1">
                    <Calendar size={12} />
                    {new Date(doc.uploaded_at).toLocaleDateString()}
                  </div>
                </div>
              </div>
            </div>
          </div>
          <button
            onClick={() => onDelete(doc.document_id)}
            disabled={isLoading}
            className="ml-4 p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
            title="Delete document"
          >
            <Trash2 size={20} />
          </button>
        </div>
      ))}
    </div>
  );
};

export default DocumentList;

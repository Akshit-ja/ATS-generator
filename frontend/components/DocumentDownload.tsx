import React from 'react';
import { Document } from '../types/document';

interface DocumentDownloadProps {
  document: Document;
  className?: string;
}

const DocumentDownload: React.FC<DocumentDownloadProps> = ({ document, className = '' }) => {
  const handleDownload = () => {
    // Open the document URL in a new tab
    window.open(document.s3_url, '_blank');
  };

  const handlePreview = () => {
    // For PDF files, we can preview them directly
    if (document.file_type === 'pdf' || document.content_type === 'application/pdf') {
      window.open(document.s3_url, '_blank');
    } else {
      // For other file types, just download them
      window.open(document.s3_url, '_blank');
    }
  };

  return (
    <div className={`flex flex-col space-y-2 ${className}`}>
      <div className="flex items-center">
        <svg className="w-5 h-5 text-gray-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <span className="text-sm font-medium truncate" title={document.filename}>
          {document.filename}
        </span>
      </div>
      
      <div className="flex space-x-2">
        <button
          onClick={handleDownload}
          className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
        >
          Download
        </button>
        <button
          onClick={handlePreview}
          className="px-3 py-1 bg-gray-200 text-gray-800 text-sm rounded hover:bg-gray-300 transition-colors"
        >
          Preview
        </button>
      </div>
    </div>
  );
};

export default DocumentDownload;
import React from 'react';

interface DownloadButtonsProps {
  docxUrl: string | null;
  pdfUrl: string | null;
  isDisabled: boolean;
}

export default function DownloadButtons({ docxUrl, pdfUrl, isDisabled }: DownloadButtonsProps) {
  const handleDownload = async (url: string, filename: string) => {
    if (!url || isDisabled) return;
    
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (!response.ok) {
        throw new Error('Download failed');
      }
      
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(downloadUrl);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Download error:', error);
      alert('Download failed. Please try again.');
    }
  };

  return (
    <div className="flex flex-col sm:flex-row gap-3">
      <button
        className={`flex items-center justify-center px-4 py-2 rounded-lg ${
          docxUrl && !isDisabled
            ? 'bg-blue-600 text-white hover:bg-blue-700'
            : 'bg-gray-300 text-gray-500 cursor-not-allowed'
        }`}
        onClick={() => handleDownload(docxUrl || '', 'resume.docx')}
        disabled={!docxUrl || isDisabled}
      >
        <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
          <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
        </svg>
        Download DOCX
      </button>
      
      <button
        className={`flex items-center justify-center px-4 py-2 rounded-lg ${
          pdfUrl && !isDisabled
            ? 'bg-red-600 text-white hover:bg-red-700'
            : 'bg-gray-300 text-gray-500 cursor-not-allowed'
        }`}
        onClick={() => handleDownload(pdfUrl || '', 'resume.pdf')}
        disabled={!pdfUrl || isDisabled}
      >
        <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
          <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
        </svg>
        Download PDF
      </button>
    </div>
  );
}
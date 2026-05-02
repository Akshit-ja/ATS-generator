import React, { useState } from 'react';

interface ResumePreviewProps {
  originalResume: string | null;
  generatedResume: string | null;
}

export default function ResumePreview({ originalResume, generatedResume }: ResumePreviewProps) {
  const [activeTab, setActiveTab] = useState<'side-by-side' | 'original' | 'generated'>('side-by-side');

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="flex border-b">
        <button
          className={`flex-1 py-3 px-4 text-center font-medium ${
            activeTab === 'side-by-side' ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'
          }`}
          onClick={() => setActiveTab('side-by-side')}
        >
          Side by Side
        </button>
        <button
          className={`flex-1 py-3 px-4 text-center font-medium ${
            activeTab === 'original' ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'
          }`}
          onClick={() => setActiveTab('original')}
        >
          Original
        </button>
        <button
          className={`flex-1 py-3 px-4 text-center font-medium ${
            activeTab === 'generated' ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'
          }`}
          onClick={() => setActiveTab('generated')}
        >
          Generated
        </button>
      </div>

      <div className="p-4">
        {activeTab === 'side-by-side' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="border rounded-lg p-4">
              <h3 className="font-medium text-gray-700 mb-2">Original Resume</h3>
              <div className="bg-gray-50 p-4 rounded h-96 overflow-auto whitespace-pre-wrap text-sm">
                {originalResume || (
                  <div className="flex items-center justify-center h-full text-gray-400">
                    No original resume content available
                  </div>
                )}
              </div>
            </div>
            <div className="border rounded-lg p-4">
              <h3 className="font-medium text-gray-700 mb-2">Generated Resume</h3>
              <div className="bg-gray-50 p-4 rounded h-96 overflow-auto whitespace-pre-wrap text-sm">
                {generatedResume || (
                  <div className="flex items-center justify-center h-full text-gray-400">
                    No generated resume content available
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'original' && (
          <div className="border rounded-lg p-4">
            <h3 className="font-medium text-gray-700 mb-2">Original Resume</h3>
            <div className="bg-gray-50 p-4 rounded h-96 overflow-auto whitespace-pre-wrap text-sm">
              {originalResume || (
                <div className="flex items-center justify-center h-full text-gray-400">
                  No original resume content available
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'generated' && (
          <div className="border rounded-lg p-4">
            <h3 className="font-medium text-gray-700 mb-2">Generated Resume</h3>
            <div className="bg-gray-50 p-4 rounded h-96 overflow-auto whitespace-pre-wrap text-sm">
              {generatedResume || (
                <div className="flex items-center justify-center h-full text-gray-400">
                  No generated resume content available
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
import React, { useState } from 'react';

interface ResultsDisplayProps {
  matchScore: number;
  keywordAnalysis: {
    matched?: string[];
    missing?: string[];
  };
  atsReport: {
    overall_score: number;
    passed: boolean;
    rule_results: {
      single_column?: boolean;
      standard_fonts?: boolean;
      no_images_tables_textboxes?: boolean;
      recognized_section_headers?: boolean;
      proper_date_formats?: boolean;
      text_extractable?: boolean;
    };
  } | null;
}

export default function ResultsDisplay({ matchScore, keywordAnalysis, atsReport }: ResultsDisplayProps) {
  const [activeTab, setActiveTab] = useState('match');

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="flex border-b">
        <button
          className={`flex-1 py-3 px-4 text-center font-medium ${
            activeTab === 'match' ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'
          }`}
          onClick={() => setActiveTab('match')}
        >
          Match Score
        </button>
        <button
          className={`flex-1 py-3 px-4 text-center font-medium ${
            activeTab === 'keywords' ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'
          }`}
          onClick={() => setActiveTab('keywords')}
        >
          Keyword Analysis
        </button>
        <button
          className={`flex-1 py-3 px-4 text-center font-medium ${
            activeTab === 'ats' ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'
          }`}
          onClick={() => setActiveTab('ats')}
        >
          ATS Compliance
        </button>
      </div>

      <div className="p-6">
        {activeTab === 'match' && (
          <div className="text-center">
            <div className="inline-block rounded-full h-36 w-36 flex items-center justify-center border-8 border-blue-100">
              <div className="text-3xl font-bold text-blue-600">{matchScore}%</div>
            </div>
            <h3 className="mt-4 text-xl font-semibold">Job Match Score</h3>
            <p className="mt-2 text-gray-600">
              {matchScore >= 80
                ? 'Excellent match! Your resume is well-aligned with this job.'
                : matchScore >= 60
                ? 'Good match. Some improvements could help your chances.'
                : 'Your resume needs optimization for this job.'}
            </p>
          </div>
        )}

        {activeTab === 'keywords' && (
          <div>
            <h3 className="text-xl font-semibold mb-4">Keyword Analysis</h3>
            
            <div className="mb-6">
              <h4 className="font-medium text-green-600 mb-2">Matched Keywords</h4>
              {keywordAnalysis.matched && keywordAnalysis.matched.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {keywordAnalysis.matched.map((keyword, index) => (
                    <span key={index} className="bg-green-100 text-green-800 px-2 py-1 rounded text-sm">
                      {keyword}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No matched keywords found</p>
              )}
            </div>
            
            <div>
              <h4 className="font-medium text-red-600 mb-2">Missing Keywords</h4>
              {keywordAnalysis.missing && keywordAnalysis.missing.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {keywordAnalysis.missing.map((keyword, index) => (
                    <span key={index} className="bg-red-100 text-red-800 px-2 py-1 rounded text-sm">
                      {keyword}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No missing keywords</p>
              )}
            </div>
          </div>
        )}

        {activeTab === 'ats' && (
          <div>
            <h3 className="text-xl font-semibold mb-4">ATS Compliance Report</h3>
            
            {atsReport ? (
              <>
                <div className="flex items-center mb-6">
                  <div className="w-24 h-24 rounded-full flex items-center justify-center border-4 border-gray-200">
                    <span className={`text-2xl font-bold ${
                      atsReport.overall_score >= 80 ? 'text-green-600' : 
                      atsReport.overall_score >= 60 ? 'text-yellow-600' : 'text-red-600'
                    }`}>
                      {atsReport.overall_score}%
                    </span>
                  </div>
                  <div className="ml-4">
                    <h4 className="text-lg font-medium">
                      {atsReport.passed ? 'ATS Friendly' : 'Needs Improvement'}
                    </h4>
                    <p className="text-gray-600">
                      {atsReport.passed 
                        ? 'Your resume is optimized for ATS systems' 
                        : 'Your resume may be filtered out by ATS systems'}
                    </p>
                  </div>
                </div>
                
                <div className="space-y-3">
                  {Object.entries(atsReport.rule_results).map(([rule, passed], index) => {
                    const ruleLabels: {[key: string]: string} = {
                      single_column: 'Single Column Layout',
                      standard_fonts: 'Standard Fonts',
                      no_images_tables_textboxes: 'No Images/Tables/Text Boxes',
                      recognized_section_headers: 'Recognized Section Headers',
                      proper_date_formats: 'Proper Date Formats',
                      text_extractable: 'Text Extractable'
                    };
                    
                    return (
                      <div key={index} className="flex items-center">
                        {passed ? (
                          <svg className="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        ) : (
                          <svg className="w-5 h-5 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        )}
                        <span className={passed ? 'text-gray-800' : 'text-gray-600'}>
                          {ruleLabels[rule] || rule}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </>
            ) : (
              <div className="text-center py-8 text-gray-500">
                ATS report not available yet
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
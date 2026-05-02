import React, { useState } from 'react';

interface Question {
  question: string;
  answer: string;
  type: string;
}

interface InterviewQuestionsListProps {
  questions: {
    behavioral_questions: Question[];
    technical_questions: Question[];
    company_questions: Question[];
  };
}

const InterviewQuestionsList: React.FC<InterviewQuestionsListProps> = ({ questions }) => {
  const [activeTab, setActiveTab] = useState<'behavioral' | 'technical' | 'company'>('behavioral');
  const [expandedQuestions, setExpandedQuestions] = useState<Record<string, boolean>>({});

  const toggleQuestion = (questionId: string) => {
    setExpandedQuestions(prev => ({
      ...prev,
      [questionId]: !prev[questionId]
    }));
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const downloadAllQuestions = () => {
    const allQuestions = [
      ...questions.behavioral_questions.map(q => ({ ...q, category: 'Behavioral' })),
      ...questions.technical_questions.map(q => ({ ...q, category: 'Technical' })),
      ...questions.company_questions.map(q => ({ ...q, category: 'Company-Specific' }))
    ];

    let content = "# Interview Questions and Answers\n\n";
    
    allQuestions.forEach(q => {
      content += `## ${q.category}: ${q.question}\n\n`;
      content += `${q.answer}\n\n`;
    });

    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'interview-questions.md';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const renderQuestionList = (questionList: Question[], type: string) => {
    return (
      <div className="space-y-4">
        {questionList.map((q, index) => {
          const questionId = `${type}-${index}`;
          const isExpanded = expandedQuestions[questionId] || false;
          
          return (
            <div key={questionId} className="border rounded-lg overflow-hidden bg-white">
              <div 
                className="p-4 flex justify-between items-center cursor-pointer hover:bg-gray-50"
                onClick={() => toggleQuestion(questionId)}
              >
                <h3 className="text-lg font-medium text-gray-900">{q.question}</h3>
                <svg 
                  className={`h-5 w-5 text-gray-500 transform ${isExpanded ? 'rotate-180' : ''}`} 
                  xmlns="http://www.w3.org/2000/svg" 
                  viewBox="0 0 20 20" 
                  fill="currentColor"
                >
                  <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </div>
              
              {isExpanded && (
                <div className="p-4 bg-gray-50 border-t">
                  <div className="prose max-w-none">
                    <p className="whitespace-pre-wrap">{q.answer}</p>
                  </div>
                  <div className="mt-4 flex justify-end">
                    <button 
                      onClick={() => copyToClipboard(q.answer)}
                      className="inline-flex items-center px-3 py-1 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      <svg className="mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                      </svg>
                      Copy Answer
                    </button>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="bg-white shadow-md rounded-lg overflow-hidden">
      <div className="border-b border-gray-200">
        <nav className="flex -mb-px">
          <button
            onClick={() => setActiveTab('behavioral')}
            className={`py-4 px-6 text-center border-b-2 font-medium text-sm ${
              activeTab === 'behavioral'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Behavioral ({questions.behavioral_questions.length})
          </button>
          <button
            onClick={() => setActiveTab('technical')}
            className={`py-4 px-6 text-center border-b-2 font-medium text-sm ${
              activeTab === 'technical'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Technical ({questions.technical_questions.length})
          </button>
          <button
            onClick={() => setActiveTab('company')}
            className={`py-4 px-6 text-center border-b-2 font-medium text-sm ${
              activeTab === 'company'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Company-Specific ({questions.company_questions.length})
          </button>
        </nav>
      </div>

      <div className="p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-gray-900">
            {activeTab === 'behavioral' && 'Behavioral Questions'}
            {activeTab === 'technical' && 'Technical Questions'}
            {activeTab === 'company' && 'Company-Specific Questions'}
          </h2>
          
          <button
            onClick={downloadAllQuestions}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg className="mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Download All
          </button>
        </div>

        {activeTab === 'behavioral' && renderQuestionList(questions.behavioral_questions, 'behavioral')}
        {activeTab === 'technical' && renderQuestionList(questions.technical_questions, 'technical')}
        {activeTab === 'company' && renderQuestionList(questions.company_questions, 'company')}
      </div>
    </div>
  );
};

export default InterviewQuestionsList;
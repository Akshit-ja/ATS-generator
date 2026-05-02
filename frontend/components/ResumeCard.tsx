import React from 'react';
import Link from 'next/link';

interface ResumeCardProps {
  id: number;
  title: string;
  createdAt: string;
  score?: number;
  onClick?: () => void;
}

const ResumeCard: React.FC<ResumeCardProps> = ({ id, title, createdAt, score, onClick }) => {
  const formattedDate = new Date(createdAt).toLocaleDateString();
  
  return (
    <div 
      className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 overflow-hidden cursor-pointer"
      onClick={onClick}
    >
      <div className="p-5">
        <div className="flex justify-between items-start">
          <h3 className="text-lg font-semibold text-gray-800 mb-2 truncate">{title}</h3>
          {score !== undefined && (
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
              score >= 80 ? 'bg-green-100 text-green-800' : 
              score >= 60 ? 'bg-yellow-100 text-yellow-800' : 
              'bg-red-100 text-red-800'
            }`}>
              {score}%
            </span>
          )}
        </div>
        
        <div className="flex justify-between items-center mt-4">
          <span className="text-sm text-gray-500">{formattedDate}</span>
          <Link href={`/dashboard/resume/${id}`}>
            <span className="inline-flex items-center text-sm font-medium text-blue-600 hover:text-blue-800">
              View
              <svg className="ml-1 w-4 h-4" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
              </svg>
            </span>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ResumeCard;
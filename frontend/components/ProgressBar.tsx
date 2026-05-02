import React from 'react';

interface ProgressBarProps {
  progress: number;
}

export default function ProgressBar({ progress }: ProgressBarProps) {
  return (
    <div className="w-full">
      <div className="flex justify-between mb-1">
        <span className="text-sm font-medium text-blue-700">Processing</span>
        <span className="text-sm font-medium text-blue-700">{progress}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div 
          className="bg-blue-600 h-2.5 rounded-full transition-all duration-500 ease-out" 
          style={{ width: `${progress}%` }}
        ></div>
      </div>
      <div className="mt-2 text-sm text-gray-500 text-center">
        {progress < 20 && "Starting..."}
        {progress >= 20 && progress < 40 && "Analyzing resume..."}
        {progress >= 40 && progress < 60 && "Matching with job description..."}
        {progress >= 60 && progress < 80 && "Generating optimized content..."}
        {progress >= 80 && progress < 100 && "Finalizing..."}
        {progress === 100 && "Complete!"}
      </div>
    </div>
  );
}
import React from 'react';

interface JobDescriptionProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export default function JobDescription({ value, onChange, disabled = false }: JobDescriptionProps) {
  return (
    <div className="w-full">
      <textarea
        className={`w-full h-64 p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none
          ${disabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}
        `}
        placeholder="Paste the job description here..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
      />
      <p className="mt-2 text-sm text-gray-500">
        Paste the complete job description to get the best results
      </p>
    </div>
  );
}
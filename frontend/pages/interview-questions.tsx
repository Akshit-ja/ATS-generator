import React, { useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '../components/Layout';
import DashboardHeader from '../components/DashboardHeader';
import InterviewQuestionsList from '../components/InterviewQuestionsList';
import axios from 'axios';

interface UserProfileItem {
  company: string;
  position: string;
  start_date: string;
  end_date: string;
  description: string;
}

interface UserProfile {
  name: string;
  email: string;
  skills: string[];
  work_history: UserProfileItem[];
  education: { [key: string]: string }[];
}

interface Question {
  question: string;
  answer: string;
  type: string;
}

export default function InterviewQuestions() {
  const router = useRouter();
  const [jobDescription, setJobDescription] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [questions, setQuestions] = useState<{
    behavioral_questions: Question[];
    technical_questions: Question[];
    company_questions: Question[];
  } | null>(null);

  // Mock user profile data - in a real app, this would come from the user's account
  const userProfile: UserProfile = {
    name: "John Doe",
    email: "john.doe@example.com",
    skills: ["JavaScript", "React", "Node.js", "Python", "FastAPI", "SQL"],
    work_history: [
      {
        company: "Tech Solutions Inc.",
        position: "Senior Frontend Developer",
        start_date: "2020-01",
        end_date: "Present",
        description: "Led development of React-based applications, improved performance by 40%, mentored junior developers."
      },
      {
        company: "Web Innovations",
        position: "Full Stack Developer",
        start_date: "2017-03",
        end_date: "2019-12",
        description: "Developed and maintained web applications using React, Node.js, and MongoDB. Implemented CI/CD pipelines."
      }
    ],
    education: [
      {
        "degree": "Bachelor of Science",
        "major": "Computer Science",
        "university": "University of Technology",
        "year": "2017"
      }
    ]
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!jobDescription.trim()) {
      setError('Please enter a job description');
      return;
    }
    
    setError(null);
    setIsLoading(true);
    
    try {
      const response = await axios.post('http://localhost:8000/api/v1/interview-questions', {
        job_description: jobDescription,
        user_profile: userProfile
      }, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });
      
      setQuestions(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate interview questions');
      console.error('Error generating interview questions:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Layout title="Interview Questions - Resume AI Generator">
      <DashboardHeader />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Interview Question Generator</h1>
        
        <div className="bg-white shadow-md rounded-lg p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Generate Interview Questions</h2>
          <p className="text-gray-600 mb-4">
            Paste a job description below to generate personalized interview questions and STAR method answers
            based on your profile and work history.
          </p>
          
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label htmlFor="jobDescription" className="block text-sm font-medium text-gray-700 mb-1">
                Job Description
              </label>
              <textarea
                id="jobDescription"
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                rows={8}
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste the job description here..."
                required
              />
            </div>
            
            <button
              type="submit"
              disabled={isLoading}
              className={`w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
                isLoading ? 'opacity-70 cursor-not-allowed' : ''
              }`}
            >
              {isLoading ? 'Generating...' : 'Generate Interview Questions'}
            </button>
          </form>
        </div>
        
        {error && (
          <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-8">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}
        
        {questions && <InterviewQuestionsList questions={questions} />}
      </div>
    </Layout>
  );
}
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import ResumeUpload from '../components/ResumeUpload';
import JobDescription from '../components/JobDescription';
import ProgressBar from '../components/ProgressBar';
import DownloadButtons from '../components/DownloadButtons';

export default function Dashboard() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState<any | null>(null);
  const [generatedResume, setGeneratedResume] = useState<string | null>(null);
  const [docxUrl, setDocxUrl] = useState<string | null>(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeMode, setActiveMode] = useState<'generate' | 'optimize'>('generate');

  // Check authentication on component mount
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (!token) {
      router.push('/login');
      return;
    }

    // Verify token validity
    verifyToken(token);
  }, []);

  // Verify JWT token
  const verifyToken = async (token: string) => {
    try {
      const response = await fetch('http://localhost:8000/auth/verify', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        setIsAuthenticated(true);
      } else {
        localStorage.removeItem('authToken');
        router.push('/login');
      }
    } catch (err) {
      localStorage.removeItem('authToken');
      router.push('/login');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    router.push('/login');
  };

  const handleFileUpload = (file: File) => {
    setResumeFile(file);
    setError(null);
    if (docxUrl) {
      URL.revokeObjectURL(docxUrl);
      setDocxUrl(null);
    }
    if (pdfUrl) {
      URL.revokeObjectURL(pdfUrl);
      setPdfUrl(null);
    }
  };

  const handleJobDescriptionChange = (value: string) => {
    setJobDescription(value);
  };

  const handleGenerateNewResume = async () => {
    if (!jobDescription.trim()) {
      setError('Please provide a job description');
      return;
    }

    setIsProcessing(true);
    setProgress(10);
    setError(null);
    setResults(null);

    try {
      // For new resume generation, we don't send a file
      const formData = new FormData();
      formData.append('job_description', jobDescription);

      const response = await fetch('http://localhost:8000/api/v1/generate-resume', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
        },
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate resume');
      }
      
      const data = await response.json();
      
      setProgress(100);
      setIsProcessing(false);
      setResults(data);
      setGeneratedResume(data.professional_summary || 'Resume generated successfully!');
      
      // Set download URLs if available
      if (data.docx_url) {
        setDocxUrl(`http://localhost:8000${data.docx_url}`);
      }
      if (data.pdf_url) {
        setPdfUrl(`http://localhost:8000${data.pdf_url}`);
      }
      
    } catch (err: any) {
      setIsProcessing(false);
      setProgress(0);
      setError(err.message || 'An error occurred while generating resume');
      console.error('Error generating resume:', err);
    }
  };

  const handleOptimizeResume = async () => {
    if (!jobDescription.trim()) {
      setError('Please provide a job description');
      return;
    }

    if (!resumeFile) {
      setError('Please upload your resume to optimize');
      return;
    }

    setIsProcessing(true);
    setProgress(10);
    setError(null);
    setResults(null);

    try {
      // For resume optimization, we send both the file and job description
      const formData = new FormData();
      formData.append('resume_file', resumeFile);
      formData.append('job_description', jobDescription);

      const response = await fetch('http://localhost:8000/api/v1/generate-resume', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
        },
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to optimize resume');
      }
      
      const data = await response.json();
      
      setProgress(100);
      setIsProcessing(false);
      setResults(data);
      setGeneratedResume(data.professional_summary || 'Resume optimized successfully!');
      
      // Set download URLs if available
      if (data.docx_url) {
        setDocxUrl(`http://localhost:8000${data.docx_url}`);
      }
      if (data.pdf_url) {
        setPdfUrl(`http://localhost:8000${data.pdf_url}`);
      }
      
    } catch (err: any) {
      setIsProcessing(false);
      setProgress(0);
      setError(err.message || 'An error occurred while optimizing resume');
      console.error('Error optimizing resume:', err);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="flex justify-center items-center min-h-screen bg-gray-100">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Resume AI Generator</h1>
          <button
            onClick={handleLogout}
            className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
          >
            Logout
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
            {error}
          </div>
        )}

        {/* Mode Selection */}
        <div className="bg-white p-6 rounded-lg shadow-md mb-8">
          <h2 className="text-2xl font-semibold mb-4">Choose Your Resume Service</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              onClick={() => {
                setActiveMode('generate');
                setResumeFile(null);
                setError(null);
                setResults(null);
              }}
              className={`p-6 rounded-lg border-2 transition-all ${
                activeMode === 'generate'
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="text-4xl mb-2">🆕</div>
              <h3 className="text-lg font-semibold mb-2">Generate New Resume</h3>
              <p className="text-sm text-gray-600">
                Create a brand new resume from scratch using AI based on a job description
              </p>
            </button>

            <button
              onClick={() => {
                setActiveMode('optimize');
                setError(null);
                setResults(null);
              }}
              className={`p-6 rounded-lg border-2 transition-all ${
                activeMode === 'optimize'
                  ? 'border-green-500 bg-green-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="text-4xl mb-2">🔧</div>
              <h3 className="text-lg font-semibold mb-2">Optimize Existing Resume</h3>
              <p className="text-sm text-gray-600">
                Upload your current resume and optimize it for a specific job posting
              </p>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Input Section */}
          <div className="space-y-6">
            {activeMode === 'optimize' && (
              <div className="bg-white p-6 rounded-lg shadow-md">
                <h2 className="text-xl font-semibold mb-2">Upload Your Current Resume</h2>
                <p className="text-sm text-gray-500 mb-4">� Required - Upload your existing resume to optimize</p>
                <ResumeUpload 
                  onFileUpload={handleFileUpload} 
                  disabled={isProcessing}
                />
                {resumeFile && (
                  <p className="mt-2 text-sm text-green-600">
                    ✅ Selected file: {resumeFile.name}
                  </p>
                )}
              </div>
            )}

            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-semibold mb-4">
                {activeMode === 'generate' ? 'Target Job Description' : 'Job Description to Optimize For'}
              </h2>
              <p className="text-sm text-gray-500 mb-4">
                {activeMode === 'generate' 
                  ? '📝 Paste the job description and AI will create a tailored resume' 
                  : '🎯 Paste the job description to optimize your resume for this specific role'
                }
              </p>
              <JobDescription 
                value={jobDescription}
                onChange={handleJobDescriptionChange}
                disabled={isProcessing}
              />
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md">
              {activeMode === 'generate' ? (
                <button
                  onClick={handleGenerateNewResume}
                  disabled={isProcessing || !jobDescription.trim()}
                  className={`w-full py-3 px-4 rounded-lg font-medium text-white transition-colors ${
                    isProcessing || !jobDescription.trim()
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-blue-600 hover:bg-blue-700'
                  }`}
                >
                  {isProcessing ? '🔄 Generating New Resume...' : '🆕 Generate New Resume with AI'}
                </button>
              ) : (
                <button
                  onClick={handleOptimizeResume}
                  disabled={isProcessing || !jobDescription.trim() || !resumeFile}
                  className={`w-full py-3 px-4 rounded-lg font-medium text-white transition-colors ${
                    isProcessing || !jobDescription.trim() || !resumeFile
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-green-600 hover:bg-green-700'
                  }`}
                >
                  {isProcessing ? '🔄 Optimizing Resume...' : '🔧 Optimize Resume for Job'}
                </button>
              )}
              {activeMode === 'optimize' && !resumeFile && (
                <p className="mt-2 text-sm text-red-600">
                  ⚠️ Please upload your resume first
                </p>
              )}
            </div>

            {isProcessing && (
              <div className="bg-white p-6 rounded-lg shadow-md">
                <ProgressBar progress={progress} />
              </div>
            )}
          </div>

          {/* Right Column - Results Section */}
          <div className="space-y-6">
            {results && (
              <>
                <div className="bg-white p-6 rounded-lg shadow-md">
                  <h2 className="text-xl font-semibold mb-4">
                    {activeMode === 'generate' ? '🎉 AI-Generated Resume' : '🎉 Optimized Resume'}
                  </h2>
                  
                  {/* Professional Summary */}
                  {results.professional_summary && (
                    <div className="mb-6">
                      <h3 className="text-lg font-medium text-gray-900 mb-2">📝 Professional Summary</h3>
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <p className="text-gray-700 leading-relaxed">{results.professional_summary}</p>
                      </div>
                    </div>
                  )}

                  {/* Technical Skills */}
                  {results.technical_skills && (
                    <div className="mb-6">
                      <h3 className="text-lg font-medium text-gray-900 mb-2">🛠️ Technical Skills</h3>
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <p className="text-gray-700">{results.technical_skills}</p>
                      </div>
                    </div>
                  )}

                  {/* Work Experience */}
                  {results.work_experience && (
                    <div className="mb-6">
                      <h3 className="text-lg font-medium text-gray-900 mb-2">💼 Work Experience</h3>
                      <div className="bg-green-50 p-4 rounded-lg">
                        <p className="text-gray-700 whitespace-pre-line">{results.work_experience}</p>
                      </div>
                    </div>
                  )}

                  {/* Education */}
                  {results.education && (
                    <div className="mb-6">
                      <h3 className="text-lg font-medium text-gray-900 mb-2">🎓 Education</h3>
                      <div className="bg-purple-50 p-4 rounded-lg">
                        <p className="text-gray-700">{results.education}</p>
                      </div>
                    </div>
                  )}

                  {/* Success Message */}
                  <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-lg">
                    <p className="font-medium">
                      {activeMode === 'generate' 
                        ? '✅ New resume successfully generated using AI for the job description!' 
                        : '✅ Your resume has been successfully optimized for this specific job posting!'
                      }
                    </p>
                  </div>
                </div>

                <div className="bg-white p-6 rounded-lg shadow-md">
                  <h2 className="text-xl font-semibold mb-4">Download Optimized Resume</h2>
                  <DownloadButtons 
                    docxUrl={docxUrl}
                    pdfUrl={pdfUrl}
                    isDisabled={!docxUrl && !pdfUrl}
                  />
                </div>
              </>
            )}

            {!results && !isProcessing && (
              <div className="bg-white p-8 rounded-lg shadow-md flex flex-col items-center justify-center text-center">
                <div className="text-6xl mb-4">
                  {activeMode === 'generate' ? '🆕' : '🔧'}
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  {activeMode === 'generate' ? 'Ready to Generate New Resume' : 'Ready to Optimize Resume'}
                </h3>
                <p className="text-gray-500">
                  {activeMode === 'generate' 
                    ? 'Provide a job description and AI will create a tailored resume for you.' 
                    : 'Upload your resume and provide a job description to optimize it for the role.'
                  }
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';
import { randomItem } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// Custom metrics
const resumeGenerationTrend = new Trend('resume_generation_time');
const matchScoreTrend = new Trend('match_score_time');
const validationTrend = new Trend('validation_time');
const errorRate = new Rate('error_rate');
const successRate = new Rate('success_rate');
const requestCounter = new Counter('total_requests');

// Test configuration
export const options = {
  scenarios: {
    resume_generation_load: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 20 },  // Ramp up to 20 users
        { duration: '1m', target: 50 },   // Ramp up to 50 users
        { duration: '1m', target: 100 },  // Ramp up to 100 users
        { duration: '2m', target: 100 },  // Stay at 100 users for 2 minutes
        { duration: '30s', target: 0 },   // Ramp down to 0 users
      ],
      gracefulRampDown: '30s',
    },
  },
  thresholds: {
    'resume_generation_time': ['p(95)<3000'], // 95% of resume generations should be under 3s
    'match_score_time': ['p(95)<1000'],       // 95% of match score calculations should be under 1s
    'validation_time': ['p(95)<1000'],        // 95% of validations should be under 1s
    'error_rate': ['rate<0.1'],               // Error rate should be less than 10%
    'http_req_duration': ['p(95)<3000'],      // 95% of requests should be under 3s
  },
};

// Sample data
const sampleResumes = [
  {
    name: "John Smith",
    email: "john.smith@example.com",
    phone: "123-456-7890",
    location: "New York, NY",
    summary: "Experienced software engineer with 5+ years in web development",
    skills: ["Python", "JavaScript", "React", "FastAPI"],
    experience: [
      {
        title: "Senior Developer",
        company: "Tech Company",
        location: "New York, NY",
        start_date: "2020-01",
        end_date: "Present",
        description: "Led development of web applications"
      }
    ],
    education: [
      {
        degree: "Bachelor of Science in Computer Science",
        institution: "University of Technology",
        location: "Boston, MA",
        graduation_date: "2017-05"
      }
    ]
  },
  {
    name: "Jane Doe",
    email: "jane.doe@example.com",
    phone: "987-654-3210",
    location: "San Francisco, CA",
    summary: "Full stack developer with expertise in modern JavaScript frameworks",
    skills: ["JavaScript", "React", "Node.js", "MongoDB"],
    experience: [
      {
        title: "Full Stack Developer",
        company: "Web Solutions Inc.",
        location: "San Francisco, CA",
        start_date: "2019-03",
        end_date: "Present",
        description: "Developed and maintained web applications using React and Node.js"
      }
    ],
    education: [
      {
        degree: "Master of Computer Science",
        institution: "Tech University",
        location: "San Francisco, CA",
        graduation_date: "2018-12"
      }
    ]
  }
];

const sampleJobDescriptions = [
  "Senior Software Engineer with Python experience needed for a fast-paced tech company. Requirements: 5+ years of experience with Python, web frameworks like FastAPI or Flask, and cloud services.",
  "Full Stack Developer position available. Looking for someone with React, Node.js, and database experience. Must be able to work in an agile environment.",
  "Data Scientist role for a growing startup. Must have experience with Python, machine learning libraries, and data visualization tools."
];

// Helper function to generate auth token (mock)
function getAuthToken() {
  // In a real test, you would authenticate and get a real token
  return "mock_auth_token";
}

function buildResumeData() {
  const baseResume = randomItem(sampleResumes);
  const resumeData = { ...baseResume };

  resumeData.job_description = randomItem(sampleJobDescriptions);
  resumeData.template = "modern";

  return resumeData;
}

// Main test function
export default function() {
  // Default to local API base URL when no environment override is provided.
  const baseUrl = __ENV.LOAD_TEST_BASE_URL || 'http://localhost:8000/api/v1';
  const authToken = getAuthToken();
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${authToken}`,
  };

  // 1. Generate a resume
  const resumeData = buildResumeData();

  const startResumeGen = new Date();
  const resumeResponse = http.post(`${baseUrl}/resumes/generate`, JSON.stringify(resumeData), { headers });
  const resumeGenTime = new Date() - startResumeGen;
  resumeGenerationTrend.add(resumeGenTime);
  requestCounter.add(1);
  
  const resumeSuccess = check(resumeResponse, {
    'resume generation status is 200': (r) => r.status === 200,
    'resume generation has content': (r) => r.json().hasOwnProperty('content'),
    'resume generation time under threshold': () => resumeGenTime < 3000,
  });
  
  successRate.add(resumeSuccess);
  errorRate.add(!resumeSuccess);

  if (resumeSuccess) {
    const generatedResume = resumeResponse.json().content;
    
    // 2. Match resume to job
    const matchData = {
      resume_text: generatedResume,
      job_description: resumeData.job_description
    };
    
    const startMatch = new Date();
    const matchResponse = http.post(`${baseUrl}/resumes/match-score`, JSON.stringify(matchData), { headers });
    const matchTime = new Date() - startMatch;
    matchScoreTrend.add(matchTime);
    requestCounter.add(1);
    
    const matchSuccess = check(matchResponse, {
      'match score status is 200': (r) => r.status === 200,
      'match score has overall score': (r) => r.json().hasOwnProperty('overall_match_score'),
      'match score time under threshold': () => matchTime < 1000
    });
    
    successRate.add(matchSuccess);
    errorRate.add(!matchSuccess);
    
    // 3. Validate resume for ATS compliance
    const validationData = {
      resume_text: generatedResume,
      job_description: resumeData.job_description
    };
    
    const startValidation = new Date();
    const validationResponse = http.post(`${baseUrl}/validate/resume`, JSON.stringify(validationData), { headers });
    validationTrend.add(new Date() - startValidation);
    requestCounter.add(1);
    
    const validationSuccess = check(validationResponse, {
      'validation status is 200': (r) => r.status === 200,
      'validation has overall score': (r) => r.json().hasOwnProperty('overall_score'),
    });
    
    successRate.add(validationSuccess);
    errorRate.add(!validationSuccess);
  }
  
  // Wait between iterations to simulate real user behavior
  sleep(Math.random() * 3 + 2); // Random sleep between 2-5 seconds
}

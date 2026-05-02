"""
OpenAI API integration service for resume generation and enhancement
"""
from openai import OpenAI
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service for OpenAI API interactions"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key or self.api_key.startswith("your-"):
            logger.warning("OpenAI API key not found or is placeholder. AI features will be disabled.")
            self.enabled = False
            self.client = None
        else:
            try:
                self.client = OpenAI(api_key=self.api_key)
                self.enabled = True
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.enabled = False
                self.client = None
        
        # Model configurations - using commonly available models
        self.models = {
            "resume_generation": "gpt-3.5-turbo",  # More commonly available
            "interview_questions": "gpt-3.5-turbo",
            "resume_enhancement": "gpt-3.5-turbo",  # More commonly available  
            "job_matching": "gpt-3.5-turbo"
        }
    
    def generate_resume_content(self, user_profile: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        """
        Generate tailored resume content using OpenAI
        
        Args:
            user_profile: User's profile data including experience, skills, education
            job_description: Target job description to tailor resume for
            
        Returns:
            Dict containing generated resume sections
        """
        if not self.enabled:
            return self._get_mock_resume_content()
        
        try:
            prompt = self._build_resume_prompt(user_profile, job_description)
            
            response = self.client.chat.completions.create(
                model=self.models["resume_generation"],
                messages=[
                    {"role": "system", "content": "You are an expert resume writer who creates compelling, ATS-friendly resumes tailored to specific job descriptions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            return self._parse_resume_response(content)
            
        except Exception as e:
            logger.error(f"OpenAI resume generation failed: {str(e)}")
            return self._get_mock_resume_content()
    
    def generate_interview_questions(self, job_description: str, user_profile: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate interview questions using OpenAI
        
        Args:
            job_description: Job description text
            user_profile: User's profile information
            
        Returns:
            Dict containing categorized questions
        """
        if not self.enabled:
            return self._get_mock_interview_questions()
        
        try:
            prompt = self._build_interview_prompt(job_description, user_profile)
            
            response = self.client.chat.completions.create(
                model=self.models["interview_questions"],
                messages=[
                    {"role": "system", "content": "You are an expert interviewer who creates realistic, role-specific interview questions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.8
            )
            
            content = response.choices[0].message.content
            return self._parse_interview_response(content)
            
        except Exception as e:
            logger.error(f"OpenAI interview questions generation failed: {str(e)}")
            return self._get_mock_interview_questions()
    
    def enhance_resume_section(self, section_content: str, section_type: str, job_keywords: List[str]) -> str:
        """
        Enhance a specific resume section using OpenAI
        
        Args:
            section_content: Current section content
            section_type: Type of section (summary, experience, skills, etc.)
            job_keywords: Keywords from job description to incorporate
            
        Returns:
            Enhanced section content
        """
        if not self.enabled:
            return section_content
        
        try:
            prompt = f"""
            Enhance this {section_type} section for a resume to better match the job requirements.
            
            Current content:
            {section_content}
            
            Job keywords to incorporate: {', '.join(job_keywords)}
            
            Instructions:
            - Make it more compelling and ATS-friendly
            - Incorporate relevant keywords naturally
            - Use action verbs and quantify achievements where possible
            - Keep the same structure but improve the language
            
            Enhanced {section_type}:
            """
            
            response = self.client.chat.completions.create(
                model=self.models["resume_enhancement"],
                messages=[
                    {"role": "system", "content": "You are an expert resume writer focused on ATS optimization and compelling content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.6
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI section enhancement failed: {str(e)}")
            return section_content
    
    def calculate_job_match_score(self, resume_content: str, job_description: str) -> Dict[str, Any]:
        """
        Calculate how well a resume matches a job description using OpenAI
        
        Args:
            resume_content: Full resume content
            job_description: Job description text
            
        Returns:
            Dict with match score and recommendations
        """
        if not self.enabled:
            return self._get_mock_match_score()
        
        try:
            prompt = f"""
            Analyze how well this resume matches the job description and provide a detailed assessment.
            
            Resume:
            {resume_content}
            
            Job Description:
            {job_description}
            
            Please provide your analysis in JSON format with:
            {{
                "overall_score": <number 0-100>,
                "strengths": [<list of matching strengths>],
                "gaps": [<list of missing requirements>],
                "recommendations": [<list of improvement suggestions>],
                "keyword_matches": [<list of matched keywords>],
                "missing_keywords": [<list of important missing keywords>]
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.models["job_matching"],
                messages=[
                    {"role": "system", "content": "You are an expert ATS system and recruiter who analyzes resume-job matches."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"OpenAI job matching failed: {str(e)}")
            return self._get_mock_match_score()
    
    def _build_resume_prompt(self, user_profile: Dict[str, Any], job_description: str) -> str:
        """Build prompt for resume generation"""
        return f"""
        Create a professional, ATS-friendly resume tailored to this job description.
        
        User Profile:
        Name: {user_profile.get('name', 'User')}
        Email: {user_profile.get('email', '')}
        Skills: {', '.join(user_profile.get('skills', []))}
        
        Work Experience:
        {self._format_work_history(user_profile.get('work_history', []))}
        
        Education:
        {self._format_education(user_profile.get('education', []))}
        
        Target Job Description:
        {job_description}
        
        Please generate a resume with these sections in markdown format:
        ## Professional Summary
        ## Technical Skills  
        ## Professional Experience
        ## Education
        ## Additional Skills
        
        Focus on:
        - ATS optimization with relevant keywords
        - Quantified achievements
        - Action verbs
        - Tailored content for the specific role
        """
    
    def _build_interview_prompt(self, job_description: str, user_profile: Dict[str, Any]) -> str:
        """Build prompt for interview questions generation"""
        return f"""
        Generate realistic interview questions for this job position based on the candidate's background.
        
        Job Description:
        {job_description}
        
        Candidate Background:
        Skills: {', '.join(user_profile.get('skills', []))}
        Experience: {len(user_profile.get('work_history', []))} years
        
        Please generate questions in JSON format:
        {{
            "behavioral_questions": [
                {{"question": "...", "category": "behavioral", "difficulty": "medium"}},
                ...
            ],
            "technical_questions": [
                {{"question": "...", "category": "technical", "difficulty": "hard"}},
                ...
            ],
            "company_questions": [
                {{"question": "...", "category": "company", "difficulty": "easy"}},
                ...
            ]
        }}
        
        Generate 5 questions for each category.
        """
    
    def _format_work_history(self, work_history: List[Dict]) -> str:
        """Format work history for prompt"""
        if not work_history:
            return "No work experience provided"
        
        formatted = []
        for job in work_history:
            formatted.append(f"- {job.get('position')} at {job.get('company')} ({job.get('start_date')} - {job.get('end_date')}): {job.get('description', '')}")
        return '\n'.join(formatted)
    
    def _format_education(self, education: List[Dict]) -> str:
        """Format education for prompt"""
        if not education:
            return "No education provided"
        
        formatted = []
        for edu in education:
            formatted.append(f"- {edu.get('degree')} in {edu.get('major')} from {edu.get('university')} ({edu.get('year')})")
        return '\n'.join(formatted)
    
    def _parse_resume_response(self, content: str) -> Dict[str, str]:
        """Parse OpenAI resume response"""
        sections = {}
        current_section = None
        current_content = []
        
        for line in content.split('\n'):
            if line.startswith('## '):
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line[3:].strip().lower().replace(' ', '_')
                current_content = []
            else:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _parse_interview_response(self, content: str) -> Dict[str, List[Dict[str, Any]]]:
        """Parse OpenAI interview response"""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return self._get_mock_interview_questions()
    
    def _get_mock_resume_content(self) -> Dict[str, str]:
        """Mock resume content when OpenAI is not available"""
        return {
            "professional_summary": "Experienced software developer with strong technical skills and proven track record of delivering high-quality solutions.",
            "technical_skills": "Python, JavaScript, React, Node.js, SQL, Git, Agile methodologies",
            "professional_experience": "Software Developer | Tech Company | 2020-2023\n• Developed and maintained web applications\n• Collaborated with cross-functional teams\n• Improved system performance by 30%",
            "education": "Bachelor of Science in Computer Science | University | 2019",
            "additional_skills": "Problem-solving, Team collaboration, Communication, Project management"
        }
    
    def _get_mock_interview_questions(self) -> Dict[str, List[Dict[str, Any]]]:
        """Mock interview questions when OpenAI is not available"""
        return {
            "behavioral_questions": [
                {"question": "Tell me about a challenging project you worked on.", "category": "behavioral", "difficulty": "medium"},
                {"question": "How do you handle tight deadlines?", "category": "behavioral", "difficulty": "medium"},
                {"question": "Describe a time you had to work with a difficult team member.", "category": "behavioral", "difficulty": "hard"},
                {"question": "What motivates you in your work?", "category": "behavioral", "difficulty": "easy"},
                {"question": "How do you stay updated with new technologies?", "category": "behavioral", "difficulty": "medium"}
            ],
            "technical_questions": [
                {"question": "Explain the difference between SQL and NoSQL databases.", "category": "technical", "difficulty": "medium"},
                {"question": "How would you optimize a slow-running query?", "category": "technical", "difficulty": "hard"},
                {"question": "What is the difference between REST and GraphQL?", "category": "technical", "difficulty": "medium"},
                {"question": "Explain the concept of microservices.", "category": "technical", "difficulty": "hard"},
                {"question": "How do you ensure code quality?", "category": "technical", "difficulty": "medium"}
            ],
            "company_questions": [
                {"question": "Why do you want to work at our company?", "category": "company", "difficulty": "easy"},
                {"question": "What do you know about our products?", "category": "company", "difficulty": "medium"},
                {"question": "How do you see yourself contributing to our team?", "category": "company", "difficulty": "medium"},
                {"question": "What are your salary expectations?", "category": "company", "difficulty": "hard"},
                {"question": "Do you have any questions for us?", "category": "company", "difficulty": "easy"}
            ]
        }
    
    def _get_mock_match_score(self) -> Dict[str, Any]:
        """Mock job match score when OpenAI is not available"""
        return {
            "overall_score": 75,
            "strengths": ["Strong technical skills", "Relevant experience", "Good communication"],
            "gaps": ["Missing cloud experience", "Limited leadership experience"],
            "recommendations": ["Add cloud certifications", "Highlight project leadership"],
            "keyword_matches": ["Python", "JavaScript", "Agile", "Team collaboration"],
            "missing_keywords": ["AWS", "Docker", "Kubernetes", "CI/CD"]
        }
"""
Multi-Provider AI Service
Supports OpenAI, Anthropic Claude, Google Gemini, and other AI providers
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime

logger = logging.getLogger(__name__)

class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    @abstractmethod
    def __init__(self, api_key: str, **kwargs):
        pass
    
    @abstractmethod
    def generate_completion(self, messages: List[Dict], model: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        pass

class OpenAIProvider(AIProvider):
    """OpenAI provider implementation"""
    
    def __init__(self, api_key: str, **kwargs):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
            self.available = True
            logger.info("OpenAI provider initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI provider: {e}")
            self.available = False
            self.client = None
    
    def generate_completion(self, messages: List[Dict], model: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        if not self.available:
            raise Exception("OpenAI provider not available")
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content
    
    def is_available(self) -> bool:
        return self.available

class AnthropicProvider(AIProvider):
    """Anthropic Claude provider implementation"""
    
    def __init__(self, api_key: str, **kwargs):
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
            self.available = True
            logger.info("Anthropic provider initialized successfully")
        except ImportError:
            logger.warning("Anthropic library not installed. Install with: pip install anthropic")
            self.available = False
            self.client = None
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic provider: {e}")
            self.available = False
            self.client = None
    
    def generate_completion(self, messages: List[Dict], model: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        if not self.available:
            raise Exception("Anthropic provider not available")
        
        # Convert messages format for Anthropic
        system_message = ""
        user_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                user_messages.append(msg)
        
        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_message,
            messages=user_messages
        )
        return response.content[0].text
    
    def is_available(self) -> bool:
        return self.available

class GoogleProvider(AIProvider):
    """Google Gemini provider implementation"""
    
    def __init__(self, api_key: str, **kwargs):
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.genai = genai
            self.available = True
            logger.info("Google Gemini provider initialized successfully")
        except ImportError:
            logger.warning("Google Generative AI library not installed. Install with: pip install google-generativeai")
            self.available = False
            self.genai = None
        except Exception as e:
            logger.error(f"Failed to initialize Google provider: {e}")
            self.available = False
            self.genai = None
    
    def generate_completion(self, messages: List[Dict], model: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        if not self.available:
            raise Exception("Google provider not available")
        
        # Convert messages to Google format
        prompt = ""
        for msg in messages:
            if msg["role"] == "system":
                prompt += f"System: {msg['content']}\n\n"
            elif msg["role"] == "user":
                prompt += f"User: {msg['content']}\n\n"
        
        model_instance = self.genai.GenerativeModel(model)
        response = model_instance.generate_content(
            prompt,
            generation_config=self.genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature
            )
        )
        return response.text
    
    def is_available(self) -> bool:
        return self.available

class OllamaProvider(AIProvider):
    """Ollama local AI provider implementation"""
    
    def __init__(self, api_key: str = None, base_url: str = "http://localhost:11434", **kwargs):
        try:
            import requests
            self.base_url = base_url
            self.session = requests.Session()
            # Test connection
            response = self.session.get(f"{self.base_url}/api/tags")
            self.available = response.status_code == 200
            logger.info("Ollama provider initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama provider: {e}")
            self.available = False
            self.session = None
    
    def generate_completion(self, messages: List[Dict], model: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        if not self.available:
            raise Exception("Ollama provider not available")
        
        # Convert messages to prompt
        prompt = ""
        for msg in messages:
            if msg["role"] == "system":
                prompt += f"System: {msg['content']}\n\n"
            elif msg["role"] == "user":
                prompt += f"User: {msg['content']}\n\n"
        
        data = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        response = self.session.post(f"{self.base_url}/api/generate", json=data)
        response.raise_for_status()
        return response.json()["response"]
    
    def is_available(self) -> bool:
        return self.available

class MultiProviderAIService:
    """Multi-provider AI service that can work with any AI model"""
    
    def __init__(self):
        # Load configuration from environment
        self.config = self._load_config()
        self.provider = None
        self._initialize_provider()
        
        # Default models for each provider
        self.default_models = {
            "openai": {
                "resume_generation": "gpt-3.5-turbo",
                "interview_questions": "gpt-3.5-turbo",
                "resume_enhancement": "gpt-3.5-turbo",
                "job_matching": "gpt-3.5-turbo"
            },
            "anthropic": {
                "resume_generation": "claude-3-haiku-20240307",
                "interview_questions": "claude-3-haiku-20240307",
                "resume_enhancement": "claude-3-haiku-20240307",
                "job_matching": "claude-3-haiku-20240307"
            },
            "google": {
                "resume_generation": "gemini-1.5-flash",
                "interview_questions": "gemini-1.5-flash",
                "resume_enhancement": "gemini-1.5-flash",
                "job_matching": "gemini-1.5-flash"
            },
            "ollama": {
                "resume_generation": "llama3.1",
                "interview_questions": "llama3.1",
                "resume_enhancement": "llama3.1",
                "job_matching": "llama3.1"
            }
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """Load AI provider configuration from environment variables"""
        return {
            "provider": os.getenv("AI_PROVIDER", "openai").lower(),
            "api_key": os.getenv("AI_API_KEY") or os.getenv("OPENAI_API_KEY"),  # Fallback to OpenAI key
            "base_url": os.getenv("AI_BASE_URL", "http://localhost:11434"),  # For Ollama
            "custom_models": {
                "resume_generation": os.getenv("AI_MODEL_RESUME"),
                "interview_questions": os.getenv("AI_MODEL_INTERVIEW"),
                "resume_enhancement": os.getenv("AI_MODEL_ENHANCE"),
                "job_matching": os.getenv("AI_MODEL_MATCHING")
            }
        }
    
    def _initialize_provider(self):
        """Initialize the selected AI provider"""
        provider_name = self.config["provider"]
        api_key = self.config["api_key"]
        
        if not api_key and provider_name != "ollama":
            logger.warning(f"No API key found for {provider_name}. AI features will be disabled.")
            self.enabled = False
            return
        
        try:
            if provider_name == "openai":
                self.provider = OpenAIProvider(api_key)
            elif provider_name == "anthropic":
                self.provider = AnthropicProvider(api_key)
            elif provider_name == "google":
                self.provider = GoogleProvider(api_key)
            elif provider_name == "ollama":
                self.provider = OllamaProvider(base_url=self.config["base_url"])
            else:
                logger.error(f"Unknown AI provider: {provider_name}")
                self.enabled = False
                return
            
            self.enabled = self.provider.is_available()
            if self.enabled:
                logger.info(f"AI service initialized with {provider_name} provider")
            else:
                logger.warning(f"AI provider {provider_name} is not available")
                
        except Exception as e:
            logger.error(f"Failed to initialize AI provider {provider_name}: {e}")
            self.enabled = False
    
    def get_model(self, task: str) -> str:
        """Get the model name for a specific task"""
        provider_name = self.config["provider"]
        
        # Check for custom model override
        custom_model = self.config["custom_models"].get(task)
        if custom_model:
            return custom_model
        
        # Use default model for provider
        return self.default_models.get(provider_name, {}).get(task, "gpt-3.5-turbo")
    
    def generate_resume_content(self, user_profile: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        """Generate tailored resume content using the configured AI provider"""
        if not self.enabled:
            return self._get_mock_resume_content()
        
        try:
            prompt = self._build_resume_prompt(user_profile, job_description)
            model = self.get_model("resume_generation")
            
            messages = [
                {"role": "system", "content": "You are an expert resume writer who creates compelling, ATS-friendly resumes tailored to specific job descriptions."},
                {"role": "user", "content": prompt}
            ]
            
            content = self.provider.generate_completion(
                messages=messages,
                model=model,
                max_tokens=2000,
                temperature=0.7
            )
            
            return self._parse_resume_response(content)
            
        except Exception as e:
            logger.error(f"AI resume generation failed: {str(e)}")
            return self._get_mock_resume_content()
    
    def generate_interview_questions(self, job_description: str, user_profile: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Generate interview questions using the configured AI provider"""
        if not self.enabled:
            return self._get_mock_interview_questions()
        
        try:
            prompt = self._build_interview_prompt(job_description, user_profile)
            model = self.get_model("interview_questions")
            
            messages = [
                {"role": "system", "content": "You are an expert interviewer who creates realistic, role-specific interview questions."},
                {"role": "user", "content": prompt}
            ]
            
            content = self.provider.generate_completion(
                messages=messages,
                model=model,
                max_tokens=1500,
                temperature=0.8
            )
            
            return self._parse_interview_response(content)
            
        except Exception as e:
            logger.error(f"AI interview questions generation failed: {str(e)}")
            return self._get_mock_interview_questions()
    
    def enhance_resume_section(self, section_content: str, section_type: str, job_description: str) -> str:
        """Enhance a specific resume section using the configured AI provider"""
        if not self.enabled:
            return section_content
        
        try:
            model = self.get_model("resume_enhancement")
            
            prompt = f"""
            Please enhance this {section_type} section for a resume. The target job is: {job_description[:200]}...
            
            Current {section_type}:
            {section_content}
            
            Please improve it by:
            - Making it more relevant to the target job
            - Using stronger action words and metrics
            - Optimizing for ATS systems
            - Keeping the same structure but enhancing the language
            
            Enhanced {section_type}:
            """
            
            messages = [
                {"role": "system", "content": "You are an expert resume writer focused on ATS optimization and compelling content."},
                {"role": "user", "content": prompt}
            ]
            
            return self.provider.generate_completion(
                messages=messages,
                model=model,
                max_tokens=800,
                temperature=0.6
            ).strip()
            
        except Exception as e:
            logger.error(f"AI section enhancement failed: {str(e)}")
            return section_content
    
    def analyze_job_match(self, resume_content: str, job_description: str) -> Dict[str, Any]:
        """Analyze job match using the configured AI provider"""
        if not self.enabled:
            return self._get_mock_job_match()
        
        try:
            model = self.get_model("job_matching")
            
            prompt = f"""
            Analyze how well this resume matches the job description. Provide a detailed analysis in JSON format.
            
            Job Description:
            {job_description}
            
            Resume:
            {resume_content}
            
            Please provide analysis in this exact JSON format:
            {{
                "overall_score": <score 0-100>,
                "strengths": ["strength1", "strength2", "strength3"],
                "gaps": ["gap1", "gap2"],
                "recommendations": ["rec1", "rec2", "rec3"],
                "keyword_matches": ["keyword1", "keyword2"],
                "missing_keywords": ["missing1", "missing2"]
            }}
            """
            
            messages = [
                {"role": "system", "content": "You are an expert ATS system and recruiter who analyzes resume-job matches."},
                {"role": "user", "content": prompt}
            ]
            
            content = self.provider.generate_completion(
                messages=messages,
                model=model,
                max_tokens=1000,
                temperature=0.3
            )
            
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"AI job matching failed: {str(e)}")
            return self._get_mock_job_match()
    
    # Helper methods (same as before but moved here)
    def _build_resume_prompt(self, user_profile: Dict[str, Any], job_description: str) -> str:
        """Build resume generation prompt"""
        return f"""
        Create a professional resume tailored to this job description:
        
        Job Description:
        {job_description}
        
        User Profile:
        Name: {user_profile.get('name', 'N/A')}
        Email: {user_profile.get('email', 'N/A')}
        Skills: {', '.join(user_profile.get('skills', []))}
        
        Work Experience:
        {self._format_work_history(user_profile.get('work_history', []))}
        
        Education:
        {self._format_education(user_profile.get('education', []))}
        
        Please create a resume with these sections:
        - Professional Summary (3-4 sentences highlighting relevant experience)
        - Technical Skills (relevant to the job)
        - Professional Experience (enhanced descriptions with metrics)
        - Education
        - Additional Skills (soft skills and certifications)
        
        Make it ATS-friendly and tailored to the job requirements.
        """
    
    def _build_interview_prompt(self, job_description: str, user_profile: Dict[str, Any]) -> str:
        """Build interview questions prompt"""
        return f"""
        Generate interview questions for this position:
        
        Job Description:
        {job_description}
        
        Candidate Background:
        Skills: {', '.join(user_profile.get('skills', []))}
        Experience: {len(user_profile.get('work_history', []))} positions
        
        Create 15 questions total:
        - 5 behavioral questions
        - 5 technical questions specific to the role
        - 5 company/role-specific questions
        
        Format as JSON with categories.
        """
    
    def _format_work_history(self, work_history: List[Dict]) -> str:
        """Format work history for prompt"""
        if not work_history:
            return "No work experience provided"
        
        formatted = []
        for job in work_history:
            formatted.append(f"• {job.get('position', 'N/A')} at {job.get('company', 'N/A')} ({job.get('start_date', 'N/A')} - {job.get('end_date', 'Present')})")
            formatted.append(f"  {job.get('description', 'No description')}")
        
        return "\n".join(formatted)
    
    def _format_education(self, education: List[Dict]) -> str:
        """Format education for prompt"""
        if not education:
            return "No education provided"
        
        formatted = []
        for edu in education:
            formatted.append(f"• {edu.get('degree', 'N/A')} in {edu.get('major', 'N/A')} from {edu.get('university', 'N/A')} ({edu.get('year', 'N/A')})")
        
        return "\n".join(formatted)
    
    def _parse_resume_response(self, content: str) -> Dict[str, Any]:
        """Parse AI response into resume sections"""
        # Simple parsing - you can enhance this
        sections = {
            "professional_summary": "Experienced professional with strong skills and proven track record.",
            "technical_skills": "Various technical skills relevant to the position.",
            "professional_experience": "Professional experience with demonstrated achievements.",
            "education": "Educational background and qualifications.",
            "additional_skills": "Additional skills and competencies.",
            "match_score": self._get_mock_job_match()
        }
        
        # Try to extract sections from content
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['summary', 'professional summary']):
                current_section = 'professional_summary'
                sections[current_section] = ""
            elif any(keyword in line.lower() for keyword in ['technical skills', 'skills']):
                current_section = 'technical_skills'
                sections[current_section] = ""
            elif any(keyword in line.lower() for keyword in ['experience', 'professional experience']):
                current_section = 'professional_experience'
                sections[current_section] = ""
            elif any(keyword in line.lower() for keyword in ['education']):
                current_section = 'education'
                sections[current_section] = ""
            elif current_section and line:
                sections[current_section] += line + "\n"
        
        return sections
    
    def _parse_interview_response(self, content: str) -> Dict[str, List[Dict[str, Any]]]:
        """Parse interview questions from AI response"""
        try:
            return json.loads(content)
        except:
            return self._get_mock_interview_questions()
    
    def _get_mock_resume_content(self) -> Dict[str, Any]:
        """Fallback mock resume content"""
        return {
            "professional_summary": "Experienced software developer with strong technical skills and proven track record of delivering high-quality solutions.",
            "technical_skills": "Python, JavaScript, React, Node.js, SQL, Git, Agile methodologies",
            "professional_experience": "Software Developer | Tech Company | 2020-2023\n• Developed and maintained web applications\n• Collaborated with cross-functional teams\n• Improved system performance by 30%",
            "education": "Bachelor of Science in Computer Science | University | 2019",
            "additional_skills": "Problem-solving, Team collaboration, Communication, Project management",
            "match_score": self._get_mock_job_match()
        }
    
    def _get_mock_interview_questions(self) -> Dict[str, List[Dict[str, Any]]]:
        """Fallback mock interview questions"""
        return {
            "behavioral_questions": [
                {"question": "Tell me about a challenging project you worked on.", "answer": "Use the STAR method to describe a specific project where you overcame significant technical challenges.", "category": "behavioral"},
                {"question": "How do you handle tight deadlines?", "answer": "Describe your time management and prioritization strategies with specific examples.", "category": "behavioral"},
                {"question": "Describe a time you had to learn something new quickly.", "answer": "Share an example of rapidly acquiring new skills or technologies for a project.", "category": "behavioral"},
                {"question": "How do you handle conflicts with team members?", "answer": "Explain your approach to resolving disagreements professionally and constructively.", "category": "behavioral"},
                {"question": "Tell me about a mistake you made and how you handled it.", "answer": "Show accountability and learning from errors with a specific example.", "category": "behavioral"}
            ],
            "technical_questions": [
                {"question": "Explain your experience with the technologies mentioned in the job description.", "answer": "Detail your hands-on experience with relevant technologies and specific projects.", "category": "technical"},
                {"question": "How do you approach debugging complex issues?", "answer": "Describe your systematic methodology for identifying and resolving technical problems.", "category": "technical"},
                {"question": "What's your experience with version control systems?", "answer": "Explain your proficiency with Git, branching strategies, and collaborative workflows.", "category": "technical"},
                {"question": "How do you ensure code quality in your projects?", "answer": "Discuss your approach to code reviews, testing, and maintaining clean code standards.", "category": "technical"},
                {"question": "Describe your testing methodology.", "answer": "Explain your experience with unit testing, integration testing, and test-driven development.", "category": "technical"}
            ],
            "company_questions": [
                {"question": "Why are you interested in this position?", "answer": "Connect your career goals and interests to the specific role and company mission.", "category": "company"},
                {"question": "What do you know about our company?", "answer": "Demonstrate research about the company's products, values, and recent developments.", "category": "company"},
                {"question": "How do you see yourself contributing to our team?", "answer": "Highlight specific skills and experiences that align with the team's needs.", "category": "company"},
                {"question": "What motivates you in your work?", "answer": "Share what drives your passion for technology and professional growth.", "category": "company"},
                {"question": "Where do you see yourself in 5 years?", "answer": "Describe your career aspirations and how they align with the company's growth.", "category": "company"}
            ]
        }
    
    def _get_mock_job_match(self) -> Dict[str, Any]:
        """Fallback mock job match analysis"""
        return {
            "overall_score": 75,
            "strengths": ["Strong technical skills", "Relevant experience", "Good communication"],
            "gaps": ["Missing cloud experience", "Limited leadership experience"],
            "recommendations": ["Add cloud certifications", "Highlight project leadership"],
            "keyword_matches": ["Python", "JavaScript", "Agile", "Team collaboration"],
            "missing_keywords": ["AWS", "Docker", "Kubernetes", "CI/CD"]
        }
    
    def calculate_job_match_score(self, resume_content: str, job_description: str) -> Dict[str, Any]:
        """Calculate job match score - alias for analyze_job_match for backward compatibility"""
        return self.analyze_job_match(resume_content, job_description)

# Create an alias for backward compatibility
MultiAIService = MultiProviderAIService
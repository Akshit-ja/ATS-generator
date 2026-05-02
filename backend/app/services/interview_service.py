from typing import List, Dict, Any
from sqlalchemy.orm import Session
from ..models import User
from .token_tracker import TokenTracker, EndpointType
from .multi_ai_service import MultiAIService
import json

class InterviewService:
    """Service for generating interview questions and answers based on job descriptions and user profiles."""
    
    def __init__(self, db: Session):
        self.db = db
        self.token_tracker = TokenTracker(db)
        self.ai_service = MultiAIService()
    
    def generate_interview_questions(self, user_id: int, job_description: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate interview questions based on job description and user profile.
        
        Args:
            user_id: The ID of the user
            job_description: The job description text
            user_profile: Dictionary containing user's work history and skills
            
        Returns:
            Dictionary containing categorized questions and answers
        """
        # Use AI service for real AI-powered question generation
        questions = self.ai_service.generate_interview_questions(job_description, user_profile)
        questions_with_answers = []  # Initialize for token tracking
        
        # Fallback to mock questions if OpenAI fails
        if not questions or not any(questions.values()):
            # Extract key requirements from job description
            technical_skills = self._extract_technical_skills(job_description)
            company_values = self._extract_company_values(job_description)
            
            # Generate questions based on extracted information
            behavioral_questions = self._generate_behavioral_questions(job_description, user_profile)
            technical_questions = self._generate_technical_questions(technical_skills, user_profile)
            company_questions = self._generate_company_questions(company_values)
            
            # Generate STAR method answers based on user's work history
            questions_with_answers = self._generate_answers(
                behavioral_questions + technical_questions + company_questions,
                user_profile
            )
            
            questions = {
                "behavioral_questions": [q for q in questions_with_answers if q["category"] == "behavioral"],
                "technical_questions": [q for q in questions_with_answers if q["category"] == "technical"],
                "company_questions": [q for q in questions_with_answers if q["category"] == "company"],
            }
        else:
            # Convert OpenAI questions to the format expected for token tracking
            all_questions = (questions.get("behavioral_questions", []) + 
                           questions.get("technical_questions", []) + 
                           questions.get("company_questions", []))
            questions_with_answers = all_questions
        
        # Mock token usage tracking
        mock_response = {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": 1677858242,
            "model": "gpt-3.5-turbo-0613",
            "usage": {
                "prompt_tokens": 1200,
                "completion_tokens": 600,
                "total_tokens": 1800
            },
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": json.dumps(questions_with_answers)
                    },
                    "finish_reason": "stop",
                    "index": 0
                }
            ]
        }
        
        # Track token usage
        self.token_tracker.track_usage_from_response(
            user_id=user_id,
            endpoint_type=EndpointType.INTERVIEW_QUESTIONS,
            response=mock_response
        )
        
        return {
            "behavioral_questions": [q for q in questions_with_answers if q["category"] == "behavioral"],
            "technical_questions": [q for q in questions_with_answers if q["category"] == "technical"],
            "company_questions": [q for q in questions_with_answers if q["category"] == "company"],
        }
    
    def _extract_technical_skills(self, job_description: str) -> List[str]:
        """Extract technical skills from job description."""
        # In a real implementation, this would use NLP or LLM
        # For now, return mock data
        return [
            "Python", "FastAPI", "React", "SQL", "Docker",
            "CI/CD", "AWS", "Agile methodology"
        ]
    
    def _extract_company_values(self, job_description: str) -> List[str]:
        """Extract company values from job description."""
        # In a real implementation, this would use NLP or LLM
        # For now, return mock data
        return [
            "Innovation", "Teamwork", "Customer focus",
            "Continuous learning", "Work-life balance"
        ]
    
    def _generate_behavioral_questions(self, job_description: str, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate behavioral interview questions."""
        # In a real implementation, this would use LLM
        # For now, return mock data
        return [
            {
                "question": "Tell me about a time when you had to meet a tight deadline.",
                "category": "behavioral",
                "importance": "high"
            },
            {
                "question": "Describe a situation where you had to work with a difficult team member.",
                "category": "behavioral",
                "importance": "medium"
            },
            {
                "question": "Give an example of a time when you showed leadership skills.",
                "category": "behavioral",
                "importance": "high"
            },
            {
                "question": "Tell me about a time when you failed and what you learned from it.",
                "category": "behavioral",
                "importance": "medium"
            },
            {
                "question": "Describe a situation where you had to make a difficult decision with limited information.",
                "category": "behavioral",
                "importance": "high"
            }
        ]
    
    def _generate_technical_questions(self, technical_skills: List[str], user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate technical interview questions based on required skills."""
        # In a real implementation, this would use LLM
        # For now, return mock data
        return [
            {
                "question": "Explain how you would design a RESTful API for a resume generation service.",
                "category": "technical",
                "importance": "high"
            },
            {
                "question": "How would you optimize database queries for large datasets?",
                "category": "technical",
                "importance": "medium"
            },
            {
                "question": "Describe your experience with containerization and Docker.",
                "category": "technical",
                "importance": "high"
            },
            {
                "question": "How do you approach testing in your development workflow?",
                "category": "technical",
                "importance": "medium"
            },
            {
                "question": "Explain your experience with CI/CD pipelines.",
                "category": "technical",
                "importance": "medium"
            }
        ]
    
    def _generate_company_questions(self, company_values: List[str]) -> List[Dict[str, Any]]:
        """Generate company-specific interview questions."""
        # In a real implementation, this would use LLM
        # For now, return mock data
        return [
            {
                "question": "What interests you about working at our company?",
                "category": "company",
                "importance": "high"
            },
            {
                "question": "How do your values align with our company's mission?",
                "category": "company",
                "importance": "medium"
            },
            {
                "question": "Where do you see yourself in 5 years?",
                "category": "company",
                "importance": "medium"
            },
            {
                "question": "What do you know about our company's products/services?",
                "category": "company",
                "importance": "high"
            },
            {
                "question": "Why are you leaving your current position?",
                "category": "company",
                "importance": "medium"
            }
        ]
    
    def _generate_answers(self, questions: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate STAR method answers for each question based on user's work history."""
        # In a real implementation, this would use LLM
        # For now, add mock answers to the questions
        
        for question in questions:
            if question["category"] == "behavioral":
                question["answer"] = self._generate_star_answer(question["question"], user_profile)
            elif question["category"] == "technical":
                question["answer"] = self._generate_technical_answer(question["question"], user_profile)
            else:  # company
                question["answer"] = self._generate_company_answer(question["question"], user_profile)
        
        return questions
    
    def _generate_star_answer(self, question: str, user_profile: Dict[str, Any]) -> Dict[str, str]:
        """Generate a STAR method answer for a behavioral question."""
        # In a real implementation, this would use LLM to generate personalized answers
        # For now, return a structured mock answer
        
        return {
            "situation": "At my previous company, we had a critical client project that was falling behind schedule due to unexpected technical challenges.",
            "task": "As the lead developer, I was responsible for ensuring we delivered the project on time without compromising quality.",
            "action": "I reorganized the team's priorities, implemented daily stand-ups focused specifically on blockers, and personally took on the most challenging technical issues.",
            "result": "We delivered the project two days ahead of the revised deadline, and the client was so impressed with our work that they increased their contract value by 30% for the next phase.",
            "full_answer": "At my previous company, we had a critical client project that was falling behind schedule due to unexpected technical challenges. As the lead developer, I was responsible for ensuring we delivered the project on time without compromising quality. I reorganized the team's priorities, implemented daily stand-ups focused specifically on blockers, and personally took on the most challenging technical issues. We delivered the project two days ahead of the revised deadline, and the client was so impressed with our work that they increased their contract value by 30% for the next phase."
        }
    
    def _generate_technical_answer(self, question: str, user_profile: Dict[str, Any]) -> Dict[str, str]:
        """Generate an answer for a technical question."""
        # In a real implementation, this would use LLM
        # For now, return a mock answer
        
        return {
            "key_points": [
                "Designed microservices architecture for scalability",
                "Implemented RESTful API with FastAPI",
                "Used PostgreSQL for data persistence",
                "Added Redis for caching to improve performance",
                "Implemented comprehensive test suite with pytest"
            ],
            "full_answer": "I would approach designing a RESTful API for a resume generation service by first identifying the core resources: users, resumes, jobs, and analytics. I'd implement a microservices architecture to ensure scalability, with FastAPI for the backend due to its performance and type checking. For data persistence, I'd use PostgreSQL with SQLAlchemy ORM, and add Redis for caching frequently accessed data. The API would follow REST principles with proper status codes, authentication using JWT, and comprehensive documentation with OpenAPI. I'd ensure the design includes rate limiting, proper error handling, and a comprehensive test suite using pytest."
        }
    
    def _generate_company_answer(self, question: str, user_profile: Dict[str, Any]) -> Dict[str, str]:
        """Generate an answer for a company-specific question."""
        # In a real implementation, this would use LLM
        # For now, return a mock answer
        
        return {
            "key_points": [
                "Researched company's innovative AI products",
                "Aligned with company's mission to democratize AI tools",
                "Excited about company's growth trajectory",
                "Impressed by company culture and work-life balance",
                "See opportunity to contribute to cutting-edge technology"
            ],
            "full_answer": "I'm particularly interested in working at your company because of your innovative approach to AI-powered resume tools. I've been following your growth for the past year and am impressed by how you're democratizing access to career advancement tools. Your mission to help job seekers compete effectively in a challenging market aligns perfectly with my personal values. Additionally, I'm excited about the opportunity to work with cutting-edge AI technology in a practical application that genuinely helps people. From my research and conversations with current employees, I also appreciate your company culture that emphasizes work-life balance while still pushing technical boundaries."
        }
import re
from collections import Counter
from typing import Dict, List, Set
import logging
from sqlalchemy.orm import Session
# from ..db.models import EndpointType  # Commented out for now
from .token_tracker import TokenTracker

logger = logging.getLogger(__name__)

class JobAnalyzer:
    """Service for analyzing job descriptions and extracting key information"""
    
    def __init__(self, db: Session = None):
        # Simplified version without spaCy
        self.nlp = None
            
        self.db = db
        self.token_tracker = TokenTracker(db) if db else None
        
        # Define categories for classification
        self.categories = {
            "skills": set([
                "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "php", "swift", "kotlin",
                "react", "angular", "vue", "node", "express", "django", "flask", "spring", "asp.net",
                "sql", "nosql", "mongodb", "postgresql", "mysql", "oracle", "firebase", "dynamodb",
                "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins", "git", "github",
                "machine learning", "deep learning", "nlp", "computer vision", "data science", "ai"
            ]),
            "tools": set([
                "jira", "confluence", "slack", "teams", "github", "gitlab", "bitbucket", "jenkins", "travis",
                "circleci", "docker", "kubernetes", "terraform", "ansible", "puppet", "chef", "prometheus",
                "grafana", "datadog", "splunk", "elasticsearch", "kibana", "logstash", "kafka", "rabbitmq",
                "redis", "memcached", "nginx", "apache", "iis", "tomcat", "webpack", "babel", "npm", "yarn",
                "gradle", "maven", "sbt", "make", "cmake", "visual studio", "intellij", "eclipse", "vscode"
            ]),
            "methodologies": set([
                "agile", "scrum", "kanban", "waterfall", "lean", "xp", "tdd", "bdd", "ci/cd", "devops",
                "sre", "microservices", "serverless", "rest", "graphql", "soap", "mvc", "mvvm", "clean code",
                "solid", "design patterns", "object-oriented", "functional programming", "reactive programming"
            ]),
            "soft_skills": set([
                "communication", "teamwork", "leadership", "problem solving", "critical thinking",
                "creativity", "adaptability", "time management", "organization", "collaboration",
                "presentation", "negotiation", "conflict resolution", "mentoring", "coaching"
            ])
        }
        
        # Experience level indicators
        self.experience_levels = {
            "entry": ["entry level", "junior", "0-1 year", "0-2 years", "graduate", "recent graduate", "intern"],
            "mid": ["mid level", "intermediate", "2-5 years", "3-5 years", "experienced"],
            "senior": ["senior", "lead", "5+ years", "7+ years", "10+ years", "principal", "architect", "manager"]
        }
    
    def analyze_job_description(self, job_description: str) -> Dict:
        """
        Analyze job description and extract key information
        
        Args:
            job_description: The job description text
            
        Returns:
            Dictionary with categorized keywords and experience level
        """
        try:
            # Clean and normalize text
            cleaned_text = self._clean_text(job_description)
            
            # Extract keywords using spaCy and TF-IDF
            keywords = self._extract_keywords(cleaned_text)
            
            # Categorize keywords
            categorized_keywords = self._categorize_keywords(keywords)
            
            # Determine experience level
            experience_level = self._determine_experience_level(cleaned_text)
            
            return {
                "skills": categorized_keywords.get("skills", [])[:10],
                "tools": categorized_keywords.get("tools", [])[:10],
                "methodologies": categorized_keywords.get("methodologies", [])[:10],
                "soft_skills": categorized_keywords.get("soft_skills", [])[:10],
                "experience_level": experience_level
            }
        except Exception as e:
            logger.error(f"Error analyzing job description: {str(e)}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and extra whitespace
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords using simple word analysis"""
        # Split into words and filter
        words = text.split()
        
        # Filter words (remove common stop words and short words)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        
        filtered_words = []
        for word in words:
            word_clean = re.sub(r'[^\w]', '', word.lower())
            if len(word_clean) > 2 and word_clean not in stop_words:
                filtered_words.append(word_clean)
        
        # Count frequency
        counter = Counter(filtered_words)
        
        # Return most common keywords
        return [item[0] for item in counter.most_common(50)]
    
    def _categorize_keywords(self, keywords: List[str]) -> Dict[str, List[str]]:
        """Categorize keywords into predefined categories"""
        result = {category: [] for category in self.categories.keys()}
        
        for keyword in keywords:
            categorized = False
            for category, terms in self.categories.items():
                for term in terms:
                    if term in keyword or keyword in term:
                        if keyword not in result[category]:
                            result[category].append(keyword)
                            categorized = True
                            break
                if categorized:
                    break
        
        return result
    
    def _determine_experience_level(self, text: str) -> str:
        """Determine required experience level from text"""
        # Count occurrences of experience level indicators
        level_counts = {level: 0 for level in self.experience_levels.keys()}
        
        for level, indicators in self.experience_levels.items():
            for indicator in indicators:
                if indicator in text:
                    level_counts[level] += 1
        
        # Return the level with the most indicators
        if sum(level_counts.values()) == 0:
            return "not specified"
        
        return max(level_counts.items(), key=lambda x: x[1])[0]
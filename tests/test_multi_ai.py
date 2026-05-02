#!/usr/bin/env python3
"""
Quick test to verify the multi-provider AI service is working correctly
"""
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.multi_ai_service import MultiAIService

def test_multi_ai_service():
    """Test the multi-provider AI service"""
    print("🚀 Testing Multi-Provider AI Service")
    print("=" * 50)
    
    # Initialize the service
    ai_service = MultiAIService()
    
    print(f"✅ Service initialized successfully")
    print(f"📊 Current Provider: {ai_service.current_provider}")
    print(f"🔧 Service Enabled: {ai_service.enabled}")
    
    # Test resume generation
    print("\n🎯 Testing Resume Generation...")
    user_profile = {
        "name": "John Doe",
        "skills": ["Python", "FastAPI", "React"],
        "experience": ["Software Engineer at TechCorp for 3 years"],
        "education": ["BS Computer Science"]
    }
    
    job_description = "Software Engineer position requiring Python, web development, and problem-solving skills."
    
    try:
        resume_sections = ai_service.generate_resume_content(user_profile, job_description)
        print("✅ Resume generation successful!")
        print(f"📝 Generated sections: {list(resume_sections.keys())}")
        
        # Show a sample section (first 100 characters)
        if resume_sections:
            first_section = list(resume_sections.keys())[0]
            content = resume_sections[first_section][:100] + "..." if len(resume_sections[first_section]) > 100 else resume_sections[first_section]
            print(f"📄 Sample ({first_section}): {content}")
        
    except Exception as e:
        print(f"❌ Resume generation failed: {e}")
    
    # Test interview questions
    print("\n🎤 Testing Interview Questions...")
    try:
        questions = ai_service.generate_interview_questions(job_description, user_profile)
        print("✅ Interview questions generation successful!")
        print(f"❓ Generated categories: {list(questions.keys()) if questions else 'None'}")
        
    except Exception as e:
        print(f"❌ Interview questions failed: {e}")
    
    # Test job matching
    print("\n🎯 Testing Job Matching...")
    sample_resume = "Experienced Python developer with FastAPI and React skills."
    
    try:
        match_result = ai_service.calculate_job_match_score(sample_resume, job_description)
        print("✅ Job matching successful!")
        print(f"🎯 Match score: {match_result.get('score', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Job matching failed: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Multi-Provider AI Service Test Complete!")
    
    # Show environment information
    print(f"\n🔧 Environment Info:")
    print(f"   AI_PROVIDER: {os.getenv('AI_PROVIDER', 'Not set')}")
    print(f"   AI_API_KEY: {'Set' if os.getenv('AI_API_KEY') else 'Not set'}")
    print(f"   OPENAI_API_KEY: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not set'}")

if __name__ == "__main__":
    test_multi_ai_service()
"""
Detailed OpenAI Integration Test
"""
import requests
import json

def detailed_openai_test():
    print("🔍 Detailed OpenAI Integration Test\n")
    
    base_url = "http://localhost:8000"
    
    # Login first
    session = requests.Session()
    login_data = {
        "username": "integration_test@example.com",
        "password": "testpassword123"
    }
    
    response = session.post(f"{base_url}/auth/token", data=login_data)
    if response.status_code != 200:
        print("❌ Authentication failed")
        return
    
    token = response.json().get("access_token")
    session.headers.update({"Authorization": f"Bearer {token}"})
    print("✅ Authentication successful")
    
    # Test with a very specific request to see if we get real AI response
    print("\n🧪 Testing with specific request to detect real vs mock AI...")
    
    test_data = {
        "user_profile": {
            "name": "Dr. Sarah Chen",
            "email": "sarah.chen@example.com",
            "skills": ["Quantum Computing", "Machine Learning", "Python", "TensorFlow", "Research"],
            "work_history": [{
                "company": "Quantum Research Institute",
                "position": "Senior Quantum Scientist",
                "start_date": "2019-01-01",
                "end_date": "2024-01-01",
                "description": "Led breakthrough research in quantum machine learning algorithms, published 15 peer-reviewed papers, and developed novel quantum neural networks that achieved 30% faster processing than classical methods."
            }],
            "education": [{
                "degree": "PhD",
                "major": "Quantum Physics",
                "university": "MIT",
                "year": "2018"
            }]
        },
        "job_description": """
        Senior AI Research Scientist - Quantum Computing Division
        
        We are seeking a world-class AI Research Scientist to join our Quantum Computing Division. 
        The ideal candidate will have:
        
        - PhD in Quantum Physics, Computer Science, or related field
        - 5+ years of experience in quantum computing research
        - Expertise in quantum machine learning algorithms
        - Strong publication record in top-tier journals
        - Experience with TensorFlow Quantum or similar frameworks
        - Leadership experience in research teams
        
        Responsibilities:
        - Lead cutting-edge research in quantum AI
        - Develop novel quantum algorithms for machine learning
        - Collaborate with international research teams
        - Publish research in prestigious journals
        - Mentor junior researchers and PhD students
        
        This is a rare opportunity to work at the forefront of quantum AI research.
        """
    }
    
    print("Sending request with quantum computing profile...")
    response = session.post(f"{base_url}/api/v1/generate-resume", json=test_data)
    
    if response.status_code == 200:
        result = response.json()
        
        print("\n✅ Response received!")
        print("\n📋 Generated Content Analysis:")
        
        # Check professional summary for quantum-specific content
        prof_summary = result.get('professional_summary', '')
        print(f"\n**Professional Summary:**")
        print(prof_summary)
        
        # Look for quantum-specific terms that would indicate real AI
        quantum_terms = ['quantum', 'quantum computing', 'quantum machine learning', 'quantum algorithms', 'quantum neural networks']
        found_terms = [term for term in quantum_terms if term.lower() in prof_summary.lower()]
        
        if found_terms:
            print(f"\n🎯 **REAL AI DETECTED!** Found quantum-specific terms: {found_terms}")
            print("The AI is generating content specific to the quantum computing field!")
        else:
            print(f"\n⚠️  **MOCK RESPONSE DETECTED** - Generic content without quantum-specific terms")
            print("The system is still using fallback mock responses")
        
        # Check technical skills
        tech_skills = result.get('technical_skills', '')
        print(f"\n**Technical Skills:**")
        print(tech_skills)
        
        # Check match score
        if 'match_score' in result:
            match_score = result['match_score']
            print(f"\n**Match Score:** {match_score.get('overall_score', 'N/A')}%")
            
            # Check if recommendations are specific to quantum field
            recommendations = match_score.get('recommendations', [])
            quantum_recs = [rec for rec in recommendations if 'quantum' in rec.lower()]
            if quantum_recs:
                print(f"🎯 **REAL AI RECOMMENDATIONS:** {quantum_recs}")
            else:
                print(f"⚠️  Generic recommendations: {recommendations}")
    
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    detailed_openai_test()
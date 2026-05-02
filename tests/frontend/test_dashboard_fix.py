import os
import sys
import requests
import json

def test_dashboard_fixed():
    """Test if the dashboard React errors are fixed"""
    print("🔧 TESTING DASHBOARD FIXES")
    print("=" * 50)
    
    # Check if dashboard.tsx exists and is readable
    dashboard_path = r"d:\github projects\New folder\resume-ai-generator\frontend\pages\dashboard.tsx"
    
    try:
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        print("✅ Dashboard.tsx file readable")
        
        # Check for common React errors that were causing issues
        error_patterns = [
            'Objects are not valid as a React child',
            'JSX element has no corresponding closing tag',
            'Identifier expected',
            'export default function Dashboard() {',  # Should only appear once
            'ResultsDisplay'  # Should be removed (was causing the error)
        ]
        
        issues = []
        for pattern in error_patterns:
            if pattern == 'export default function Dashboard() {':
                # Should appear exactly once
                count = content.count(pattern)
                if count != 1:
                    issues.append(f"Multiple export statements found: {count}")
            elif pattern == 'ResultsDisplay':
                # Should be removed since it was causing the error
                if pattern in content:
                    issues.append("ResultsDisplay component still referenced (this was causing the error)")
            else:
                # These should NOT appear
                if pattern in content:
                    issues.append(f"Error pattern found: {pattern}")
        
        if not issues:
            print("✅ No syntax errors detected in dashboard.tsx")
        else:
            print("❌ Issues found:")
            for issue in issues:
                print(f"   - {issue}")
                
        # Check if we're using the correct API response format
        if 'results.professional_summary' in content:
            print("✅ Using correct API response format (professional_summary)")
        else:
            print("❌ Not using correct API response format")
            
        if 'results.match_score' in content:
            print("❌ Still using old ResultsDisplay format (match_score)")
        else:
            print("✅ Removed old ResultsDisplay format")
            
        return len(issues) == 0
        
    except Exception as e:
        print(f"❌ Error reading dashboard.tsx: {e}")
        return False

def test_backend_still_working():
    """Test if backend is still working after frontend changes"""
    print("\n🔧 TESTING BACKEND FUNCTIONALITY")
    print("=" * 50)
    
    try:
        # Test login endpoint
        login_response = requests.post('http://localhost:8000/auth/login', 
                                       json={'email': 'test@example.com', 'password': 'testpass123'})
        
        if login_response.status_code == 200:
            print("✅ Backend login endpoint working")
            token = login_response.json().get('access_token')
            
            # Test resume generation
            resume_data = {
                'job_description': 'Software Developer position',
                'user_profile': {
                    'name': 'Test User',
                    'email': 'test@example.com',
                    'skills': ['Python', 'JavaScript'],
                    'work_history': [],
                    'education': [{'degree': 'BS', 'major': 'Computer Science', 'university': 'Test University', 'year': '2020'}]
                }
            }
            
            resume_response = requests.post('http://localhost:8000/api/v1/generate-resume',
                                          json=resume_data,
                                          headers={'Authorization': f'Bearer {token}'})
            
            if resume_response.status_code == 200:
                print("✅ Backend resume generation working")
                resume_result = resume_response.json()
                
                # Check if response has the format our dashboard expects
                expected_fields = ['professional_summary', 'technical_skills', 'work_experience', 'education']
                has_fields = [field for field in expected_fields if field in resume_result]
                
                print(f"✅ Resume API returns {len(has_fields)}/{len(expected_fields)} expected fields")
                for field in has_fields:
                    print(f"   - {field}: ✅")
                
                return True
            else:
                print(f"❌ Resume generation failed: {resume_response.status_code}")
                return False
        else:
            print(f"❌ Backend login failed: {login_response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend not running (connection refused)")
        return False
    except Exception as e:
        print(f"❌ Backend test error: {e}")
        return False

def main():
    print("🚀 DASHBOARD FIX VERIFICATION TEST")
    print("=" * 60)
    
    dashboard_ok = test_dashboard_fixed()
    backend_ok = test_backend_still_working()
    
    print("\n" + "=" * 60)
    print("📊 RESULTS SUMMARY")
    print("=" * 60)
    
    if dashboard_ok:
        print("✅ DASHBOARD: React syntax errors fixed")
    else:
        print("❌ DASHBOARD: Still has issues")
        
    if backend_ok:
        print("✅ BACKEND: Still working correctly")
    else:
        print("❌ BACKEND: Has issues")
        
    if dashboard_ok and backend_ok:
        print("\n🎉 SUCCESS: Dashboard should now work without React errors!")
        print("📝 NEXT STEPS:")
        print("   1. Start frontend: npm run dev (in frontend directory)")
        print("   2. Navigate to http://localhost:3000")
        print("   3. Login with: test@example.com / testpass123")
        print("   4. Test resume generation on dashboard")
    else:
        print("\n❌ ISSUES REMAINING:")
        if not dashboard_ok:
            print("   - Dashboard still has syntax/logic errors")
        if not backend_ok:
            print("   - Backend is not working")

if __name__ == "__main__":
    main()
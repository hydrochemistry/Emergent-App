#!/usr/bin/env python3
"""
Research Log Creation API Test
Focus: Test research log creation functionality after fixing data validation issue
"""

import requests
import json
from datetime import datetime

class ResearchLogTester:
    def __init__(self):
        self.base_url = "https://researchpulse.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.student_token = None
        self.supervisor_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_log_id = None

    def log_result(self, test_name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}: PASSED {details}")
        else:
            print(f"❌ {test_name}: FAILED {details}")

    def make_request(self, method, endpoint, data=None, token=None, expected_status=200):
        """Make HTTP request with proper headers"""
        url = f"{self.api_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            
            success = response.status_code == expected_status
            return success, response.status_code, response.json() if response.text else {}
        except Exception as e:
            return False, 0, {"error": str(e)}

    def setup_authentication(self):
        """Create test users and get authentication tokens"""
        print("🔧 Setting up authentication...")
        
        # Create supervisor
        supervisor_data = {
            "email": f"supervisor_test_{datetime.now().strftime('%H%M%S')}@test.com",
            "password": "TestPass123!",
            "full_name": "Dr. Test Supervisor",
            "role": "supervisor",
            "department": "Computer Science",
            "research_area": "Machine Learning"
        }
        
        success, status, response = self.make_request("POST", "/auth/register", supervisor_data)
        if success and 'access_token' in response:
            self.supervisor_token = response['access_token']
            supervisor_email = response['user_data']['email']
            print(f"✅ Supervisor created: {supervisor_email}")
        else:
            print(f"❌ Failed to create supervisor: {status} - {response}")
            return False

        # Create student
        student_data = {
            "email": f"student_test_{datetime.now().strftime('%H%M%S')}@test.com",
            "password": "TestPass123!",
            "full_name": "Test Student",
            "role": "student",
            "department": "Computer Science",
            "research_area": "Deep Learning",
            "supervisor_email": supervisor_email,
            "student_id": "ST123456",
            "program_type": "phd_research"
        }
        
        success, status, response = self.make_request("POST", "/auth/register", student_data)
        if success and 'access_token' in response:
            self.student_token = response['access_token']
            print(f"✅ Student created: {response['user_data']['email']}")
            return True
        else:
            print(f"❌ Failed to create student: {status} - {response}")
            return False

    def test_research_log_creation_with_frontend_format(self):
        """Test research log creation with exact frontend data format"""
        print("\n🔍 Testing Research Log Creation with Frontend Data Format...")
        
        # Test data matching the exact format from the review request
        test_data = {
            "activity_type": "experiment",
            "title": "Test Research Log",
            "description": "Testing research log creation after fix",
            "duration_hours": 3.5,
            "findings": "Test findings",
            "challenges": "Test challenges",
            "next_steps": "Test next steps",
            "tags": ["test", "research"],
            "log_date": "2025-01-15",
            "log_time": "14:30"
        }
        
        success, status, response = self.make_request(
            "POST", "/research-logs", test_data, self.student_token, 200
        )
        
        if success:
            self.created_log_id = response.get('id')
            self.log_result(
                "Research Log Creation (Frontend Format)", 
                True, 
                f"- Created log ID: {self.created_log_id}"
            )
            return True
        else:
            self.log_result(
                "Research Log Creation (Frontend Format)", 
                False, 
                f"- Status: {status}, Response: {response}"
            )
            return False

    def test_research_log_creation_comprehensive(self):
        """Test research log creation with comprehensive data"""
        print("\n🔍 Testing Research Log Creation with Comprehensive Data...")
        
        comprehensive_data = {
            "activity_type": "literature_review",
            "title": "Comprehensive Literature Review on Neural Networks",
            "description": "Conducted extensive literature review on recent advances in neural network architectures",
            "duration_hours": 6.0,
            "findings": "Found 15 relevant papers on transformer architectures. Key insight: attention mechanisms are crucial for performance.",
            "challenges": "Difficulty accessing some paywalled journals. Need institutional access.",
            "next_steps": "1. Implement baseline transformer model 2. Compare with existing approaches 3. Write summary report",
            "tags": ["literature-review", "neural-networks", "transformers", "attention-mechanisms"],
            "log_date": "2025-01-15",
            "log_time": "09:00"
        }
        
        success, status, response = self.make_request(
            "POST", "/research-logs", comprehensive_data, self.student_token, 200
        )
        
        if success:
            log_id = response.get('id')
            self.log_result(
                "Research Log Creation (Comprehensive)", 
                True, 
                f"- Created log ID: {log_id}"
            )
            return True
        else:
            self.log_result(
                "Research Log Creation (Comprehensive)", 
                False, 
                f"- Status: {status}, Response: {response}"
            )
            return False

    def test_research_log_creation_minimal(self):
        """Test research log creation with minimal required data"""
        print("\n🔍 Testing Research Log Creation with Minimal Data...")
        
        minimal_data = {
            "activity_type": "meeting",
            "title": "Weekly Supervisor Meeting",
            "description": "Discussed progress on current research project"
        }
        
        success, status, response = self.make_request(
            "POST", "/research-logs", minimal_data, self.student_token, 200
        )
        
        if success:
            log_id = response.get('id')
            self.log_result(
                "Research Log Creation (Minimal)", 
                True, 
                f"- Created log ID: {log_id}"
            )
            return True
        else:
            self.log_result(
                "Research Log Creation (Minimal)", 
                False, 
                f"- Status: {status}, Response: {response}"
            )
            return False

    def test_research_log_retrieval(self):
        """Test research log retrieval"""
        print("\n🔍 Testing Research Log Retrieval...")
        
        success, status, response = self.make_request(
            "GET", "/research-logs", token=self.student_token, expected_status=200
        )
        
        if success:
            logs = response if isinstance(response, list) else []
            self.log_result(
                "Research Log Retrieval", 
                True, 
                f"- Retrieved {len(logs)} logs"
            )
            
            # Verify our created log is in the list
            if self.created_log_id:
                found_log = any(log.get('id') == self.created_log_id for log in logs)
                if found_log:
                    print("   ✅ Created log found in retrieval")
                else:
                    print("   ⚠️ Created log not found in retrieval")
            
            return True
        else:
            self.log_result(
                "Research Log Retrieval", 
                False, 
                f"- Status: {status}, Response: {response}"
            )
            return False

    def test_supervisor_research_log_access(self):
        """Test supervisor access to student research logs"""
        print("\n🔍 Testing Supervisor Access to Research Logs...")
        
        success, status, response = self.make_request(
            "GET", "/research-logs", token=self.supervisor_token, expected_status=200
        )
        
        if success:
            logs = response if isinstance(response, list) else []
            self.log_result(
                "Supervisor Research Log Access", 
                True, 
                f"- Supervisor can access {len(logs)} logs"
            )
            
            # Check if logs include student information
            if logs:
                first_log = logs[0]
                has_student_info = any(key in first_log for key in ['student_name', 'student_id', 'student_email'])
                if has_student_info:
                    print("   ✅ Logs include student information for supervisor view")
                else:
                    print("   ⚠️ Logs missing student information for supervisor view")
            
            return True
        else:
            self.log_result(
                "Supervisor Research Log Access", 
                False, 
                f"- Status: {status}, Response: {response}"
            )
            return False

    def test_unauthenticated_access(self):
        """Test that unauthenticated requests are properly blocked"""
        print("\n🔍 Testing Unauthenticated Access Protection...")
        
        success, status, response = self.make_request(
            "POST", "/research-logs", 
            {"title": "Test", "description": "Test", "activity_type": "experiment"}, 
            token=None, 
            expected_status=403
        )
        
        self.log_result(
            "Unauthenticated Access Protection", 
            success, 
            f"- Status: {status} (expected 403)"
        )
        return success

    def run_all_tests(self):
        """Run all research log tests"""
        print("🚀 Starting Research Log Creation API Tests")
        print("=" * 60)
        
        # Setup
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot proceed with tests.")
            return
        
        # Run tests
        print("\n📋 Running Research Log Tests...")
        self.test_unauthenticated_access()
        self.test_research_log_creation_with_frontend_format()
        self.test_research_log_creation_comprehensive()
        self.test_research_log_creation_minimal()
        self.test_research_log_retrieval()
        self.test_supervisor_research_log_access()
        
        # Summary
        print("\n" + "=" * 60)
        print(f"🎯 TEST SUMMARY")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED - Research Log Creation API is working perfectly!")
            return True
        else:
            print(f"⚠️ {self.tests_run - self.tests_passed} tests failed")
            return False

if __name__ == "__main__":
    tester = ResearchLogTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)
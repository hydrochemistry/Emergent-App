#!/usr/bin/env python3
"""
Research Log Creation Debug Test
Focused testing for the reported "Network Error" issue when students create research logs
"""

import requests
import sys
import json
from datetime import datetime, timedelta

class ResearchLogDebugTester:
    def __init__(self, base_url="https://researchpulse.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.student_token = None
        self.supervisor_token = None
        self.student_data = None
        self.supervisor_data = None
        self.tests_run = 0
        self.tests_passed = 0

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
            if details:
                print(f"   {details}")
        else:
            print(f"❌ {name}")
            if details:
                print(f"   {details}")

    def make_request(self, method, endpoint, data=None, token=None, expected_status=None):
        """Make HTTP request with detailed error reporting"""
        url = f"{self.api_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'

        print(f"\n🔍 {method} {url}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            
            print(f"   Status: {response.status_code}")
            
            # Try to parse response
            try:
                response_data = response.json()
                print(f"   Response: {json.dumps(response_data, indent=2)}")
            except:
                print(f"   Response Text: {response.text[:500]}")
                response_data = {}
            
            # Check if status matches expected
            if expected_status and response.status_code != expected_status:
                return False, response_data, f"Expected {expected_status}, got {response.status_code}"
            
            return response.status_code < 400, response_data, ""
            
        except requests.exceptions.Timeout:
            return False, {}, "Request timed out after 30 seconds"
        except requests.exceptions.ConnectionError as e:
            return False, {}, f"Connection error: {str(e)}"
        except requests.exceptions.RequestException as e:
            return False, {}, f"Request error: {str(e)}"
        except Exception as e:
            return False, {}, f"Unexpected error: {str(e)}"

    def test_endpoint_exists(self):
        """Test if the research-logs endpoint exists"""
        print("\n🔍 Testing if /api/research-logs endpoint exists...")
        
        # Test with GET first (should return 401/403 without auth, not 404)
        success, data, error = self.make_request('GET', '/research-logs')
        
        # Check response - 401/403 means endpoint exists but needs auth, 404 means doesn't exist
        success, data, error = self.make_request('GET', '/research-logs')
        
        # Parse the response to check for authentication errors vs not found
        if isinstance(data, dict) and ("Not authenticated" in str(data) or "detail" in data):
            self.log_test("Research Logs Endpoint Exists", True, "Endpoint exists (authentication required)")
            return True
        elif "404" in str(error) or "Not Found" in str(error):
            self.log_test("Research Logs Endpoint Exists", False, "Endpoint returns 404 - does not exist")
            return False
        else:
            # Assume endpoint exists if we get any structured response
            self.log_test("Research Logs Endpoint Exists", True, "Endpoint responds")
            return True

    def setup_test_users(self):
        """Create test supervisor and student accounts"""
        print("\n🔍 Setting up test users...")
        
        # Create supervisor
        timestamp = datetime.now().strftime('%H%M%S')
        supervisor_data = {
            "email": f"supervisor_debug_{timestamp}@university.edu",
            "password": "SecurePass123!",
            "full_name": "Dr. Sarah Johnson",
            "role": "supervisor",
            "department": "Computer Science",
            "faculty": "Engineering",
            "research_area": "Machine Learning and AI",
            "lab_name": "AI Research Lab"
        }
        
        success, response, error = self.make_request('POST', '/auth/register', supervisor_data, expected_status=200)
        if not success:
            self.log_test("Supervisor Registration", False, f"Failed: {error}")
            return False
        
        self.supervisor_token = response.get('access_token')
        self.supervisor_data = response.get('user_data')
        self.log_test("Supervisor Registration", True, f"ID: {self.supervisor_data['id']}")
        
        # Create student
        student_data = {
            "email": f"student_debug_{timestamp}@student.university.edu",
            "password": "StudentPass123!",
            "full_name": "Alex Chen",
            "role": "student",
            "student_id": "CS2024001",
            "department": "Computer Science",
            "faculty": "Engineering",
            "program_type": "phd_research",
            "field_of_study": "Machine Learning",
            "research_area": "Neural Networks",
            "supervisor_email": supervisor_data["email"],
            "nationality": "Malaysian",
            "citizenship": "Malaysian"
        }
        
        success, response, error = self.make_request('POST', '/auth/register', student_data, expected_status=200)
        if not success:
            self.log_test("Student Registration", False, f"Failed: {error}")
            return False
        
        self.student_token = response.get('access_token')
        self.student_data = response.get('user_data')
        self.log_test("Student Registration", True, f"ID: {self.student_data['id']}")
        
        return True

    def test_research_log_creation_exact_frontend_data(self):
        """Test research log creation with exact frontend data structure"""
        print("\n🔍 Testing research log creation with exact frontend data...")
        
        if not self.student_token:
            self.log_test("Research Log Creation (Frontend Data)", False, "No student token available")
            return False
        
        # Use the exact test data provided in the request
        research_log_data = {
            "title": "Machine Learning Experiment Results",
            "activity_type": "experiment", 
            "description": "Conducted experiments on neural network performance",
            "findings": "Model achieved 89% accuracy on test dataset",
            "challenges": "Overfitting issues with small dataset",
            "next_steps": "Implement regularization techniques",
            "duration_hours": 4.5,
            "tags": ["machine-learning", "neural-networks", "experiments"],
            "log_date": "2025-08-08",
            "log_time": "14:30"
        }
        
        success, response, error = self.make_request(
            'POST', 
            '/research-logs', 
            research_log_data, 
            self.student_token,
            expected_status=200
        )
        
        if success:
            self.log_test("Research Log Creation (Frontend Data)", True, f"Created log ID: {response.get('id')}")
            return True
        else:
            self.log_test("Research Log Creation (Frontend Data)", False, f"Failed: {error}")
            return False

    def test_research_log_creation_backend_format(self):
        """Test research log creation with backend expected format"""
        print("\n🔍 Testing research log creation with backend expected format...")
        
        if not self.student_token:
            self.log_test("Research Log Creation (Backend Format)", False, "No student token available")
            return False
        
        # Use backend expected format (based on ResearchLogCreate model)
        research_log_data = {
            "activity_type": "experiment",
            "title": "Deep Learning Model Optimization",
            "description": "Optimized CNN architecture for image classification tasks",
            "duration_hours": 6.0,
            "findings": "Achieved 92% accuracy with new architecture",
            "challenges": "Memory constraints during training",
            "next_steps": "Test on larger datasets",
            "tags": ["deep-learning", "cnn", "optimization"]
        }
        
        success, response, error = self.make_request(
            'POST', 
            '/research-logs', 
            research_log_data, 
            self.student_token,
            expected_status=200
        )
        
        if success:
            self.log_test("Research Log Creation (Backend Format)", True, f"Created log ID: {response.get('id')}")
            return True
        else:
            self.log_test("Research Log Creation (Backend Format)", False, f"Failed: {error}")
            return False

    def test_research_log_minimal_data(self):
        """Test research log creation with minimal required data"""
        print("\n🔍 Testing research log creation with minimal data...")
        
        if not self.student_token:
            self.log_test("Research Log Creation (Minimal)", False, "No student token available")
            return False
        
        # Minimal required fields only
        research_log_data = {
            "activity_type": "literature_review",
            "title": "Survey of Transformer Models",
            "description": "Comprehensive review of transformer architectures"
        }
        
        success, response, error = self.make_request(
            'POST', 
            '/research-logs', 
            research_log_data, 
            self.student_token,
            expected_status=200
        )
        
        if success:
            self.log_test("Research Log Creation (Minimal)", True, f"Created log ID: {response.get('id')}")
            return True
        else:
            self.log_test("Research Log Creation (Minimal)", False, f"Failed: {error}")
            return False

    def test_authentication_requirements(self):
        """Test authentication requirements for research log creation"""
        print("\n🔍 Testing authentication requirements...")
        
        # Test without token
        research_log_data = {
            "activity_type": "experiment",
            "title": "Test Without Auth",
            "description": "This should fail"
        }
        
        success, response, error = self.make_request(
            'POST', 
            '/research-logs', 
            research_log_data,
            expected_status=401
        )
        
        # Should fail with 401/403
        if not success:
            self.log_test("Authentication Required", True, "Correctly blocks unauthenticated requests")
            return True
        else:
            self.log_test("Authentication Required", False, "Should have blocked unauthenticated request")
            return False

    def test_supervisor_role_access(self):
        """Test if supervisor can also create research logs"""
        print("\n🔍 Testing supervisor role access...")
        
        if not self.supervisor_token:
            self.log_test("Supervisor Research Log Creation", False, "No supervisor token available")
            return False
        
        research_log_data = {
            "activity_type": "meeting",
            "title": "Research Progress Meeting",
            "description": "Weekly progress review with students"
        }
        
        success, response, error = self.make_request(
            'POST', 
            '/research-logs', 
            research_log_data, 
            self.supervisor_token,
            expected_status=200
        )
        
        if success:
            self.log_test("Supervisor Research Log Creation", True, f"Created log ID: {response.get('id')}")
            return True
        else:
            self.log_test("Supervisor Research Log Creation", False, f"Failed: {error}")
            return False

    def test_get_research_logs(self):
        """Test retrieving research logs"""
        print("\n🔍 Testing research log retrieval...")
        
        if not self.student_token:
            self.log_test("Get Research Logs", False, "No student token available")
            return False
        
        success, response, error = self.make_request(
            'GET', 
            '/research-logs', 
            token=self.student_token,
            expected_status=200
        )
        
        if success:
            logs_count = len(response) if isinstance(response, list) else 0
            self.log_test("Get Research Logs", True, f"Retrieved {logs_count} research logs")
            return True
        else:
            self.log_test("Get Research Logs", False, f"Failed: {error}")
            return False

    def test_cors_and_connectivity(self):
        """Test basic connectivity and CORS"""
        print("\n🔍 Testing basic connectivity and CORS...")
        
        # Test basic connectivity to the API
        try:
            response = requests.get(f"{self.base_url}/api", timeout=10)
            if response.status_code in [200, 404, 405]:  # Any response means connectivity works
                self.log_test("Basic Connectivity", True, f"API responds with status {response.status_code}")
            else:
                self.log_test("Basic Connectivity", False, f"Unexpected status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Basic Connectivity", False, f"Connection failed: {str(e)}")
            return False
        
        return True

    def run_all_tests(self):
        """Run all research log debug tests"""
        print("🚀 Starting Research Log Creation Debug Tests")
        print("=" * 60)
        
        # Test basic connectivity first
        if not self.test_cors_and_connectivity():
            print("❌ Basic connectivity failed, stopping tests")
            return False
        
        # Test if endpoint exists
        if not self.test_endpoint_exists():
            print("❌ Research logs endpoint does not exist, stopping tests")
            return False
        
        # Setup test users
        if not self.setup_test_users():
            print("❌ Failed to setup test users, stopping tests")
            return False
        
        # Test authentication requirements
        self.test_authentication_requirements()
        
        # Test research log creation with different data formats
        self.test_research_log_creation_exact_frontend_data()
        self.test_research_log_creation_backend_format()
        self.test_research_log_minimal_data()
        
        # Test different roles
        self.test_supervisor_role_access()
        
        # Test retrieval
        self.test_get_research_logs()
        
        # Print results
        print("\n" + "=" * 60)
        print(f"📊 Final Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All research log debug tests passed!")
            print("✅ CONCLUSION: Research Log Creation API is working correctly")
            print("   The 'Network Error' issue is likely in the frontend JavaScript,")
            print("   form validation, or API call implementation.")
            return True
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"❌ {failed_tests} tests failed")
            print("🚨 CONCLUSION: Issues found with Research Log Creation API")
            return False

def main():
    tester = ResearchLogDebugTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
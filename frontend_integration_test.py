import requests
import sys
import json
from datetime import datetime, timedelta

class FrontendIntegrationTester:
    def __init__(self, base_url="https://c5e539fb-9522-486d-b275-1bb355b557d8.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.student_token = None
        self.student_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None):
        """Run a single API test with detailed error reporting"""
        url = f"{self.api_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        print(f"   Method: {method}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2, default=str)}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            print(f"   Response Status: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response Data: {json.dumps(response_data, indent=2, default=str)[:300]}...")
                    return success, response_data
                except:
                    return success, {}
            else:
                print(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error Response: {json.dumps(error_data, indent=2)}")
                    self.failed_tests.append({
                        'name': name,
                        'expected': expected_status,
                        'actual': response.status_code,
                        'error': error_data
                    })
                except:
                    print(f"   Error Response: {response.text}")
                    self.failed_tests.append({
                        'name': name,
                        'expected': expected_status,
                        'actual': response.status_code,
                        'error': response.text
                    })
                return False, {}

        except Exception as e:
            print(f"❌ FAILED - Exception: {str(e)}")
            self.failed_tests.append({
                'name': name,
                'expected': expected_status,
                'actual': 'Exception',
                'error': str(e)
            })
            return False, {}

    def create_student_account(self):
        """Create a student account for testing"""
        print("👤 Creating student account for frontend integration testing...")
        
        timestamp = datetime.now().strftime('%H%M%S')
        student_data = {
            "email": f"frontend_student_{timestamp}@test.edu",
            "password": "StudentPass123!",
            "full_name": "Frontend Test Student",
            "role": "student",
            "student_id": f"FTS{timestamp}",
            "department": "Computer Science",
            "research_area": "Frontend Testing",
            "program_type": "phd_research",
            "field_of_study": "Computer Science",
            "faculty": "Engineering",
            "institute": "Test University",
            "nationality": "Malaysian",
            "citizenship": "Malaysian",
            "contact_number": "+60123456789"
        }
        
        success, response = self.run_test(
            "Student Account Creation",
            "POST",
            "/auth/register",
            200,
            data=student_data
        )
        
        if success and 'access_token' in response:
            self.student_token = response['access_token']
            self.student_data = response['user_data']
            print(f"   ✅ Student created: {self.student_data['id']}")
            return True
        else:
            print("❌ Failed to create student account")
            return False

    def test_student_create_scenarios(self):
        """Test all create scenarios as a student would experience them"""
        print("\n" + "="*80)
        print("🎓 TESTING STUDENT CREATE SCENARIOS")
        print("="*80)
        
        if not self.student_token:
            print("❌ No student token available")
            return False
            
        results = {}
        
        # Test 1: Research Log Creation (Student should be able to create)
        print("\n📝 Testing Research Log Creation as Student...")
        log_data = {
            "activity_type": "literature_review",
            "title": "Frontend Testing Research Log",
            "description": "Testing research log creation from frontend perspective",
            "duration_hours": 2.0,
            "findings": "Frontend integration appears to be working",
            "challenges": "Need to verify all form fields are properly sent",
            "next_steps": "Continue testing other create endpoints",
            "tags": ["frontend", "testing", "integration"]
        }
        
        success, response = self.run_test(
            "Research Log Creation (Student)",
            "POST",
            "/research-logs",
            200,
            data=log_data,
            token=self.student_token
        )
        results['research_log'] = success
        
        # Test 2: Meeting Creation (Student should NOT be able to create - only supervisors)
        print("\n📅 Testing Meeting Creation as Student (Should Fail)...")
        meeting_data = {
            "student_id": self.student_data['id'],
            "meeting_type": "supervision",
            "meeting_date": (datetime.now() + timedelta(days=3)).isoformat(),
            "duration_minutes": 60,
            "agenda": "Test meeting creation",
            "discussion_points": ["Test point"],
            "action_items": ["Test action"]
        }
        
        success, response = self.run_test(
            "Meeting Creation (Student - Should Fail)",
            "POST",
            "/meetings",
            403,  # Should fail with 403 Forbidden
            data=meeting_data,
            token=self.student_token
        )
        results['meeting_creation_blocked'] = success
        
        # Test 3: Reminder Creation (Student should be able to create for themselves)
        print("\n⏰ Testing Self-Reminder Creation as Student...")
        reminder_data = {
            "user_id": self.student_data['id'],
            "title": "Frontend Test Reminder",
            "description": "Testing reminder creation from frontend",
            "reminder_date": (datetime.now() + timedelta(days=2)).isoformat(),
            "priority": "medium",
            "reminder_type": "general"
        }
        
        success, response = self.run_test(
            "Self-Reminder Creation (Student)",
            "POST",
            "/reminders",
            200,
            data=reminder_data,
            token=self.student_token
        )
        results['reminder'] = success
        
        # Test 4: Bulletin Creation (Student should be able to create)
        print("\n📢 Testing Bulletin Creation as Student...")
        bulletin_data = {
            "title": "Frontend Test Announcement",
            "content": "Testing bulletin creation from frontend perspective",
            "category": "general",
            "is_highlight": False
        }
        
        success, response = self.run_test(
            "Bulletin Creation (Student)",
            "POST",
            "/bulletins",
            200,
            data=bulletin_data,
            token=self.student_token
        )
        results['bulletin'] = success
        
        # Test 5: Grant Creation (Student should NOT be able to create - only supervisors)
        print("\n💰 Testing Grant Creation as Student (Should Fail)...")
        grant_data = {
            "title": "Frontend Test Grant",
            "funding_agency": "Test Agency",
            "funding_type": "national",
            "total_amount": 50000.0,
            "status": "active",
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=365)).isoformat(),
            "description": "Test grant creation"
        }
        
        success, response = self.run_test(
            "Grant Creation (Student - Should Fail)",
            "POST",
            "/grants",
            403,  # Should fail with 403 Forbidden
            data=grant_data,
            token=self.student_token
        )
        results['grant_creation_blocked'] = success
        
        return results

    def test_authentication_edge_cases(self):
        """Test authentication edge cases that might cause frontend issues"""
        print("\n" + "="*80)
        print("🔐 TESTING AUTHENTICATION EDGE CASES")
        print("="*80)
        
        results = {}
        
        # Test 1: No token provided
        print("\n🚫 Testing API calls without authentication token...")
        log_data = {
            "activity_type": "experiment",
            "title": "Unauthorized Test",
            "description": "This should fail",
            "tags": ["test"]
        }
        
        success, response = self.run_test(
            "Research Log Creation (No Token)",
            "POST",
            "/research-logs",
            401,  # Should fail with 401 Unauthorized
            data=log_data
        )
        results['no_token'] = success
        
        # Test 2: Invalid token
        print("\n🔑 Testing API calls with invalid token...")
        success, response = self.run_test(
            "Research Log Creation (Invalid Token)",
            "POST",
            "/research-logs",
            401,  # Should fail with 401 Unauthorized
            data=log_data,
            token="invalid_token_12345"
        )
        results['invalid_token'] = success
        
        # Test 3: Expired token simulation (using malformed token)
        print("\n⏰ Testing API calls with malformed token...")
        success, response = self.run_test(
            "Research Log Creation (Malformed Token)",
            "POST",
            "/research-logs",
            401,  # Should fail with 401 Unauthorized
            data=log_data,
            token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
        )
        results['malformed_token'] = success
        
        return results

    def test_data_validation_issues(self):
        """Test data validation issues that might cause frontend problems"""
        print("\n" + "="*80)
        print("📋 TESTING DATA VALIDATION ISSUES")
        print("="*80)
        
        if not self.student_token:
            print("❌ No student token available")
            return {}
            
        results = {}
        
        # Test 1: Missing required fields
        print("\n❌ Testing Research Log Creation with missing required fields...")
        incomplete_log_data = {
            "activity_type": "experiment",
            # Missing title and description
            "tags": ["test"]
        }
        
        success, response = self.run_test(
            "Research Log Creation (Missing Fields)",
            "POST",
            "/research-logs",
            422,  # Should fail with 422 Validation Error
            data=incomplete_log_data,
            token=self.student_token
        )
        results['missing_fields'] = success
        
        # Test 2: Invalid enum values
        print("\n🔄 Testing Research Log Creation with invalid enum value...")
        invalid_enum_data = {
            "activity_type": "invalid_activity_type",
            "title": "Test Log",
            "description": "Testing invalid enum",
            "tags": ["test"]
        }
        
        success, response = self.run_test(
            "Research Log Creation (Invalid Enum)",
            "POST",
            "/research-logs",
            422,  # Should fail with 422 Validation Error
            data=invalid_enum_data,
            token=self.student_token
        )
        results['invalid_enum'] = success
        
        # Test 3: Invalid date format
        print("\n📅 Testing Reminder Creation with invalid date format...")
        invalid_date_data = {
            "user_id": self.student_data['id'],
            "title": "Test Reminder",
            "description": "Testing invalid date",
            "reminder_date": "invalid_date_format",
            "priority": "medium",
            "reminder_type": "general"
        }
        
        success, response = self.run_test(
            "Reminder Creation (Invalid Date)",
            "POST",
            "/reminders",
            422,  # Should fail with 422 Validation Error
            data=invalid_date_data,
            token=self.student_token
        )
        results['invalid_date'] = success
        
        return results

    def run_comprehensive_frontend_tests(self):
        """Run comprehensive frontend integration tests"""
        print("🌐 FRONTEND INTEGRATION TESTING")
        print("Simulating frontend create button scenarios")
        print("="*80)
        
        # Setup
        if not self.create_student_account():
            print("❌ Failed to create student account, cannot proceed")
            return False
            
        # Run all test categories
        create_results = self.test_student_create_scenarios()
        auth_results = self.test_authentication_edge_cases()
        validation_results = self.test_data_validation_issues()
        
        # Print comprehensive summary
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE FRONTEND INTEGRATION TEST RESULTS")
        print("="*80)
        
        print("\n🎓 Student Create Scenarios:")
        for test_name, result in create_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name}: {status}")
        
        print("\n🔐 Authentication Edge Cases:")
        for test_name, result in auth_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name}: {status}")
        
        print("\n📋 Data Validation Tests:")
        for test_name, result in validation_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name}: {status}")
        
        # Overall assessment
        all_results = {**create_results, **auth_results, **validation_results}
        total_tests = len(all_results)
        passed_tests = sum(1 for result in all_results.values() if result)
        
        print(f"\n📈 Overall Results: {passed_tests}/{total_tests} tests passed")
        
        # Detailed failure analysis
        if self.failed_tests:
            print("\n" + "="*80)
            print("🔍 DETAILED FAILURE ANALYSIS")
            print("="*80)
            for failure in self.failed_tests:
                print(f"\n❌ {failure['name']}")
                print(f"   Expected: {failure['expected']}")
                print(f"   Actual: {failure['actual']}")
                print(f"   Error: {failure['error']}")
        
        return passed_tests == total_tests

def main():
    print("🌐 FRONTEND INTEGRATION TESTING")
    print("Testing create APIs from frontend perspective")
    print("="*80)
    
    tester = FrontendIntegrationTester()
    
    success = tester.run_comprehensive_frontend_tests()
    
    print(f"\n📊 Final Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if success:
        print("🎉 All frontend integration tests passed!")
        return 0
    else:
        print("❌ Some frontend integration tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
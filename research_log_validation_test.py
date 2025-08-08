#!/usr/bin/env python3
"""
Comprehensive Research Log Validation Test
Focus: Verify the exact data validation fix and field handling
"""

import requests
import json
from datetime import datetime

class ResearchLogValidationTester:
    def __init__(self):
        self.base_url = "https://271c89aa-8749-475f-8a8f-92c118c46442.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.student_token = None
        self.tests_run = 0
        self.tests_passed = 0

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
            
            success = response.status_code == expected_status
            return success, response.status_code, response.json() if response.text else {}
        except Exception as e:
            return False, 0, {"error": str(e)}

    def setup_student_auth(self):
        """Create student user for testing"""
        print("🔧 Setting up student authentication...")
        
        student_data = {
            "email": f"validation_test_{datetime.now().strftime('%H%M%S')}@test.com",
            "password": "TestPass123!",
            "full_name": "Validation Test Student",
            "role": "student",
            "department": "Computer Science",
            "research_area": "Data Validation Testing",
            "student_id": "VT123456"
        }
        
        success, status, response = self.make_request("POST", "/auth/register", student_data)
        if success and 'access_token' in response:
            self.student_token = response['access_token']
            print(f"✅ Student created for validation testing")
            return True
        else:
            print(f"❌ Failed to create student: {status} - {response}")
            return False

    def test_exact_frontend_data_format(self):
        """Test with the EXACT data format from review request"""
        print("\n🔍 Testing EXACT Frontend Data Format from Review Request...")
        
        # This is the exact data format specified in the review request
        exact_test_data = {
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
            "POST", "/research-logs", exact_test_data, self.student_token, 200
        )
        
        if success:
            # Verify the response contains the created log
            log_id = response.get('id')
            if log_id:
                self.log_result(
                    "Exact Frontend Data Format", 
                    True, 
                    f"- Successfully created log with ID: {log_id}"
                )
                return True, log_id
            else:
                self.log_result(
                    "Exact Frontend Data Format", 
                    False, 
                    "- No log ID returned in response"
                )
                return False, None
        else:
            self.log_result(
                "Exact Frontend Data Format", 
                False, 
                f"- Status: {status}, Response: {response}"
            )
            return False, None

    def test_field_validation_acceptance(self):
        """Test that log_date and log_time fields are accepted without validation errors"""
        print("\n🔍 Testing Field Validation - log_date and log_time acceptance...")
        
        test_cases = [
            {
                "name": "With both log_date and log_time",
                "data": {
                    "activity_type": "data_collection",
                    "title": "Data Collection Session",
                    "description": "Collecting experimental data",
                    "log_date": "2025-01-16",
                    "log_time": "10:30"
                }
            },
            {
                "name": "With only log_date",
                "data": {
                    "activity_type": "analysis",
                    "title": "Data Analysis",
                    "description": "Analyzing collected data",
                    "log_date": "2025-01-17"
                }
            },
            {
                "name": "With only log_time",
                "data": {
                    "activity_type": "writing",
                    "title": "Report Writing",
                    "description": "Writing research report",
                    "log_time": "15:45"
                }
            },
            {
                "name": "Without date/time fields",
                "data": {
                    "activity_type": "meeting",
                    "title": "Team Meeting",
                    "description": "Weekly team meeting"
                }
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            success, status, response = self.make_request(
                "POST", "/research-logs", test_case["data"], self.student_token, 200
            )
            
            if success:
                print(f"   ✅ {test_case['name']}: Accepted")
            else:
                print(f"   ❌ {test_case['name']}: Rejected - Status: {status}")
                all_passed = False
        
        self.log_result(
            "Field Validation Acceptance", 
            all_passed, 
            "- All date/time field combinations accepted" if all_passed else "- Some field combinations rejected"
        )
        return all_passed

    def test_no_unexpected_field_errors(self):
        """Test that there are no 'unexpected field' validation errors"""
        print("\n🔍 Testing for Absence of 'Unexpected Field' Errors...")
        
        # Test with all possible fields that frontend might send
        comprehensive_data = {
            "activity_type": "experiment",
            "title": "Comprehensive Field Test",
            "description": "Testing all possible fields",
            "duration_hours": 4.0,
            "findings": "All fields should be accepted",
            "challenges": "No validation errors expected",
            "next_steps": "Verify field acceptance",
            "tags": ["validation", "comprehensive", "fields"],
            "log_date": "2025-01-18",
            "log_time": "11:15"
        }
        
        success, status, response = self.make_request(
            "POST", "/research-logs", comprehensive_data, self.student_token, 200
        )
        
        if success:
            self.log_result(
                "No Unexpected Field Errors", 
                True, 
                "- All fields accepted without validation errors"
            )
            return True
        else:
            # Check if the error is related to unexpected fields
            error_message = str(response)
            has_unexpected_field_error = "unexpected" in error_message.lower() or "extra" in error_message.lower()
            
            self.log_result(
                "No Unexpected Field Errors", 
                False, 
                f"- Status: {status}, Has unexpected field error: {has_unexpected_field_error}, Response: {response}"
            )
            return False

    def test_data_persistence_and_retrieval(self, created_log_id):
        """Test that created research logs are properly persisted and retrievable"""
        print("\n🔍 Testing Data Persistence and Retrieval...")
        
        if not created_log_id:
            self.log_result("Data Persistence", False, "- No log ID to test with")
            return False
        
        success, status, response = self.make_request(
            "GET", "/research-logs", token=self.student_token, expected_status=200
        )
        
        if success:
            logs = response if isinstance(response, list) else []
            found_log = None
            
            for log in logs:
                if log.get('id') == created_log_id:
                    found_log = log
                    break
            
            if found_log:
                # Verify the log contains the expected fields
                expected_fields = ['id', 'title', 'description', 'activity_type', 'date']
                has_all_fields = all(field in found_log for field in expected_fields)
                
                # Check if date/time was properly processed
                has_date = 'date' in found_log and found_log['date']
                
                self.log_result(
                    "Data Persistence", 
                    has_all_fields and has_date, 
                    f"- Log found with all fields: {has_all_fields}, Has date: {has_date}"
                )
                return has_all_fields and has_date
            else:
                self.log_result("Data Persistence", False, "- Created log not found in retrieval")
                return False
        else:
            self.log_result("Data Persistence", False, f"- Failed to retrieve logs: {status}")
            return False

    def test_network_connectivity(self):
        """Test that there are no network connectivity issues"""
        print("\n🔍 Testing Network Connectivity...")
        
        # Simple endpoint test to verify connectivity
        success, status, response = self.make_request(
            "GET", "/research-logs", token=self.student_token, expected_status=200
        )
        
        if success:
            self.log_result(
                "Network Connectivity", 
                True, 
                "- API endpoint accessible, no network errors"
            )
            return True
        else:
            self.log_result(
                "Network Connectivity", 
                False, 
                f"- Network or connectivity issue: Status {status}"
            )
            return False

    def run_validation_tests(self):
        """Run all validation tests"""
        print("🚀 Starting Research Log Validation Tests")
        print("Focus: Verify data validation fix and field handling")
        print("=" * 70)
        
        # Setup
        if not self.setup_student_auth():
            print("❌ Authentication setup failed. Cannot proceed with tests.")
            return False
        
        # Run tests
        print("\n📋 Running Validation Tests...")
        
        # Test network connectivity first
        self.test_network_connectivity()
        
        # Test exact frontend data format
        success, log_id = self.test_exact_frontend_data_format()
        
        # Test field validation
        self.test_field_validation_acceptance()
        
        # Test for unexpected field errors
        self.test_no_unexpected_field_errors()
        
        # Test data persistence
        if log_id:
            self.test_data_persistence_and_retrieval(log_id)
        
        # Summary
        print("\n" + "=" * 70)
        print(f"🎯 VALIDATION TEST SUMMARY")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL VALIDATION TESTS PASSED!")
            print("✅ Research log creation data validation issue is RESOLVED")
            print("✅ No 'Network connection failed' errors")
            print("✅ All frontend data fields are properly accepted")
            return True
        else:
            print(f"⚠️ {self.tests_run - self.tests_passed} validation tests failed")
            return False

if __name__ == "__main__":
    tester = ResearchLogValidationTester()
    success = tester.run_validation_tests()
    exit(0 if success else 1)
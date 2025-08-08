#!/usr/bin/env python3
"""
Additional Edge Case Tests for Enhanced Grants and Research Log Features
"""

import requests
import sys
import json
from datetime import datetime, timedelta

class EdgeCaseGrantsResearchTester:
    def __init__(self, base_url="https://271c89aa-8749-475f-8a8f-92c118c46442.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.supervisor_token = None
        self.student_token = None
        self.supervisor_data = None
        self.student_data = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None):
        """Run a single API test"""
        url = f"{self.api_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"   Response: {response.json()}")
                except:
                    print(f"   Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def setup_users(self):
        """Create supervisor and student users for testing"""
        print("🚀 Setting up edge case test users...")
        
        # Create supervisor
        supervisor_data = {
            "email": f"supervisor_edge_{datetime.now().strftime('%H%M%S')}@test.com",
            "password": "SupervisorPass123!",
            "full_name": "Dr. Edge Case Supervisor",
            "role": "supervisor",
            "department": "Research Department",
            "research_area": "Edge Case Testing"
        }
        
        success, response = self.run_test(
            "Edge Case Supervisor Registration",
            "POST",
            "/auth/register",
            200,
            data=supervisor_data
        )
        
        if success and 'access_token' in response:
            self.supervisor_token = response['access_token']
            self.supervisor_data = response['user_data']
        else:
            return False
            
        # Create student
        student_data = {
            "email": f"student_edge_{datetime.now().strftime('%H%M%S')}@test.com",
            "password": "StudentPass123!",
            "full_name": "Edge Case Student",
            "role": "student",
            "department": "Research Department",
            "research_area": "Edge Case Research",
            "supervisor_email": supervisor_data["email"],
            "student_id": "EDGE001"
        }
        
        success, response = self.run_test(
            "Edge Case Student Registration",
            "POST",
            "/auth/register",
            200,
            data=student_data
        )
        
        if success and 'access_token' in response:
            self.student_token = response['access_token']
            self.student_data = response['user_data']
            return True
        return False

    def test_research_log_review_edge_cases(self):
        """Test edge cases in research log review system"""
        print("\n🧪 Testing Research Log Review Edge Cases...")
        
        # Create a research log first
        log_data = {
            "activity_type": "experiment",
            "title": "Edge Case Research Log",
            "description": "Testing edge cases in review system",
            "duration_hours": 2.0,
            "findings": "Edge case findings",
            "challenges": "Edge case challenges",
            "next_steps": "Edge case next steps",
            "tags": ["edge-case", "testing"]
        }
        
        success, response = self.run_test(
            "Create Research Log for Edge Case Testing",
            "POST",
            "/research-logs",
            200,
            data=log_data,
            token=self.student_token
        )
        
        if not success or 'id' not in response:
            return False
            
        log_id = response['id']
        
        # Test invalid review action
        invalid_review = {
            "action": "invalid_action",
            "feedback": "This should fail"
        }
        
        success, _ = self.run_test(
            "Invalid Review Action (Should Fail)",
            "POST",
            f"/research-logs/{log_id}/review",
            400,  # Should return 400 for invalid action
            data=invalid_review,
            token=self.supervisor_token
        )
        
        if not success:
            return False
            
        # Test student trying to review (should fail)
        valid_review = {
            "action": "accepted",
            "feedback": "Student should not be able to review"
        }
        
        success, _ = self.run_test(
            "Student Review Attempt (Should Fail)",
            "POST",
            f"/research-logs/{log_id}/review",
            403,  # Should return 403 for unauthorized
            data=valid_review,
            token=self.student_token
        )
        
        if not success:
            return False
            
        # Test all valid review actions
        review_actions = ["accepted", "revision", "rejected"]
        
        for action in review_actions:
            review_data = {
                "action": action,
                "feedback": f"Testing {action} review action with comprehensive feedback"
            }
            
            success, _ = self.run_test(
                f"Valid Review Action: {action}",
                "POST",
                f"/research-logs/{log_id}/review",
                200,
                data=review_data,
                token=self.supervisor_token
            )
            
            if not success:
                return False
        
        return True

    def test_grants_access_control(self):
        """Test grants access control edge cases"""
        print("\n🔐 Testing Grants Access Control Edge Cases...")
        
        # Test student cannot create grants
        grant_data = {
            "title": "Student Should Not Create This",
            "funding_agency": "Test Agency",
            "total_amount": 50000.0,
            "status": "active",
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=365)).isoformat()
        }
        
        success, _ = self.run_test(
            "Student Grant Creation (Should Fail)",
            "POST",
            "/grants",
            403,  # Should return 403 for unauthorized
            data=grant_data,
            token=self.student_token
        )
        
        if not success:
            return False
            
        # Create a grant as supervisor for update testing
        success, response = self.run_test(
            "Supervisor Grant Creation for Update Testing",
            "POST",
            "/grants",
            200,
            data=grant_data,
            token=self.supervisor_token
        )
        
        if not success or 'id' not in response:
            return False
            
        grant_id = response['id']
        
        # Test unauthorized grant update (student not assigned as PIC)
        update_data = {
            "status": "completed",
            "current_balance": 25000.0
        }
        
        success, _ = self.run_test(
            "Unauthorized Grant Update (Should Fail)",
            "PUT",
            f"/grants/{grant_id}",
            403,  # Should return 403 for unauthorized
            data=update_data,
            token=self.student_token
        )
        
        return success

    def test_research_log_data_integrity(self):
        """Test research log data integrity with various input formats"""
        print("\n📊 Testing Research Log Data Integrity...")
        
        # Test with minimal required data
        minimal_log = {
            "activity_type": "meeting",
            "title": "Minimal Research Log",
            "description": "Testing minimal data requirements"
        }
        
        success, response = self.run_test(
            "Minimal Research Log Creation",
            "POST",
            "/research-logs",
            200,
            data=minimal_log,
            token=self.student_token
        )
        
        if not success:
            return False
            
        # Test with comprehensive data including date/time
        comprehensive_log = {
            "activity_type": "experiment",
            "title": "Comprehensive Research Log",
            "description": "Testing comprehensive data with all fields",
            "duration_hours": 8.5,
            "findings": "Comprehensive findings with detailed analysis",
            "challenges": "Multiple challenges encountered during research",
            "next_steps": "Detailed next steps for continuation",
            "tags": ["comprehensive", "testing", "data-integrity"],
            "log_date": "2025-01-15",
            "log_time": "09:30"
        }
        
        success, response = self.run_test(
            "Comprehensive Research Log Creation",
            "POST",
            "/research-logs",
            200,
            data=comprehensive_log,
            token=self.student_token
        )
        
        return success

    def test_grants_balance_edge_cases(self):
        """Test grants balance calculation edge cases"""
        print("\n💰 Testing Grants Balance Edge Cases...")
        
        # Create grants with different statuses
        grant_statuses = ["active", "completed", "on_hold", "cancelled"]
        
        for status in grant_statuses:
            grant_data = {
                "title": f"Grant with {status} status",
                "funding_agency": "Test Agency",
                "total_amount": 100000.0,
                "status": status,
                "start_date": datetime.now().isoformat(),
                "end_date": (datetime.now() + timedelta(days=365)).isoformat()
            }
            
            success, response = self.run_test(
                f"Create Grant with {status} Status",
                "POST",
                "/grants",
                200,
                data=grant_data,
                token=self.supervisor_token
            )
            
            if not success:
                return False
        
        # Test grants retrieval and balance calculations
        success, grants = self.run_test(
            "Get All Grants for Balance Testing",
            "GET",
            "/grants",
            200,
            token=self.student_token
        )
        
        if not success:
            return False
            
        # Verify balance fields are present for all grants
        balance_fields_present = True
        for grant in grants:
            if 'remaining_balance' not in grant and 'balance' not in grant:
                balance_fields_present = False
                break
        
        if balance_fields_present:
            print("✅ All grants have balance calculation fields")
            return True
        else:
            print("❌ Some grants missing balance calculation fields")
            return False

    def run_edge_case_tests(self):
        """Run all edge case tests"""
        print("🧪 Enhanced Grants and Research Log Edge Case Test Suite")
        print("=" * 70)
        
        # Setup phase
        if not self.setup_users():
            print("❌ Failed to setup edge case test users")
            return False
            
        # Run edge case tests
        tests = [
            self.test_research_log_review_edge_cases,
            self.test_grants_access_control,
            self.test_research_log_data_integrity,
            self.test_grants_balance_edge_cases
        ]
        
        for test in tests:
            if not test():
                print(f"❌ {test.__name__} failed")
                return False
        
        # Final results
        print("\n" + "=" * 70)
        print(f"🎉 EDGE CASE TEST RESULTS:")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("✅ ALL EDGE CASE TESTS PASSED!")
            return True
        else:
            print("❌ Some edge case tests failed")
            return False

if __name__ == "__main__":
    tester = EdgeCaseGrantsResearchTester()
    success = tester.run_edge_case_tests()
    sys.exit(0 if success else 1)
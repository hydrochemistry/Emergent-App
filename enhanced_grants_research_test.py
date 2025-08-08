#!/usr/bin/env python3
"""
Enhanced Grants Synchronization and Research Log Status Tracking Test
Tests the new functionality for grants visibility and research log review system
"""

import requests
import sys
import json
from datetime import datetime, timedelta

class EnhancedGrantsResearchTester:
    def __init__(self, base_url="https://271c89aa-8749-475f-8a8f-92c118c46442.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.supervisor_token = None
        self.student_token = None
        self.supervisor_data = None
        self.student_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_grant_id = None
        self.created_log_id = None

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
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

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
        print("🚀 Setting up test users...")
        
        # Create supervisor
        supervisor_data = {
            "email": f"supervisor_grants_{datetime.now().strftime('%H%M%S')}@test.com",
            "password": "SupervisorPass123!",
            "full_name": "Dr. Grant Manager",
            "role": "supervisor",
            "department": "Research Department",
            "research_area": "Grant Management",
            "lab_name": "Advanced Research Lab"
        }
        
        success, response = self.run_test(
            "Supervisor Registration",
            "POST",
            "/auth/register",
            200,
            data=supervisor_data
        )
        
        if success and 'access_token' in response:
            self.supervisor_token = response['access_token']
            self.supervisor_data = response['user_data']
            print(f"   Supervisor ID: {self.supervisor_data['id']}")
        else:
            print("❌ Failed to create supervisor")
            return False
            
        # Create student
        student_data = {
            "email": f"student_grants_{datetime.now().strftime('%H%M%S')}@test.com",
            "password": "StudentPass123!",
            "full_name": "Alice Research Student",
            "role": "student",
            "department": "Research Department",
            "research_area": "Data Science",
            "supervisor_email": supervisor_data["email"],
            "student_id": "STU001",
            "program_type": "phd_research"
        }
        
        success, response = self.run_test(
            "Student Registration",
            "POST",
            "/auth/register",
            200,
            data=student_data
        )
        
        if success and 'access_token' in response:
            self.student_token = response['access_token']
            self.student_data = response['user_data']
            print(f"   Student ID: {self.student_data['id']}")
            return True
        else:
            print("❌ Failed to create student")
            return False

    def test_grant_creation_by_supervisor(self):
        """Test grant creation by supervisor"""
        if not self.supervisor_token:
            print("❌ No supervisor token available")
            return False
            
        grant_data = {
            "title": "Advanced AI Research Grant",
            "funding_agency": "National Science Foundation",
            "funding_type": "national",
            "total_amount": 150000.0,
            "status": "active",
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=365*2)).isoformat(),
            "description": "Research grant for advanced AI applications",
            "person_in_charge": self.student_data['id'],  # Assign student as PIC
            "grant_vote_number": "NSF-2024-001",
            "duration_months": 24,
            "grant_type": "research"
        }
        
        success, response = self.run_test(
            "Grant Creation by Supervisor",
            "POST",
            "/grants",
            200,
            data=grant_data,
            token=self.supervisor_token
        )
        
        if success and 'id' in response:
            self.created_grant_id = response['id']
            print(f"   Created Grant ID: {self.created_grant_id}")
            return True
        return False

    def test_grants_visibility_all_users(self):
        """Test that all users can see all grants (enhanced synchronization)"""
        print("\n📊 Testing Enhanced Grants Synchronization...")
        
        # Test supervisor can see grants
        success, supervisor_grants = self.run_test(
            "Supervisor Grants Visibility",
            "GET",
            "/grants",
            200,
            token=self.supervisor_token
        )
        
        if not success:
            return False
            
        # Test student can see grants (this is the key enhancement)
        success, student_grants = self.run_test(
            "Student Grants Visibility (Enhanced Feature)",
            "GET",
            "/grants",
            200,
            token=self.student_token
        )
        
        if not success:
            return False
            
        # Verify both users see the same grants
        if len(supervisor_grants) == len(student_grants):
            print(f"✅ Both users see {len(supervisor_grants)} grants - Enhanced synchronization working")
            
            # Check if our created grant is visible to both
            supervisor_grant_ids = [g['id'] for g in supervisor_grants]
            student_grant_ids = [g['id'] for g in student_grants]
            
            if self.created_grant_id in supervisor_grant_ids and self.created_grant_id in student_grant_ids:
                print("✅ Created grant visible to both supervisor and student")
                
                # Verify balance calculations are present
                for grant in student_grants:
                    if grant['id'] == self.created_grant_id:
                        print(f"   Grant fields: {list(grant.keys())}")
                        # Check for any balance-related fields
                        balance_fields = ['remaining_balance', 'current_balance', 'balance', 'total_amount']
                        found_balance_fields = [field for field in balance_fields if field in grant]
                        
                        if found_balance_fields:
                            print(f"✅ Grant balance calculations present: {found_balance_fields}")
                            for field in found_balance_fields:
                                print(f"   - {field}: {grant.get(field)}")
                            return True
                        else:
                            print("❌ Grant balance calculations missing")
                            return False
            else:
                print("❌ Created grant not visible to both users")
                return False
        else:
            print(f"❌ Grant visibility mismatch - Supervisor sees {len(supervisor_grants)}, Student sees {len(student_grants)}")
            return False

    def test_research_log_creation(self):
        """Create a research log for testing review status"""
        if not self.student_token:
            print("❌ No student token available")
            return False
            
        log_data = {
            "activity_type": "experiment",
            "title": "Machine Learning Model Training Results",
            "description": "Conducted comprehensive training of neural network models for grant-funded research",
            "duration_hours": 6.5,
            "findings": "Achieved 92% accuracy on validation dataset with improved architecture",
            "challenges": "Memory constraints during training with large datasets",
            "next_steps": "Optimize model architecture and implement distributed training",
            "tags": ["machine-learning", "neural-networks", "grant-research"],
            "log_date": "2025-01-15",
            "log_time": "14:30"
        }
        
        success, response = self.run_test(
            "Research Log Creation by Student",
            "POST",
            "/research-logs",
            200,
            data=log_data,
            token=self.student_token
        )
        
        if success and 'id' in response:
            self.created_log_id = response['id']
            print(f"   Created Research Log ID: {self.created_log_id}")
            return True
        return False

    def test_research_log_review_system(self):
        """Test the research log review system"""
        if not self.created_log_id or not self.supervisor_token:
            print("❌ Missing research log ID or supervisor token")
            return False
            
        print("\n📝 Testing Research Log Review System...")
        
        # Test supervisor can review research log
        review_data = {
            "action": "accepted",
            "feedback": "Excellent work on the neural network training. The accuracy improvements are impressive and the methodology is sound. Please proceed with the optimization phase as outlined in your next steps."
        }
        
        success, response = self.run_test(
            "Research Log Review by Supervisor",
            "POST",
            f"/research-logs/{self.created_log_id}/review",
            200,
            data=review_data,
            token=self.supervisor_token
        )
        
        return success

    def test_research_log_status_tracking(self):
        """Test research log status tracking for students"""
        print("\n📊 Testing Research Log Status Tracking...")
        
        # Test student can see review status
        success, student_logs = self.run_test(
            "Student Research Logs with Review Status",
            "GET",
            "/research-logs",
            200,
            token=self.student_token
        )
        
        if not success:
            return False
            
        # Find our created log and check review status
        student_log_found = False
        for log in student_logs:
            if log['id'] == self.created_log_id:
                student_log_found = True
                required_fields = ['review_status', 'review_feedback', 'reviewed_by', 'reviewed_at', 'reviewer_name']
                missing_fields = [field for field in required_fields if field not in log or log[field] is None]
                
                if not missing_fields:
                    print(f"✅ Research log includes all review status fields:")
                    print(f"   - Review Status: {log['review_status']}")
                    print(f"   - Review Feedback: {log['review_feedback'][:50]}...")
                    print(f"   - Reviewed By: {log['reviewed_by']}")
                    print(f"   - Reviewed At: {log['reviewed_at']}")
                    print(f"   - Reviewer Name: {log['reviewer_name']}")
                else:
                    print(f"❌ Missing review status fields: {missing_fields}")
                    return False
                break
        
        if not student_log_found:
            print("❌ Created research log not found in student's logs")
            return False
        
        # Test supervisor can see student information in logs
        success, supervisor_logs = self.run_test(
            "Supervisor Research Logs with Student Info",
            "GET",
            "/research-logs",
            200,
            token=self.supervisor_token
        )
        
        if not success:
            return False
            
        # Find our created log and check student information
        supervisor_log_found = False
        for log in supervisor_logs:
            if log['id'] == self.created_log_id:
                supervisor_log_found = True
                student_fields = ['student_name', 'student_id', 'student_email']
                missing_fields = [field for field in student_fields if field not in log or log[field] is None]
                
                if not missing_fields:
                    print(f"✅ Supervisor view includes student information:")
                    print(f"   - Student Name: {log['student_name']}")
                    print(f"   - Student ID: {log['student_id']}")
                    print(f"   - Student Email: {log['student_email']}")
                else:
                    print(f"❌ Missing student information fields: {missing_fields}")
                    return False
                break
        
        if not supervisor_log_found:
            print("❌ Created research log not found in supervisor's logs")
            return False
            
        return True

    def test_active_grants_balance_calculation(self):
        """Test active grants balance calculation"""
        print("\n💰 Testing Active Grants Balance Calculation...")
        
        # Get grants and filter active ones
        success, grants = self.run_test(
            "Get All Grants for Balance Calculation",
            "GET",
            "/grants",
            200,
            token=self.supervisor_token
        )
        
        if not success:
            return False
            
        active_grants = [g for g in grants if g.get('status') == 'active']
        
        if not active_grants:
            print("❌ No active grants found for balance calculation")
            return False
            
        print(f"✅ Found {len(active_grants)} active grants")
        
        # Calculate cumulative balance
        total_active_balance = 0
        for grant in active_grants:
            remaining_balance = grant.get('remaining_balance', 0)
            current_balance = grant.get('current_balance', 0)
            total_active_balance += max(remaining_balance, current_balance)
            
            print(f"   Grant: {grant['title']}")
            print(f"   - Total Amount: ${grant.get('total_amount', 0):,.2f}")
            print(f"   - Remaining Balance: ${remaining_balance:,.2f}")
            print(f"   - Current Balance: ${current_balance:,.2f}")
        
        print(f"✅ Cumulative Active Grant Balance: ${total_active_balance:,.2f}")
        return True

    def run_all_tests(self):
        """Run all enhanced grants and research log tests"""
        print("🎯 Enhanced Grants Synchronization and Research Log Status Tracking Test Suite")
        print("=" * 80)
        
        # Setup phase
        if not self.setup_users():
            print("❌ Failed to setup test users")
            return False
            
        # Test grant creation
        if not self.test_grant_creation_by_supervisor():
            print("❌ Failed to create test grant")
            return False
            
        # Test enhanced grants synchronization
        if not self.test_grants_visibility_all_users():
            print("❌ Enhanced grants synchronization test failed")
            return False
            
        # Test research log creation
        if not self.test_research_log_creation():
            print("❌ Failed to create test research log")
            return False
            
        # Test research log review system
        if not self.test_research_log_review_system():
            print("❌ Research log review system test failed")
            return False
            
        # Test research log status tracking
        if not self.test_research_log_status_tracking():
            print("❌ Research log status tracking test failed")
            return False
            
        # Test active grants balance calculation
        if not self.test_active_grants_balance_calculation():
            print("❌ Active grants balance calculation test failed")
            return False
        
        # Final results
        print("\n" + "=" * 80)
        print(f"🎉 ENHANCED FEATURES TEST RESULTS:")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("✅ ALL ENHANCED FEATURES WORKING PERFECTLY!")
            return True
        else:
            print("❌ Some enhanced features need attention")
            return False

if __name__ == "__main__":
    tester = EnhancedGrantsResearchTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
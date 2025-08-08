#!/usr/bin/env python3
"""
Research Log Review System Testing
Tests the new research log review functionality implemented in the backend.
"""

import requests
import json
from datetime import datetime, timedelta
import sys

class ResearchLogReviewTester:
    def __init__(self, base_url="https://271c89aa-8749-475f-8a8f-92c118c46442.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.supervisor_token = None
        self.student_token = None
        self.supervisor_data = None
        self.student_data = None
        self.tests_run = 0
        self.tests_passed = 0
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
                    print(f"   Raw Response: {response.text}")
                return False, {}
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False, {}

    def setup_test_users(self):
        """Create test supervisor and student accounts"""
        print("\n🚀 Setting up test users...")
        
        # Create supervisor
        supervisor_data = {
            "email": "supervisor.review@test.com",
            "password": "TestPass123!",
            "full_name": "Dr. Review Supervisor",
            "role": "supervisor",
            "department": "Computer Science",
            "research_area": "Machine Learning",
            "lab_name": "AI Research Lab"
        }
        
        success, response = self.run_test(
            "Create Supervisor Account", 
            "POST", 
            "/auth/register", 
            200, 
            supervisor_data
        )
        
        if success:
            self.supervisor_token = response.get('access_token')
            self.supervisor_data = response.get('user_data')
            print(f"   Supervisor ID: {self.supervisor_data.get('id')}")
        
        # Create student
        student_data = {
            "email": "student.review@test.com",
            "password": "TestPass123!",
            "full_name": "Alice Review Student",
            "role": "student",
            "student_id": "STU2025001",
            "department": "Computer Science",
            "program_type": "phd_research",
            "field_of_study": "Artificial Intelligence",
            "supervisor_email": "supervisor.review@test.com"
        }
        
        success, response = self.run_test(
            "Create Student Account", 
            "POST", 
            "/auth/register", 
            200, 
            student_data
        )
        
        if success:
            self.student_token = response.get('access_token')
            self.student_data = response.get('user_data')
            print(f"   Student ID: {self.student_data.get('id')}")

    def test_research_log_creation(self):
        """Test creating a research log as student"""
        print("\n📝 Testing Research Log Creation...")
        
        log_data = {
            "activity_type": "experiment",
            "title": "Neural Network Performance Analysis",
            "description": "Conducted comprehensive analysis of different neural network architectures for image classification tasks",
            "duration_hours": 6.5,
            "findings": "ResNet-50 achieved 94.2% accuracy on test dataset, outperforming VGG-16 by 3.1%",
            "challenges": "Overfitting issues with smaller datasets, required extensive data augmentation",
            "next_steps": "Implement regularization techniques and test on larger datasets",
            "tags": ["neural-networks", "image-classification", "performance-analysis"]
        }
        
        success, response = self.run_test(
            "Create Research Log (Student)",
            "POST",
            "/research-logs",
            200,
            log_data,
            self.student_token
        )
        
        if success:
            self.created_log_id = response.get('id')
            print(f"   Created Log ID: {self.created_log_id}")
            return True
        return False

    def test_research_log_review_authentication(self):
        """Test that only supervisors can review research logs"""
        print("\n🔐 Testing Review Authentication...")
        
        if not self.created_log_id:
            print("❌ No research log available for testing")
            return False
        
        # Test student cannot review (should fail)
        review_data = {
            "action": "accepted",
            "feedback": "Good work on the analysis"
        }
        
        success, response = self.run_test(
            "Student Cannot Review (Should Fail)",
            "POST",
            f"/research-logs/{self.created_log_id}/review",
            403,  # Expecting forbidden
            review_data,
            self.student_token
        )
        
        # Test unauthenticated request (should fail)
        success, response = self.run_test(
            "Unauthenticated Review (Should Fail)",
            "POST",
            f"/research-logs/{self.created_log_id}/review",
            401,  # Expecting unauthorized
            review_data,
            None
        )
        
        return True

    def test_research_log_review_actions(self):
        """Test all three review actions: accepted, revision, rejected"""
        print("\n⭐ Testing Research Log Review Actions...")
        
        if not self.created_log_id:
            print("❌ No research log available for testing")
            return False
        
        # Test 1: Accept review
        accept_data = {
            "action": "accepted",
            "feedback": "Excellent analysis! The methodology is sound and results are well-documented. Great work on comparing different architectures."
        }
        
        success, response = self.run_test(
            "Review Action: Accept",
            "POST",
            f"/research-logs/{self.created_log_id}/review",
            200,
            accept_data,
            self.supervisor_token
        )
        
        if not success:
            return False
        
        # Create another log for revision test
        log_data_2 = {
            "activity_type": "literature_review",
            "title": "Deep Learning Survey",
            "description": "Literature review on recent advances in deep learning",
            "duration_hours": 4.0,
            "findings": "Found 25 relevant papers",
            "challenges": "Too many papers to review",
            "next_steps": "Focus on specific subtopics",
            "tags": ["literature-review", "deep-learning"]
        }
        
        success, response = self.run_test(
            "Create Second Research Log",
            "POST",
            "/research-logs",
            200,
            log_data_2,
            self.student_token
        )
        
        if success:
            log_id_2 = response.get('id')
            
            # Test 2: Request revision
            revision_data = {
                "action": "revision",
                "feedback": "Good start, but needs more depth. Please include more detailed analysis of the methodologies used in the papers. Also add a comparison table."
            }
            
            success, response = self.run_test(
                "Review Action: Revision",
                "POST",
                f"/research-logs/{log_id_2}/review",
                200,
                revision_data,
                self.supervisor_token
            )
        
        # Create third log for rejection test
        log_data_3 = {
            "activity_type": "data_collection",
            "title": "Dataset Preparation",
            "description": "Prepared dataset for experiments",
            "duration_hours": 2.0,
            "findings": "Collected 100 samples",
            "challenges": "Data quality issues",
            "next_steps": "Clean the data",
            "tags": ["data-collection"]
        }
        
        success, response = self.run_test(
            "Create Third Research Log",
            "POST",
            "/research-logs",
            200,
            log_data_3,
            self.student_token
        )
        
        if success:
            log_id_3 = response.get('id')
            
            # Test 3: Reject
            reject_data = {
                "action": "rejected",
                "feedback": "This log lacks sufficient detail and analysis. Please provide more comprehensive documentation of your methodology and findings before resubmission."
            }
            
            success, response = self.run_test(
                "Review Action: Reject",
                "POST",
                f"/research-logs/{log_id_3}/review",
                200,
                reject_data,
                self.supervisor_token
            )
        
        return True

    def test_invalid_review_actions(self):
        """Test invalid review actions are rejected"""
        print("\n🚫 Testing Invalid Review Actions...")
        
        if not self.created_log_id:
            print("❌ No research log available for testing")
            return False
        
        # Test invalid action
        invalid_data = {
            "action": "invalid_action",
            "feedback": "This should fail"
        }
        
        success, response = self.run_test(
            "Invalid Review Action (Should Fail)",
            "POST",
            f"/research-logs/{self.created_log_id}/review",
            400,  # Expecting bad request
            invalid_data,
            self.supervisor_token
        )
        
        # Test missing action
        missing_action_data = {
            "feedback": "Missing action field"
        }
        
        success, response = self.run_test(
            "Missing Action Field (Should Fail)",
            "POST",
            f"/research-logs/{self.created_log_id}/review",
            400,  # Expecting bad request
            missing_action_data,
            self.supervisor_token
        )
        
        # Test review of non-existent log
        valid_data = {
            "action": "accepted",
            "feedback": "This log doesn't exist"
        }
        
        success, response = self.run_test(
            "Review Non-existent Log (Should Fail)",
            "POST",
            "/research-logs/non-existent-id/review",
            404,  # Expecting not found
            valid_data,
            self.supervisor_token
        )
        
        return True

    def test_enhanced_research_log_retrieval(self):
        """Test that research logs now include review information"""
        print("\n📋 Testing Enhanced Research Log Retrieval...")
        
        # Test student view - should see their own logs with review status
        success, response = self.run_test(
            "Get Research Logs (Student View)",
            "GET",
            "/research-logs",
            200,
            None,
            self.student_token
        )
        
        if success:
            logs = response if isinstance(response, list) else []
            print(f"   Student sees {len(logs)} logs")
            
            # Check if logs include review information
            for log in logs:
                if log.get('id') == self.created_log_id:
                    review_status = log.get('review_status')
                    review_feedback = log.get('review_feedback')
                    reviewed_by = log.get('reviewed_by')
                    reviewed_at = log.get('reviewed_at')
                    reviewer_name = log.get('reviewer_name')
                    
                    print(f"   ✅ Review Status: {review_status}")
                    print(f"   ✅ Review Feedback: {review_feedback[:50]}..." if review_feedback else "   ✅ No feedback")
                    print(f"   ✅ Reviewed By: {reviewed_by}")
                    print(f"   ✅ Reviewed At: {reviewed_at}")
                    print(f"   ✅ Reviewer Name: {reviewer_name}")
                    
                    if review_status == 'accepted':
                        print("   ✅ Review information correctly included in student view")
                    break
        
        # Test supervisor view - should see all logs with student information
        success, response = self.run_test(
            "Get Research Logs (Supervisor View)",
            "GET",
            "/research-logs",
            200,
            None,
            self.supervisor_token
        )
        
        if success:
            logs = response if isinstance(response, list) else []
            print(f"   Supervisor sees {len(logs)} logs")
            
            # Check if logs include student information
            for log in logs:
                student_name = log.get('student_name')
                student_id = log.get('student_id')
                student_email = log.get('student_email')
                review_status = log.get('review_status')
                
                if student_name:
                    print(f"   ✅ Student Name: {student_name}")
                    print(f"   ✅ Student ID: {student_id}")
                    print(f"   ✅ Student Email: {student_email}")
                    print(f"   ✅ Review Status: {review_status}")
                    print("   ✅ Student information correctly included in supervisor view")
                    break
        
        return True

    def test_review_data_persistence(self):
        """Test that review data persists correctly"""
        print("\n💾 Testing Review Data Persistence...")
        
        if not self.created_log_id:
            print("❌ No research log available for testing")
            return False
        
        # Get the specific log and verify review data
        success, response = self.run_test(
            "Verify Review Data Persistence",
            "GET",
            "/research-logs",
            200,
            None,
            self.supervisor_token
        )
        
        if success:
            logs = response if isinstance(response, list) else []
            
            for log in logs:
                if log.get('id') == self.created_log_id:
                    # Verify all review fields are present and correct
                    expected_status = 'accepted'
                    expected_feedback = "Excellent analysis! The methodology is sound and results are well-documented. Great work on comparing different architectures."
                    
                    actual_status = log.get('review_status')
                    actual_feedback = log.get('review_feedback')
                    reviewed_by = log.get('reviewed_by')
                    reviewed_at = log.get('reviewed_at')
                    reviewer_name = log.get('reviewer_name')
                    
                    if actual_status == expected_status:
                        print(f"   ✅ Review status persisted correctly: {actual_status}")
                    else:
                        print(f"   ❌ Review status mismatch: expected {expected_status}, got {actual_status}")
                    
                    if actual_feedback == expected_feedback:
                        print(f"   ✅ Review feedback persisted correctly")
                    else:
                        print(f"   ❌ Review feedback mismatch")
                    
                    if reviewed_by == self.supervisor_data.get('id'):
                        print(f"   ✅ Reviewer ID persisted correctly")
                    else:
                        print(f"   ❌ Reviewer ID mismatch")
                    
                    if reviewed_at:
                        print(f"   ✅ Review timestamp persisted: {reviewed_at}")
                    else:
                        print(f"   ❌ Review timestamp missing")
                    
                    if reviewer_name == self.supervisor_data.get('full_name'):
                        print(f"   ✅ Reviewer name persisted correctly: {reviewer_name}")
                    else:
                        print(f"   ❌ Reviewer name mismatch")
                    
                    return True
            
            print("   ❌ Could not find the reviewed log")
            return False
        
        return False

    def run_all_tests(self):
        """Run all research log review tests"""
        print("🧪 RESEARCH LOG REVIEW SYSTEM TESTING")
        print("=" * 50)
        
        # Setup
        self.setup_test_users()
        
        if not self.supervisor_token or not self.student_token:
            print("❌ Failed to setup test users. Cannot continue.")
            return
        
        # Test research log creation (prerequisite)
        if not self.test_research_log_creation():
            print("❌ Failed to create research log. Cannot test review functionality.")
            return
        
        # Test review functionality
        self.test_research_log_review_authentication()
        self.test_research_log_review_actions()
        self.test_invalid_review_actions()
        self.test_enhanced_research_log_retrieval()
        self.test_review_data_persistence()
        
        # Summary
        print("\n" + "=" * 50)
        print(f"🏁 TESTING COMPLETE")
        print(f"📊 Tests Run: {self.tests_run}")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📈 Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED! Research Log Review System is working perfectly.")
        else:
            print("⚠️  Some tests failed. Please review the issues above.")

if __name__ == "__main__":
    tester = ResearchLogReviewTester()
    tester.run_all_tests()
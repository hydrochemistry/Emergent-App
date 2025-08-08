#!/usr/bin/env python3

import asyncio
import httpx
import json
import os
from datetime import datetime, timedelta
import sys

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://271c89aa-8749-475f-8a8f-92c118c46442.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class CriticalFixesTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.supervisor_token = None
        self.student_token = None
        self.supervisor_id = None
        self.student_id = None
        self.test_results = []
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details or {}
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    async def setup_test_users(self):
        """Create and authenticate test users (supervisor and student)"""
        try:
            # Setup supervisor user
            supervisor_data = {
                "email": "supervisor.test@research.lab",
                "password": "TestPassword123!",
                "full_name": "Dr. Test Supervisor",
                "role": "supervisor",
                "department": "Computer Science",
                "research_area": "Machine Learning",
                "lab_name": "AI Research Lab"
            }
            
            response = await self.client.post(f"{API_BASE}/auth/register", json=supervisor_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.supervisor_token = data["access_token"]
                self.supervisor_id = data["user_data"]["id"]
                self.log_result("Supervisor Setup", True, "Test supervisor user created and authenticated")
            elif response.status_code == 400 and "already registered" in response.text:
                # Try to login instead
                login_data = {
                    "email": "supervisor.test@research.lab",
                    "password": "TestPassword123!"
                }
                response = await self.client.post(f"{API_BASE}/auth/login", json=login_data)
                if response.status_code == 200:
                    data = response.json()
                    self.supervisor_token = data["access_token"]
                    self.supervisor_id = data["user_data"]["id"]
                    self.log_result("Supervisor Setup", True, "Logged in with existing test supervisor user")
                else:
                    self.log_result("Supervisor Setup", False, f"Failed to login supervisor: {response.status_code}")
                    return False
            else:
                self.log_result("Supervisor Setup", False, f"Failed to setup supervisor: {response.status_code}")
                return False
            
            # Setup student user
            student_data = {
                "email": "student.test@research.lab",
                "password": "TestPassword123!",
                "full_name": "Jane Test Student",
                "role": "student",
                "student_id": "CS2024002",
                "department": "Computer Science",
                "program_type": "phd_research",
                "supervisor_email": "supervisor.test@research.lab"
            }
            
            response = await self.client.post(f"{API_BASE}/auth/register", json=student_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.student_token = data["access_token"]
                self.student_id = data["user_data"]["id"]
                self.log_result("Student Setup", True, "Test student user created and authenticated")
                
                # Approve the student user if needed
                await self.approve_student_if_needed()
                
            elif response.status_code == 400 and "already registered" in response.text:
                # Try to login instead
                login_data = {
                    "email": "student.test@research.lab",
                    "password": "TestPassword123!"
                }
                response = await self.client.post(f"{API_BASE}/auth/login", json=login_data)
                if response.status_code == 200:
                    data = response.json()
                    self.student_token = data["access_token"]
                    self.student_id = data["user_data"]["id"]
                    self.log_result("Student Setup", True, "Logged in with existing test student user")
                    
                    # Approve the student user if needed
                    await self.approve_student_if_needed()
                else:
                    self.log_result("Student Setup", False, f"Failed to login student: {response.status_code}")
                    return False
            else:
                self.log_result("Student Setup", False, f"Failed to setup student: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_result("User Setup", False, f"Exception during user setup: {str(e)}")
            return False
    
    async def approve_student_if_needed(self):
        """Approve student user if they are not approved yet"""
        try:
            # Test if student can access system
            response = await self.client.get(
                f"{API_BASE}/research-logs",
                headers=self.get_student_headers()
            )
            
            if response.status_code == 403 and "pending approval" in response.text:
                # Student needs approval, approve them
                response = await self.client.post(
                    f"{API_BASE}/users/{self.student_id}/approve",
                    headers=self.get_supervisor_headers()
                )
                
                if response.status_code == 200:
                    self.log_result("Student Auto-Approval", True, "Student user approved for testing")
                else:
                    self.log_result("Student Auto-Approval", False, f"Failed to approve student: {response.status_code}")
            elif response.status_code == 200:
                self.log_result("Student Already Approved", True, "Student user already approved")
                
        except Exception as e:
            self.log_result("Student Approval Check", False, f"Exception: {str(e)}")
    
    def get_supervisor_headers(self):
        """Get supervisor authorization headers"""
        return {"Authorization": f"Bearer {self.supervisor_token}"}
    
    def get_student_headers(self):
        """Get student authorization headers"""
        return {"Authorization": f"Bearer {self.student_token}"}
    
    async def test_research_log_submissions_status_fix(self):
        """Test 1: Research Log Submissions Status Fix"""
        print("\n🔍 TESTING: Research Log Submissions Status Fix")
        
        try:
            # Step 1: Create research log as student
            research_log_data = {
                "activity_type": "experiment",
                "title": "Machine Learning Model Training",
                "description": "Training neural network for image classification",
                "duration_hours": 4.5,
                "findings": "Model achieved 92% accuracy on validation set",
                "challenges": "Overfitting issues with small dataset",
                "next_steps": "Implement data augmentation techniques",
                "tags": ["machine-learning", "neural-networks", "training"]
            }
            
            response = await self.client.post(
                f"{API_BASE}/research-logs",
                json=research_log_data,
                headers=self.get_student_headers()
            )
            
            if response.status_code in [200, 201]:
                log_data = response.json()
                log_id = log_data["id"]
                self.log_result("Research Log Creation", True, "Student successfully created research log")
                
                # Step 2: Test that student can see their own research logs
                response = await self.client.get(
                    f"{API_BASE}/research-logs",
                    headers=self.get_student_headers()
                )
                
                if response.status_code == 200:
                    logs = response.json()
                    student_log_found = False
                    for log in logs:
                        if log.get("id") == log_id and (log.get("user_id") == self.student_id or log.get("student_id") == self.student_id):
                            student_log_found = True
                            break
                    
                    if student_log_found:
                        self.log_result("Student Log Visibility", True, "Student can see their own research logs")
                    else:
                        self.log_result("Student Log Visibility", False, "Student cannot see their own research logs - filtering issue")
                else:
                    self.log_result("Student Log Visibility", False, f"Failed to retrieve logs as student: {response.status_code}")
                
                # Step 3: Test supervisor can see student logs with student info
                response = await self.client.get(
                    f"{API_BASE}/research-logs",
                    headers=self.get_supervisor_headers()
                )
                
                if response.status_code == 200:
                    logs = response.json()
                    supervisor_can_see_student_log = False
                    student_info_present = False
                    
                    for log in logs:
                        if log.get("id") == log_id:
                            supervisor_can_see_student_log = True
                            if log.get("student_name") or log.get("student_id") or log.get("student_email"):
                                student_info_present = True
                            break
                    
                    if supervisor_can_see_student_log:
                        self.log_result("Supervisor Log Visibility", True, "Supervisor can see student research logs")
                        
                        if student_info_present:
                            self.log_result("Student Info in Logs", True, "Research logs include student information for supervisor view")
                        else:
                            self.log_result("Student Info in Logs", False, "Research logs missing student information for supervisor view")
                    else:
                        self.log_result("Supervisor Log Visibility", False, "Supervisor cannot see student research logs")
                else:
                    self.log_result("Supervisor Log Visibility", False, f"Failed to retrieve logs as supervisor: {response.status_code}")
                
                return log_id  # Return for use in review test
                
            else:
                self.log_result("Research Log Creation", False, f"Failed to create research log: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Research Log Status Test", False, f"Exception: {str(e)}")
            return None
    
    async def test_supervisor_review_system(self, log_id=None):
        """Test 2: Supervisor Review System"""
        print("\n🔍 TESTING: Supervisor Review System")
        
        try:
            if not log_id:
                # Create a research log if not provided
                research_log_data = {
                    "activity_type": "literature_review",
                    "title": "Review of Deep Learning Papers",
                    "description": "Comprehensive review of recent deep learning literature",
                    "duration_hours": 6.0,
                    "findings": "Identified key trends in transformer architectures",
                    "challenges": "Large volume of papers to review",
                    "next_steps": "Focus on specific application domains",
                    "tags": ["literature-review", "deep-learning"]
                }
                
                response = await self.client.post(
                    f"{API_BASE}/research-logs",
                    json=research_log_data,
                    headers=self.get_student_headers()
                )
                
                if response.status_code in [200, 201]:
                    log_data = response.json()
                    log_id = log_data["id"]
                    self.log_result("Review Test Log Creation", True, "Created research log for review testing")
                else:
                    self.log_result("Review Test Log Creation", False, "Failed to create research log for review testing")
                    return
            
            # Test 1: Accept review
            review_data = {
                "action": "accepted",
                "feedback": "Excellent work! The research methodology is sound and findings are well-documented."
            }
            
            response = await self.client.post(
                f"{API_BASE}/research-logs/{log_id}/review",
                json=review_data,
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                self.log_result("Review Accept", True, "Supervisor can accept research logs")
                
                # Verify review status is stored
                response = await self.client.get(
                    f"{API_BASE}/research-logs",
                    headers=self.get_student_headers()
                )
                
                if response.status_code == 200:
                    logs = response.json()
                    reviewed_log = None
                    for log in logs:
                        if log.get("id") == log_id:
                            reviewed_log = log
                            break
                    
                    if reviewed_log and reviewed_log.get("review_status") == "accepted":
                        self.log_result("Review Status Storage", True, "Review status properly stored and retrievable")
                        
                        if reviewed_log.get("review_feedback"):
                            self.log_result("Review Feedback Storage", True, "Review feedback properly stored")
                        else:
                            self.log_result("Review Feedback Storage", False, "Review feedback not stored")
                            
                        if reviewed_log.get("reviewer_name"):
                            self.log_result("Reviewer Info Storage", True, "Reviewer information properly stored")
                        else:
                            self.log_result("Reviewer Info Storage", False, "Reviewer information not stored")
                    else:
                        self.log_result("Review Status Storage", False, "Review status not properly stored")
                else:
                    self.log_result("Review Status Storage", False, "Failed to retrieve logs to verify review status")
            else:
                self.log_result("Review Accept", False, f"Failed to accept research log: {response.status_code} - {response.text}")
            
            # Test 2: Revision review
            review_data = {
                "action": "revision",
                "feedback": "Good work, but please add more details about the experimental setup and include statistical analysis."
            }
            
            response = await self.client.post(
                f"{API_BASE}/research-logs/{log_id}/review",
                json=review_data,
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                self.log_result("Review Revision", True, "Supervisor can request revisions")
            else:
                self.log_result("Review Revision", False, f"Failed to request revision: {response.status_code}")
            
            # Test 3: Reject review
            review_data = {
                "action": "rejected",
                "feedback": "The research methodology needs significant improvement. Please consult with me before proceeding."
            }
            
            response = await self.client.post(
                f"{API_BASE}/research-logs/{log_id}/review",
                json=review_data,
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                self.log_result("Review Reject", True, "Supervisor can reject research logs")
            else:
                self.log_result("Review Reject", False, f"Failed to reject research log: {response.status_code}")
            
            # Test 4: Student cannot review (authorization test)
            review_data = {
                "action": "accepted",
                "feedback": "Student trying to review"
            }
            
            response = await self.client.post(
                f"{API_BASE}/research-logs/{log_id}/review",
                json=review_data,
                headers=self.get_student_headers()
            )
            
            if response.status_code == 403:
                self.log_result("Review Authorization", True, "Students properly blocked from reviewing")
            else:
                self.log_result("Review Authorization", False, f"Students not properly blocked from reviewing: {response.status_code}")
            
            # Test 5: Invalid action validation
            review_data = {
                "action": "invalid_action",
                "feedback": "Testing invalid action"
            }
            
            response = await self.client.post(
                f"{API_BASE}/research-logs/{log_id}/review",
                json=review_data,
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 400:
                self.log_result("Review Validation", True, "Invalid review actions properly rejected")
            else:
                self.log_result("Review Validation", False, f"Invalid actions not properly validated: {response.status_code}")
                
        except Exception as e:
            self.log_result("Supervisor Review Test", False, f"Exception: {str(e)}")
    
    async def test_user_registration_approval_system(self):
        """Test 3: User Registration Approval System"""
        print("\n🔍 TESTING: User Registration Approval System")
        
        try:
            # Test 1: Create unapproved user
            unapproved_user_data = {
                "email": "unapproved.student@research.lab",
                "password": "TestPassword123!",
                "full_name": "Unapproved Test Student",
                "role": "student",
                "student_id": "CS2024003",
                "department": "Computer Science",
                "program_type": "msc_research",
                "supervisor_email": "supervisor.test@research.lab"
            }
            
            response = await self.client.post(f"{API_BASE}/auth/register", json=unapproved_user_data)
            
            if response.status_code in [200, 201]:
                unapproved_data = response.json()
                unapproved_user_id = unapproved_data["user_data"]["id"]
                unapproved_token = unapproved_data["access_token"]
                self.log_result("Unapproved User Creation", True, "Unapproved user created successfully")
                
                # Test 2: Check if unapproved user gets 403 when accessing system
                response = await self.client.get(
                    f"{API_BASE}/research-logs",
                    headers={"Authorization": f"Bearer {unapproved_token}"}
                )
                
                if response.status_code == 403:
                    self.log_result("Unapproved User Access Block", True, "Unapproved users properly blocked from system access")
                else:
                    self.log_result("Unapproved User Access Block", False, f"Unapproved users not properly blocked: {response.status_code}")
                
                # Test 3: Get pending registrations (supervisor view)
                response = await self.client.get(
                    f"{API_BASE}/pending-registrations",
                    headers=self.get_supervisor_headers()
                )
                
                if response.status_code == 200:
                    pending_users = response.json()
                    pending_user_found = False
                    for user in pending_users:
                        if user.get("id") == unapproved_user_id:
                            pending_user_found = True
                            break
                    
                    if pending_user_found:
                        self.log_result("Pending Registrations Endpoint", True, "Pending registrations endpoint working")
                    else:
                        self.log_result("Pending Registrations Endpoint", False, "Unapproved user not found in pending registrations")
                elif response.status_code == 404:
                    self.log_result("Pending Registrations Endpoint", False, "GET /api/pending-registrations endpoint not found - needs implementation")
                else:
                    self.log_result("Pending Registrations Endpoint", False, f"Pending registrations endpoint failed: {response.status_code}")
                
                # Test 4: Approve user
                response = await self.client.post(
                    f"{API_BASE}/users/{unapproved_user_id}/approve",
                    headers=self.get_supervisor_headers()
                )
                
                if response.status_code == 200:
                    self.log_result("User Approval", True, "User approval endpoint working")
                    
                    # Test 5: Check if approved user can now access system
                    response = await self.client.get(
                        f"{API_BASE}/research-logs",
                        headers={"Authorization": f"Bearer {unapproved_token}"}
                    )
                    
                    if response.status_code == 200:
                        self.log_result("Approved User Access", True, "Approved users can access system")
                    else:
                        self.log_result("Approved User Access", False, f"Approved users still blocked: {response.status_code}")
                        
                elif response.status_code == 404:
                    self.log_result("User Approval", False, "POST /api/users/{user_id}/approve endpoint not found - needs implementation")
                else:
                    self.log_result("User Approval", False, f"User approval failed: {response.status_code}")
                
                # Test 6: Create another unapproved user for rejection test
                reject_user_data = {
                    "email": "reject.student@research.lab",
                    "password": "TestPassword123!",
                    "full_name": "Reject Test Student",
                    "role": "student",
                    "student_id": "CS2024004",
                    "department": "Computer Science",
                    "program_type": "msc_research",
                    "supervisor_email": "supervisor.test@research.lab"
                }
                
                response = await self.client.post(f"{API_BASE}/auth/register", json=reject_user_data)
                
                if response.status_code in [200, 201]:
                    reject_data = response.json()
                    reject_user_id = reject_data["user_data"]["id"]
                    
                    # Test 7: Reject user
                    response = await self.client.post(
                        f"{API_BASE}/users/{reject_user_id}/reject",
                        headers=self.get_supervisor_headers()
                    )
                    
                    if response.status_code == 200:
                        self.log_result("User Rejection", True, "User rejection endpoint working")
                    elif response.status_code == 404:
                        self.log_result("User Rejection", False, "POST /api/users/{user_id}/reject endpoint not found - needs implementation")
                    else:
                        self.log_result("User Rejection", False, f"User rejection failed: {response.status_code}")
                else:
                    self.log_result("Reject User Creation", False, "Failed to create user for rejection test")
                    
            else:
                self.log_result("Unapproved User Creation", False, f"Failed to create unapproved user: {response.status_code}")
                
        except Exception as e:
            self.log_result("User Approval System Test", False, f"Exception: {str(e)}")
    
    async def test_enhanced_user_management_endpoints(self):
        """Test 4: Enhanced User Management Endpoints"""
        print("\n🔍 TESTING: Enhanced User Management Endpoints")
        
        try:
            # Test 1: PUT /api/users/{user_id}/edit for profile editing
            edit_data = {
                "full_name": "Updated Test Student Name",
                "contact_number": "+1234567890",
                "research_area": "Updated Research Area"
            }
            
            response = await self.client.put(
                f"{API_BASE}/users/{self.student_id}/edit",
                json=edit_data,
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                self.log_result("User Profile Edit", True, "User profile edit endpoint working")
            elif response.status_code == 404:
                self.log_result("User Profile Edit", False, "PUT /api/users/{user_id}/edit endpoint not found - needs implementation")
            else:
                self.log_result("User Profile Edit", False, f"Profile edit failed: {response.status_code}")
            
            # Test 2: POST /api/users/{user_id}/freeze for access control
            response = await self.client.post(
                f"{API_BASE}/users/{self.student_id}/freeze",
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                self.log_result("User Freeze", True, "User freeze endpoint working")
                
                # Test if frozen user cannot access system
                response = await self.client.get(
                    f"{API_BASE}/research-logs",
                    headers=self.get_student_headers()
                )
                
                if response.status_code == 403:
                    self.log_result("Frozen User Access Block", True, "Frozen users properly blocked from system access")
                else:
                    self.log_result("Frozen User Access Block", False, f"Frozen users not properly blocked: {response.status_code}")
                    
            elif response.status_code == 404:
                self.log_result("User Freeze", False, "POST /api/users/{user_id}/freeze endpoint not found - needs implementation")
            else:
                self.log_result("User Freeze", False, f"User freeze failed: {response.status_code}")
            
            # Test 3: POST /api/users/{user_id}/unfreeze for access restoration
            response = await self.client.post(
                f"{API_BASE}/users/{self.student_id}/unfreeze",
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                self.log_result("User Unfreeze", True, "User unfreeze endpoint working")
                
                # Test if unfrozen user can access system again
                response = await self.client.get(
                    f"{API_BASE}/research-logs",
                    headers=self.get_student_headers()
                )
                
                if response.status_code == 200:
                    self.log_result("Unfrozen User Access Restore", True, "Unfrozen users can access system again")
                else:
                    self.log_result("Unfrozen User Access Restore", False, f"Unfrozen users still blocked: {response.status_code}")
                    
            elif response.status_code == 404:
                self.log_result("User Unfreeze", False, "POST /api/users/{user_id}/unfreeze endpoint not found - needs implementation")
            else:
                self.log_result("User Unfreeze", False, f"User unfreeze failed: {response.status_code}")
            
            # Test 4: Authorization - student cannot manage other users
            response = await self.client.post(
                f"{API_BASE}/users/{self.supervisor_id}/freeze",
                headers=self.get_student_headers()
            )
            
            if response.status_code == 403:
                self.log_result("User Management Authorization", True, "Students properly blocked from user management")
            else:
                self.log_result("User Management Authorization", False, f"Students not properly blocked from user management: {response.status_code}")
            
            # Test 5: DELETE /api/users/{user_id} for profile deletion (careful test)
            # Create a temporary user for deletion test
            temp_user_data = {
                "email": "temp.delete@research.lab",
                "password": "TestPassword123!",
                "full_name": "Temporary Delete User",
                "role": "student",
                "student_id": "CS2024999",
                "department": "Computer Science",
                "supervisor_email": "supervisor.test@research.lab"
            }
            
            response = await self.client.post(f"{API_BASE}/auth/register", json=temp_user_data)
            
            if response.status_code in [200, 201]:
                temp_data = response.json()
                temp_user_id = temp_data["user_data"]["id"]
                
                # Test deletion
                response = await self.client.delete(
                    f"{API_BASE}/users/{temp_user_id}",
                    headers=self.get_supervisor_headers()
                )
                
                if response.status_code == 200:
                    self.log_result("User Deletion", True, "User deletion endpoint working")
                elif response.status_code == 404:
                    self.log_result("User Deletion", False, "DELETE /api/users/{user_id} endpoint not found - needs implementation")
                else:
                    self.log_result("User Deletion", False, f"User deletion failed: {response.status_code}")
            else:
                self.log_result("Temp User Creation", False, "Failed to create temporary user for deletion test")
                
        except Exception as e:
            self.log_result("Enhanced User Management Test", False, f"Exception: {str(e)}")
    
    async def run_all_critical_tests(self):
        """Run all critical fix tests"""
        print("🚀 STARTING CRITICAL FIXES TESTING")
        print("=" * 60)
        
        # Setup test users
        if not await self.setup_test_users():
            print("❌ Cannot proceed without authenticated users")
            return
        
        # Run all critical tests
        log_id = await self.test_research_log_submissions_status_fix()
        await self.test_supervisor_review_system(log_id)
        await self.test_user_registration_approval_system()
        await self.test_enhanced_user_management_endpoints()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 CRITICAL FIXES TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if "✅ PASS" in r["status"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            print(f"{result['status']}: {result['test']} - {result['message']}")
        
        return passed_tests, failed_tests

async def main():
    async with CriticalFixesTester() as tester:
        await tester.run_all_critical_tests()

if __name__ == "__main__":
    asyncio.run(main())
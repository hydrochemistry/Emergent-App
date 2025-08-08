#!/usr/bin/env python3

import asyncio
import httpx
import json
import os
from datetime import datetime, timedelta
import sys

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://c5e539fb-9522-486d-b275-1bb355b557d8.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class RealUserIssuesTester:
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
        """Create supervisor and student users with proper relationship"""
        try:
            # Create supervisor first
            supervisor_data = {
                "email": "real.supervisor@testlab.com",
                "password": "RealTest123!",
                "full_name": "Dr. Real Supervisor",
                "role": "supervisor",
                "department": "Computer Science",
                "research_area": "AI Research",
                "lab_name": "Real Test Lab"
            }
            
            response = await self.client.post(f"{API_BASE}/auth/register", json=supervisor_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.supervisor_token = data["access_token"]
                self.supervisor_id = data["user_data"]["id"]
                self.log_result("Supervisor Setup", True, "Test supervisor created")
            elif response.status_code == 400 and "already registered" in response.text:
                # Login existing supervisor
                login_data = {"email": "real.supervisor@testlab.com", "password": "RealTest123!"}
                response = await self.client.post(f"{API_BASE}/auth/login", json=login_data)
                if response.status_code == 200:
                    data = response.json()
                    self.supervisor_token = data["access_token"]
                    self.supervisor_id = data["user_data"]["id"]
                    self.log_result("Supervisor Setup", True, "Using existing supervisor")
                else:
                    self.log_result("Supervisor Setup", False, f"Login failed: {response.status_code}")
                    return False
            else:
                self.log_result("Supervisor Setup", False, f"Registration failed: {response.status_code}")
                return False
            
            # Create student with supervisor assignment
            student_data = {
                "email": "real.student@testlab.com",
                "password": "RealTest123!",
                "full_name": "Real Test Student",
                "role": "student",
                "student_id": "RT2024001",
                "department": "Computer Science",
                "program_type": "phd_research",
                "supervisor_email": "real.supervisor@testlab.com",
                "research_area": "Machine Learning"
            }
            
            response = await self.client.post(f"{API_BASE}/auth/register", json=student_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.student_token = data["access_token"]
                self.student_id = data["user_data"]["id"]
                self.log_result("Student Setup", True, "Test student created with supervisor assignment")
            elif response.status_code == 400 and "already registered" in response.text:
                # Login existing student
                login_data = {"email": "real.student@testlab.com", "password": "RealTest123!"}
                response = await self.client.post(f"{API_BASE}/auth/login", json=login_data)
                if response.status_code == 200:
                    data = response.json()
                    self.student_token = data["access_token"]
                    self.student_id = data["user_data"]["id"]
                    self.log_result("Student Setup", True, "Using existing student")
                else:
                    self.log_result("Student Setup", False, f"Student login failed: {response.status_code}")
                    return False
            else:
                self.log_result("Student Setup", False, f"Student registration failed: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_result("User Setup", False, f"Exception: {str(e)}")
            return False
    
    def get_supervisor_headers(self):
        return {"Authorization": f"Bearer {self.supervisor_token}"}
    
    def get_student_headers(self):
        return {"Authorization": f"Bearer {self.student_token}"}
    
    async def test_user_management_panel_empty_issue(self):
        """Test Issue 1: User Management Panel Empty - Test GET /api/students and user management endpoints"""
        print("\n🔍 TESTING: User Management Panel Empty Issue")
        
        try:
            # Test GET /api/students endpoint (if it exists)
            response = await self.client.get(
                f"{API_BASE}/students",
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                students = response.json()
                if isinstance(students, list) and len(students) > 0:
                    self.log_result("GET /api/students", True, f"Found {len(students)} students")
                    # Check if our test student is in the list
                    found_test_student = any(s.get("id") == self.student_id for s in students)
                    if found_test_student:
                        self.log_result("Student Visibility", True, "Test student visible to supervisor")
                    else:
                        self.log_result("Student Visibility", False, "Test student NOT visible to supervisor")
                else:
                    self.log_result("GET /api/students", False, "Students endpoint returns empty list")
            elif response.status_code == 404:
                self.log_result("GET /api/students", False, "GET /api/students endpoint does not exist")
                
                # Try alternative: GET /api/users with role filter
                response = await self.client.get(
                    f"{API_BASE}/users?role=student",
                    headers=self.get_supervisor_headers()
                )
                
                if response.status_code == 200:
                    users = response.json()
                    students = [u for u in users if u.get("role") == "student"]
                    if students:
                        self.log_result("Alternative Students Query", True, f"Found {len(students)} students via /api/users")
                    else:
                        self.log_result("Alternative Students Query", False, "No students found via /api/users")
                else:
                    self.log_result("Alternative Students Query", False, f"Users endpoint failed: {response.status_code}")
            else:
                self.log_result("GET /api/students", False, f"Students endpoint failed: {response.status_code} - {response.text}")
            
            # Test new user management endpoints
            if self.student_id:
                # Test PUT /api/users/{user_id}/edit
                edit_data = {
                    "full_name": "Updated Real Test Student",
                    "research_area": "Updated Machine Learning"
                }
                
                response = await self.client.put(
                    f"{API_BASE}/users/{self.student_id}/edit",
                    json=edit_data,
                    headers=self.get_supervisor_headers()
                )
                
                if response.status_code == 200:
                    self.log_result("User Edit Endpoint", True, "PUT /api/users/{user_id}/edit working")
                elif response.status_code == 404:
                    self.log_result("User Edit Endpoint", False, "PUT /api/users/{user_id}/edit endpoint missing")
                else:
                    self.log_result("User Edit Endpoint", False, f"Edit endpoint failed: {response.status_code}")
                
                # Test POST /api/users/{user_id}/freeze
                response = await self.client.post(
                    f"{API_BASE}/users/{self.student_id}/freeze",
                    headers=self.get_supervisor_headers()
                )
                
                if response.status_code == 200:
                    self.log_result("User Freeze Endpoint", True, "POST /api/users/{user_id}/freeze working")
                elif response.status_code == 404:
                    self.log_result("User Freeze Endpoint", False, "POST /api/users/{user_id}/freeze endpoint missing")
                else:
                    self.log_result("User Freeze Endpoint", False, f"Freeze endpoint failed: {response.status_code}")
                
                # Test DELETE /api/users/{user_id} (be careful with this one)
                # We'll test with a non-existent user ID to avoid deleting our test user
                response = await self.client.delete(
                    f"{API_BASE}/users/non-existent-user-id",
                    headers=self.get_supervisor_headers()
                )
                
                if response.status_code == 404:
                    self.log_result("User Delete Endpoint", True, "DELETE /api/users/{user_id} endpoint exists (returned 404 for non-existent user)")
                elif response.status_code == 405:
                    self.log_result("User Delete Endpoint", False, "DELETE /api/users/{user_id} endpoint missing (405 Method Not Allowed)")
                else:
                    self.log_result("User Delete Endpoint", True, f"DELETE endpoint exists (status: {response.status_code})")
                
        except Exception as e:
            self.log_result("User Management Test", False, f"Exception: {str(e)}")
    
    async def test_students_see_empty_data_issue(self):
        """Test Issue 2: Students See Empty Data - Test lab-wide data visibility for students"""
        print("\n🔍 TESTING: Students See Empty Data Issue")
        
        try:
            # First, create some test data as supervisor
            await self.create_test_lab_data()
            
            # Test GET /api/research-logs as student
            response = await self.client.get(
                f"{API_BASE}/research-logs",
                headers=self.get_student_headers()
            )
            
            if response.status_code == 200:
                logs = response.json()
                if isinstance(logs, list) and len(logs) > 0:
                    self.log_result("Student Research Logs Access", True, f"Student can see {len(logs)} research logs")
                    
                    # Check if student sees lab-wide data (not just their own)
                    supervisor_logs = [log for log in logs if log.get("user_id") == self.supervisor_id]
                    if supervisor_logs:
                        self.log_result("Lab-wide Research Logs", True, "Student can see supervisor's research logs (lab-wide data)")
                    else:
                        self.log_result("Lab-wide Research Logs", False, "Student cannot see supervisor's research logs")
                else:
                    self.log_result("Student Research Logs Access", False, "Student sees empty research logs list")
            else:
                self.log_result("Student Research Logs Access", False, f"Research logs failed: {response.status_code}")
            
            # Test GET /api/publications as student
            response = await self.client.get(
                f"{API_BASE}/publications",
                headers=self.get_student_headers()
            )
            
            if response.status_code == 200:
                publications = response.json()
                if isinstance(publications, list) and len(publications) > 0:
                    self.log_result("Student Publications Access", True, f"Student can see {len(publications)} publications")
                else:
                    self.log_result("Student Publications Access", False, "Student sees empty publications list")
            else:
                self.log_result("Student Publications Access", False, f"Publications failed: {response.status_code}")
            
            # Test GET /api/grants as student
            response = await self.client.get(
                f"{API_BASE}/grants",
                headers=self.get_student_headers()
            )
            
            if response.status_code == 200:
                grants = response.json()
                if isinstance(grants, list) and len(grants) > 0:
                    self.log_result("Student Grants Access", True, f"Student can see {len(grants)} grants")
                else:
                    self.log_result("Student Grants Access", False, "Student sees empty grants list")
            else:
                self.log_result("Student Grants Access", False, f"Grants failed: {response.status_code}")
            
            # Verify student has supervisor_id properly assigned
            response = await self.client.get(
                f"{API_BASE}/users/profile",
                headers=self.get_student_headers()
            )
            
            if response.status_code == 200:
                profile = response.json()
                if profile.get("supervisor_id") == self.supervisor_id:
                    self.log_result("Student Supervisor Assignment", True, "Student has correct supervisor_id assigned")
                else:
                    self.log_result("Student Supervisor Assignment", False, f"Student supervisor_id mismatch: expected {self.supervisor_id}, got {profile.get('supervisor_id')}")
            else:
                self.log_result("Student Supervisor Assignment", False, f"Profile access failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("Student Data Access Test", False, f"Exception: {str(e)}")
    
    async def create_test_lab_data(self):
        """Create test data for the lab"""
        try:
            # Create a research log as supervisor
            research_log_data = {
                "activity_type": "experiment",
                "title": "Supervisor Research Log for Lab Data",
                "description": "This should be visible to students in the lab",
                "duration_hours": 3.0,
                "findings": "Important lab findings",
                "challenges": "Lab challenges",
                "next_steps": "Lab next steps",
                "tags": ["lab-data", "supervisor"]
            }
            
            await self.client.post(
                f"{API_BASE}/research-logs",
                json=research_log_data,
                headers=self.get_supervisor_headers()
            )
            
            # Create a grant as supervisor
            grant_data = {
                "title": "Test Lab Grant",
                "funding_agency": "Test Funding Agency",
                "total_amount": 50000.0,
                "status": "active",
                "start_date": datetime.utcnow().isoformat(),
                "end_date": (datetime.utcnow() + timedelta(days=365)).isoformat(),
                "description": "Test grant for lab visibility"
            }
            
            await self.client.post(
                f"{API_BASE}/grants",
                json=grant_data,
                headers=self.get_supervisor_headers()
            )
            
            # Create a bulletin/announcement
            bulletin_data = {
                "title": "Lab Announcement",
                "content": "Important lab announcement for all members",
                "category": "general",
                "is_highlight": True
            }
            
            await self.client.post(
                f"{API_BASE}/bulletins",
                json=bulletin_data,
                headers=self.get_supervisor_headers()
            )
            
        except Exception as e:
            print(f"Warning: Could not create all test data: {str(e)}")
    
    async def test_research_log_creation_still_failing(self):
        """Test Issue 3: Research Log Creation Still Failing - Enhanced error logging"""
        print("\n🔍 TESTING: Research Log Creation Still Failing")
        
        try:
            # Test with exact frontend data format that users are sending
            frontend_data = {
                "activity_type": "experiment",
                "title": "Real User Research Log Test",
                "description": "Testing with exact data format from frontend",
                "findings": "Test findings from real user scenario",
                "challenges": "Real user challenges",
                "next_steps": "Real user next steps",
                "duration_hours": 4.5,
                "tags": ["real-user-test", "frontend-format"],
                "log_date": "2025-01-15",
                "log_time": "14:30"
            }
            
            response = await self.client.post(
                f"{API_BASE}/research-logs",
                json=frontend_data,
                headers=self.get_student_headers()
            )
            
            if response.status_code in [200, 201]:
                log_data = response.json()
                self.log_result("Research Log Creation (Student)", True, "Student can create research logs successfully")
                
                # Verify the created log has all expected fields
                expected_fields = ["id", "title", "description", "activity_type", "findings", "challenges", "next_steps"]
                missing_fields = [field for field in expected_fields if field not in log_data]
                
                if not missing_fields:
                    self.log_result("Research Log Fields", True, "All expected fields present in response")
                else:
                    self.log_result("Research Log Fields", False, f"Missing fields: {missing_fields}")
                
                # Test with minimal data
                minimal_data = {
                    "activity_type": "writing",
                    "title": "Minimal Research Log",
                    "description": "Testing with minimal required fields"
                }
                
                response = await self.client.post(
                    f"{API_BASE}/research-logs",
                    json=minimal_data,
                    headers=self.get_student_headers()
                )
                
                if response.status_code in [200, 201]:
                    self.log_result("Minimal Research Log", True, "Research log creation works with minimal data")
                else:
                    self.log_result("Minimal Research Log", False, f"Minimal data failed: {response.status_code} - {response.text}")
                
                # Test with invalid data to check error handling
                invalid_data = {
                    "activity_type": "invalid_type",
                    "title": "",  # Empty title
                    "description": "Testing invalid data"
                }
                
                response = await self.client.post(
                    f"{API_BASE}/research-logs",
                    json=invalid_data,
                    headers=self.get_student_headers()
                )
                
                if response.status_code == 400:
                    self.log_result("Research Log Validation", True, "Proper validation for invalid data")
                else:
                    self.log_result("Research Log Validation", False, f"Invalid data not properly rejected: {response.status_code}")
                
            else:
                self.log_result("Research Log Creation (Student)", False, f"Research log creation failed: {response.status_code} - {response.text}")
                
                # Enhanced error logging
                error_details = {
                    "status_code": response.status_code,
                    "response_text": response.text,
                    "request_data": frontend_data
                }
                self.log_result("Research Log Error Details", False, "Detailed error information", error_details)
            
            # Test authentication issues
            response = await self.client.post(
                f"{API_BASE}/research-logs",
                json=frontend_data
                # No headers - unauthenticated request
            )
            
            if response.status_code in [401, 403]:
                self.log_result("Research Log Authentication", True, "Proper authentication required")
            else:
                self.log_result("Research Log Authentication", False, f"Authentication not properly enforced: {response.status_code}")
                
        except Exception as e:
            self.log_result("Research Log Creation Test", False, f"Exception: {str(e)}")
    
    async def test_data_synchronization_verification(self):
        """Test Issue 4: Data Synchronization - Verify students with supervisor_id see lab data"""
        print("\n🔍 TESTING: Data Synchronization Verification")
        
        try:
            # Verify supervisor_id logic is working correctly
            
            # 1. Test that students see the same data as their supervisors
            supervisor_logs_response = await self.client.get(
                f"{API_BASE}/research-logs",
                headers=self.get_supervisor_headers()
            )
            
            student_logs_response = await self.client.get(
                f"{API_BASE}/research-logs",
                headers=self.get_student_headers()
            )
            
            if supervisor_logs_response.status_code == 200 and student_logs_response.status_code == 200:
                supervisor_logs = supervisor_logs_response.json()
                student_logs = student_logs_response.json()
                
                # Check if student sees supervisor's data
                supervisor_log_ids = {log.get("id") for log in supervisor_logs if log.get("user_id") == self.supervisor_id}
                student_visible_supervisor_logs = {log.get("id") for log in student_logs if log.get("user_id") == self.supervisor_id}
                
                if supervisor_log_ids and supervisor_log_ids.issubset(student_visible_supervisor_logs):
                    self.log_result("Research Log Synchronization", True, "Students can see supervisor's research logs")
                elif not supervisor_log_ids:
                    self.log_result("Research Log Synchronization", False, "No supervisor research logs found to test synchronization")
                else:
                    self.log_result("Research Log Synchronization", False, "Students cannot see supervisor's research logs")
            else:
                self.log_result("Research Log Synchronization", False, "Failed to retrieve research logs for comparison")
            
            # 2. Test grants synchronization
            supervisor_grants_response = await self.client.get(
                f"{API_BASE}/grants",
                headers=self.get_supervisor_headers()
            )
            
            student_grants_response = await self.client.get(
                f"{API_BASE}/grants",
                headers=self.get_student_headers()
            )
            
            if supervisor_grants_response.status_code == 200 and student_grants_response.status_code == 200:
                supervisor_grants = supervisor_grants_response.json()
                student_grants = student_grants_response.json()
                
                if len(supervisor_grants) == len(student_grants):
                    self.log_result("Grants Synchronization", True, f"Students see same grants as supervisor ({len(student_grants)} grants)")
                else:
                    self.log_result("Grants Synchronization", False, f"Grant count mismatch: supervisor sees {len(supervisor_grants)}, student sees {len(student_grants)}")
            else:
                self.log_result("Grants Synchronization", False, "Failed to retrieve grants for comparison")
            
            # 3. Test publications synchronization
            supervisor_pubs_response = await self.client.get(
                f"{API_BASE}/publications",
                headers=self.get_supervisor_headers()
            )
            
            student_pubs_response = await self.client.get(
                f"{API_BASE}/publications",
                headers=self.get_student_headers()
            )
            
            if supervisor_pubs_response.status_code == 200 and student_pubs_response.status_code == 200:
                supervisor_pubs = supervisor_pubs_response.json()
                student_pubs = student_pubs_response.json()
                
                if len(supervisor_pubs) == len(student_pubs):
                    self.log_result("Publications Synchronization", True, f"Students see same publications as supervisor ({len(student_pubs)} publications)")
                else:
                    self.log_result("Publications Synchronization", False, f"Publication count mismatch: supervisor sees {len(supervisor_pubs)}, student sees {len(student_pubs)}")
            else:
                self.log_result("Publications Synchronization", False, "Failed to retrieve publications for comparison")
            
            # 4. Test bulletins synchronization
            supervisor_bulletins_response = await self.client.get(
                f"{API_BASE}/bulletins",
                headers=self.get_supervisor_headers()
            )
            
            student_bulletins_response = await self.client.get(
                f"{API_BASE}/bulletins",
                headers=self.get_student_headers()
            )
            
            if supervisor_bulletins_response.status_code == 200 and student_bulletins_response.status_code == 200:
                supervisor_bulletins = supervisor_bulletins_response.json()
                student_bulletins = student_bulletins_response.json()
                
                # Students should see approved bulletins
                approved_bulletins = [b for b in supervisor_bulletins if b.get("status") == "approved"]
                
                if len(student_bulletins) >= len(approved_bulletins):
                    self.log_result("Bulletins Synchronization", True, f"Students can see bulletins ({len(student_bulletins)} visible)")
                else:
                    self.log_result("Bulletins Synchronization", False, f"Students see fewer bulletins than expected")
            else:
                self.log_result("Bulletins Synchronization", False, "Failed to retrieve bulletins for comparison")
                
        except Exception as e:
            self.log_result("Data Synchronization Test", False, f"Exception: {str(e)}")
    
    async def run_all_tests(self):
        """Run all real user issue tests"""
        print("🚨 TESTING REAL USER ISSUES - STOP CLAIMING FALSE SUCCESS")
        print("=" * 70)
        
        # Setup test users
        if not await self.setup_test_users():
            print("❌ Cannot proceed without proper user setup")
            return
        
        # Run the real user issue tests
        await self.test_user_management_panel_empty_issue()
        await self.test_students_see_empty_data_issue()
        await self.test_research_log_creation_still_failing()
        await self.test_data_synchronization_verification()
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 REAL USER ISSUES TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if "✅ PASS" in r["status"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n📋 CRITICAL FINDINGS:")
        critical_failures = []
        for result in self.test_results:
            if "❌ FAIL" in result["status"]:
                critical_failures.append(f"• {result['test']}: {result['message']}")
        
        if critical_failures:
            print("🚨 CRITICAL ISSUES FOUND:")
            for failure in critical_failures:
                print(failure)
        else:
            print("✅ All critical user issues appear to be resolved")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            print(f"{result['status']}: {result['test']} - {result['message']}")
        
        return passed_tests, failed_tests

async def main():
    async with RealUserIssuesTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
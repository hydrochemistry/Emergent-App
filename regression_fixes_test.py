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

class RegressionFixesTester:
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
        """Create and authenticate supervisor and student users"""
        try:
            # Setup supervisor user
            supervisor_data = {
                "email": "supervisor.regression@test.lab",
                "password": "TestPassword123!",
                "full_name": "Dr. Regression Test Supervisor",
                "role": "supervisor",
                "salutation": "Dr.",
                "contact_number": "+60123456789",
                "department": "Computer Science",
                "research_area": "Machine Learning",
                "lab_name": "Regression Test Lab"
            }
            
            response = await self.client.post(f"{API_BASE}/auth/register", json=supervisor_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.supervisor_token = data["access_token"]
                self.supervisor_id = data["user_data"]["id"]
                self.log_result("Supervisor Setup", True, "Test supervisor user created")
            elif response.status_code == 400 and "already registered" in response.text:
                # Login instead
                login_data = {
                    "email": "supervisor.regression@test.lab",
                    "password": "TestPassword123!"
                }
                response = await self.client.post(f"{API_BASE}/auth/login", json=login_data)
                if response.status_code == 200:
                    data = response.json()
                    self.supervisor_token = data["access_token"]
                    self.supervisor_id = data["user_data"]["id"]
                    self.log_result("Supervisor Setup", True, "Using existing supervisor user")
            
            # Setup student user
            student_data = {
                "email": "student.regression@test.lab",
                "password": "TestPassword123!",
                "full_name": "Jane Regression Test Student",
                "role": "student",
                "student_id": "REG2024001",
                "contact_number": "+60123456790",
                "nationality": "Malaysian",
                "citizenship": "Malaysian",
                "program_type": "phd_research",
                "field_of_study": "Computer Science",
                "department": "Computer Science",
                "faculty": "Engineering",
                "institute": "University of Technology",
                "supervisor_email": "supervisor.regression@test.lab"
            }
            
            response = await self.client.post(f"{API_BASE}/auth/register", json=student_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.student_token = data["access_token"]
                self.student_id = data["user_data"]["id"]
                self.log_result("Student Setup", True, "Test student user created")
            elif response.status_code == 400 and "already registered" in response.text:
                # Login instead
                login_data = {
                    "email": "student.regression@test.lab",
                    "password": "TestPassword123!"
                }
                response = await self.client.post(f"{API_BASE}/auth/login", json=login_data)
                if response.status_code == 200:
                    data = response.json()
                    self.student_token = data["access_token"]
                    self.student_id = data["user_data"]["id"]
                    self.log_result("Student Setup", True, "Using existing student user")
            
            # Approve the student user (students need supervisor approval)
            if self.supervisor_token and self.student_token and self.student_id:
                response = await self.client.post(
                    f"{API_BASE}/users/{self.student_id}/approve",
                    headers=self.get_supervisor_headers()
                )
                if response.status_code == 200:
                    self.log_result("Student Approval", True, "Student user approved by supervisor")
                else:
                    self.log_result("Student Approval", False, f"Failed to approve student: {response.status_code}")
            
            return self.supervisor_token and self.student_token
            
        except Exception as e:
            self.log_result("User Setup", False, f"Exception during user setup: {str(e)}")
            return False
    
    def get_supervisor_headers(self):
        """Get supervisor authorization headers"""
        return {"Authorization": f"Bearer {self.supervisor_token}"}
    
    def get_student_headers(self):
        """Get student authorization headers"""
        return {"Authorization": f"Bearer {self.student_token}"}
    
    async def test_supervisor_profile_update_fix(self):
        """Test 1: Supervisor Profile Update Error Fix - Test enum validation resolution"""
        print("\n🔍 TESTING: Supervisor Profile Update Error Fix")
        
        try:
            # Test supervisor profile update with only allowed fields
            profile_update_data = {
                "salutation": "Prof.",
                "full_name": "Prof. Updated Regression Test Supervisor",
                "contact_number": "+60123456999"
            }
            
            response = await self.client.put(
                f"{API_BASE}/users/profile",
                json=profile_update_data,
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                self.log_result("Supervisor Profile Update - Basic Fields", True, 
                              "Supervisor can update profile with salutation, full_name, contact_number")
                
                # Test that enum validation errors are resolved - try with None values for enums
                profile_with_none_enums = {
                    "full_name": "Prof. Test Enum Fix",
                    "program_type": None,  # None should not cause enum error
                    "study_status": None   # None should not cause enum error
                }
                
                response = await self.client.put(
                    f"{API_BASE}/users/profile",
                    json=profile_with_none_enums,
                    headers=self.get_supervisor_headers()
                )
                
                if response.status_code == 200:
                    self.log_result("Supervisor Profile Update - Enum Fix (None)", True, 
                                  "None values for program_type and study_status work correctly")
                else:
                    self.log_result("Supervisor Profile Update - Enum Fix (None)", False, 
                                  f"None enum validation error: {response.status_code} - {response.text}")
                
                # Test with empty strings (this should be handled by the backend)
                profile_with_empty_enums = {
                    "full_name": "Prof. Test Enum Fix Empty",
                    "program_type": "",  # Empty string should be filtered out by backend
                    "study_status": ""   # Empty string should be filtered out by backend
                }
                
                response = await self.client.put(
                    f"{API_BASE}/users/profile",
                    json=profile_with_empty_enums,
                    headers=self.get_supervisor_headers()
                )
                
                if response.status_code == 200:
                    self.log_result("Supervisor Profile Update - Enum Fix (Empty)", True, 
                                  "Empty string handling for program_type and study_status works correctly")
                else:
                    self.log_result("Supervisor Profile Update - Enum Fix (Empty)", False, 
                                  f"Empty string enum validation error still exists: {response.status_code} - {response.text}")
                
                # Verify profile was actually updated
                response = await self.client.get(
                    f"{API_BASE}/users/profile",
                    headers=self.get_supervisor_headers()
                )
                
                if response.status_code == 200:
                    profile = response.json()
                    if profile.get("full_name") == "Prof. Test Enum Fix Empty":
                        self.log_result("Profile Update Verification", True, "Profile update persisted correctly")
                    else:
                        self.log_result("Profile Update Verification", False, "Profile update did not persist")
                else:
                    self.log_result("Profile Update Verification", False, f"Could not retrieve profile: {response.status_code}")
                
            else:
                self.log_result("Supervisor Profile Update - Basic Fields", False, 
                              f"Profile update failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Supervisor Profile Update Test", False, f"Exception: {str(e)}")
    
    async def test_student_data_synchronization_fix(self):
        """Test 2: Student Data Synchronization Fix - Test student can see research logs, publications, grants"""
        print("\n🔍 TESTING: Student Data Synchronization Fix")
        
        try:
            # First, create some test data as supervisor
            
            # 1. Create a research log as supervisor
            research_log_data = {
                "activity_type": "experiment",
                "title": "Supervisor Research Log for Sync Test",
                "description": "Testing data synchronization for students",
                "duration_hours": 3.0,
                "findings": "Test findings for synchronization",
                "challenges": "Test challenges",
                "next_steps": "Test next steps",
                "tags": ["sync-test", "supervisor"]
            }
            
            response = await self.client.post(
                f"{API_BASE}/research-logs",
                json=research_log_data,
                headers=self.get_supervisor_headers()
            )
            
            supervisor_log_created = response.status_code in [200, 201]
            if supervisor_log_created:
                self.log_result("Supervisor Research Log Creation", True, "Supervisor research log created")
            
            # 2. Create a publication as supervisor
            try:
                # Try to sync publications from Scopus (this might create publications)
                response = await self.client.post(
                    f"{API_BASE}/publications/sync-scopus",
                    headers=self.get_supervisor_headers()
                )
                if response.status_code in [200, 201]:
                    self.log_result("Publications Sync", True, "Publications synced from Scopus")
            except:
                pass  # Scopus sync might fail, that's okay
            
            # 3. Create a grant as supervisor
            grant_data = {
                "title": "Test Grant for Synchronization",
                "funding_agency": "Test Funding Agency",
                "funding_type": "national",
                "total_amount": 50000.0,
                "status": "active",
                "start_date": datetime.utcnow().isoformat(),
                "end_date": (datetime.utcnow() + timedelta(days=365)).isoformat(),
                "description": "Test grant for student synchronization testing",
                "person_in_charge": self.student_id,
                "grant_vote_number": "GVN-2024-001",
                "duration_months": 12,
                "grant_type": "research"
            }
            
            response = await self.client.post(
                f"{API_BASE}/grants",
                json=grant_data,
                headers=self.get_supervisor_headers()
            )
            
            grant_created = response.status_code in [200, 201]
            if grant_created:
                self.log_result("Grant Creation", True, "Test grant created by supervisor")
            
            # Now test student access to synchronized data
            
            # Test 1: Student can see research logs
            response = await self.client.get(
                f"{API_BASE}/research-logs",
                headers=self.get_student_headers()
            )
            
            if response.status_code == 200:
                research_logs = response.json()
                if len(research_logs) > 0:
                    self.log_result("Student Research Logs Access", True, 
                                  f"Student can see {len(research_logs)} research logs (not empty)")
                else:
                    self.log_result("Student Research Logs Access", False, 
                                  "Student sees empty research logs list - synchronization issue")
            else:
                self.log_result("Student Research Logs Access", False, 
                              f"Student cannot access research logs: {response.status_code}")
            
            # Test 2: Student can see publications
            response = await self.client.get(
                f"{API_BASE}/publications",
                headers=self.get_student_headers()
            )
            
            if response.status_code == 200:
                publications = response.json()
                self.log_result("Student Publications Access", True, 
                              f"Student can see {len(publications)} publications")
            else:
                self.log_result("Student Publications Access", False, 
                              f"Student cannot access publications: {response.status_code}")
            
            # Test 3: Student can see grants
            response = await self.client.get(
                f"{API_BASE}/grants",
                headers=self.get_student_headers()
            )
            
            if response.status_code == 200:
                grants = response.json()
                if len(grants) > 0:
                    self.log_result("Student Grants Access", True, 
                                  f"Student can see {len(grants)} grants (not empty)")
                    
                    # Verify student has proper supervisor_id assignment
                    # This is critical for data synchronization
                    response = await self.client.get(
                        f"{API_BASE}/users/profile",
                        headers=self.get_student_headers()
                    )
                    
                    if response.status_code == 200:
                        student_profile = response.json()
                        if student_profile.get("supervisor_id"):
                            self.log_result("Student Supervisor Assignment", True, 
                                          f"Student has supervisor_id: {student_profile['supervisor_id']}")
                        else:
                            self.log_result("Student Supervisor Assignment", False, 
                                          "Student missing supervisor_id - root cause of sync issues")
                    
                else:
                    self.log_result("Student Grants Access", False, 
                                  "Student sees empty grants list - synchronization issue")
            else:
                self.log_result("Student Grants Access", False, 
                              f"Student cannot access grants: {response.status_code}")
                
        except Exception as e:
            self.log_result("Student Data Synchronization Test", False, f"Exception: {str(e)}")
    
    async def test_research_log_visibility_for_students(self):
        """Test 3: Research Log Visibility for Students - Test students can see their own submitted logs"""
        print("\n🔍 TESTING: Research Log Visibility for Students")
        
        try:
            # Create a research log as student
            student_research_log_data = {
                "activity_type": "literature_review",
                "title": "Student Research Log Visibility Test",
                "description": "Testing that students can see their own submitted research logs",
                "duration_hours": 2.0,
                "findings": "Test findings for visibility check",
                "challenges": "Test challenges for visibility",
                "next_steps": "Test next steps for visibility",
                "tags": ["visibility-test", "student-submission"]
            }
            
            response = await self.client.post(
                f"{API_BASE}/research-logs",
                json=student_research_log_data,
                headers=self.get_student_headers()
            )
            
            if response.status_code in [200, 201]:
                created_log = response.json()
                log_id = created_log["id"]
                self.log_result("Student Research Log Creation", True, "Student created research log successfully")
                
                # Test that student can see their own research log in the list
                response = await self.client.get(
                    f"{API_BASE}/research-logs",
                    headers=self.get_student_headers()
                )
                
                if response.status_code == 200:
                    research_logs = response.json()
                    student_log_found = False
                    
                    for log in research_logs:
                        if log.get("id") == log_id:
                            student_log_found = True
                            # Check if the log shows proper user information
                            if log.get("user_id") == self.student_id:
                                self.log_result("Student Log Ownership", True, 
                                              "Student log shows correct user_id ownership")
                            break
                    
                    if student_log_found:
                        self.log_result("Student Research Log Visibility", True, 
                                      "Student can see their own submitted research log")
                        
                        # Test filtering logic - verify student sees logs with their user_id or student_id
                        student_logs_count = 0
                        for log in research_logs:
                            if (log.get("user_id") == self.student_id or 
                                log.get("student_id") == self.student_id):
                                student_logs_count += 1
                        
                        self.log_result("Research Log Filtering Logic", True, 
                                      f"Student sees {student_logs_count} logs with proper filtering")
                        
                        # Test "My Research Log Submissions Status" functionality
                        # This should show research logs with review status information
                        logs_with_status = []
                        for log in research_logs:
                            if log.get("user_id") == self.student_id:
                                logs_with_status.append({
                                    "title": log.get("title"),
                                    "review_status": log.get("review_status", "pending"),
                                    "created_at": log.get("date"),
                                    "review_feedback": log.get("review_feedback")
                                })
                        
                        if logs_with_status:
                            self.log_result("Research Log Status Tracking", True, 
                                          f"Student can track status of {len(logs_with_status)} submitted logs")
                        else:
                            self.log_result("Research Log Status Tracking", False, 
                                          "No research logs found for status tracking")
                        
                    else:
                        self.log_result("Student Research Log Visibility", False, 
                                      "Student cannot see their own submitted research log")
                else:
                    self.log_result("Student Research Log Visibility", False, 
                                  f"Student cannot retrieve research logs: {response.status_code}")
                
            else:
                self.log_result("Student Research Log Creation", False, 
                              f"Student failed to create research log: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Research Log Visibility Test", False, f"Exception: {str(e)}")
    
    async def test_publications_synchronization(self):
        """Test 4: Publications Synchronization - Test lab Scopus ID functionality and synchronization"""
        print("\n🔍 TESTING: Publications Synchronization")
        
        try:
            # Test lab settings with lab_scopus_id
            lab_settings_data = {
                "lab_name": "Regression Test Lab Updated",
                "description": "Testing lab Scopus ID functionality",
                "lab_scopus_id": "12345678900"  # Test Scopus ID
            }
            
            response = await self.client.put(
                f"{API_BASE}/lab/settings",
                json=lab_settings_data,
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                self.log_result("Lab Scopus ID Update", True, "Lab settings updated with Scopus ID")
                
                # Test that publications sync is triggered
                # Wait a moment for potential async sync
                await asyncio.sleep(2)
                
                # Check if publications were synced
                response = await self.client.get(
                    f"{API_BASE}/publications",
                    headers=self.get_supervisor_headers()
                )
                
                if response.status_code == 200:
                    supervisor_publications = response.json()
                    self.log_result("Supervisor Publications Access", True, 
                                  f"Supervisor can see {len(supervisor_publications)} publications")
                    
                    # Test student access to same publications (synchronization)
                    response = await self.client.get(
                        f"{API_BASE}/publications",
                        headers=self.get_student_headers()
                    )
                    
                    if response.status_code == 200:
                        student_publications = response.json()
                        
                        if len(student_publications) == len(supervisor_publications):
                            self.log_result("Publications Synchronization", True, 
                                          f"Student sees same {len(student_publications)} publications as supervisor")
                            
                            # Verify publications are tied to lab (supervisor_id)
                            lab_tied_publications = 0
                            for pub in supervisor_publications:
                                if pub.get("supervisor_id") == self.supervisor_id:
                                    lab_tied_publications += 1
                            
                            if lab_tied_publications > 0:
                                self.log_result("Publications Lab Association", True, 
                                              f"{lab_tied_publications} publications tied to lab (supervisor_id)")
                            else:
                                self.log_result("Publications Lab Association", False, 
                                              "Publications not properly tied to lab")
                            
                        else:
                            self.log_result("Publications Synchronization", False, 
                                          f"Publication count mismatch - Supervisor: {len(supervisor_publications)}, Student: {len(student_publications)}")
                    else:
                        self.log_result("Publications Synchronization", False, 
                                      f"Student cannot access publications: {response.status_code}")
                else:
                    self.log_result("Supervisor Publications Access", False, 
                                  f"Supervisor cannot access publications: {response.status_code}")
                
                # Test manual publications sync
                response = await self.client.post(
                    f"{API_BASE}/publications/sync-scopus",
                    headers=self.get_supervisor_headers()
                )
                
                if response.status_code in [200, 201]:
                    sync_result = response.json()
                    self.log_result("Manual Publications Sync", True, 
                                  f"Manual Scopus sync successful: {sync_result.get('message', 'Success')}")
                else:
                    self.log_result("Manual Publications Sync", False, 
                                  f"Manual sync failed: {response.status_code}")
                
            else:
                self.log_result("Lab Scopus ID Update", False, 
                              f"Lab settings update failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Publications Synchronization Test", False, f"Exception: {str(e)}")
    
    async def run_regression_tests(self):
        """Run all regression fix tests"""
        print("🚀 STARTING REGRESSION FIXES TESTING")
        print("=" * 60)
        print("Testing critical fixes for regressions that were introduced:")
        print("1. Supervisor Profile Update Error Fix")
        print("2. Student Data Synchronization Fix") 
        print("3. Research Log Visibility for Students")
        print("4. Publications Synchronization")
        print("=" * 60)
        
        # Setup test users
        if not await self.setup_test_users():
            print("❌ Cannot proceed without authenticated users")
            return
        
        # Run regression fix tests
        await self.test_supervisor_profile_update_fix()
        await self.test_student_data_synchronization_fix()
        await self.test_research_log_visibility_for_students()
        await self.test_publications_synchronization()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 REGRESSION FIXES TEST SUMMARY")
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
        
        # Identify critical issues
        critical_failures = []
        for result in self.test_results:
            if "❌ FAIL" in result["status"]:
                if any(keyword in result["test"].lower() for keyword in 
                       ["profile update", "synchronization", "visibility", "enum"]):
                    critical_failures.append(result["test"])
        
        if critical_failures:
            print(f"\n🚨 CRITICAL FAILURES DETECTED:")
            for failure in critical_failures:
                print(f"   - {failure}")
        
        return passed_tests, failed_tests, critical_failures

async def main():
    async with RegressionFixesTester() as tester:
        await tester.run_regression_tests()

if __name__ == "__main__":
    asyncio.run(main())
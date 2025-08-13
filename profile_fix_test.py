#!/usr/bin/env python3

import asyncio
import httpx
import json
import os
from datetime import datetime, timedelta
import sys

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://researchpulse.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class ProfileFixTester:
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
        """Create and authenticate test supervisor and student users"""
        try:
            # Setup supervisor user
            supervisor_data = {
                "email": "supervisor.fix@research.lab",
                "password": "TestPassword123!",
                "full_name": "Dr. Fix Test Supervisor",
                "role": "supervisor",
                "salutation": "Dr.",
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
                    "email": "supervisor.fix@research.lab",
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
                self.log_result("Supervisor Setup", False, f"Failed to setup supervisor: {response.status_code} - {response.text}")
                return False
            
            # Setup student user
            student_data = {
                "email": "student.fix@research.lab",
                "password": "TestPassword123!",
                "full_name": "Jane Fix Test Student",
                "role": "student",
                "student_id": "CS2024002",
                "department": "Computer Science",
                "program_type": "phd_research",
                "study_status": "active",
                "supervisor_email": "supervisor.fix@research.lab",
                "nationality": "Malaysian",
                "citizenship": "Malaysian"
            }
            
            response = await self.client.post(f"{API_BASE}/auth/register", json=student_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.student_token = data["access_token"]
                self.student_id = data["user_data"]["id"]
                self.log_result("Student Setup", True, "Test student user created and authenticated")
            elif response.status_code == 400 and "already registered" in response.text:
                # Try to login instead
                login_data = {
                    "email": "student.fix@research.lab",
                    "password": "TestPassword123!"
                }
                response = await self.client.post(f"{API_BASE}/auth/login", json=login_data)
                if response.status_code == 200:
                    data = response.json()
                    self.student_token = data["access_token"]
                    self.student_id = data["user_data"]["id"]
                    self.log_result("Student Setup", True, "Logged in with existing test student user")
                else:
                    self.log_result("Student Setup", False, f"Failed to login student: {response.status_code}")
                    return False
            else:
                self.log_result("Student Setup", False, f"Failed to setup student: {response.status_code} - {response.text}")
                return False
            
            return True
            
        except Exception as e:
            self.log_result("User Setup", False, f"Exception during user setup: {str(e)}")
            return False
    
    def get_supervisor_headers(self):
        """Get supervisor authorization headers"""
        return {"Authorization": f"Bearer {self.supervisor_token}"}
    
    def get_student_headers(self):
        """Get student authorization headers"""
        return {"Authorization": f"Bearer {self.student_token}"}
    
    async def test_profile_update_enum_fix(self):
        """Test 1: Profile Update API Fix - Test supervisor profile updates with enum fields"""
        print("\n🔍 TESTING: Profile Update API Fix for Supervisor Enum Fields")
        
        try:
            # Test 1a: Supervisor profile update with empty strings for enum fields
            update_data = {
                "salutation": "Prof.",
                "full_name": "Prof. Updated Test Supervisor",
                "contact_number": "+60123456789",
                "program_type": "",  # Empty string should be handled gracefully
                "study_status": ""   # Empty string should be handled gracefully
            }
            
            response = await self.client.put(
                f"{API_BASE}/users/profile",
                json=update_data,
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                self.log_result("Supervisor Profile Update (Empty Enums)", True, 
                              "Supervisor profile update with empty enum strings works correctly")
            else:
                self.log_result("Supervisor Profile Update (Empty Enums)", False, 
                              f"Failed to update supervisor profile: {response.status_code} - {response.text}")
            
            # Test 1b: Supervisor profile update with only relevant fields
            minimal_update = {
                "salutation": "Dr.",
                "full_name": "Dr. Minimal Update Supervisor",
                "contact_number": "+60987654321"
            }
            
            response = await self.client.put(
                f"{API_BASE}/users/profile",
                json=minimal_update,
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                self.log_result("Supervisor Minimal Profile Update", True, 
                              "Supervisor profile update with minimal fields works correctly")
            else:
                self.log_result("Supervisor Minimal Profile Update", False, 
                              f"Failed minimal supervisor profile update: {response.status_code} - {response.text}")
            
            # Test 1c: Verify profile updates persist correctly
            response = await self.client.get(
                f"{API_BASE}/users/profile",
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                profile = response.json()
                if profile.get("full_name") == "Dr. Minimal Update Supervisor":
                    self.log_result("Profile Update Persistence", True, 
                                  "Profile updates persist correctly in database")
                else:
                    self.log_result("Profile Update Persistence", False, 
                                  "Profile updates not persisting correctly")
            else:
                self.log_result("Profile Update Persistence", False, 
                              f"Failed to retrieve updated profile: {response.status_code}")
            
            # Test 1d: Student profile update with valid enum values
            student_update = {
                "full_name": "Jane Updated Test Student",
                "program_type": "phd_research",
                "study_status": "active",
                "nationality": "Malaysian",
                "citizenship": "Malaysian"
            }
            
            response = await self.client.put(
                f"{API_BASE}/users/profile",
                json=student_update,
                headers=self.get_student_headers()
            )
            
            if response.status_code == 200:
                self.log_result("Student Profile Update (Valid Enums)", True, 
                              "Student profile update with valid enum values works correctly")
            else:
                self.log_result("Student Profile Update (Valid Enums)", False, 
                              f"Failed student profile update: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Profile Update Enum Fix Test", False, f"Exception: {str(e)}")
    
    async def test_student_data_visibility(self):
        """Test 2: Student Data Visibility - Test student access to bulletins, publications, grants, research logs"""
        print("\n🔍 TESTING: Student Data Visibility Issues")
        
        try:
            # Test 2a: Student access to bulletins/news
            response = await self.client.get(
                f"{API_BASE}/bulletins",
                headers=self.get_student_headers()
            )
            
            if response.status_code == 200:
                bulletins = response.json()
                self.log_result("Student Bulletins Access", True, 
                              f"Student can access bulletins - Found {len(bulletins)} bulletins")
            else:
                self.log_result("Student Bulletins Access", False, 
                              f"Student cannot access bulletins: {response.status_code}")
            
            # Test 2b: Student access to bulletin highlights
            response = await self.client.get(
                f"{API_BASE}/bulletins/highlights",
                headers=self.get_student_headers()
            )
            
            if response.status_code == 200:
                highlights = response.json()
                self.log_result("Student Bulletin Highlights Access", True, 
                              f"Student can access bulletin highlights - Found {len(highlights)} highlights")
            else:
                self.log_result("Student Bulletin Highlights Access", False, 
                              f"Student cannot access bulletin highlights: {response.status_code}")
            
            # Test 2c: Student access to publications
            response = await self.client.get(
                f"{API_BASE}/publications",
                headers=self.get_student_headers()
            )
            
            if response.status_code == 200:
                publications = response.json()
                self.log_result("Student Publications Access", True, 
                              f"Student can access publications - Found {len(publications)} publications")
            else:
                self.log_result("Student Publications Access", False, 
                              f"Student cannot access publications: {response.status_code}")
            
            # Test 2d: Student access to grants
            response = await self.client.get(
                f"{API_BASE}/grants",
                headers=self.get_student_headers()
            )
            
            if response.status_code == 200:
                grants = response.json()
                self.log_result("Student Grants Access", True, 
                              f"Student can access grants - Found {len(grants)} grants")
            else:
                self.log_result("Student Grants Access", False, 
                              f"Student cannot access grants: {response.status_code}")
            
            # Test 2e: Student access to their own research logs
            response = await self.client.get(
                f"{API_BASE}/research-logs",
                headers=self.get_student_headers()
            )
            
            if response.status_code == 200:
                research_logs = response.json()
                # Filter to only student's own logs
                student_logs = [log for log in research_logs if log.get("user_id") == self.student_id]
                self.log_result("Student Research Logs Access", True, 
                              f"Student can access their research logs - Found {len(student_logs)} own logs out of {len(research_logs)} total")
            else:
                self.log_result("Student Research Logs Access", False, 
                              f"Student cannot access research logs: {response.status_code}")
                
        except Exception as e:
            self.log_result("Student Data Visibility Test", False, f"Exception: {str(e)}")
    
    async def test_publications_synchronization(self):
        """Test 3: Publications Synchronization - Test latest publications system"""
        print("\n🔍 TESTING: Publications Synchronization System")
        
        try:
            # Test 3a: Publications controlled by supervisor's Scopus ID
            response = await self.client.get(
                f"{API_BASE}/publications",
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                supervisor_publications = response.json()
                self.log_result("Supervisor Publications Access", True, 
                              f"Supervisor can access publications - Found {len(supervisor_publications)} publications")
                
                # Test 3b: Student sees same publications (synchronized)
                response = await self.client.get(
                    f"{API_BASE}/publications",
                    headers=self.get_student_headers()
                )
                
                if response.status_code == 200:
                    student_publications = response.json()
                    if len(student_publications) == len(supervisor_publications):
                        self.log_result("Publications Synchronization", True, 
                                      f"Publications synchronized - Both supervisor and student see {len(student_publications)} publications")
                    else:
                        self.log_result("Publications Synchronization", False, 
                                      f"Publications not synchronized - Supervisor: {len(supervisor_publications)}, Student: {len(student_publications)}")
                else:
                    self.log_result("Publications Synchronization", False, 
                                  f"Student cannot access publications for synchronization test: {response.status_code}")
            else:
                self.log_result("Supervisor Publications Access", False, 
                              f"Supervisor cannot access publications: {response.status_code}")
            
            # Test 3c: Publications/all endpoint with enhanced view
            response = await self.client.get(
                f"{API_BASE}/publications/all",
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                all_publications = response.json()
                self.log_result("Enhanced Publications View", True, 
                              f"Enhanced publications view accessible - Found {len(all_publications)} publications")
            else:
                self.log_result("Enhanced Publications View", False, 
                              f"Enhanced publications view not accessible: {response.status_code}")
            
            # Test 3d: Scopus sync functionality (if available)
            sync_data = {
                "scopus_id": "12345678900"  # Test Scopus ID
            }
            
            response = await self.client.post(
                f"{API_BASE}/publications/sync-scopus",
                json=sync_data,
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                self.log_result("Scopus Sync Functionality", True, 
                              "Scopus synchronization endpoint working")
            elif response.status_code == 404:
                self.log_result("Scopus Sync Functionality", False, 
                              "Scopus sync endpoint not found - may need implementation")
            else:
                self.log_result("Scopus Sync Functionality", False, 
                              f"Scopus sync failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Publications Synchronization Test", False, f"Exception: {str(e)}")
    
    async def test_research_log_visibility(self):
        """Test 4: Research Log Visibility - Test student access to their own research logs with review status"""
        print("\n🔍 TESTING: Research Log Visibility and Status Tracking")
        
        try:
            # Test 4a: Create a research log as student
            research_log_data = {
                "activity_type": "experiment",
                "title": "Test Research Log for Visibility",
                "description": "Testing research log visibility and status tracking",
                "duration_hours": 3.0,
                "findings": "Test findings for visibility check",
                "challenges": "Test challenges",
                "next_steps": "Test next steps",
                "tags": ["test", "visibility"]
            }
            
            response = await self.client.post(
                f"{API_BASE}/research-logs",
                json=research_log_data,
                headers=self.get_student_headers()
            )
            
            if response.status_code in [200, 201]:
                log_data = response.json()
                log_id = log_data["id"]
                self.log_result("Research Log Creation", True, "Student can create research logs")
                
                # Test 4b: Student can see their own research logs
                response = await self.client.get(
                    f"{API_BASE}/research-logs",
                    headers=self.get_student_headers()
                )
                
                if response.status_code == 200:
                    logs = response.json()
                    student_own_logs = [log for log in logs if log.get("user_id") == self.student_id]
                    if len(student_own_logs) > 0:
                        self.log_result("Student Own Logs Visibility", True, 
                                      f"Student can see their own research logs - Found {len(student_own_logs)} own logs")
                    else:
                        self.log_result("Student Own Logs Visibility", False, 
                                      "Student cannot see their own research logs")
                else:
                    self.log_result("Student Own Logs Visibility", False, 
                                  f"Student cannot access research logs: {response.status_code}")
                
                # Test 4c: Supervisor reviews the research log
                review_data = {
                    "action": "accepted",
                    "feedback": "Excellent work on the research log visibility test"
                }
                
                response = await self.client.post(
                    f"{API_BASE}/research-logs/{log_id}/review",
                    json=review_data,
                    headers=self.get_supervisor_headers()
                )
                
                if response.status_code == 200:
                    self.log_result("Research Log Review", True, "Supervisor can review research logs")
                    
                    # Test 4d: Student can see review status and feedback
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
                        
                        if reviewed_log and reviewed_log.get("review_status"):
                            review_fields = ["review_status", "review_feedback", "reviewed_by", "reviewed_at", "reviewer_name"]
                            present_fields = [field for field in review_fields if reviewed_log.get(field)]
                            self.log_result("Research Log Review Status Visibility", True, 
                                          f"Student can see review information - Fields present: {present_fields}")
                        else:
                            self.log_result("Research Log Review Status Visibility", False, 
                                          "Student cannot see review status information")
                    else:
                        self.log_result("Research Log Review Status Visibility", False, 
                                      f"Failed to retrieve logs for review status check: {response.status_code}")
                else:
                    self.log_result("Research Log Review", False, 
                                  f"Supervisor cannot review research logs: {response.status_code}")
            else:
                self.log_result("Research Log Creation", False, 
                              f"Student cannot create research logs: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Research Log Visibility Test", False, f"Exception: {str(e)}")
    
    async def run_all_tests(self):
        """Run all the profile fix and critical functionality tests"""
        print("🚀 STARTING PROFILE FIX AND CRITICAL FUNCTIONALITY TESTING")
        print("=" * 70)
        
        # Setup test users
        if not await self.setup_test_users():
            print("❌ Cannot proceed without authenticated users")
            return
        
        # Run the critical fix tests
        await self.test_profile_update_enum_fix()
        await self.test_student_data_visibility()
        await self.test_publications_synchronization()
        await self.test_research_log_visibility()
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 PROFILE FIX TEST SUMMARY")
        print("=" * 70)
        
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
    async with ProfileFixTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
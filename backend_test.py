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

class BackendTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.auth_token = None
        self.test_user_id = None
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
    
    async def setup_test_user(self):
        """Create and authenticate a test user"""
        try:
            # Register a test supervisor user
            register_data = {
                "email": "test.supervisor@research.lab",
                "password": "TestPassword123!",
                "full_name": "Dr. Test Supervisor",
                "role": "supervisor",
                "department": "Computer Science",
                "research_area": "Machine Learning",
                "lab_name": "AI Research Lab"
            }
            
            response = await self.client.post(f"{API_BASE}/auth/register", json=register_data)
            if response.status_code == 201 or response.status_code == 200:
                data = response.json()
                self.auth_token = data["access_token"]
                self.test_user_id = data["user_data"]["id"]
                self.log_result("User Setup", True, "Test supervisor user created and authenticated")
                return True
            elif response.status_code == 400 and "already registered" in response.text:
                # Try to login instead
                login_data = {
                    "email": "test.supervisor@research.lab",
                    "password": "TestPassword123!"
                }
                response = await self.client.post(f"{API_BASE}/auth/login", json=login_data)
                if response.status_code == 200:
                    data = response.json()
                    self.auth_token = data["access_token"]
                    self.test_user_id = data["user_data"]["id"]
                    self.log_result("User Setup", True, "Logged in with existing test supervisor user")
                    return True
            
            self.log_result("User Setup", False, f"Failed to setup user: {response.status_code} - {response.text}")
            return False
            
        except Exception as e:
            self.log_result("User Setup", False, f"Exception during user setup: {str(e)}")
            return False
    
    async def create_test_student(self):
        """Create a test student for testing purposes"""
        try:
            register_data = {
                "email": "test.student@research.lab",
                "password": "TestPassword123!",
                "full_name": "John Test Student",
                "role": "student",
                "student_id": "CS2024001",
                "department": "Computer Science",
                "program_type": "phd_research",
                "supervisor_email": "test.supervisor@research.lab"
            }
            
            response = await self.client.post(f"{API_BASE}/auth/register", json=register_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.log_result("Student Setup", True, "Test student user created")
                return data["user_data"]["id"]
            elif response.status_code == 400 and "already registered" in response.text:
                # Login to get student ID
                login_data = {
                    "email": "test.student@research.lab",
                    "password": "TestPassword123!"
                }
                response = await self.client.post(f"{API_BASE}/auth/login", json=login_data)
                if response.status_code == 200:
                    data = response.json()
                    self.log_result("Student Setup", True, "Using existing test student user")
                    return data["user_data"]["id"]
            
            self.log_result("Student Setup", False, f"Failed to create student: {response.status_code}")
            return None
            
        except Exception as e:
            self.log_result("Student Setup", False, f"Exception during student setup: {str(e)}")
            return None
    
    def get_auth_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.auth_token}"}
    
    async def test_research_log_submissions_status(self):
        """Test 1: ClipboardCheck Import Error Fix - Test research log submissions status backend support"""
        print("\n🔍 TESTING: Research Log Submissions Status (ClipboardCheck Fix Support)")
        
        try:
            # Create a test student first
            student_id = await self.create_test_student()
            if not student_id:
                self.log_result("Research Log Status Test", False, "Could not create test student")
                return
            
            # Login as student to create research log
            login_data = {
                "email": "test.student@research.lab",
                "password": "TestPassword123!"
            }
            response = await self.client.post(f"{API_BASE}/auth/login", json=login_data)
            if response.status_code != 200:
                self.log_result("Student Login", False, "Could not login as student")
                return
            
            student_token = response.json()["access_token"]
            student_headers = {"Authorization": f"Bearer {student_token}"}
            
            # Create a research log as student
            research_log_data = {
                "activity_type": "experiment",
                "title": "Test Research Log for Status Tracking",
                "description": "Testing research log creation for status display",
                "duration_hours": 2.5,
                "findings": "Test findings for status tracking",
                "challenges": "Test challenges",
                "next_steps": "Test next steps",
                "tags": ["test", "status-tracking"]
            }
            
            response = await self.client.post(
                f"{API_BASE}/research-logs",
                json=research_log_data,
                headers=student_headers
            )
            
            if response.status_code in [200, 201]:
                log_data = response.json()
                log_id = log_data["id"]
                self.log_result("Research Log Creation", True, "Research log created successfully")
                
                # Test research log review (supervisor reviewing)
                review_data = {
                    "action": "accepted",
                    "feedback": "Excellent work on the research log"
                }
                
                response = await self.client.post(
                    f"{API_BASE}/research-logs/{log_id}/review",
                    json=review_data,
                    headers=self.get_auth_headers()  # Supervisor token
                )
                
                if response.status_code == 200:
                    self.log_result("Research Log Review", True, "Research log review functionality working")
                    
                    # Test getting research logs with status information (as supervisor)
                    response = await self.client.get(
                        f"{API_BASE}/research-logs",
                        headers=self.get_auth_headers()  # Supervisor token
                    )
                    
                    if response.status_code == 200:
                        logs = response.json()
                        if logs and len(logs) > 0:
                            # Check if the log has review status information
                            test_log = None
                            for log in logs:
                                if log.get("id") == log_id:
                                    test_log = log
                                    break
                            
                            if test_log and test_log.get("review_status"):
                                self.log_result("Research Log Status Retrieval", True, 
                                              f"Research log status tracking working - Status: {test_log['review_status']}")
                            else:
                                self.log_result("Research Log Status Retrieval", False, 
                                              "Research log status information not found in response")
                        else:
                            self.log_result("Research Log Status Retrieval", False, "No research logs found")
                    else:
                        self.log_result("Research Log Status Retrieval", False, 
                                      f"Failed to retrieve research logs: {response.status_code}")
                else:
                    self.log_result("Research Log Review", False, 
                                  f"Research log review failed: {response.status_code} - {response.text}")
            else:
                self.log_result("Research Log Creation", False, 
                              f"Failed to create research log: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Research Log Status Test", False, f"Exception: {str(e)}")
    
    async def test_reminder_action_buttons(self):
        """Test 2: Reminder Action Buttons - Test PUT and DELETE endpoints for reminders"""
        print("\n🔍 TESTING: Reminder Action Buttons (PUT/DELETE Operations)")
        
        try:
            # Create a test reminder first
            reminder_data = {
                "user_id": self.test_user_id,
                "title": "Test Reminder for Actions",
                "description": "Testing reminder edit and delete functionality",
                "reminder_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
                "priority": "medium",
                "reminder_type": "general"
            }
            
            response = await self.client.post(
                f"{API_BASE}/reminders",
                json=reminder_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code in [200, 201]:
                reminder = response.json()
                reminder_id = reminder["id"]
                self.log_result("Reminder Creation", True, "Test reminder created successfully")
                
                # Test PUT /api/reminders/{reminder_id} for editing
                edit_data = {
                    "title": "Updated Test Reminder",
                    "description": "Updated description for testing",
                    "priority": "high"
                }
                
                response = await self.client.put(
                    f"{API_BASE}/reminders/{reminder_id}",
                    json=edit_data,
                    headers=self.get_auth_headers()
                )
                
                if response.status_code == 200:
                    self.log_result("Reminder Edit (PUT)", True, "Reminder edit endpoint working")
                elif response.status_code == 404:
                    self.log_result("Reminder Edit (PUT)", False, "PUT /api/reminders/{reminder_id} endpoint not found - needs implementation")
                else:
                    self.log_result("Reminder Edit (PUT)", False, f"PUT endpoint failed: {response.status_code} - {response.text}")
                
                # Test PUT /api/reminders/{reminder_id}/complete (existing endpoint)
                response = await self.client.put(
                    f"{API_BASE}/reminders/{reminder_id}/complete",
                    headers=self.get_auth_headers()
                )
                
                if response.status_code == 200:
                    self.log_result("Reminder Complete (PUT)", True, "Reminder completion endpoint working")
                else:
                    self.log_result("Reminder Complete (PUT)", False, f"Complete endpoint failed: {response.status_code}")
                
                # Test reminder snooze functionality (updating reminder_date)
                snooze_data = {
                    "reminder_date": (datetime.utcnow() + timedelta(days=2)).isoformat()
                }
                
                response = await self.client.put(
                    f"{API_BASE}/reminders/{reminder_id}",
                    json=snooze_data,
                    headers=self.get_auth_headers()
                )
                
                if response.status_code == 200:
                    self.log_result("Reminder Snooze", True, "Reminder snooze functionality working")
                elif response.status_code == 404:
                    self.log_result("Reminder Snooze", False, "Reminder snooze requires PUT endpoint implementation")
                else:
                    self.log_result("Reminder Snooze", False, f"Snooze failed: {response.status_code}")
                
                # Test DELETE /api/reminders/{reminder_id} for deleting
                response = await self.client.delete(
                    f"{API_BASE}/reminders/{reminder_id}",
                    headers=self.get_auth_headers()
                )
                
                if response.status_code == 200:
                    self.log_result("Reminder Delete (DELETE)", True, "Reminder delete endpoint working")
                elif response.status_code == 404:
                    self.log_result("Reminder Delete (DELETE)", False, "DELETE /api/reminders/{reminder_id} endpoint not found - needs implementation")
                else:
                    self.log_result("Reminder Delete (DELETE)", False, f"DELETE endpoint failed: {response.status_code} - {response.text}")
                
            else:
                self.log_result("Reminder Creation", False, f"Failed to create test reminder: {response.status_code}")
                
        except Exception as e:
            self.log_result("Reminder Actions Test", False, f"Exception: {str(e)}")
    
    async def test_scopus_publication_integration(self):
        """Test 3: Scopus Publication Integration - Test POST /api/publications/scopus endpoint"""
        print("\n🔍 TESTING: Scopus Publication Integration")
        
        try:
            # Test POST /api/publications/scopus endpoint
            scopus_data = {
                "scopus_id": "2-s2.0-85123456789"
            }
            
            response = await self.client.post(
                f"{API_BASE}/publications/scopus",
                json=scopus_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code in [200, 201]:
                publication = response.json()
                self.log_result("Scopus Publication Creation", True, 
                              f"Publication created from Scopus ID: {publication.get('title', 'Unknown')}")
                
                # Verify the publication includes scopus_id field
                if publication.get("scopus_id") == scopus_data["scopus_id"]:
                    self.log_result("Scopus ID Field", True, "Publication includes correct scopus_id field")
                else:
                    self.log_result("Scopus ID Field", False, "Publication missing or incorrect scopus_id field")
                
                # Test that the publication appears in publications list
                response = await self.client.get(
                    f"{API_BASE}/publications",
                    headers=self.get_auth_headers()
                )
                
                if response.status_code == 200:
                    publications = response.json()
                    found_publication = False
                    for pub in publications:
                        if pub.get("scopus_id") == scopus_data["scopus_id"]:
                            found_publication = True
                            break
                    
                    if found_publication:
                        self.log_result("Publication List Integration", True, 
                                      "Scopus publication appears in publications list")
                    else:
                        self.log_result("Publication List Integration", False, 
                                      "Scopus publication not found in publications list")
                else:
                    self.log_result("Publication List Integration", False, 
                                  f"Failed to retrieve publications list: {response.status_code}")
                
                # Test with invalid Scopus ID
                invalid_data = {"scopus_id": ""}
                response = await self.client.post(
                    f"{API_BASE}/publications/scopus",
                    json=invalid_data,
                    headers=self.get_auth_headers()
                )
                
                if response.status_code == 400:
                    self.log_result("Scopus Validation", True, "Proper validation for empty Scopus ID")
                else:
                    self.log_result("Scopus Validation", False, f"Invalid validation response: {response.status_code}")
                
            elif response.status_code == 404:
                self.log_result("Scopus Publication Creation", False, 
                              "POST /api/publications/scopus endpoint not found - needs implementation")
            else:
                self.log_result("Scopus Publication Creation", False, 
                              f"Scopus endpoint failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Scopus Integration Test", False, f"Exception: {str(e)}")
    
    async def run_all_tests(self):
        """Run all the specific tests for the 3 fixes"""
        print("🚀 STARTING BACKEND TESTING FOR 3 SPECIFIC FIXES")
        print("=" * 60)
        
        # Setup test user
        if not await self.setup_test_user():
            print("❌ Cannot proceed without authenticated user")
            return
        
        # Run the 3 specific tests
        await self.test_research_log_submissions_status()
        await self.test_reminder_action_buttons()
        await self.test_scopus_publication_integration()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
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
    async with BackendTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3

import asyncio
import httpx
import json
import os
import websockets
from datetime import datetime, timedelta
import sys
import uuid

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://c5e539fb-9522-486d-b275-1bb355b557d8.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"
WS_BASE = BACKEND_URL.replace('https://', 'wss://').replace('http://', 'ws://')

class RealTimeBackendTester:
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
                "email": "supervisor.realtime@research.lab",
                "password": "TestPassword123!",
                "full_name": "Dr. RealTime Supervisor",
                "role": "supervisor",
                "department": "Computer Science",
                "research_area": "Real-time Systems",
                "lab_name": "RealTime Research Lab",
                "scopus_id": "12345678900"
            }
            
            response = await self.client.post(f"{API_BASE}/auth/register", json=supervisor_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.supervisor_token = data["access_token"]
                self.supervisor_id = data["user_data"]["id"]
                self.log_result("Supervisor Setup", True, "Test supervisor user created and authenticated")
            elif response.status_code == 400 and "already registered" in response.text:
                # Login instead
                login_data = {"email": "supervisor.realtime@research.lab", "password": "TestPassword123!"}
                response = await self.client.post(f"{API_BASE}/auth/login", json=login_data)
                if response.status_code == 200:
                    data = response.json()
                    self.supervisor_token = data["access_token"]
                    self.supervisor_id = data["user_data"]["id"]
                    self.log_result("Supervisor Setup", True, "Logged in with existing supervisor user")
            
            # Setup student user
            student_data = {
                "email": "student.realtime@research.lab",
                "password": "TestPassword123!",
                "full_name": "Alice RealTime Student",
                "role": "student",
                "student_id": "RT2024001",
                "department": "Computer Science",
                "program_type": "phd_research",
                "supervisor_email": "supervisor.realtime@research.lab",
                "research_area": "Real-time Applications"
            }
            
            response = await self.client.post(f"{API_BASE}/auth/register", json=student_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.student_token = data["access_token"]
                self.student_id = data["user_data"]["id"]
                self.log_result("Student Setup", True, "Test student user created and authenticated")
            elif response.status_code == 400 and "already registered" in response.text:
                # Login instead
                login_data = {"email": "student.realtime@research.lab", "password": "TestPassword123!"}
                response = await self.client.post(f"{API_BASE}/auth/login", json=login_data)
                if response.status_code == 200:
                    data = response.json()
                    self.student_token = data["access_token"]
                    self.student_id = data["user_data"]["id"]
                    self.log_result("Student Setup", True, "Logged in with existing student user")
            
            return self.supervisor_token and self.student_token
            
        except Exception as e:
            self.log_result("User Setup", False, f"Exception during user setup: {str(e)}")
            return False
    
    def get_supervisor_headers(self):
        return {"Authorization": f"Bearer {self.supervisor_token}"}
    
    def get_student_headers(self):
        return {"Authorization": f"Bearer {self.student_token}"}
    
    async def test_websocket_connectivity(self):
        """Test 1: WebSocket endpoint connectivity for real-time updates"""
        print("\n🔍 TESTING: WebSocket Connectivity (/ws/{user_id})")
        
        try:
            # Test WebSocket connection for supervisor
            ws_url = f"{WS_BASE}/ws/{self.supervisor_id}"
            
            try:
                async with websockets.connect(ws_url, timeout=10) as websocket:
                    # Send ping message
                    ping_message = {"type": "ping"}
                    await websocket.send(json.dumps(ping_message))
                    
                    # Wait for pong response
                    response = await asyncio.wait_for(websocket.recv(), timeout=5)
                    response_data = json.loads(response)
                    
                    if response_data.get("type") == "pong":
                        self.log_result("WebSocket Ping/Pong", True, "WebSocket ping/pong functionality working")
                    else:
                        self.log_result("WebSocket Ping/Pong", False, f"Unexpected response: {response_data}")
                    
                    self.log_result("WebSocket Connection", True, "WebSocket endpoint accessible and functional")
                    
            except websockets.exceptions.ConnectionClosed:
                self.log_result("WebSocket Connection", False, "WebSocket connection closed unexpectedly")
            except asyncio.TimeoutError:
                self.log_result("WebSocket Connection", False, "WebSocket connection timeout")
            except Exception as ws_e:
                self.log_result("WebSocket Connection", False, f"WebSocket error: {str(ws_e)}")
                
        except Exception as e:
            self.log_result("WebSocket Test", False, f"Exception: {str(e)}")
    
    async def test_research_log_workflow_state_machine(self):
        """Test 2: Research Log Workflow State Machine (DRAFT→SUBMITTED→RETURNED/ACCEPTED/DECLINED)"""
        print("\n🔍 TESTING: Research Log Workflow State Machine")
        
        try:
            # Create research log as student (should start as DRAFT)
            log_data = {
                "activity_type": "experiment",
                "title": "Real-time Research Log Workflow Test",
                "description": "Testing the new workflow state machine",
                "duration_hours": 3.0,
                "findings": "Workflow state transitions working correctly",
                "challenges": "Testing all state transitions",
                "next_steps": "Verify real-time notifications",
                "tags": ["workflow", "real-time", "testing"]
            }
            
            response = await self.client.post(
                f"{API_BASE}/research-logs",
                json=log_data,
                headers=self.get_student_headers()
            )
            
            if response.status_code in [200, 201]:
                log = response.json()
                log_id = log["id"]
                initial_status = log.get("status", "draft")
                self.log_result("Research Log Creation", True, f"Research log created with status: {initial_status}")
                
                # Test DRAFT → SUBMITTED transition
                response = await self.client.post(
                    f"{API_BASE}/research-logs/{log_id}/submit",
                    headers=self.get_student_headers()
                )
                
                if response.status_code == 200:
                    self.log_result("DRAFT→SUBMITTED Transition", True, "Research log submitted successfully")
                    
                    # Test SUBMITTED → RETURNED transition (supervisor action)
                    response = await self.client.post(
                        f"{API_BASE}/research-logs/{log_id}/return",
                        json={"comment": "Please add more details to the findings section"},
                        headers=self.get_supervisor_headers()
                    )
                    
                    if response.status_code == 200:
                        self.log_result("SUBMITTED→RETURNED Transition", True, "Research log returned for revision")
                        
                        # Test RETURNED → SUBMITTED transition (resubmit)
                        response = await self.client.post(
                            f"{API_BASE}/research-logs/{log_id}/submit",
                            headers=self.get_student_headers()
                        )
                        
                        if response.status_code == 200:
                            self.log_result("RETURNED→SUBMITTED Transition", True, "Research log resubmitted successfully")
                            
                            # Test SUBMITTED → ACCEPTED transition
                            response = await self.client.post(
                                f"{API_BASE}/research-logs/{log_id}/accept",
                                json={"comment": "Excellent work! Well documented research."},
                                headers=self.get_supervisor_headers()
                            )
                            
                            if response.status_code == 200:
                                self.log_result("SUBMITTED→ACCEPTED Transition", True, "Research log accepted successfully")
                            else:
                                self.log_result("SUBMITTED→ACCEPTED Transition", False, f"Accept failed: {response.status_code}")
                        else:
                            self.log_result("RETURNED→SUBMITTED Transition", False, f"Resubmit failed: {response.status_code}")
                    else:
                        self.log_result("SUBMITTED→RETURNED Transition", False, f"Return failed: {response.status_code}")
                        
                        # Test SUBMITTED → DECLINED transition instead
                        response = await self.client.post(
                            f"{API_BASE}/research-logs/{log_id}/decline",
                            json={"comment": "Research methodology needs significant improvement"},
                            headers=self.get_supervisor_headers()
                        )
                        
                        if response.status_code == 200:
                            self.log_result("SUBMITTED→DECLINED Transition", True, "Research log declined successfully")
                        else:
                            self.log_result("SUBMITTED→DECLINED Transition", False, f"Decline failed: {response.status_code}")
                else:
                    self.log_result("DRAFT→SUBMITTED Transition", False, f"Submit failed: {response.status_code}")
                    
                # Test status transition validation
                response = await self.client.get(
                    f"{API_BASE}/research-logs",
                    headers=self.get_student_headers()
                )
                
                if response.status_code == 200:
                    logs = response.json()
                    test_log = next((log for log in logs if log["id"] == log_id), None)
                    if test_log and test_log.get("status"):
                        self.log_result("Status Validation", True, f"Research log status properly tracked: {test_log['status']}")
                    else:
                        self.log_result("Status Validation", False, "Status information missing from research log")
                else:
                    self.log_result("Status Validation", False, "Could not retrieve research logs for validation")
                    
            else:
                self.log_result("Research Log Creation", False, f"Failed to create research log: {response.status_code}")
                
        except Exception as e:
            self.log_result("Research Log Workflow Test", False, f"Exception: {str(e)}")
    
    async def test_publications_visibility_system(self):
        """Test 3: Enhanced Publications Visibility System with SCOPUS integration"""
        print("\n🔍 TESTING: Publications Visibility System")
        
        try:
            # Test lab-wide publications visibility (GET /api/publications)
            response = await self.client.get(
                f"{API_BASE}/publications",
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                supervisor_publications = response.json()
                self.log_result("Supervisor Publications Access", True, f"Supervisor can access {len(supervisor_publications)} publications")
                
                # Test student access to same publications
                response = await self.client.get(
                    f"{API_BASE}/publications",
                    headers=self.get_student_headers()
                )
                
                if response.status_code == 200:
                    student_publications = response.json()
                    self.log_result("Student Publications Access", True, f"Student can access {len(student_publications)} publications")
                    
                    # Verify lab-wide synchronization (both should see same publications)
                    if len(supervisor_publications) == len(student_publications):
                        self.log_result("Publications Synchronization", True, "Lab-wide publications synchronization working")
                    else:
                        self.log_result("Publications Synchronization", False, 
                                      f"Publication count mismatch: Supervisor({len(supervisor_publications)}) vs Student({len(student_publications)})")
                else:
                    self.log_result("Student Publications Access", False, f"Student access failed: {response.status_code}")
                
                # Test SCOPUS integration with automatic database storage
                response = await self.client.post(
                    f"{API_BASE}/publications/sync-scopus",
                    headers=self.get_supervisor_headers()
                )
                
                if response.status_code == 200:
                    sync_result = response.json()
                    self.log_result("SCOPUS Integration", True, f"SCOPUS sync successful: {sync_result.get('message', 'Synced')}")
                    
                    # Verify publications were stored/updated in database
                    response = await self.client.get(
                        f"{API_BASE}/publications",
                        headers=self.get_supervisor_headers()
                    )
                    
                    if response.status_code == 200:
                        updated_publications = response.json()
                        if len(updated_publications) >= len(supervisor_publications):
                            self.log_result("SCOPUS Database Storage", True, "Publications properly stored/updated in database")
                        else:
                            self.log_result("SCOPUS Database Storage", False, "Publications not properly stored after SCOPUS sync")
                    else:
                        self.log_result("SCOPUS Database Storage", False, "Could not verify database storage")
                else:
                    self.log_result("SCOPUS Integration", False, f"SCOPUS sync failed: {response.status_code}")
                    
            else:
                self.log_result("Supervisor Publications Access", False, f"Publications access failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("Publications Visibility Test", False, f"Exception: {str(e)}")
    
    async def test_avatar_system_realtime_updates(self):
        """Test 4: Avatar System with Real-time Updates"""
        print("\n🔍 TESTING: Avatar System with Real-time Updates")
        
        try:
            # Test avatar update endpoint (PUT /api/users/{user_id}/avatar)
            avatar_data = {
                "avatar_emoji": "🧑‍🔬"
            }
            
            response = await self.client.put(
                f"{API_BASE}/users/{self.student_id}/avatar",
                json=avatar_data,
                headers=self.get_student_headers()
            )
            
            if response.status_code == 200:
                self.log_result("Avatar Update", True, "Avatar emoji updated successfully")
                
                # Test authorization check (user can only update their own avatar)
                response = await self.client.put(
                    f"{API_BASE}/users/{self.supervisor_id}/avatar",
                    json={"avatar_emoji": "👨‍🏫"},
                    headers=self.get_student_headers()  # Student trying to update supervisor's avatar
                )
                
                if response.status_code == 403:
                    self.log_result("Avatar Authorization", True, "Proper authorization check - users can only update own avatars")
                else:
                    self.log_result("Avatar Authorization", False, f"Authorization check failed: {response.status_code}")
                
                # Verify avatar persistence and retrieval
                response = await self.client.get(
                    f"{API_BASE}/users/profile",
                    headers=self.get_student_headers()
                )
                
                if response.status_code == 200:
                    profile = response.json()
                    if profile.get("avatar_emoji") == "🧑‍🔬":
                        self.log_result("Avatar Persistence", True, "Avatar emoji properly persisted and retrieved")
                    else:
                        self.log_result("Avatar Persistence", False, f"Avatar not persisted correctly: {profile.get('avatar_emoji')}")
                else:
                    self.log_result("Avatar Persistence", False, "Could not retrieve profile to verify avatar")
                    
            else:
                self.log_result("Avatar Update", False, f"Avatar update failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("Avatar System Test", False, f"Exception: {str(e)}")
    
    async def test_enhanced_bulletins_system(self):
        """Test 5: Enhanced Bulletins/Announcements System with lab-wide visibility"""
        print("\n🔍 TESTING: Enhanced Bulletins System")
        
        try:
            # Create bulletin as supervisor
            bulletin_data = {
                "title": "Lab-wide Real-time Announcement",
                "content": "Testing lab-wide bulletin visibility and real-time synchronization",
                "category": "general",
                "is_highlight": True
            }
            
            response = await self.client.post(
                f"{API_BASE}/bulletins",
                json=bulletin_data,
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code in [200, 201]:
                bulletin = response.json()
                bulletin_id = bulletin["id"]
                self.log_result("Bulletin Creation", True, "Lab-wide bulletin created successfully")
                
                # Approve the bulletin so students can see it
                approval_data = {
                    "bulletin_id": bulletin_id,
                    "approved": True,
                    "comments": "Approved for testing"
                }
                
                response = await self.client.post(
                    f"{API_BASE}/bulletins/{bulletin_id}/approve",
                    json=approval_data,
                    headers=self.get_supervisor_headers()
                )
                
                if response.status_code == 200:
                    self.log_result("Bulletin Approval", True, "Bulletin approved successfully")
                else:
                    self.log_result("Bulletin Approval", False, f"Bulletin approval failed: {response.status_code}")
                
                # Test lab-wide visibility - student should see approved bulletin
                response = await self.client.get(
                    f"{API_BASE}/bulletins",
                    headers=self.get_student_headers()
                )
                
                if response.status_code == 200:
                    student_bulletins = response.json()
                    found_bulletin = any(b["id"] == bulletin_id for b in student_bulletins)
                    
                    if found_bulletin:
                        self.log_result("Lab-wide Bulletin Visibility", True, "Students can see lab-wide bulletins")
                    else:
                        self.log_result("Lab-wide Bulletin Visibility", False, "Student cannot see lab bulletin")
                else:
                    self.log_result("Lab-wide Bulletin Visibility", False, f"Student bulletin access failed: {response.status_code}")
                
                # Test supervisor can see all bulletins in their lab
                response = await self.client.get(
                    f"{API_BASE}/bulletins",
                    headers=self.get_supervisor_headers()
                )
                
                if response.status_code == 200:
                    supervisor_bulletins = response.json()
                    found_bulletin = any(b["id"] == bulletin_id for b in supervisor_bulletins)
                    
                    if found_bulletin:
                        self.log_result("Supervisor Bulletin Access", True, "Supervisors can see all lab bulletins")
                    else:
                        self.log_result("Supervisor Bulletin Access", False, "Supervisor cannot see own bulletin")
                else:
                    self.log_result("Supervisor Bulletin Access", False, f"Supervisor bulletin access failed: {response.status_code}")
                    
            else:
                self.log_result("Bulletin Creation", False, f"Bulletin creation failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("Bulletins System Test", False, f"Exception: {str(e)}")
    
    async def test_enhanced_dashboard_stats(self):
        """Test 6: Enhanced Dashboard Stats with Active Grants"""
        print("\n🔍 TESTING: Enhanced Dashboard Stats")
        
        try:
            # Test student dashboard stats with new fields
            response = await self.client.get(
                f"{API_BASE}/dashboard/stats",
                headers=self.get_student_headers()
            )
            
            if response.status_code == 200:
                student_stats = response.json()
                
                # Check for new student fields
                expected_fields = [
                    "approved_research_logs", "pending_research_logs", 
                    "revision_research_logs", "active_grants_count", "active_grants_balance"
                ]
                
                missing_fields = [field for field in expected_fields if field not in student_stats]
                
                if not missing_fields:
                    self.log_result("Student Dashboard Stats", True, "All new student dashboard fields present")
                else:
                    self.log_result("Student Dashboard Stats", False, f"Missing fields: {missing_fields}")
                    
            else:
                self.log_result("Student Dashboard Stats", False, f"Student stats failed: {response.status_code}")
            
            # Test supervisor dashboard stats with enhanced fields
            response = await self.client.get(
                f"{API_BASE}/dashboard/stats",
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                supervisor_stats = response.json()
                
                # Check for enhanced supervisor fields
                expected_fields = ["active_grants_count", "active_grants_balance", "active_grants"]
                
                missing_fields = [field for field in expected_fields if field not in supervisor_stats]
                
                if not missing_fields:
                    self.log_result("Supervisor Dashboard Stats", True, "All enhanced supervisor dashboard fields present")
                else:
                    self.log_result("Supervisor Dashboard Stats", False, f"Missing fields: {missing_fields}")
                    
            else:
                self.log_result("Supervisor Dashboard Stats", False, f"Supervisor stats failed: {response.status_code}")
            
            # Test active grants endpoint
            response = await self.client.get(
                f"{API_BASE}/grants/active",
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                active_grants = response.json()
                self.log_result("Active Grants Endpoint", True, f"Active grants endpoint working: {len(active_grants)} grants")
            else:
                self.log_result("Active Grants Endpoint", False, f"Active grants endpoint failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("Dashboard Stats Test", False, f"Exception: {str(e)}")
    
    async def test_notification_system(self):
        """Test 7: Notification System with real-time events"""
        print("\n🔍 TESTING: Notification System")
        
        try:
            # Create a research log that should trigger notifications
            log_data = {
                "activity_type": "writing",
                "title": "Notification Test Research Log",
                "description": "Testing notification system",
                "duration_hours": 1.0,
                "findings": "Notifications working",
                "challenges": "Testing real-time events",
                "next_steps": "Verify notification delivery",
                "tags": ["notifications", "testing"]
            }
            
            response = await self.client.post(
                f"{API_BASE}/research-logs",
                json=log_data,
                headers=self.get_student_headers()
            )
            
            if response.status_code in [200, 201]:
                log = response.json()
                log_id = log["id"]
                
                # Submit the research log (should create notification for supervisor)
                response = await self.client.post(
                    f"{API_BASE}/research-logs/{log_id}/submit",
                    headers=self.get_student_headers()
                )
                
                if response.status_code == 200:
                    self.log_result("Notification Trigger", True, "Research log submission should trigger notification")
                    
                    # Check if notifications endpoint exists
                    response = await self.client.get(
                        f"{API_BASE}/notifications",
                        headers=self.get_supervisor_headers()
                    )
                    
                    if response.status_code == 200:
                        notifications = response.json()
                        self.log_result("Notification Retrieval", True, f"Notifications endpoint working: {len(notifications)} notifications")
                    elif response.status_code == 404:
                        self.log_result("Notification Retrieval", False, "Notifications endpoint not implemented")
                    else:
                        self.log_result("Notification Retrieval", False, f"Notifications endpoint failed: {response.status_code}")
                else:
                    self.log_result("Notification Trigger", False, f"Research log submission failed: {response.status_code}")
            else:
                self.log_result("Notification Test Setup", False, f"Could not create test research log: {response.status_code}")
                
        except Exception as e:
            self.log_result("Notification System Test", False, f"Exception: {str(e)}")
    
    async def test_lab_wide_data_synchronization(self):
        """Test 8: Lab-wide Data Synchronization"""
        print("\n🔍 TESTING: Lab-wide Data Synchronization")
        
        try:
            # Test grants synchronization
            response = await self.client.get(
                f"{API_BASE}/grants",
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                supervisor_grants = response.json()
                
                # Student should see same grants (lab-wide visibility)
                response = await self.client.get(
                    f"{API_BASE}/grants",
                    headers=self.get_student_headers()
                )
                
                if response.status_code == 200:
                    student_grants = response.json()
                    
                    if len(supervisor_grants) == len(student_grants):
                        self.log_result("Grants Synchronization", True, "Lab-wide grants synchronization working")
                    else:
                        self.log_result("Grants Synchronization", False, 
                                      f"Grants count mismatch: Supervisor({len(supervisor_grants)}) vs Student({len(student_grants)})")
                else:
                    self.log_result("Student Grants Access", False, f"Student grants access failed: {response.status_code}")
            else:
                self.log_result("Supervisor Grants Access", False, f"Supervisor grants access failed: {response.status_code}")
            
            # Test research logs lab-wide filtering
            response = await self.client.get(
                f"{API_BASE}/research-logs",
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                supervisor_logs = response.json()
                self.log_result("Lab Research Logs Access", True, f"Supervisor can access {len(supervisor_logs)} research logs")
                
                # Verify supervisor sees student information in logs
                if supervisor_logs:
                    sample_log = supervisor_logs[0]
                    student_info_fields = ["student_name", "student_id", "student_email"]
                    has_student_info = any(field in sample_log for field in student_info_fields)
                    
                    if has_student_info:
                        self.log_result("Student Info in Logs", True, "Research logs include student information for supervisors")
                    else:
                        self.log_result("Student Info in Logs", False, "Research logs missing student information")
            else:
                self.log_result("Lab Research Logs Access", False, f"Research logs access failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("Lab Synchronization Test", False, f"Exception: {str(e)}")
    
    async def run_all_tests(self):
        """Run all real-time system tests"""
        print("🚀 STARTING COMPREHENSIVE REAL-TIME BACKEND TESTING")
        print("=" * 70)
        
        # Setup test users
        if not await self.setup_test_users():
            print("❌ Cannot proceed without authenticated users")
            return
        
        # Run all real-time tests
        await self.test_websocket_connectivity()
        await self.test_research_log_workflow_state_machine()
        await self.test_publications_visibility_system()
        await self.test_avatar_system_realtime_updates()
        await self.test_enhanced_bulletins_system()
        await self.test_enhanced_dashboard_stats()
        await self.test_notification_system()
        await self.test_lab_wide_data_synchronization()
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 REAL-TIME SYSTEM TEST SUMMARY")
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
    async with RealTimeBackendTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
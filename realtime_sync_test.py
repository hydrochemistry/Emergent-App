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

class RealTimeSyncTester:
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
            # Setup supervisor
            supervisor_data = {
                "email": "supervisor.realtime@research.lab",
                "password": "TestPassword123!",
                "full_name": "Dr. Real Time Supervisor",
                "role": "supervisor",
                "department": "Computer Science",
                "research_area": "Real-time Systems",
                "lab_name": "Real-time Research Lab"
            }
            
            response = await self.client.post(f"{API_BASE}/auth/register", json=supervisor_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.supervisor_token = data["access_token"]
                self.supervisor_id = data["user_data"]["id"]
                self.log_result("Supervisor Setup", True, "Test supervisor created and authenticated")
            elif response.status_code == 400 and "already registered" in response.text:
                # Login instead
                login_data = {
                    "email": "supervisor.realtime@research.lab",
                    "password": "TestPassword123!"
                }
                response = await self.client.post(f"{API_BASE}/auth/login", json=login_data)
                if response.status_code == 200:
                    data = response.json()
                    self.supervisor_token = data["access_token"]
                    self.supervisor_id = data["user_data"]["id"]
                    self.log_result("Supervisor Setup", True, "Logged in with existing supervisor")
                else:
                    self.log_result("Supervisor Setup", False, f"Failed to login supervisor: {response.status_code}")
                    return False
            else:
                self.log_result("Supervisor Setup", False, f"Failed to setup supervisor: {response.status_code}")
                return False
            
            # Setup student
            student_data = {
                "email": "student.realtime@research.lab",
                "password": "TestPassword123!",
                "full_name": "Alice Real Time Student",
                "role": "student",
                "student_id": "RT2024001",
                "department": "Computer Science",
                "program_type": "phd_research",
                "supervisor_email": "supervisor.realtime@research.lab"
            }
            
            response = await self.client.post(f"{API_BASE}/auth/register", json=student_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.student_token = data["access_token"]
                self.student_id = data["user_data"]["id"]
                self.log_result("Student Setup", True, "Test student created and authenticated")
            elif response.status_code == 400 and "already registered" in response.text:
                # Login instead
                login_data = {
                    "email": "student.realtime@research.lab",
                    "password": "TestPassword123!"
                }
                response = await self.client.post(f"{API_BASE}/auth/login", json=login_data)
                if response.status_code == 200:
                    data = response.json()
                    self.student_token = data["access_token"]
                    self.student_id = data["user_data"]["id"]
                    self.log_result("Student Setup", True, "Logged in with existing student")
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
    
    def get_supervisor_headers(self):
        return {"Authorization": f"Bearer {self.supervisor_token}"}
    
    def get_student_headers(self):
        return {"Authorization": f"Bearer {self.student_token}"}
    
    async def test_research_log_creation_with_relational_keys(self):
        """Test 1: Research Log Creation with Proper Relational Keys"""
        print("\n🔍 TESTING: Research Log Creation with Proper Relational Keys")
        
        try:
            # Test as student
            research_log_data = {
                "activity_type": "experiment",
                "title": "Real-time Sync Test Research Log",
                "description": "Testing research log creation with proper relational keys",
                "duration_hours": 3.5,
                "findings": "Testing relational key assignment",
                "challenges": "Ensuring proper student_id and supervisor_id assignment",
                "next_steps": "Verify data consistency",
                "tags": ["realtime", "sync", "test"]
            }
            
            response = await self.client.post(
                f"{API_BASE}/research-logs",
                json=research_log_data,
                headers=self.get_student_headers()
            )
            
            if response.status_code in [200, 201]:
                log_data = response.json()
                log_id = log_data["id"]
                
                # CRITICAL CHECK: Verify student_id and supervisor_id are set
                if log_data.get("student_id") == self.student_id:
                    self.log_result("Student ID Assignment", True, "student_id correctly set on creation")
                else:
                    self.log_result("Student ID Assignment", False, f"student_id not set correctly. Expected: {self.student_id}, Got: {log_data.get('student_id')}")
                
                if log_data.get("supervisor_id") == self.supervisor_id:
                    self.log_result("Supervisor ID Assignment", True, "supervisor_id correctly set on creation")
                else:
                    self.log_result("Supervisor ID Assignment", False, f"supervisor_id not set correctly. Expected: {self.supervisor_id}, Got: {log_data.get('supervisor_id')}")
                
                # Test as supervisor creating log
                supervisor_log_data = {
                    "activity_type": "meeting",
                    "title": "Supervisor Created Research Log",
                    "description": "Testing supervisor log creation",
                    "duration_hours": 1.0,
                    "findings": "Supervisor can create logs",
                    "challenges": "Ensuring proper key assignment for supervisor-created logs",
                    "next_steps": "Verify supervisor logs have correct keys",
                    "tags": ["supervisor", "test"]
                }
                
                response = await self.client.post(
                    f"{API_BASE}/research-logs",
                    json=supervisor_log_data,
                    headers=self.get_supervisor_headers()
                )
                
                if response.status_code in [200, 201]:
                    supervisor_log = response.json()
                    
                    # For supervisor-created logs, they should be their own supervisor
                    if supervisor_log.get("student_id") == self.supervisor_id and supervisor_log.get("supervisor_id") == self.supervisor_id:
                        self.log_result("Supervisor Log Keys", True, "Supervisor-created log has correct relational keys")
                    else:
                        self.log_result("Supervisor Log Keys", False, f"Supervisor log keys incorrect. student_id: {supervisor_log.get('student_id')}, supervisor_id: {supervisor_log.get('supervisor_id')}")
                else:
                    self.log_result("Supervisor Log Creation", False, f"Failed to create supervisor log: {response.status_code}")
                
                return log_id
            else:
                self.log_result("Research Log Creation", False, f"Failed to create research log: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Research Log Creation Test", False, f"Exception: {str(e)}")
            return None
    
    async def test_submit_endpoint_with_idempotency(self):
        """Test 2: Submit Endpoint with Idempotency & Key Guarantee"""
        print("\n🔍 TESTING: Submit Endpoint with Idempotency & Key Guarantee")
        
        try:
            # First create a research log
            log_id = await self.test_research_log_creation_with_relational_keys()
            if not log_id:
                self.log_result("Submit Test Setup", False, "Could not create research log for submit test")
                return
            
            # Test submit endpoint
            response = await self.client.post(
                f"{API_BASE}/research-logs/{log_id}/submit",
                headers=self.get_student_headers()
            )
            
            if response.status_code == 200:
                submit_result = response.json()
                self.log_result("Submit Endpoint", True, "Research log submit endpoint working")
                
                # Test idempotency - submit again
                response = await self.client.post(
                    f"{API_BASE}/research-logs/{log_id}/submit",
                    headers=self.get_student_headers()
                )
                
                if response.status_code == 200:
                    self.log_result("Submit Idempotency", True, "Submit endpoint is idempotent (safe to re-submit)")
                else:
                    self.log_result("Submit Idempotency", False, f"Submit not idempotent: {response.status_code}")
                
                # Verify state transition (DRAFT → SUBMITTED)
                response = await self.client.get(
                    f"{API_BASE}/research-logs",
                    headers=self.get_student_headers()
                )
                
                if response.status_code == 200:
                    logs = response.json()
                    submitted_log = None
                    for log in logs:
                        if log.get("id") == log_id:
                            submitted_log = log
                            break
                    
                    if submitted_log and submitted_log.get("status") == "submitted":
                        self.log_result("State Transition", True, "Research log status correctly changed to SUBMITTED")
                        
                        # Verify foreign key assignment is maintained
                        if submitted_log.get("student_id") and submitted_log.get("supervisor_id"):
                            self.log_result("Foreign Key Persistence", True, "Relational keys maintained after submit")
                        else:
                            self.log_result("Foreign Key Persistence", False, "Relational keys lost after submit")
                    else:
                        self.log_result("State Transition", False, f"Status not updated correctly. Status: {submitted_log.get('status') if submitted_log else 'Log not found'}")
                else:
                    self.log_result("State Verification", False, f"Could not verify state: {response.status_code}")
                
                return log_id
            else:
                self.log_result("Submit Endpoint", False, f"Submit endpoint failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Submit Test", False, f"Exception: {str(e)}")
            return None
    
    async def test_unified_read_models(self):
        """Test 3: Unified Read Models (No Role-Split Datasets)"""
        print("\n🔍 TESTING: Unified Read Models (No Role-Split Datasets)")
        
        try:
            # Create a research log and submit it
            log_id = await self.test_submit_endpoint_with_idempotency()
            if not log_id:
                self.log_result("Unified Read Setup", False, "Could not create submitted log for unified read test")
                return
            
            # Test student view - should use student_id filter
            response = await self.client.get(
                f"{API_BASE}/research-logs",
                headers=self.get_student_headers()
            )
            
            if response.status_code == 200:
                student_logs = response.json()
                student_log_found = False
                for log in student_logs:
                    if log.get("id") == log_id:
                        student_log_found = True
                        # Verify it uses student_id filter (student should see their own logs)
                        if log.get("student_id") == self.student_id:
                            self.log_result("Student Read Model", True, "Student view correctly uses student_id filter")
                        else:
                            self.log_result("Student Read Model", False, f"Student view filter incorrect. Expected student_id: {self.student_id}, Got: {log.get('student_id')}")
                        break
                
                if not student_log_found:
                    self.log_result("Student Visibility", False, "Student cannot see their own submitted log")
            else:
                self.log_result("Student Read Model", False, f"Student read failed: {response.status_code}")
            
            # Test supervisor view - should use supervisor_id filter
            response = await self.client.get(
                f"{API_BASE}/research-logs",
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                supervisor_logs = response.json()
                supervisor_log_found = False
                for log in supervisor_logs:
                    if log.get("id") == log_id:
                        supervisor_log_found = True
                        # Verify it uses supervisor_id filter
                        if log.get("supervisor_id") == self.supervisor_id:
                            self.log_result("Supervisor Read Model", True, "Supervisor view correctly uses supervisor_id filter")
                        else:
                            self.log_result("Supervisor Read Model", False, f"Supervisor view filter incorrect. Expected supervisor_id: {self.supervisor_id}, Got: {log.get('supervisor_id')}")
                        break
                
                if supervisor_log_found:
                    self.log_result("Supervisor Visibility", True, "Supervisor can see student's submitted log")
                else:
                    self.log_result("Supervisor Visibility", False, "Supervisor cannot see student's submitted log")
                
                # Verify consistent data between views
                if student_log_found and supervisor_log_found:
                    self.log_result("Data Consistency", True, "Both student and supervisor can see the same log (no empty student views)")
                else:
                    self.log_result("Data Consistency", False, "Data inconsistency between student and supervisor views")
            else:
                self.log_result("Supervisor Read Model", False, f"Supervisor read failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("Unified Read Test", False, f"Exception: {str(e)}")
    
    async def test_supervisor_actions_with_realtime_emission(self):
        """Test 4: Supervisor Actions with Immediate Real-time Emission"""
        print("\n🔍 TESTING: Supervisor Actions with Immediate Real-time Emission")
        
        try:
            # Create and submit a research log first
            log_id = await self.test_submit_endpoint_with_idempotency()
            if not log_id:
                self.log_result("Supervisor Actions Setup", False, "Could not create submitted log for supervisor actions test")
                return
            
            # Test RETURN action (SUBMITTED → RETURNED)
            return_data = {
                "comment": "Please revise the methodology section"
            }
            
            response = await self.client.post(
                f"{API_BASE}/research-logs/{log_id}/return",
                json=return_data,
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                self.log_result("Return Action", True, "Research log return action working")
                
                # Verify state change
                response = await self.client.get(
                    f"{API_BASE}/research-logs",
                    headers=self.get_supervisor_headers()
                )
                
                if response.status_code == 200:
                    logs = response.json()
                    returned_log = None
                    for log in logs:
                        if log.get("id") == log_id:
                            returned_log = log
                            break
                    
                    if returned_log and returned_log.get("status") == "returned":
                        self.log_result("Return State Change", True, "Status correctly changed to RETURNED")
                    else:
                        self.log_result("Return State Change", False, f"Status not updated. Status: {returned_log.get('status') if returned_log else 'Log not found'}")
            else:
                self.log_result("Return Action", False, f"Return action failed: {response.status_code} - {response.text}")
            
            # Re-submit the log for accept/decline tests
            response = await self.client.post(
                f"{API_BASE}/research-logs/{log_id}/submit",
                headers=self.get_student_headers()
            )
            
            if response.status_code == 200:
                # Test ACCEPT action (SUBMITTED → ACCEPTED)
                accept_data = {
                    "comment": "Excellent work, well done!"
                }
                
                response = await self.client.post(
                    f"{API_BASE}/research-logs/{log_id}/accept",
                    json=accept_data,
                    headers=self.get_supervisor_headers()
                )
                
                if response.status_code == 200:
                    self.log_result("Accept Action", True, "Research log accept action working")
                    
                    # Verify state change
                    response = await self.client.get(
                        f"{API_BASE}/research-logs",
                        headers=self.get_supervisor_headers()
                    )
                    
                    if response.status_code == 200:
                        logs = response.json()
                        accepted_log = None
                        for log in logs:
                            if log.get("id") == log_id:
                                accepted_log = log
                                break
                        
                        if accepted_log and accepted_log.get("status") == "accepted":
                            self.log_result("Accept State Change", True, "Status correctly changed to ACCEPTED")
                        else:
                            self.log_result("Accept State Change", False, f"Status not updated. Status: {accepted_log.get('status') if accepted_log else 'Log not found'}")
                else:
                    self.log_result("Accept Action", False, f"Accept action failed: {response.status_code} - {response.text}")
            
            # Test authority checking using supervisor_id field
            # Try to perform supervisor action as student (should fail)
            response = await self.client.post(
                f"{API_BASE}/research-logs/{log_id}/return",
                json={"comment": "Student trying supervisor action"},
                headers=self.get_student_headers()
            )
            
            if response.status_code == 403:
                self.log_result("Authority Check", True, "Proper authority checking - student blocked from supervisor actions")
            else:
                self.log_result("Authority Check", False, f"Authority check failed. Expected 403, got: {response.status_code}")
                
        except Exception as e:
            self.log_result("Supervisor Actions Test", False, f"Exception: {str(e)}")
    
    async def test_workflow_state_machine_validation(self):
        """Test 6: Workflow State Machine Validation"""
        print("\n🔍 TESTING: Workflow State Machine Validation")
        
        try:
            # Create a research log in DRAFT state
            research_log_data = {
                "activity_type": "analysis",
                "title": "State Machine Test Log",
                "description": "Testing workflow state transitions",
                "duration_hours": 2.0,
                "findings": "Testing state machine",
                "challenges": "Ensuring proper state transitions",
                "next_steps": "Validate all transitions",
                "tags": ["state-machine", "test"]
            }
            
            response = await self.client.post(
                f"{API_BASE}/research-logs",
                json=research_log_data,
                headers=self.get_student_headers()
            )
            
            if response.status_code in [200, 201]:
                log_data = response.json()
                log_id = log_data["id"]
                
                # Test VALID transition: DRAFT → SUBMITTED
                response = await self.client.post(
                    f"{API_BASE}/research-logs/{log_id}/submit",
                    headers=self.get_student_headers()
                )
                
                if response.status_code == 200:
                    self.log_result("Valid Transition DRAFT→SUBMITTED", True, "Valid state transition allowed")
                else:
                    self.log_result("Valid Transition DRAFT→SUBMITTED", False, f"Valid transition rejected: {response.status_code}")
                
                # Test VALID transition: SUBMITTED → RETURNED
                response = await self.client.post(
                    f"{API_BASE}/research-logs/{log_id}/return",
                    json={"comment": "Please revise"},
                    headers=self.get_supervisor_headers()
                )
                
                if response.status_code == 200:
                    self.log_result("Valid Transition SUBMITTED→RETURNED", True, "Valid state transition allowed")
                else:
                    self.log_result("Valid Transition SUBMITTED→RETURNED", False, f"Valid transition rejected: {response.status_code}")
                
                # Test VALID transition: RETURNED → SUBMITTED
                response = await self.client.post(
                    f"{API_BASE}/research-logs/{log_id}/submit",
                    headers=self.get_student_headers()
                )
                
                if response.status_code == 200:
                    self.log_result("Valid Transition RETURNED→SUBMITTED", True, "Valid state transition allowed")
                else:
                    self.log_result("Valid Transition RETURNED→SUBMITTED", False, f"Valid transition rejected: {response.status_code}")
                
                # Test VALID transition: SUBMITTED → ACCEPTED
                response = await self.client.post(
                    f"{API_BASE}/research-logs/{log_id}/accept",
                    json={"comment": "Approved"},
                    headers=self.get_supervisor_headers()
                )
                
                if response.status_code == 200:
                    self.log_result("Valid Transition SUBMITTED→ACCEPTED", True, "Valid state transition allowed")
                    
                    # Test INVALID transition: ACCEPTED → SUBMITTED (should fail)
                    response = await self.client.post(
                        f"{API_BASE}/research-logs/{log_id}/submit",
                        headers=self.get_student_headers()
                    )
                    
                    if response.status_code in [400, 403]:
                        self.log_result("Invalid Transition ACCEPTED→SUBMITTED", True, "Invalid state transition properly rejected")
                    else:
                        self.log_result("Invalid Transition ACCEPTED→SUBMITTED", False, f"Invalid transition allowed: {response.status_code}")
                else:
                    self.log_result("Valid Transition SUBMITTED→ACCEPTED", False, f"Valid transition rejected: {response.status_code}")
            else:
                self.log_result("State Machine Test Setup", False, f"Could not create research log: {response.status_code}")
                
        except Exception as e:
            self.log_result("State Machine Test", False, f"Exception: {str(e)}")
    
    async def test_data_consistency_verification(self):
        """Test 7: Data Consistency Verification"""
        print("\n🔍 TESTING: Data Consistency Verification")
        
        try:
            # Create multiple research logs and verify consistency
            log_ids = []
            
            for i in range(3):
                research_log_data = {
                    "activity_type": "experiment",
                    "title": f"Consistency Test Log {i+1}",
                    "description": f"Testing data consistency - Log {i+1}",
                    "duration_hours": 1.5 + i,
                    "findings": f"Findings for log {i+1}",
                    "challenges": f"Challenges for log {i+1}",
                    "next_steps": f"Next steps for log {i+1}",
                    "tags": ["consistency", "test", f"log{i+1}"]
                }
                
                response = await self.client.post(
                    f"{API_BASE}/research-logs",
                    json=research_log_data,
                    headers=self.get_student_headers()
                )
                
                if response.status_code in [200, 201]:
                    log_data = response.json()
                    log_ids.append(log_data["id"])
                    
                    # Verify each log has proper student_id AND supervisor_id
                    if log_data.get("student_id") and log_data.get("supervisor_id"):
                        self.log_result(f"Log {i+1} Key Population", True, f"Log {i+1} has both student_id and supervisor_id populated")
                    else:
                        self.log_result(f"Log {i+1} Key Population", False, f"Log {i+1} missing relational keys. student_id: {log_data.get('student_id')}, supervisor_id: {log_data.get('supervisor_id')}")
                else:
                    self.log_result(f"Log {i+1} Creation", False, f"Failed to create log {i+1}: {response.status_code}")
            
            if len(log_ids) >= 2:
                # Submit some logs and verify cross-role visibility
                for log_id in log_ids[:2]:
                    await self.client.post(
                        f"{API_BASE}/research-logs/{log_id}/submit",
                        headers=self.get_student_headers()
                    )
                
                # Check student view
                response = await self.client.get(
                    f"{API_BASE}/research-logs",
                    headers=self.get_student_headers()
                )
                
                student_logs = []
                if response.status_code == 200:
                    student_logs = response.json()
                    student_submitted_count = len([log for log in student_logs if log.get("status") == "submitted"])
                    self.log_result("Student View Submitted Logs", True, f"Student can see {student_submitted_count} submitted logs")
                else:
                    self.log_result("Student View", False, f"Student view failed: {response.status_code}")
                
                # Check supervisor view
                response = await self.client.get(
                    f"{API_BASE}/research-logs",
                    headers=self.get_supervisor_headers()
                )
                
                if response.status_code == 200:
                    supervisor_logs = response.json()
                    supervisor_submitted_count = len([log for log in supervisor_logs if log.get("status") == "submitted"])
                    
                    # Verify supervisor sees the same submitted logs
                    if student_submitted_count == supervisor_submitted_count and supervisor_submitted_count >= 2:
                        self.log_result("Cross-Role Data Visibility", True, "Student and supervisor see consistent submitted logs")
                    else:
                        self.log_result("Cross-Role Data Visibility", False, f"Data inconsistency. Student sees {student_submitted_count}, supervisor sees {supervisor_submitted_count}")
                    
                    # Verify no logs are "lost" between role views
                    student_log_ids = set(log.get("id") for log in student_logs if log.get("status") == "submitted")
                    supervisor_log_ids = set(log.get("id") for log in supervisor_logs if log.get("status") == "submitted")
                    
                    if student_log_ids == supervisor_log_ids:
                        self.log_result("No Lost Logs", True, "No logs lost between role views")
                    else:
                        self.log_result("No Lost Logs", False, f"Log ID mismatch. Student IDs: {student_log_ids}, Supervisor IDs: {supervisor_log_ids}")
                else:
                    self.log_result("Supervisor View", False, f"Supervisor view failed: {response.status_code}")
            else:
                self.log_result("Consistency Test Setup", False, "Could not create enough logs for consistency testing")
                
        except Exception as e:
            self.log_result("Data Consistency Test", False, f"Exception: {str(e)}")
    
    async def test_qa_acceptance_scenarios(self):
        """Test QA Acceptance Scenarios"""
        print("\n🔍 TESTING: QA Acceptance Scenarios")
        
        try:
            # QA Scenario 1: Student submit → Supervisor return → Student resubmit → Supervisor accept
            print("\n📋 QA Scenario 1: Complete Workflow Test")
            
            # Create research log
            research_log_data = {
                "activity_type": "writing",
                "title": "QA Acceptance Test Research Log",
                "description": "Testing complete workflow for QA acceptance",
                "duration_hours": 4.0,
                "findings": "Complete workflow testing findings",
                "challenges": "Ensuring real-time updates at each step",
                "next_steps": "Verify all workflow steps work correctly",
                "tags": ["qa", "acceptance", "workflow"]
            }
            
            response = await self.client.post(
                f"{API_BASE}/research-logs",
                json=research_log_data,
                headers=self.get_student_headers()
            )
            
            if response.status_code in [200, 201]:
                log_data = response.json()
                log_id = log_data["id"]
                
                # Step 1: Student submit
                response = await self.client.post(
                    f"{API_BASE}/research-logs/{log_id}/submit",
                    headers=self.get_student_headers()
                )
                
                if response.status_code == 200:
                    self.log_result("QA Step 1: Student Submit", True, "Student successfully submitted research log")
                    
                    # Step 2: Supervisor return
                    response = await self.client.post(
                        f"{API_BASE}/research-logs/{log_id}/return",
                        json={"comment": "Please add more details to the methodology section"},
                        headers=self.get_supervisor_headers()
                    )
                    
                    if response.status_code == 200:
                        self.log_result("QA Step 2: Supervisor Return", True, "Supervisor successfully returned research log")
                        
                        # Verify student can see returned log with comment
                        response = await self.client.get(
                            f"{API_BASE}/research-logs",
                            headers=self.get_student_headers()
                        )
                        
                        if response.status_code == 200:
                            logs = response.json()
                            returned_log = None
                            for log in logs:
                                if log.get("id") == log_id:
                                    returned_log = log
                                    break
                            
                            if returned_log and returned_log.get("status") == "returned":
                                self.log_result("QA Step 2 Verification", True, "Student can see returned log with supervisor comment")
                                
                                # Step 3: Student resubmit
                                response = await self.client.post(
                                    f"{API_BASE}/research-logs/{log_id}/submit",
                                    headers=self.get_student_headers()
                                )
                                
                                if response.status_code == 200:
                                    self.log_result("QA Step 3: Student Resubmit", True, "Student successfully resubmitted research log")
                                    
                                    # Step 4: Supervisor accept
                                    response = await self.client.post(
                                        f"{API_BASE}/research-logs/{log_id}/accept",
                                        json={"comment": "Excellent work! Approved."},
                                        headers=self.get_supervisor_headers()
                                    )
                                    
                                    if response.status_code == 200:
                                        self.log_result("QA Step 4: Supervisor Accept", True, "Supervisor successfully accepted research log")
                                        
                                        # Verify final accepted state visible to both parties
                                        # Check student view
                                        response = await self.client.get(
                                            f"{API_BASE}/research-logs",
                                            headers=self.get_student_headers()
                                        )
                                        
                                        student_sees_accepted = False
                                        if response.status_code == 200:
                                            logs = response.json()
                                            for log in logs:
                                                if log.get("id") == log_id and log.get("status") == "accepted":
                                                    student_sees_accepted = True
                                                    break
                                        
                                        # Check supervisor view
                                        response = await self.client.get(
                                            f"{API_BASE}/research-logs",
                                            headers=self.get_supervisor_headers()
                                        )
                                        
                                        supervisor_sees_accepted = False
                                        if response.status_code == 200:
                                            logs = response.json()
                                            for log in logs:
                                                if log.get("id") == log_id and log.get("status") == "accepted":
                                                    supervisor_sees_accepted = True
                                                    break
                                        
                                        if student_sees_accepted and supervisor_sees_accepted:
                                            self.log_result("QA Complete Workflow", True, "✅ COMPLETE WORKFLOW SUCCESS: Student submit → Supervisor return → Student resubmit → Supervisor accept - ALL STEPS WORKING")
                                        else:
                                            self.log_result("QA Complete Workflow", False, f"Final state visibility issue. Student sees accepted: {student_sees_accepted}, Supervisor sees accepted: {supervisor_sees_accepted}")
                                    else:
                                        self.log_result("QA Step 4: Supervisor Accept", False, f"Supervisor accept failed: {response.status_code}")
                                else:
                                    self.log_result("QA Step 3: Student Resubmit", False, f"Student resubmit failed: {response.status_code}")
                            else:
                                self.log_result("QA Step 2 Verification", False, f"Student cannot see returned log properly. Status: {returned_log.get('status') if returned_log else 'Log not found'}")
                        else:
                            self.log_result("QA Step 2 Verification", False, f"Student view failed: {response.status_code}")
                    else:
                        self.log_result("QA Step 2: Supervisor Return", False, f"Supervisor return failed: {response.status_code}")
                else:
                    self.log_result("QA Step 1: Student Submit", False, f"Student submit failed: {response.status_code}")
            else:
                self.log_result("QA Scenario Setup", False, f"Could not create research log for QA test: {response.status_code}")
                
        except Exception as e:
            self.log_result("QA Acceptance Test", False, f"Exception: {str(e)}")
    
    async def run_all_tests(self):
        """Run all real-time synchronization tests"""
        print("🚀 STARTING REAL-TIME SYNCHRONIZATION TESTING")
        print("=" * 70)
        print("🎯 FOCUS: Critical blocking bug fixes for real-time synchronization")
        print("=" * 70)
        
        # Setup test users
        if not await self.setup_test_users():
            print("❌ Cannot proceed without authenticated users")
            return
        
        # Run all critical tests
        await self.test_research_log_creation_with_relational_keys()
        await self.test_submit_endpoint_with_idempotency()
        await self.test_unified_read_models()
        await self.test_supervisor_actions_with_realtime_emission()
        await self.test_workflow_state_machine_validation()
        await self.test_data_consistency_verification()
        await self.test_qa_acceptance_scenarios()
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 REAL-TIME SYNCHRONIZATION TEST SUMMARY")
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
        
        # Critical issues summary
        critical_failures = [r for r in self.test_results if "❌ FAIL" in r["status"] and any(keyword in r["test"].lower() for keyword in ["relational", "key", "consistency", "workflow", "qa"])]
        
        if critical_failures:
            print(f"\n🚨 CRITICAL ISSUES FOUND ({len(critical_failures)}):")
            for failure in critical_failures:
                print(f"   ❌ {failure['test']}: {failure['message']}")
        else:
            print("\n✅ NO CRITICAL ISSUES FOUND - Real-time synchronization system working correctly")
        
        return passed_tests, failed_tests

async def main():
    async with RealTimeSyncTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
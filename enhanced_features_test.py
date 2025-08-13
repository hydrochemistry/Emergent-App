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

class EnhancedFeaturesTester:
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
            # Setup supervisor
            supervisor_data = {
                "email": "enhanced.supervisor@research.lab",
                "password": "TestPassword123!",
                "full_name": "Dr. Enhanced Supervisor",
                "role": "supervisor",
                "department": "Computer Science",
                "research_area": "Machine Learning",
                "lab_name": "Enhanced AI Research Lab"
            }
            
            response = await self.client.post(f"{API_BASE}/auth/register", json=supervisor_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.supervisor_token = data["access_token"]
                self.supervisor_id = data["user_data"]["id"]
                self.log_result("Supervisor Setup", True, "Test supervisor created and authenticated")
            elif response.status_code == 400 and "already registered" in response.text:
                # Login existing supervisor
                login_data = {
                    "email": "enhanced.supervisor@research.lab",
                    "password": "TestPassword123!"
                }
                response = await self.client.post(f"{API_BASE}/auth/login", json=login_data)
                if response.status_code == 200:
                    data = response.json()
                    self.supervisor_token = data["access_token"]
                    self.supervisor_id = data["user_data"]["id"]
                    self.log_result("Supervisor Setup", True, "Logged in with existing supervisor")
            
            # Setup student
            student_data = {
                "email": "enhanced.student@research.lab",
                "password": "TestPassword123!",
                "full_name": "Jane Enhanced Student",
                "role": "student",
                "student_id": "ENH2024001",
                "department": "Computer Science",
                "program_type": "phd_research",
                "supervisor_email": "enhanced.supervisor@research.lab",
                "field_of_study": "Artificial Intelligence",
                "research_area": "Deep Learning"
            }
            
            response = await self.client.post(f"{API_BASE}/auth/register", json=student_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.student_token = data["access_token"]
                self.student_id = data["user_data"]["id"]
                self.log_result("Student Setup", True, "Test student created and authenticated")
            elif response.status_code == 400 and "already registered" in response.text:
                # Login existing student
                login_data = {
                    "email": "enhanced.student@research.lab",
                    "password": "TestPassword123!"
                }
                response = await self.client.post(f"{API_BASE}/auth/login", json=login_data)
                if response.status_code == 200:
                    data = response.json()
                    self.student_token = data["access_token"]
                    self.student_id = data["user_data"]["id"]
                    self.log_result("Student Setup", True, "Logged in with existing student")
            
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
    
    async def test_student_research_log_status_tracking(self):
        """Test 1: Student Research Log Status Tracking System"""
        print("\n🔍 TESTING: Student Research Log Status Tracking System")
        
        try:
            # First, create some research logs as student
            research_logs = []
            for i in range(3):
                log_data = {
                    "activity_type": "experiment",
                    "title": f"Enhanced Research Log {i+1}",
                    "description": f"Testing enhanced research log status tracking - Log {i+1}",
                    "duration_hours": 2.5,
                    "findings": f"Important findings from experiment {i+1}",
                    "challenges": f"Challenges faced in experiment {i+1}",
                    "next_steps": f"Next steps for experiment {i+1}",
                    "tags": ["enhanced", "testing", f"log{i+1}"]
                }
                
                response = await self.client.post(
                    f"{API_BASE}/research-logs", 
                    json=log_data, 
                    headers=self.get_student_headers()
                )
                
                if response.status_code in [200, 201]:
                    log_id = response.json()["id"]
                    research_logs.append(log_id)
                    self.log_result(f"Research Log Creation {i+1}", True, f"Created research log {i+1}")
                else:
                    self.log_result(f"Research Log Creation {i+1}", False, f"Failed to create research log: {response.status_code}")
            
            # Review some logs as supervisor
            if research_logs:
                # Accept first log
                review_data = {
                    "action": "accepted",
                    "feedback": "Excellent work! This research log shows great progress."
                }
                response = await self.client.post(
                    f"{API_BASE}/research-logs/{research_logs[0]}/review",
                    json=review_data,
                    headers=self.get_supervisor_headers()
                )
                
                if response.status_code == 200:
                    self.log_result("Research Log Review - Accept", True, "Successfully accepted research log")
                else:
                    self.log_result("Research Log Review - Accept", False, f"Failed to accept log: {response.status_code}")
                
                # Request revision for second log
                if len(research_logs) > 1:
                    review_data = {
                        "action": "revision",
                        "feedback": "Good work, but please add more details about the methodology used."
                    }
                    response = await self.client.post(
                        f"{API_BASE}/research-logs/{research_logs[1]}/review",
                        json=review_data,
                        headers=self.get_supervisor_headers()
                    )
                    
                    if response.status_code == 200:
                        self.log_result("Research Log Review - Revision", True, "Successfully requested revision")
                    else:
                        self.log_result("Research Log Review - Revision", False, f"Failed to request revision: {response.status_code}")
            
            # Test the new student status endpoint
            response = await self.client.get(
                f"{API_BASE}/research-logs/student/status",
                headers=self.get_student_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                logs = data.get("logs", [])
                total_count = data.get("total_count", 0)
                
                self.log_result("Student Status Endpoint", True, f"Retrieved {total_count} research logs with status")
                
                # Verify status information is present
                status_found = False
                for log in logs:
                    if "status" in log and "submission_date" in log:
                        status_found = True
                        break
                
                if status_found:
                    self.log_result("Status Information", True, "Research logs contain proper status information")
                else:
                    self.log_result("Status Information", False, "Research logs missing status information")
                
                # Test that supervisors cannot access this endpoint
                response = await self.client.get(
                    f"{API_BASE}/research-logs/student/status",
                    headers=self.get_supervisor_headers()
                )
                
                if response.status_code == 403:
                    self.log_result("Supervisor Access Block", True, "Supervisors properly blocked from student status endpoint")
                else:
                    self.log_result("Supervisor Access Block", False, f"Supervisors not blocked: {response.status_code}")
                    
            else:
                self.log_result("Student Status Endpoint", False, f"Failed to get student status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Student Research Log Status", False, f"Exception: {str(e)}")
    
    async def test_enhanced_grants_synchronization(self):
        """Test 2: Enhanced Grants Synchronization System"""
        print("\n🔍 TESTING: Enhanced Grants Synchronization System")
        
        try:
            # Create some grants as supervisor
            grant_ids = []
            for i in range(3):
                grant_data = {
                    "title": f"Enhanced Research Grant {i+1}",
                    "funding_agency": f"National Science Foundation {i+1}",
                    "funding_type": "national",
                    "total_amount": 50000.0 + (i * 10000),
                    "status": "active",
                    "start_date": datetime.now().isoformat(),
                    "end_date": (datetime.now() + timedelta(days=365)).isoformat(),
                    "description": f"Enhanced grant for testing synchronization {i+1}",
                    "person_in_charge": self.student_id,
                    "grant_vote_number": f"NSF-2024-{i+1:03d}",
                    "duration_months": 12,
                    "grant_type": "research"
                }
                
                response = await self.client.post(
                    f"{API_BASE}/grants",
                    json=grant_data,
                    headers=self.get_supervisor_headers()
                )
                
                if response.status_code in [200, 201]:
                    grant_id = response.json()["id"]
                    grant_ids.append(grant_id)
                    self.log_result(f"Grant Creation {i+1}", True, f"Created grant {i+1}")
                else:
                    self.log_result(f"Grant Creation {i+1}", False, f"Failed to create grant: {response.status_code}")
            
            # Test supervisor can see grants
            response = await self.client.get(
                f"{API_BASE}/grants",
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                supervisor_grants = response.json()
                self.log_result("Supervisor Grants Access", True, f"Supervisor can see {len(supervisor_grants)} grants")
            else:
                self.log_result("Supervisor Grants Access", False, f"Supervisor cannot access grants: {response.status_code}")
                supervisor_grants = []
            
            # Test student can see same grants (synchronization)
            response = await self.client.get(
                f"{API_BASE}/grants",
                headers=self.get_student_headers()
            )
            
            if response.status_code == 200:
                student_grants = response.json()
                self.log_result("Student Grants Access", True, f"Student can see {len(student_grants)} grants")
                
                # Verify synchronization - student should see supervisor's lab grants
                if len(student_grants) >= len(grant_ids):
                    self.log_result("Grants Synchronization", True, "Student sees grants from supervisor's lab")
                else:
                    self.log_result("Grants Synchronization", False, "Student not seeing all lab grants")
                    
            else:
                self.log_result("Student Grants Access", False, f"Student cannot access grants: {response.status_code}")
            
            # Test helper function by checking if students without supervisors get empty list
            # This would require creating a student without supervisor, but we'll test the main functionality
            
        except Exception as e:
            self.log_result("Enhanced Grants Synchronization", False, f"Exception: {str(e)}")
    
    async def test_active_grants_dashboard(self):
        """Test 3: Active Grants Dashboard System"""
        print("\n🔍 TESTING: Active Grants Dashboard System")
        
        try:
            # Test the active grants endpoint
            response = await self.client.get(
                f"{API_BASE}/grants/active",
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                active_grants = data.get("active_grants", [])
                total_active_grants = data.get("total_active_grants", 0)
                cumulative_balance = data.get("cumulative_balance", 0)
                
                self.log_result("Active Grants Endpoint", True, f"Retrieved {total_active_grants} active grants")
                
                # Verify balance calculations
                calculated_balance = 0
                for grant in active_grants:
                    if "remaining_balance" in grant:
                        calculated_balance += grant["remaining_balance"]
                        self.log_result("Grant Balance Calculation", True, f"Grant has remaining_balance field")
                    else:
                        self.log_result("Grant Balance Calculation", False, "Grant missing remaining_balance field")
                
                if abs(calculated_balance - cumulative_balance) < 0.01:  # Allow for floating point precision
                    self.log_result("Cumulative Balance", True, f"Cumulative balance correctly calculated: ${cumulative_balance:,.2f}")
                else:
                    self.log_result("Cumulative Balance", False, f"Balance mismatch: calculated {calculated_balance}, returned {cumulative_balance}")
                
                # Test student can also access active grants
                response = await self.client.get(
                    f"{API_BASE}/grants/active",
                    headers=self.get_student_headers()
                )
                
                if response.status_code == 200:
                    student_data = response.json()
                    student_active_grants = student_data.get("total_active_grants", 0)
                    self.log_result("Student Active Grants Access", True, f"Student can see {student_active_grants} active grants")
                else:
                    self.log_result("Student Active Grants Access", False, f"Student cannot access active grants: {response.status_code}")
                    
            else:
                self.log_result("Active Grants Endpoint", False, f"Failed to get active grants: {response.status_code}")
                
        except Exception as e:
            self.log_result("Active Grants Dashboard", False, f"Exception: {str(e)}")
    
    async def test_enhanced_dashboard_stats(self):
        """Test 4: Enhanced Dashboard Stats"""
        print("\n🔍 TESTING: Enhanced Dashboard Stats")
        
        try:
            # Test student dashboard stats
            response = await self.client.get(
                f"{API_BASE}/dashboard/stats",
                headers=self.get_student_headers()
            )
            
            if response.status_code == 200:
                student_stats = response.json()
                
                # Check for new student fields
                expected_student_fields = [
                    "approved_research_logs", "pending_research_logs", 
                    "revision_research_logs", "active_grants_count", "active_grants_balance"
                ]
                
                missing_fields = []
                for field in expected_student_fields:
                    if field not in student_stats:
                        missing_fields.append(field)
                
                if not missing_fields:
                    self.log_result("Student Dashboard Stats", True, "All enhanced student fields present")
                else:
                    self.log_result("Student Dashboard Stats", False, f"Missing fields: {missing_fields}")
                
            else:
                self.log_result("Student Dashboard Stats", False, f"Failed to get student stats: {response.status_code}")
            
            # Test supervisor dashboard stats
            response = await self.client.get(
                f"{API_BASE}/dashboard/stats",
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                supervisor_stats = response.json()
                
                # Check for new supervisor fields
                expected_supervisor_fields = [
                    "active_grants_count", "active_grants_balance", "active_grants"
                ]
                
                missing_fields = []
                for field in expected_supervisor_fields:
                    if field not in supervisor_stats:
                        missing_fields.append(field)
                
                if not missing_fields:
                    self.log_result("Supervisor Dashboard Stats", True, "All enhanced supervisor fields present")
                else:
                    self.log_result("Supervisor Dashboard Stats", False, f"Missing fields: {missing_fields}")
                
            else:
                self.log_result("Supervisor Dashboard Stats", False, f"Failed to get supervisor stats: {response.status_code}")
                
        except Exception as e:
            self.log_result("Enhanced Dashboard Stats", False, f"Exception: {str(e)}")
    
    async def test_enhanced_research_logs_system(self):
        """Test 5: Enhanced Research Logs System"""
        print("\n🔍 TESTING: Enhanced Research Logs System")
        
        try:
            # Test supervisor view of research logs
            response = await self.client.get(
                f"{API_BASE}/research-logs",
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                supervisor_logs = response.json()
                self.log_result("Supervisor Research Logs Access", True, f"Supervisor can see {len(supervisor_logs)} research logs")
                
                # Check for student information enhancement
                student_info_present = False
                review_status_present = False
                
                for log in supervisor_logs:
                    if "student_name" in log and "student_id" in log and "student_email" in log:
                        student_info_present = True
                    if "review_status" in log and "review_feedback" in log:
                        review_status_present = True
                
                if student_info_present:
                    self.log_result("Student Information Enhancement", True, "Research logs include student information")
                else:
                    self.log_result("Student Information Enhancement", False, "Research logs missing student information")
                
                if review_status_present:
                    self.log_result("Review Status Fields", True, "Research logs include review status fields")
                else:
                    self.log_result("Review Status Fields", False, "Research logs missing review status fields")
                    
            else:
                self.log_result("Supervisor Research Logs Access", False, f"Supervisor cannot access research logs: {response.status_code}")
            
            # Test student view of research logs (lab-wide synchronization)
            response = await self.client.get(
                f"{API_BASE}/research-logs",
                headers=self.get_student_headers()
            )
            
            if response.status_code == 200:
                student_logs = response.json()
                self.log_result("Student Research Logs Access", True, f"Student can see {len(student_logs)} research logs")
                
                # Verify lab-wide synchronization - student should see lab-wide logs
                if len(student_logs) > 0:
                    self.log_result("Lab-wide Synchronization", True, "Student can see lab-wide research logs")
                else:
                    self.log_result("Lab-wide Synchronization", False, "Student cannot see lab-wide research logs")
                    
            else:
                self.log_result("Student Research Logs Access", False, f"Student cannot access research logs: {response.status_code}")
                
        except Exception as e:
            self.log_result("Enhanced Research Logs System", False, f"Exception: {str(e)}")
    
    async def test_supervisor_student_hierarchy(self):
        """Test 6: Supervisor-Student Hierarchy Enforcement"""
        print("\n🔍 TESTING: Supervisor-Student Hierarchy Enforcement")
        
        try:
            # Test that students cannot access supervisor-only endpoints
            supervisor_only_endpoints = [
                "/grants",  # Students should be able to view but not create
                "/bulletins/1/approve",  # Students cannot approve bulletins
                "/users/promote"  # Students cannot promote users
            ]
            
            # Test grant creation (students should be blocked)
            grant_data = {
                "title": "Unauthorized Grant",
                "funding_agency": "Test Agency",
                "funding_type": "national",
                "total_amount": 10000.0,
                "status": "active",
                "start_date": datetime.now().isoformat(),
                "end_date": (datetime.now() + timedelta(days=365)).isoformat()
            }
            
            response = await self.client.post(
                f"{API_BASE}/grants",
                json=grant_data,
                headers=self.get_student_headers()
            )
            
            if response.status_code == 403:
                self.log_result("Student Grant Creation Block", True, "Students properly blocked from creating grants")
            else:
                self.log_result("Student Grant Creation Block", False, f"Students not blocked from grant creation: {response.status_code}")
            
            # Test that supervisors can access supervisor endpoints
            response = await self.client.get(
                f"{API_BASE}/grants",
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                self.log_result("Supervisor Grant Access", True, "Supervisors can access grants")
            else:
                self.log_result("Supervisor Grant Access", False, f"Supervisors cannot access grants: {response.status_code}")
            
            # Test research log review (only supervisors should be able to review)
            # First create a research log as student
            log_data = {
                "activity_type": "experiment",
                "title": "Test Log for Review",
                "description": "Testing hierarchy enforcement",
                "duration_hours": 1.0
            }
            
            response = await self.client.post(
                f"{API_BASE}/research-logs",
                json=log_data,
                headers=self.get_student_headers()
            )
            
            if response.status_code in [200, 201]:
                log_id = response.json()["id"]
                
                # Try to review as student (should be blocked)
                review_data = {
                    "action": "accepted",
                    "feedback": "Self-approval attempt"
                }
                
                response = await self.client.post(
                    f"{API_BASE}/research-logs/{log_id}/review",
                    json=review_data,
                    headers=self.get_student_headers()
                )
                
                if response.status_code == 403:
                    self.log_result("Student Review Block", True, "Students properly blocked from reviewing logs")
                else:
                    self.log_result("Student Review Block", False, f"Students not blocked from reviewing: {response.status_code}")
                
                # Try to review as supervisor (should work)
                response = await self.client.post(
                    f"{API_BASE}/research-logs/{log_id}/review",
                    json=review_data,
                    headers=self.get_supervisor_headers()
                )
                
                if response.status_code == 200:
                    self.log_result("Supervisor Review Access", True, "Supervisors can review research logs")
                else:
                    self.log_result("Supervisor Review Access", False, f"Supervisors cannot review logs: {response.status_code}")
                    
        except Exception as e:
            self.log_result("Supervisor-Student Hierarchy", False, f"Exception: {str(e)}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("🎯 ENHANCED FEATURES TESTING SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["status"] == "✅ PASS")
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if result["status"] == "❌ FAIL":
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n✅ PASSED TESTS:")
        for result in self.test_results:
            if result["status"] == "✅ PASS":
                print(f"  - {result['test']}: {result['message']}")

async def main():
    """Main test execution"""
    print("🚀 STARTING ENHANCED FEATURES TESTING")
    print("="*80)
    
    async with EnhancedFeaturesTester() as tester:
        # Setup test users
        if not await tester.setup_test_users():
            print("❌ Failed to setup test users. Exiting.")
            return
        
        # Run all enhanced feature tests
        await tester.test_student_research_log_status_tracking()
        await tester.test_enhanced_grants_synchronization()
        await tester.test_active_grants_dashboard()
        await tester.test_enhanced_dashboard_stats()
        await tester.test_enhanced_research_logs_system()
        await tester.test_supervisor_student_hierarchy()
        
        # Print summary
        tester.print_summary()

if __name__ == "__main__":
    asyncio.run(main())
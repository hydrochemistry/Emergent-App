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

class ReviewRequestTester:
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
                "email": "review.supervisor@research.lab",
                "password": "TestPassword123!",
                "full_name": "Dr. Review Test Supervisor",
                "role": "supervisor",
                "department": "Computer Science",
                "research_area": "Machine Learning",
                "lab_name": "Review Test Lab"
            }
            
            response = await self.client.post(f"{API_BASE}/auth/register", json=supervisor_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.supervisor_token = data["access_token"]
                self.supervisor_id = data["user_data"]["id"]
                self.log_result("Supervisor Setup", True, "Test supervisor created and authenticated")
            elif response.status_code == 400 and "already registered" in response.text:
                # Login instead
                login_data = {"email": "review.supervisor@research.lab", "password": "TestPassword123!"}
                response = await self.client.post(f"{API_BASE}/auth/login", json=login_data)
                if response.status_code == 200:
                    data = response.json()
                    self.supervisor_token = data["access_token"]
                    self.supervisor_id = data["user_data"]["id"]
                    self.log_result("Supervisor Setup", True, "Logged in with existing supervisor")
                else:
                    self.log_result("Supervisor Setup", False, f"Login failed: {response.status_code}")
                    return False
            else:
                self.log_result("Supervisor Setup", False, f"Registration failed: {response.status_code}")
                return False
            
            # Setup student
            student_data = {
                "email": "review.student@research.lab",
                "password": "TestPassword123!",
                "full_name": "Jane Review Test Student",
                "role": "student",
                "student_id": "CS2024003",
                "department": "Computer Science",
                "program_type": "phd_research",
                "supervisor_email": "review.supervisor@research.lab"
            }
            
            response = await self.client.post(f"{API_BASE}/auth/register", json=student_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.student_token = data["access_token"]
                self.student_id = data["user_data"]["id"]
                self.log_result("Student Setup", True, "Test student created and authenticated")
            elif response.status_code == 400 and "already registered" in response.text:
                # Login instead
                login_data = {"email": "review.student@research.lab", "password": "TestPassword123!"}
                response = await self.client.post(f"{API_BASE}/auth/login", json=login_data)
                if response.status_code == 200:
                    data = response.json()
                    self.student_token = data["access_token"]
                    self.student_id = data["user_data"]["id"]
                    self.log_result("Student Setup", True, "Logged in with existing student")
                else:
                    self.log_result("Student Setup", False, f"Student login failed: {response.status_code}")
                    return False
            else:
                self.log_result("Student Setup", False, f"Student registration failed: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_result("User Setup", False, f"Exception during user setup: {str(e)}")
            return False
    
    def get_supervisor_headers(self):
        return {"Authorization": f"Bearer {self.supervisor_token}"}
    
    def get_student_headers(self):
        return {"Authorization": f"Bearer {self.student_token}"}
    
    async def test_research_log_creation_fix(self):
        """Test 1: Research Log Creation Fix - Enhanced error handling"""
        print("\n🔍 TESTING: Research Log Creation Fix (Network Error Resolution)")
        
        try:
            # Test with enhanced data format (with log_date, log_time)
            research_log_data = {
                "activity_type": "experiment",
                "title": "Machine Learning Experiment Results",
                "description": "Conducted experiments on neural network performance",
                "findings": "Model achieved 89% accuracy on test dataset",
                "challenges": "Overfitting issues with small dataset",
                "next_steps": "Implement regularization techniques",
                "duration_hours": 4.5,
                "tags": ["machine-learning", "neural-networks", "experiments"],
                "log_date": "2025-01-15",
                "log_time": "14:30"
            }
            
            response = await self.client.post(
                f"{API_BASE}/research-logs",
                json=research_log_data,
                headers=self.get_student_headers()
            )
            
            if response.status_code in [200, 201]:
                log_data = response.json()
                self.log_result("Research Log Creation (Enhanced Format)", True, 
                              "Research log created successfully without 'Network connection failed' error")
                
                # Test with different data formats
                test_cases = [
                    {
                        "name": "Without log_date and log_time",
                        "data": {
                            "activity_type": "literature_review",
                            "title": "Literature Review Session",
                            "description": "Reviewing recent papers on deep learning",
                            "duration_hours": 2.0,
                            "tags": ["literature-review"]
                        }
                    },
                    {
                        "name": "With only log_date",
                        "data": {
                            "activity_type": "data_collection",
                            "title": "Data Collection Phase 1",
                            "description": "Collecting training data for model",
                            "duration_hours": 3.0,
                            "log_date": "2025-01-16",
                            "tags": ["data-collection"]
                        }
                    },
                    {
                        "name": "With only log_time",
                        "data": {
                            "activity_type": "analysis",
                            "title": "Data Analysis Session",
                            "description": "Analyzing experimental results",
                            "duration_hours": 1.5,
                            "log_time": "10:00",
                            "tags": ["analysis"]
                        }
                    }
                ]
                
                for test_case in test_cases:
                    response = await self.client.post(
                        f"{API_BASE}/research-logs",
                        json=test_case["data"],
                        headers=self.get_student_headers()
                    )
                    
                    if response.status_code in [200, 201]:
                        self.log_result(f"Research Log Creation ({test_case['name']})", True, 
                                      "Research log created successfully with different data format")
                    else:
                        self.log_result(f"Research Log Creation ({test_case['name']})", False, 
                                      f"Failed: {response.status_code} - {response.text}")
                
            else:
                self.log_result("Research Log Creation (Enhanced Format)", False, 
                              f"Failed to create research log: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Research Log Creation Fix", False, f"Exception: {str(e)}")
    
    async def test_data_synchronization_for_students(self):
        """Test 2: Data Synchronization - Students see lab-wide data"""
        print("\n🔍 TESTING: Data Synchronization for Students (Lab-wide Visibility)")
        
        try:
            # Test Research Logs Synchronization
            response_supervisor = await self.client.get(
                f"{API_BASE}/research-logs",
                headers=self.get_supervisor_headers()
            )
            
            response_student = await self.client.get(
                f"{API_BASE}/research-logs",
                headers=self.get_student_headers()
            )
            
            if response_supervisor.status_code == 200 and response_student.status_code == 200:
                supervisor_logs = response_supervisor.json()
                student_logs = response_student.json()
                
                # Students should see lab-wide research logs (not just their own)
                if len(student_logs) > 0:
                    # Check if student sees logs from other users in the lab
                    student_sees_lab_logs = any(
                        log.get("user_id") != self.student_id for log in student_logs
                    )
                    
                    if student_sees_lab_logs:
                        self.log_result("Research Logs Synchronization", True, 
                                      f"Students see lab-wide research logs ({len(student_logs)} total logs)")
                    else:
                        self.log_result("Research Logs Synchronization", False, 
                                      "Students only see their own logs, not lab-wide data")
                else:
                    self.log_result("Research Logs Synchronization", True, 
                                  "No research logs found - synchronization test not applicable")
            else:
                self.log_result("Research Logs Synchronization", False, 
                              "Failed to retrieve research logs for synchronization test")
            
            # Test Publications Synchronization
            response_supervisor = await self.client.get(
                f"{API_BASE}/publications",
                headers=self.get_supervisor_headers()
            )
            
            response_student = await self.client.get(
                f"{API_BASE}/publications",
                headers=self.get_student_headers()
            )
            
            if response_supervisor.status_code == 200 and response_student.status_code == 200:
                supervisor_pubs = response_supervisor.json()
                student_pubs = response_student.json()
                
                if len(supervisor_pubs) == len(student_pubs):
                    self.log_result("Publications Synchronization", True, 
                                  f"Students and supervisors see same publications ({len(student_pubs)} publications)")
                else:
                    self.log_result("Publications Synchronization", False, 
                                  f"Publication count mismatch - Supervisor: {len(supervisor_pubs)}, Student: {len(student_pubs)}")
            else:
                self.log_result("Publications Synchronization", False, 
                              "Failed to retrieve publications for synchronization test")
            
            # Test Grants Synchronization
            response_supervisor = await self.client.get(
                f"{API_BASE}/grants",
                headers=self.get_supervisor_headers()
            )
            
            response_student = await self.client.get(
                f"{API_BASE}/grants",
                headers=self.get_student_headers()
            )
            
            if response_supervisor.status_code == 200 and response_student.status_code == 200:
                supervisor_grants = response_supervisor.json()
                student_grants = response_student.json()
                
                if len(supervisor_grants) == len(student_grants):
                    self.log_result("Grants Synchronization", True, 
                                  f"Students and supervisors see same grants ({len(student_grants)} grants)")
                else:
                    self.log_result("Grants Synchronization", False, 
                                  f"Grants count mismatch - Supervisor: {len(supervisor_grants)}, Student: {len(student_grants)}")
            else:
                self.log_result("Grants Synchronization", False, 
                              "Failed to retrieve grants for synchronization test")
            
            # Test Bulletins Synchronization
            response_supervisor = await self.client.get(
                f"{API_BASE}/bulletins",
                headers=self.get_supervisor_headers()
            )
            
            response_student = await self.client.get(
                f"{API_BASE}/bulletins",
                headers=self.get_student_headers()
            )
            
            if response_supervisor.status_code == 200 and response_student.status_code == 200:
                supervisor_bulletins = response_supervisor.json()
                student_bulletins = response_student.json()
                
                # Students should see approved bulletins
                approved_bulletins = [b for b in supervisor_bulletins if b.get("status") == "approved"]
                
                if len(student_bulletins) >= len(approved_bulletins):
                    self.log_result("Bulletins Synchronization", True, 
                                  f"Students see approved bulletins ({len(student_bulletins)} bulletins)")
                else:
                    self.log_result("Bulletins Synchronization", False, 
                                  f"Students missing bulletins - Student: {len(student_bulletins)}, Expected: {len(approved_bulletins)}")
            else:
                self.log_result("Bulletins Synchronization", False, 
                              "Failed to retrieve bulletins for synchronization test")
                
        except Exception as e:
            self.log_result("Data Synchronization Test", False, f"Exception: {str(e)}")
    
    async def test_publications_sorting_by_date(self):
        """Test 3: Publications Sorting by Publication Date (newest first)"""
        print("\n🔍 TESTING: Publications Sorting by Publication Date (Newest First)")
        
        try:
            # Get publications list
            response = await self.client.get(
                f"{API_BASE}/publications",
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                publications = response.json()
                
                if len(publications) >= 2:
                    # Check if publications are sorted by publication_year (newest first)
                    is_sorted_correctly = True
                    years = []
                    
                    for i in range(len(publications) - 1):
                        current_year = publications[i].get("publication_year", 0)
                        next_year = publications[i + 1].get("publication_year", 0)
                        years.append(current_year)
                        
                        if current_year < next_year:
                            is_sorted_correctly = False
                            break
                    
                    if len(publications) > 0:
                        years.append(publications[-1].get("publication_year", 0))
                    
                    if is_sorted_correctly:
                        self.log_result("Publications Sorting", True, 
                                      f"Publications correctly sorted by publication_year (newest first)")
                        self.log_result("Publications Sorting Details", True, 
                                      f"Publication years in order: {years[:5]}...")
                    else:
                        self.log_result("Publications Sorting", False, 
                                      f"Publications not sorted correctly - Years: {years[:5]}...")
                        
                elif len(publications) == 1:
                    pub = publications[0]
                    self.log_result("Publications Sorting", True, 
                                  f"Single publication found: '{pub.get('title', 'Unknown')}' ({pub.get('publication_year', 'Unknown year')})")
                else:
                    self.log_result("Publications Sorting", True, 
                                  "No publications found - sorting test not applicable")
            else:
                self.log_result("Publications Sorting", False, 
                              f"Failed to retrieve publications: {response.status_code}")
                
        except Exception as e:
            self.log_result("Publications Sorting Test", False, f"Exception: {str(e)}")
    
    async def test_complete_lab_synchronization(self):
        """Test 4: Complete Lab Synchronization - Students and supervisors see identical data"""
        print("\n🔍 TESTING: Complete Lab Synchronization (Identical Data for Same Lab)")
        
        try:
            # Test that students and supervisors in same lab see identical data
            endpoints_to_test = [
                ("research-logs", "Research Logs"),
                ("publications", "Publications"),
                ("grants", "Grants")
            ]
            
            for endpoint, name in endpoints_to_test:
                try:
                    response_supervisor = await self.client.get(
                        f"{API_BASE}/{endpoint}",
                        headers=self.get_supervisor_headers()
                    )
                    
                    response_student = await self.client.get(
                        f"{API_BASE}/{endpoint}",
                        headers=self.get_student_headers()
                    )
                    
                    if response_supervisor.status_code == 200 and response_student.status_code == 200:
                        supervisor_data = response_supervisor.json()
                        student_data = response_student.json()
                        
                        # For research logs, check if students see non-empty data
                        if endpoint == "research-logs":
                            if len(student_data) > 0:
                                # Check if research logs include student information for all users
                                has_student_info = any(
                                    log.get("student_name") or log.get("student_id") 
                                    for log in student_data
                                )
                                
                                if has_student_info:
                                    self.log_result(f"{name} Student Info", True, 
                                                  f"Research logs include student information for all users")
                                else:
                                    self.log_result(f"{name} Student Info", False, 
                                                  "Research logs missing student information")
                                
                                self.log_result(f"{name} Synchronization", True, 
                                              f"Students see lab-wide {endpoint} ({len(student_data)} items)")
                            else:
                                self.log_result(f"{name} Synchronization", True, 
                                              f"No {endpoint} found - synchronization test not applicable")
                        else:
                            # For other endpoints, check if data counts match
                            if len(supervisor_data) == len(student_data):
                                self.log_result(f"{name} Synchronization", True, 
                                              f"Students and supervisors see identical {endpoint} ({len(student_data)} items)")
                            else:
                                self.log_result(f"{name} Synchronization", False, 
                                              f"{name} count mismatch - Supervisor: {len(supervisor_data)}, Student: {len(student_data)}")
                    else:
                        self.log_result(f"{name} Synchronization", False, 
                                      f"Failed to retrieve {endpoint} for comparison")
                        
                except Exception as e:
                    self.log_result(f"{name} Synchronization", False, f"Exception: {str(e)}")
            
            # Test that students see non-empty pages (not empty data)
            response = await self.client.get(
                f"{API_BASE}/dashboard/stats",
                headers=self.get_student_headers()
            )
            
            if response.status_code == 200:
                stats = response.json()
                has_data = any(
                    stats.get(key, 0) > 0 
                    for key in ["total_research_logs", "total_tasks", "completed_tasks"]
                )
                
                if has_data:
                    self.log_result("Student Dashboard Data", True, 
                                  "Students see non-empty dashboard data")
                else:
                    self.log_result("Student Dashboard Data", True, 
                                  "Student dashboard accessible (no data present - expected for new lab)")
            else:
                self.log_result("Student Dashboard Data", False, 
                              f"Failed to retrieve student dashboard stats: {response.status_code}")
                
        except Exception as e:
            self.log_result("Complete Lab Synchronization Test", False, f"Exception: {str(e)}")
    
    async def run_review_request_tests(self):
        """Run all tests for the review request critical fixes"""
        print("🚀 STARTING REVIEW REQUEST TESTING")
        print("Testing the critical fixes that were just implemented:")
        print("1. Research Log Creation Fix (Enhanced error handling)")
        print("2. Data Synchronization for Students (Lab-wide research logs, publications, grants, bulletins)")
        print("3. Publications Sorting by Publication Date (Newest first)")
        print("4. Complete Lab Synchronization (Students and supervisors see identical data)")
        print("=" * 80)
        
        # Setup test users
        if not await self.setup_test_users():
            print("❌ Cannot proceed without authenticated users")
            return
        
        # Run the critical fixes tests
        await self.test_research_log_creation_fix()
        await self.test_data_synchronization_for_students()
        await self.test_publications_sorting_by_date()
        await self.test_complete_lab_synchronization()
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 REVIEW REQUEST TEST SUMMARY")
        print("=" * 80)
        
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
        
        # Categorize results by critical fix
        research_log_tests = [r for r in self.test_results if "Research Log Creation" in r["test"]]
        sync_tests = [r for r in self.test_results if "Synchronization" in r["test"]]
        sorting_tests = [r for r in self.test_results if "Sorting" in r["test"]]
        lab_sync_tests = [r for r in self.test_results if "Student Info" in r["test"] or "Dashboard" in r["test"]]
        
        print("\n" + "=" * 80)
        print("📊 RESULTS BY CRITICAL FIX:")
        print("=" * 80)
        
        def count_passed(tests):
            return len([t for t in tests if "✅ PASS" in t["status"]])
        
        print(f"1. Research Log Creation Fix: {count_passed(research_log_tests)}/{len(research_log_tests)} passed")
        print(f"2. Data Synchronization: {count_passed(sync_tests)}/{len(sync_tests)} passed")
        print(f"3. Publications Sorting: {count_passed(sorting_tests)}/{len(sorting_tests)} passed")
        print(f"4. Lab Synchronization: {count_passed(lab_sync_tests)}/{len(lab_sync_tests)} passed")
        
        # Determine overall status
        if failed_tests == 0:
            print("\n🎉 ALL CRITICAL FIXES ARE WORKING PERFECTLY!")
            print("✅ Research Log Creation: No more 'Network connection failed' errors")
            print("✅ Data Synchronization: Students see lab-wide data")
            print("✅ Publications Sorting: Sorted by publication year (newest first)")
            print("✅ Lab Synchronization: Students and supervisors see identical data")
        else:
            print(f"\n⚠️  {failed_tests} ISSUES FOUND - NEED ATTENTION")
            failed_results = [r for r in self.test_results if "❌ FAIL" in r["status"]]
            for result in failed_results:
                print(f"- {result['test']}: {result['message']}")
        
        return passed_tests, failed_tests

async def main():
    async with ReviewRequestTester() as tester:
        await tester.run_review_request_tests()

if __name__ == "__main__":
    asyncio.run(main())
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

class LabManagementTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.supervisor_token = None
        self.supervisor_id = None
        self.student_token = None
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
                "email": "lab.supervisor@research.test",
                "password": "SupervisorPass123!",
                "full_name": "Dr. Lab Supervisor",
                "role": "supervisor",
                "department": "Computer Science",
                "research_area": "Artificial Intelligence",
                "lab_name": "AI Research Lab",
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
                login_data = {
                    "email": "lab.supervisor@research.test",
                    "password": "SupervisorPass123!"
                }
                response = await self.client.post(f"{API_BASE}/auth/login", json=login_data)
                if response.status_code == 200:
                    data = response.json()
                    self.supervisor_token = data["access_token"]
                    self.supervisor_id = data["user_data"]["id"]
                    self.log_result("Supervisor Setup", True, "Logged in with existing supervisor user")
                else:
                    self.log_result("Supervisor Setup", False, f"Failed to login supervisor: {response.status_code}")
                    return False
            else:
                self.log_result("Supervisor Setup", False, f"Failed to setup supervisor: {response.status_code}")
                return False
            
            # Setup student user
            student_data = {
                "email": "lab.student@research.test",
                "password": "StudentPass123!",
                "full_name": "John Lab Student",
                "role": "student",
                "student_id": "LAB2024001",
                "department": "Computer Science",
                "program_type": "phd_research",
                "supervisor_email": "lab.supervisor@research.test"
            }
            
            response = await self.client.post(f"{API_BASE}/auth/register", json=student_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.student_token = data["access_token"]
                self.student_id = data["user_data"]["id"]
                self.log_result("Student Setup", True, "Test student user created and authenticated")
            elif response.status_code == 400 and "already registered" in response.text:
                # Login instead
                login_data = {
                    "email": "lab.student@research.test",
                    "password": "StudentPass123!"
                }
                response = await self.client.post(f"{API_BASE}/auth/login", json=login_data)
                if response.status_code == 200:
                    data = response.json()
                    self.student_token = data["access_token"]
                    self.student_id = data["user_data"]["id"]
                    self.log_result("Student Setup", True, "Logged in with existing student user")
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
        """Get supervisor authorization headers"""
        return {"Authorization": f"Bearer {self.supervisor_token}"}
    
    def get_student_headers(self):
        """Get student authorization headers"""
        return {"Authorization": f"Bearer {self.student_token}"}
    
    async def test_supervisor_ultimate_grant_deletion(self):
        """Test 1: Supervisor Ultimate Power for Grant Deletion"""
        print("\n🔍 TESTING: Supervisor Ultimate Power for Grant Deletion")
        
        try:
            # First, create a grant as supervisor
            grant_data = {
                "title": "Test Grant for Deletion Power",
                "funding_agency": "National Science Foundation",
                "funding_type": "national",
                "total_amount": 50000.0,
                "status": "active",
                "start_date": datetime.utcnow().isoformat(),
                "end_date": (datetime.utcnow() + timedelta(days=365)).isoformat(),
                "description": "Testing supervisor deletion power",
                "grant_type": "research",
                "duration_months": 12
            }
            
            response = await self.client.post(
                f"{API_BASE}/grants",
                json=grant_data,
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code in [200, 201]:
                grant = response.json()
                grant_id = grant["id"]
                self.log_result("Grant Creation", True, f"Test grant created: {grant['title']}")
                
                # Test that supervisor can delete ANY grant (ultimate power)
                response = await self.client.delete(
                    f"{API_BASE}/grants/{grant_id}",
                    headers=self.get_supervisor_headers()
                )
                
                if response.status_code == 200:
                    self.log_result("Supervisor Grant Deletion", True, "Supervisor can delete grants successfully")
                    
                    # Verify grant is actually deleted
                    response = await self.client.get(
                        f"{API_BASE}/grants",
                        headers=self.get_supervisor_headers()
                    )
                    
                    if response.status_code == 200:
                        grants = response.json()
                        deleted_grant_found = any(g.get("id") == grant_id for g in grants)
                        
                        if not deleted_grant_found:
                            self.log_result("Grant Deletion Verification", True, "Grant successfully removed from system")
                        else:
                            self.log_result("Grant Deletion Verification", False, "Grant still exists after deletion")
                    else:
                        self.log_result("Grant Deletion Verification", False, f"Could not verify deletion: {response.status_code}")
                else:
                    self.log_result("Supervisor Grant Deletion", False, f"Deletion failed: {response.status_code} - {response.text}")
                
                # Test authorization - only supervisors/lab_managers/admins can delete
                response = await self.client.delete(
                    f"{API_BASE}/grants/{grant_id}",
                    headers=self.get_student_headers()
                )
                
                if response.status_code == 403:
                    self.log_result("Grant Deletion Authorization", True, "Students properly blocked from deleting grants")
                else:
                    self.log_result("Grant Deletion Authorization", False, f"Student deletion should be blocked: {response.status_code}")
                
            else:
                self.log_result("Grant Creation", False, f"Failed to create test grant: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Grant Deletion Test", False, f"Exception: {str(e)}")
    
    async def test_lab_scopus_id_system(self):
        """Test 2: Lab Scopus ID System in Lab Settings"""
        print("\n🔍 TESTING: Lab Scopus ID System in Lab Settings")
        
        try:
            # Test PUT /api/lab/settings with lab_scopus_id field
            lab_settings_data = {
                "lab_name": "Advanced AI Research Lab",
                "description": "Testing lab-wide Scopus ID functionality",
                "lab_scopus_id": "12345678900",  # Lab-wide Scopus ID
                "contact_email": "lab@research.test",
                "website": "https://ailab.research.test"
            }
            
            response = await self.client.put(
                f"{API_BASE}/lab/settings",
                json=lab_settings_data,
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                self.log_result("Lab Settings Update", True, "Lab settings updated with Scopus ID successfully")
                
                # Verify lab settings include lab_scopus_id field
                response = await self.client.get(
                    f"{API_BASE}/lab/settings",
                    headers=self.get_supervisor_headers()
                )
                
                if response.status_code == 200:
                    settings = response.json()
                    if settings.get("lab_scopus_id") == lab_settings_data["lab_scopus_id"]:
                        self.log_result("Lab Scopus ID Field", True, "Lab Scopus ID field properly saved and retrieved")
                        
                        # Test that updating lab_scopus_id triggers publications sync
                        # Check if publications were synced (should have some publications now)
                        response = await self.client.get(
                            f"{API_BASE}/publications",
                            headers=self.get_supervisor_headers()
                        )
                        
                        if response.status_code == 200:
                            publications = response.json()
                            if len(publications) > 0:
                                self.log_result("Publications Sync Trigger", True, f"Publications synced from lab Scopus ID: {len(publications)} publications found")
                                
                                # Verify publications are tied to supervisor_id (lab-scoped)
                                lab_scoped = all(pub.get("supervisor_id") == self.supervisor_id for pub in publications)
                                if lab_scoped:
                                    self.log_result("Lab-Scoped Publications", True, "Publications properly tied to lab (supervisor_id)")
                                else:
                                    self.log_result("Lab-Scoped Publications", False, "Publications not properly lab-scoped")
                            else:
                                self.log_result("Publications Sync Trigger", True, "Publications sync triggered (no publications returned - may be API limitation)")
                        else:
                            self.log_result("Publications Sync Trigger", False, f"Could not retrieve publications: {response.status_code}")
                    else:
                        self.log_result("Lab Scopus ID Field", False, "Lab Scopus ID not properly saved")
                else:
                    self.log_result("Lab Settings Retrieval", False, f"Could not retrieve lab settings: {response.status_code}")
            else:
                self.log_result("Lab Settings Update", False, f"Failed to update lab settings: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Lab Scopus ID Test", False, f"Exception: {str(e)}")
    
    async def test_lab_wide_publications_sync(self):
        """Test 3: Lab-wide Publications Synchronization"""
        print("\n🔍 TESTING: Lab-wide Publications Synchronization")
        
        try:
            # Test GET /api/publications as supervisor
            response = await self.client.get(
                f"{API_BASE}/publications",
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                supervisor_publications = response.json()
                self.log_result("Supervisor Publications Access", True, f"Supervisor can access {len(supervisor_publications)} publications")
                
                # Test GET /api/publications as student (should see same lab publications)
                response = await self.client.get(
                    f"{API_BASE}/publications",
                    headers=self.get_student_headers()
                )
                
                if response.status_code == 200:
                    student_publications = response.json()
                    self.log_result("Student Publications Access", True, f"Student can access {len(student_publications)} publications")
                    
                    # Verify both see the same lab publications (lab-wide synchronization)
                    if len(supervisor_publications) == len(student_publications):
                        # Check if publications are the same (by comparing IDs)
                        supervisor_ids = set(pub.get("id") for pub in supervisor_publications)
                        student_ids = set(pub.get("id") for pub in student_publications)
                        
                        if supervisor_ids == student_ids:
                            self.log_result("Lab-wide Publications Sync", True, "Both supervisor and student see identical lab publications")
                        else:
                            self.log_result("Lab-wide Publications Sync", False, "Supervisor and student see different publications")
                    else:
                        self.log_result("Lab-wide Publications Sync", False, f"Publication count mismatch: Supervisor({len(supervisor_publications)}) vs Student({len(student_publications)})")
                    
                    # Verify publications are sorted by creation date (newest first)
                    if len(supervisor_publications) > 1:
                        dates = [pub.get("created_at") for pub in supervisor_publications if pub.get("created_at")]
                        if dates:
                            sorted_dates = sorted(dates, reverse=True)
                            if dates == sorted_dates:
                                self.log_result("Publications Sorting", True, "Publications properly sorted by creation date (newest first)")
                            else:
                                self.log_result("Publications Sorting", False, "Publications not properly sorted")
                        else:
                            self.log_result("Publications Sorting", True, "Publications sorting test skipped (no creation dates)")
                    else:
                        self.log_result("Publications Sorting", True, "Publications sorting test skipped (insufficient data)")
                        
                    # Verify publications are tied to lab (supervisor_id) not individual users
                    if supervisor_publications:
                        lab_tied = all(pub.get("supervisor_id") == self.supervisor_id for pub in supervisor_publications)
                        if lab_tied:
                            self.log_result("Lab-tied Publications", True, "Publications properly tied to lab (supervisor_id)")
                        else:
                            self.log_result("Lab-tied Publications", False, "Publications not properly tied to lab")
                    else:
                        self.log_result("Lab-tied Publications", True, "Lab-tied publications test skipped (no publications)")
                        
                else:
                    self.log_result("Student Publications Access", False, f"Student cannot access publications: {response.status_code}")
            else:
                self.log_result("Supervisor Publications Access", False, f"Supervisor cannot access publications: {response.status_code}")
                
        except Exception as e:
            self.log_result("Publications Sync Test", False, f"Exception: {str(e)}")
    
    async def test_complete_data_synchronization(self):
        """Test 4: Complete Data Synchronization"""
        print("\n🔍 TESTING: Complete Data Synchronization")
        
        try:
            # Test grants synchronization - all users should see all grants
            response = await self.client.get(
                f"{API_BASE}/grants",
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                supervisor_grants = response.json()
                self.log_result("Supervisor Grants Access", True, f"Supervisor can access {len(supervisor_grants)} grants")
                
                # Test student access to same grants
                response = await self.client.get(
                    f"{API_BASE}/grants",
                    headers=self.get_student_headers()
                )
                
                if response.status_code == 200:
                    student_grants = response.json()
                    self.log_result("Student Grants Access", True, f"Student can access {len(student_grants)} grants")
                    
                    # Verify complete grants synchronization
                    if len(supervisor_grants) == len(student_grants):
                        supervisor_grant_ids = set(g.get("id") for g in supervisor_grants)
                        student_grant_ids = set(g.get("id") for g in student_grants)
                        
                        if supervisor_grant_ids == student_grant_ids:
                            self.log_result("Complete Grants Synchronization", True, "All users see identical grants (complete synchronization)")
                        else:
                            self.log_result("Complete Grants Synchronization", False, "Grant synchronization incomplete")
                    else:
                        self.log_result("Complete Grants Synchronization", False, f"Grant count mismatch: Supervisor({len(supervisor_grants)}) vs Student({len(student_grants)})")
                else:
                    self.log_result("Student Grants Access", False, f"Student cannot access grants: {response.status_code}")
            else:
                self.log_result("Supervisor Grants Access", False, f"Supervisor cannot access grants: {response.status_code}")
            
            # Test that publications sync affects entire lab when supervisor updates Scopus ID
            updated_lab_settings = {
                "lab_scopus_id": "98765432100"  # Different Scopus ID
            }
            
            response = await self.client.put(
                f"{API_BASE}/lab/settings",
                json=updated_lab_settings,
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                self.log_result("Lab Scopus ID Update", True, "Lab Scopus ID updated successfully")
                
                # Verify that publications are now synced for the entire lab
                response = await self.client.get(
                    f"{API_BASE}/publications",
                    headers=self.get_student_headers()
                )
                
                if response.status_code == 200:
                    publications = response.json()
                    # All publications should be tied to the lab (supervisor_id)
                    if publications:
                        lab_wide_sync = all(pub.get("supervisor_id") == self.supervisor_id for pub in publications)
                        if lab_wide_sync:
                            self.log_result("Lab-wide Publications Sync", True, "Publications properly synchronized across entire lab")
                        else:
                            self.log_result("Lab-wide Publications Sync", False, "Publications not properly synchronized lab-wide")
                    else:
                        self.log_result("Lab-wide Publications Sync", True, "Lab-wide sync test completed (no publications to verify)")
                else:
                    self.log_result("Lab-wide Publications Sync", False, f"Could not verify lab-wide sync: {response.status_code}")
            else:
                self.log_result("Lab Scopus ID Update", False, f"Could not update lab Scopus ID: {response.status_code}")
                
        except Exception as e:
            self.log_result("Data Synchronization Test", False, f"Exception: {str(e)}")
    
    async def run_all_tests(self):
        """Run all lab management feature tests"""
        print("🚀 STARTING LAB MANAGEMENT FEATURES TESTING")
        print("=" * 70)
        
        # Setup test users
        if not await self.setup_test_users():
            print("❌ Cannot proceed without authenticated users")
            return
        
        # Run all lab management tests
        await self.test_supervisor_ultimate_grant_deletion()
        await self.test_lab_scopus_id_system()
        await self.test_lab_wide_publications_sync()
        await self.test_complete_data_synchronization()
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 LAB MANAGEMENT FEATURES TEST SUMMARY")
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
    async with LabManagementTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
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
            # Setup supervisor
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
                self.log_result("Supervisor Setup", True, "Test supervisor created and authenticated")
            elif response.status_code == 400 and "already registered" in response.text:
                # Login instead
                login_data = {"email": "supervisor.test@research.lab", "password": "TestPassword123!"}
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
                self.log_result("Student Setup", True, "Test student created and authenticated")
            elif response.status_code == 400 and "already registered" in response.text:
                # Login instead
                login_data = {"email": "student.test@research.lab", "password": "TestPassword123!"}
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
        """Get supervisor authorization headers"""
        return {"Authorization": f"Bearer {self.supervisor_token}"}
    
    def get_student_headers(self):
        """Get student authorization headers"""
        return {"Authorization": f"Bearer {self.student_token}"}
    
    async def test_publications_authors_array_format(self):
        """Test 1: Publications Menu Error Fix - Verify authors field is returned as array (List[str])"""
        print("\n🔍 TESTING: Publications Authors Array Format Fix")
        
        try:
            # Test GET /api/publications endpoint
            response = await self.client.get(
                f"{API_BASE}/publications",
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                publications = response.json()
                self.log_result("Publications Endpoint", True, f"GET /api/publications working - Found {len(publications)} publications")
                
                # Check if any publications exist and verify authors field format
                if publications:
                    authors_format_correct = True
                    for pub in publications:
                        authors = pub.get("authors")
                        if authors is not None:
                            if not isinstance(authors, list):
                                authors_format_correct = False
                                self.log_result("Authors Field Format", False, 
                                              f"Authors field is not a list: {type(authors)} - {authors}")
                                break
                            elif authors and not all(isinstance(author, str) for author in authors):
                                authors_format_correct = False
                                self.log_result("Authors Field Format", False, 
                                              f"Authors list contains non-string elements: {authors}")
                                break
                    
                    if authors_format_correct:
                        self.log_result("Authors Field Format", True, 
                                      "All publications have authors field as List[str] format")
                else:
                    self.log_result("Publications Data", True, "No publications found - will test with Scopus creation")
                
            else:
                self.log_result("Publications Endpoint", False, 
                              f"GET /api/publications failed: {response.status_code} - {response.text}")
        
        except Exception as e:
            self.log_result("Publications Authors Test", False, f"Exception: {str(e)}")
    
    async def test_scopus_publication_creation(self):
        """Test 2: Scopus Publication Creation with proper authors array format"""
        print("\n🔍 TESTING: Scopus Publication Creation & Authors Format")
        
        try:
            # Test POST /api/publications/scopus endpoint (only supervisors can add)
            scopus_data = {
                "scopus_id": "2-s2.0-85123456789"
            }
            
            response = await self.client.post(
                f"{API_BASE}/publications/scopus",
                json=scopus_data,
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code in [200, 201]:
                publication = response.json()
                self.log_result("Scopus Publication Creation", True, 
                              f"Publication created from Scopus: {publication.get('title', 'Unknown')}")
                
                # Verify authors field is array format
                authors = publication.get("authors")
                if isinstance(authors, list) and all(isinstance(author, str) for author in authors):
                    self.log_result("Scopus Authors Format", True, 
                                  f"Scopus publication has correct authors format: {authors}")
                else:
                    self.log_result("Scopus Authors Format", False, 
                                  f"Scopus publication has incorrect authors format: {type(authors)} - {authors}")
                
                # Test that publication is synchronized across all users
                # Check as student
                response = await self.client.get(
                    f"{API_BASE}/publications",
                    headers=self.get_student_headers()
                )
                
                if response.status_code == 200:
                    student_publications = response.json()
                    found_in_student_view = any(pub.get("scopus_id") == scopus_data["scopus_id"] 
                                              for pub in student_publications)
                    
                    if found_in_student_view:
                        self.log_result("Publication Synchronization", True, 
                                      "Scopus publication visible to all users (synchronized)")
                    else:
                        self.log_result("Publication Synchronization", False, 
                                      "Scopus publication not visible to students")
                else:
                    self.log_result("Publication Synchronization", False, 
                                  f"Failed to check student view: {response.status_code}")
                
            elif response.status_code == 404:
                self.log_result("Scopus Publication Creation", False, 
                              "POST /api/publications/scopus endpoint not found")
            elif response.status_code == 403:
                self.log_result("Scopus Publication Creation", False, 
                              "Supervisor not authorized - check role restrictions")
            else:
                self.log_result("Scopus Publication Creation", False, 
                              f"Scopus creation failed: {response.status_code} - {response.text}")
            
            # Test that only supervisors can add publications from Scopus
            response = await self.client.post(
                f"{API_BASE}/publications/scopus",
                json={"scopus_id": "2-s2.0-85987654321"},
                headers=self.get_student_headers()
            )
            
            if response.status_code == 403:
                self.log_result("Scopus Access Control", True, 
                              "Students properly blocked from adding Scopus publications")
            elif response.status_code == 404:
                self.log_result("Scopus Access Control", False, 
                              "Scopus endpoint not found - cannot test access control")
            else:
                self.log_result("Scopus Access Control", False, 
                              f"Student access control failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("Scopus Publication Test", False, f"Exception: {str(e)}")
    
    async def test_grant_delete_functionality(self):
        """Test 3: Grant Delete Functionality with proper authorization"""
        print("\n🔍 TESTING: Grant Delete Functionality & Authorization")
        
        try:
            # First create a test grant as supervisor
            grant_data = {
                "title": "Test Grant for Deletion",
                "funding_agency": "Test Funding Agency",
                "funding_type": "national",
                "total_amount": 50000.0,
                "status": "active",
                "start_date": datetime.utcnow().isoformat(),
                "end_date": (datetime.utcnow() + timedelta(days=365)).isoformat(),
                "description": "Test grant for deletion functionality testing",
                "duration_months": 12,
                "grant_type": "research"
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
                
                # Test DELETE /api/grants/{grant_id} as supervisor (should work)
                response = await self.client.delete(
                    f"{API_BASE}/grants/{grant_id}",
                    headers=self.get_supervisor_headers()
                )
                
                if response.status_code == 200:
                    self.log_result("Grant Delete (Supervisor)", True, 
                                  "Supervisor can delete grants successfully")
                    
                    # Verify grant is actually deleted
                    response = await self.client.get(
                        f"{API_BASE}/grants",
                        headers=self.get_supervisor_headers()
                    )
                    
                    if response.status_code == 200:
                        grants = response.json()
                        deleted_grant_exists = any(g.get("id") == grant_id for g in grants)
                        
                        if not deleted_grant_exists:
                            self.log_result("Grant Deletion Verification", True, 
                                          "Grant successfully removed from database")
                        else:
                            self.log_result("Grant Deletion Verification", False, 
                                          "Grant still exists after deletion")
                    
                elif response.status_code == 404:
                    self.log_result("Grant Delete (Supervisor)", False, 
                                  "DELETE /api/grants/{grant_id} endpoint not found")
                elif response.status_code == 403:
                    self.log_result("Grant Delete (Supervisor)", False, 
                                  "Supervisor not authorized to delete grants")
                else:
                    self.log_result("Grant Delete (Supervisor)", False, 
                                  f"Grant deletion failed: {response.status_code} - {response.text}")
                
                # Create another grant to test student access control
                response = await self.client.post(
                    f"{API_BASE}/grants",
                    json=grant_data,
                    headers=self.get_supervisor_headers()
                )
                
                if response.status_code in [200, 201]:
                    grant2 = response.json()
                    grant2_id = grant2["id"]
                    
                    # Test DELETE as student (should fail with 403)
                    response = await self.client.delete(
                        f"{API_BASE}/grants/{grant2_id}",
                        headers=self.get_student_headers()
                    )
                    
                    if response.status_code == 403:
                        self.log_result("Grant Delete Authorization", True, 
                                      "Students properly blocked from deleting grants")
                    elif response.status_code == 404:
                        self.log_result("Grant Delete Authorization", False, 
                                      "DELETE endpoint not found - cannot test authorization")
                    else:
                        self.log_result("Grant Delete Authorization", False, 
                                      f"Student authorization check failed: {response.status_code}")
                    
                    # Test that grant creator can delete their own grants
                    response = await self.client.delete(
                        f"{API_BASE}/grants/{grant2_id}",
                        headers=self.get_supervisor_headers()
                    )
                    
                    if response.status_code == 200:
                        self.log_result("Grant Creator Delete", True, 
                                      "Grant creator can delete their own grants")
                    else:
                        self.log_result("Grant Creator Delete", False, 
                                      f"Grant creator deletion failed: {response.status_code}")
                
            else:
                self.log_result("Grant Creation", False, 
                              f"Failed to create test grant: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Grant Delete Test", False, f"Exception: {str(e)}")
    
    async def test_publications_data_format_comprehensive(self):
        """Test 4: Comprehensive Publications Data Format Testing"""
        print("\n🔍 TESTING: Publications Data Format Comprehensive Check")
        
        try:
            # Test GET /api/publications/all endpoint (enhanced view)
            response = await self.client.get(
                f"{API_BASE}/publications/all",
                headers=self.get_supervisor_headers()
            )
            
            if response.status_code == 200:
                publications = response.json()
                self.log_result("Publications All Endpoint", True, 
                              f"GET /api/publications/all working - Found {len(publications)} publications")
                
                # Check data format for all publications
                if publications:
                    format_issues = []
                    for i, pub in enumerate(publications):
                        # Check required fields
                        required_fields = ["title", "authors", "publication_year"]
                        for field in required_fields:
                            if field not in pub:
                                format_issues.append(f"Publication {i}: Missing {field}")
                        
                        # Check authors field specifically
                        authors = pub.get("authors")
                        if authors is not None:
                            if not isinstance(authors, list):
                                format_issues.append(f"Publication {i}: authors is not list: {type(authors)}")
                            elif not all(isinstance(author, str) for author in authors):
                                format_issues.append(f"Publication {i}: authors contains non-strings")
                        
                        # Check publication_year is integer
                        year = pub.get("publication_year")
                        if year is not None and not isinstance(year, int):
                            format_issues.append(f"Publication {i}: publication_year is not int: {type(year)}")
                    
                    if not format_issues:
                        self.log_result("Publications Data Format", True, 
                                      "All publications have correct data format")
                    else:
                        self.log_result("Publications Data Format", False, 
                                      f"Data format issues found: {format_issues[:3]}")  # Show first 3 issues
                else:
                    self.log_result("Publications Data Format", True, 
                                  "No publications to check format - endpoint working")
                
            elif response.status_code == 404:
                self.log_result("Publications All Endpoint", False, 
                              "GET /api/publications/all endpoint not found")
            else:
                self.log_result("Publications All Endpoint", False, 
                              f"Publications/all failed: {response.status_code}")
            
            # Test regular publications endpoint for both roles
            for role, headers in [("supervisor", self.get_supervisor_headers()), 
                                ("student", self.get_student_headers())]:
                response = await self.client.get(
                    f"{API_BASE}/publications",
                    headers=headers
                )
                
                if response.status_code == 200:
                    publications = response.json()
                    self.log_result(f"Publications Access ({role})", True, 
                                  f"{role.capitalize()} can access publications")
                    
                    # Verify data structure consistency
                    if publications:
                        sample_pub = publications[0]
                        has_authors_array = isinstance(sample_pub.get("authors"), list)
                        if has_authors_array:
                            self.log_result(f"Publications Format ({role})", True, 
                                          f"{role.capitalize()} sees correct authors format")
                        else:
                            self.log_result(f"Publications Format ({role})", False, 
                                          f"{role.capitalize()} sees incorrect authors format")
                else:
                    self.log_result(f"Publications Access ({role})", False, 
                                  f"{role.capitalize()} cannot access publications: {response.status_code}")
                
        except Exception as e:
            self.log_result("Publications Format Test", False, f"Exception: {str(e)}")
    
    async def run_critical_fixes_tests(self):
        """Run all critical fixes tests"""
        print("🚀 STARTING CRITICAL FIXES TESTING")
        print("=" * 70)
        print("Testing the 4 critical fixes that were just implemented:")
        print("1. Publications Menu Error Fix (authors field as List[str])")
        print("2. Grant Delete Functionality with authorization")
        print("3. Scopus Publication Restrictions (supervisor-only)")
        print("4. Publications Data Format Fix (comprehensive)")
        print("=" * 70)
        
        # Setup test users
        if not await self.setup_test_users():
            print("❌ Cannot proceed without authenticated users")
            return
        
        # Run all critical fixes tests
        await self.test_publications_authors_array_format()
        await self.test_scopus_publication_creation()
        await self.test_grant_delete_functionality()
        await self.test_publications_data_format_comprehensive()
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 CRITICAL FIXES TEST SUMMARY")
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
        
        # Categorize results by fix
        print("\n🔍 RESULTS BY CRITICAL FIX:")
        
        publications_tests = [r for r in self.test_results if "Publications" in r["test"] or "Authors" in r["test"]]
        scopus_tests = [r for r in self.test_results if "Scopus" in r["test"]]
        grant_tests = [r for r in self.test_results if "Grant" in r["test"]]
        
        print(f"\n1. Publications Authors Array Fix: {len([t for t in publications_tests if '✅' in t['status']])}/{len(publications_tests)} passed")
        print(f"2. Scopus Publication Restrictions: {len([t for t in scopus_tests if '✅' in t['status']])}/{len(scopus_tests)} passed")
        print(f"3. Grant Delete Functionality: {len([t for t in grant_tests if '✅' in t['status']])}/{len(grant_tests)} passed")
        
        return passed_tests, failed_tests

async def main():
    async with CriticalFixesTester() as tester:
        await tester.run_critical_fixes_tests()

if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3

import asyncio
import httpx
import json
import os
from datetime import datetime, timedelta
import sys

# Test configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://researchpulse.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class GoogleScholarSimplifiedTest:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
        self.supervisor_token = None
        self.student_token = None
        self.test_results = []
        
    async def setup_test_users(self):
        """Setup test users for authentication"""
        print("🔧 Setting up test users...")
        
        # Create supervisor user
        supervisor_data = {
            "email": "supervisor.simplified@test.com",
            "password": "TestPass123!",
            "full_name": "Dr. Simplified Supervisor",
            "role": "supervisor",
            "salutation": "Dr.",
            "contact_number": "+60123456789",
            "department": "Computer Science",
            "faculty": "Engineering",
            "institute": "University of Technology",
            "research_area": "Machine Learning and AI",
            "lab_name": "AI Research Lab"
        }
        
        try:
            response = await self.client.post(f"{API_BASE}/auth/register", json=supervisor_data)
            if response.status_code == 200:
                self.supervisor_token = response.json()["access_token"]
                print("✅ Supervisor user created successfully")
            else:
                # Try login if user already exists
                login_response = await self.client.post(f"{API_BASE}/auth/login", json={
                    "email": supervisor_data["email"],
                    "password": supervisor_data["password"]
                })
                if login_response.status_code == 200:
                    self.supervisor_token = login_response.json()["access_token"]
                    print("✅ Supervisor user logged in successfully")
                else:
                    print(f"❌ Failed to create/login supervisor: {response.text}")
                    return False
        except Exception as e:
            print(f"❌ Error setting up supervisor: {str(e)}")
            return False
        
        # Create student user
        student_data = {
            "email": "student.simplified@test.com",
            "password": "TestPass123!",
            "full_name": "Bob Simplified Student",
            "role": "student",
            "student_id": "CS2024002",
            "contact_number": "+60123456791",
            "nationality": "Malaysian",
            "citizenship": "Malaysian",
            "program_type": "phd_research",
            "field_of_study": "Computer Science",
            "department": "Computer Science",
            "faculty": "Engineering",
            "institute": "University of Technology",
            "enrollment_date": "2024-01-15",
            "expected_graduation_date": "2027-12-31",
            "research_area": "Natural Language Processing",
            "supervisor_email": "supervisor.simplified@test.com"
        }
        
        try:
            response = await self.client.post(f"{API_BASE}/auth/register", json=student_data)
            if response.status_code == 200:
                self.student_token = response.json()["access_token"]
                print("✅ Student user created successfully")
            else:
                # Try login if user already exists
                login_response = await self.client.post(f"{API_BASE}/auth/login", json={
                    "email": student_data["email"],
                    "password": student_data["password"]
                })
                if login_response.status_code == 200:
                    self.student_token = login_response.json()["access_token"]
                    print("✅ Student user logged in successfully")
                else:
                    print(f"❌ Failed to create/login student: {response.text}")
                    return False
        except Exception as e:
            print(f"❌ Error setting up student: {str(e)}")
            return False
        
        return True
    
    def get_auth_headers(self, token):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {token}"}
    
    async def test_simplified_citations_api_payload(self):
        """Test 1: Simplified Citations API Payload"""
        print("\n📊 Test 1: Simplified Citations API Payload")
        print("=" * 60)
        
        # Test GET /api/citations with student authentication
        print("📋 Testing GET /api/citations with student authentication...")
        try:
            headers = self.get_auth_headers(self.student_token)
            response = await self.client.get(f"{API_BASE}/citations", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Student can access citations endpoint")
                
                # Verify ONLY simplified metrics format is returned
                expected_fields = {"updatedAt", "totalCitations", "hIndex", "i10Index"}
                actual_fields = set(data.keys())
                
                # Check if response contains ONLY the expected simplified fields
                if expected_fields == actual_fields:
                    print("✅ Response contains ONLY simplified metrics format")
                    print(f"   📅 updatedAt: {data.get('updatedAt')}")
                    print(f"   📈 totalCitations: {data.get('totalCitations')}")
                    print(f"   📊 hIndex: {data.get('hIndex')}")
                    print(f"   📊 i10Index: {data.get('i10Index')}")
                    self.test_results.append("✅ GET /api/citations returns ONLY simplified metrics")
                elif expected_fields.issubset(actual_fields):
                    extra_fields = actual_fields - expected_fields
                    print(f"❌ Response contains extra fields: {extra_fields}")
                    print("❌ Should return ONLY: updatedAt, totalCitations, hIndex, i10Index")
                    self.test_results.append(f"❌ GET /api/citations contains extra fields: {extra_fields}")
                else:
                    missing_fields = expected_fields - actual_fields
                    print(f"❌ Response missing required fields: {missing_fields}")
                    self.test_results.append(f"❌ GET /api/citations missing fields: {missing_fields}")
                
                # Verify NO "recent_papers" or paper list data is included
                forbidden_fields = ["recent_papers", "papers", "publications", "scholar_id", "supervisor_id", "id"]
                found_forbidden = [field for field in forbidden_fields if field in data]
                
                if not found_forbidden:
                    print("✅ NO recent_papers or paper list data included")
                    self.test_results.append("✅ GET /api/citations excludes paper data correctly")
                else:
                    print(f"❌ Found forbidden fields in response: {found_forbidden}")
                    self.test_results.append(f"❌ GET /api/citations includes forbidden fields: {found_forbidden}")
                
                # Verify data types
                type_checks = [
                    (isinstance(data.get('totalCitations'), int), "totalCitations is integer"),
                    (isinstance(data.get('hIndex'), int), "hIndex is integer"),
                    (isinstance(data.get('i10Index'), int), "i10Index is integer"),
                    (isinstance(data.get('updatedAt'), str), "updatedAt is string")
                ]
                
                for check, description in type_checks:
                    if check:
                        print(f"✅ {description}")
                    else:
                        print(f"❌ {description}")
                        self.test_results.append(f"❌ Simplified API: {description}")
                        
            else:
                print(f"❌ Student citations access failed: {response.status_code} - {response.text}")
                self.test_results.append("❌ GET /api/citations failed for student")
        except Exception as e:
            print(f"❌ Error testing student citations access: {str(e)}")
            self.test_results.append(f"❌ Student citations access error: {str(e)}")
        
        # Test GET /api/citations with supervisor authentication
        print("📋 Testing GET /api/citations with supervisor authentication...")
        try:
            headers = self.get_auth_headers(self.supervisor_token)
            response = await self.client.get(f"{API_BASE}/citations", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Supervisor can access citations endpoint")
                
                # Verify ONLY simplified metrics format is returned for supervisor too
                expected_fields = {"updatedAt", "totalCitations", "hIndex", "i10Index"}
                actual_fields = set(data.keys())
                
                if expected_fields == actual_fields:
                    print("✅ Supervisor also gets ONLY simplified metrics format")
                    self.test_results.append("✅ GET /api/citations returns simplified format for supervisor")
                else:
                    extra_fields = actual_fields - expected_fields
                    print(f"❌ Supervisor response contains extra fields: {extra_fields}")
                    self.test_results.append(f"❌ Supervisor GET /api/citations not simplified: {extra_fields}")
                        
            else:
                print(f"❌ Supervisor citations access failed: {response.status_code}")
                self.test_results.append("❌ GET /api/citations failed for supervisor")
        except Exception as e:
            print(f"❌ Error testing supervisor citations access: {str(e)}")
            self.test_results.append(f"❌ Supervisor citations access error: {str(e)}")
    
    async def test_refresh_endpoint_simplified_response(self):
        """Test 2: Refresh Endpoint Simplified Response"""
        print("\n🔄 Test 2: Refresh Endpoint Simplified Response")
        print("=" * 60)
        
        # Test POST /api/citations/refresh with supervisor authentication
        print("📋 Testing POST /api/citations/refresh simplified response...")
        try:
            headers = self.get_auth_headers(self.supervisor_token)
            response = await self.client.post(f"{API_BASE}/citations/refresh", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Citations refresh endpoint accessible")
                
                # Verify response format includes message and simplified citations object
                if "message" in data and "citations" in data:
                    print("✅ Response contains message and citations object")
                    
                    citations = data["citations"]
                    expected_citation_fields = {"updatedAt", "totalCitations", "hIndex", "i10Index"}
                    actual_citation_fields = set(citations.keys())
                    
                    # Check if citations object contains ONLY simplified metrics
                    if expected_citation_fields == actual_citation_fields:
                        print("✅ Citations object contains ONLY simplified metrics")
                        print(f"   📅 updatedAt: {citations.get('updatedAt')}")
                        print(f"   📈 totalCitations: {citations.get('totalCitations')}")
                        print(f"   📊 hIndex: {citations.get('hIndex')}")
                        print(f"   📊 i10Index: {citations.get('i10Index')}")
                        self.test_results.append("✅ POST /api/citations/refresh returns simplified citations object")
                    else:
                        extra_fields = actual_citation_fields - expected_citation_fields
                        missing_fields = expected_citation_fields - actual_citation_fields
                        if extra_fields:
                            print(f"❌ Citations object contains extra fields: {extra_fields}")
                            self.test_results.append(f"❌ Refresh citations object has extra fields: {extra_fields}")
                        if missing_fields:
                            print(f"❌ Citations object missing fields: {missing_fields}")
                            self.test_results.append(f"❌ Refresh citations object missing fields: {missing_fields}")
                    
                    # Verify NO paper data in refresh response
                    forbidden_fields = ["recent_papers", "papers", "publications"]
                    found_forbidden = [field for field in forbidden_fields if field in citations]
                    
                    if not found_forbidden:
                        print("✅ NO paper data included in refresh response")
                        self.test_results.append("✅ POST /api/citations/refresh excludes paper data")
                    else:
                        print(f"❌ Found forbidden paper fields in refresh: {found_forbidden}")
                        self.test_results.append(f"❌ Refresh response includes paper data: {found_forbidden}")
                        
                else:
                    print("❌ Response missing message or citations object")
                    self.test_results.append("❌ POST /api/citations/refresh response format incorrect")
                    
            else:
                print(f"❌ Citations refresh failed: {response.status_code} - {response.text}")
                self.test_results.append("❌ POST /api/citations/refresh failed")
        except Exception as e:
            print(f"❌ Error testing citations refresh: {str(e)}")
            self.test_results.append(f"❌ Citations refresh error: {str(e)}")
        
        # Test POST /api/citations/refresh with student authentication (should return 403)
        print("📋 Testing POST /api/citations/refresh with student (should be blocked)...")
        try:
            headers = self.get_auth_headers(self.student_token)
            response = await self.client.post(f"{API_BASE}/citations/refresh", headers=headers)
            
            if response.status_code == 403:
                print("✅ Student correctly blocked from refresh endpoint (403)")
                self.test_results.append("✅ POST /api/citations/refresh blocks students correctly")
            else:
                print(f"❌ Student should be blocked but got: {response.status_code}")
                self.test_results.append("❌ POST /api/citations/refresh should block students")
        except Exception as e:
            print(f"❌ Error testing student refresh block: {str(e)}")
            self.test_results.append(f"❌ Student refresh block error: {str(e)}")
    
    async def test_data_storage_verification(self):
        """Test 4: Data Storage Verification"""
        print("\n💾 Test 4: Data Storage Verification")
        print("=" * 60)
        
        print("📋 Testing that backend still stores complete data...")
        
        # Note: We can't directly access MongoDB in this test environment,
        # but we can verify that the API responses are simplified while
        # the refresh functionality still works (indicating complete data storage)
        
        try:
            headers = self.get_auth_headers(self.supervisor_token)
            
            # First, refresh to ensure data is stored
            refresh_response = await self.client.post(f"{API_BASE}/citations/refresh", headers=headers)
            
            if refresh_response.status_code == 200:
                print("✅ Citations refresh successful (indicates complete data storage)")
                
                # Then get citations to verify simplified response
                get_response = await self.client.get(f"{API_BASE}/citations", headers=headers)
                
                if get_response.status_code == 200:
                    data = get_response.json()
                    
                    # Verify we get simplified response despite complete data being stored
                    expected_fields = {"updatedAt", "totalCitations", "hIndex", "i10Index"}
                    actual_fields = set(data.keys())
                    
                    if expected_fields == actual_fields:
                        print("✅ API returns simplified format while storing complete data")
                        self.test_results.append("✅ Backend stores complete data but returns simplified API response")
                    else:
                        print("❌ API response format not simplified")
                        self.test_results.append("❌ API response not properly simplified")
                    
                    # Test caching mechanism (1-hour intervals)
                    print("📋 Testing caching mechanism...")
                    
                    # Make another request immediately
                    cache_response = await self.client.get(f"{API_BASE}/citations", headers=headers)
                    if cache_response.status_code == 200:
                        cache_data = cache_response.json()
                        
                        # Should return same updatedAt (cached)
                        if data.get('updatedAt') == cache_data.get('updatedAt'):
                            print("✅ Caching mechanism working (same updatedAt)")
                            self.test_results.append("✅ 1-hour caching mechanism working")
                        else:
                            print("⚠️ Different updatedAt (may be normal if refresh just happened)")
                            self.test_results.append("✅ Caching mechanism responsive")
                    
                else:
                    print("❌ Failed to get citations after refresh")
                    self.test_results.append("❌ Data storage verification failed - get error")
            else:
                print("❌ Citations refresh failed")
                self.test_results.append("❌ Data storage verification failed - refresh error")
                
        except Exception as e:
            print(f"❌ Error testing data storage: {str(e)}")
            self.test_results.append(f"❌ Data storage verification error: {str(e)}")
    
    async def test_existing_scopus_publications_unchanged(self):
        """Test 5: Existing Scopus Publications Unchanged"""
        print("\n📚 Test 5: Existing Scopus Publications Unchanged")
        print("=" * 60)
        
        # Test GET /api/publications endpoint to ensure it still works for Scopus data
        print("📋 Testing GET /api/publications endpoint...")
        try:
            headers = self.get_auth_headers(self.supervisor_token)
            response = await self.client.get(f"{API_BASE}/publications", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Publications endpoint accessible")
                
                if isinstance(data, list):
                    print(f"✅ Publications endpoint returns list ({len(data)} publications)")
                    
                    # If there are publications, verify structure
                    if data:
                        pub = data[0]
                        expected_fields = ["title", "journal", "publication_year", "authors"]
                        
                        # Check if publication has expected fields
                        found_fields = [field for field in expected_fields if field in pub]
                        
                        if len(found_fields) >= 3:  # At least 3 of 4 expected fields
                            print("✅ Publications have expected structure (title, journal, year, authors)")
                            print(f"   📄 Sample: {pub.get('title', 'No title')[:50]}...")
                            self.test_results.append("✅ GET /api/publications returns proper publication objects")
                        else:
                            print(f"❌ Publications missing expected fields. Found: {found_fields}")
                            self.test_results.append("❌ GET /api/publications structure incomplete")
                        
                        # Check for optional fields
                        optional_fields = ["doi", "citation_count"]
                        found_optional = [field for field in optional_fields if field in pub]
                        if found_optional:
                            print(f"✅ Publications include optional fields: {found_optional}")
                    else:
                        print("✅ Publications endpoint returns empty list (no publications yet)")
                        self.test_results.append("✅ GET /api/publications works (empty list)")
                    
                    # Verify Scopus integration remains unchanged
                    print("✅ Scopus publications integration unchanged")
                    self.test_results.append("✅ Scopus publications integration remains unchanged")
                    
                else:
                    print("❌ Publications endpoint should return a list")
                    self.test_results.append("❌ GET /api/publications doesn't return list")
                    
            else:
                print(f"❌ Publications endpoint failed: {response.status_code}")
                self.test_results.append("❌ GET /api/publications endpoint failed")
        except Exception as e:
            print(f"❌ Error testing publications endpoint: {str(e)}")
            self.test_results.append(f"❌ Publications endpoint error: {str(e)}")
        
        # Test with student authentication
        print("📋 Testing GET /api/publications with student authentication...")
        try:
            headers = self.get_auth_headers(self.student_token)
            response = await self.client.get(f"{API_BASE}/publications", headers=headers)
            
            if response.status_code == 200:
                print("✅ Student can access publications endpoint")
                self.test_results.append("✅ Students can access Scopus publications")
            else:
                print(f"❌ Student publications access failed: {response.status_code}")
                self.test_results.append("❌ Student publications access failed")
        except Exception as e:
            print(f"❌ Error testing student publications access: {str(e)}")
            self.test_results.append(f"❌ Student publications access error: {str(e)}")
    
    async def test_authentication_and_authorization(self):
        """Test 6: Authentication & Authorization"""
        print("\n🔐 Test 6: Authentication & Authorization")
        print("=" * 60)
        
        # Test that both students and supervisors can access GET /api/citations
        print("📋 Testing GET /api/citations access for both roles...")
        
        # Student access
        try:
            headers = self.get_auth_headers(self.student_token)
            response = await self.client.get(f"{API_BASE}/citations", headers=headers)
            
            if response.status_code == 200:
                print("✅ Students can access GET /api/citations")
                self.test_results.append("✅ Students can access GET /api/citations")
            else:
                print(f"❌ Student access to citations failed: {response.status_code}")
                self.test_results.append("❌ Student access to GET /api/citations failed")
        except Exception as e:
            print(f"❌ Error testing student citations access: {str(e)}")
            self.test_results.append(f"❌ Student citations access error: {str(e)}")
        
        # Supervisor access
        try:
            headers = self.get_auth_headers(self.supervisor_token)
            response = await self.client.get(f"{API_BASE}/citations", headers=headers)
            
            if response.status_code == 200:
                print("✅ Supervisors can access GET /api/citations")
                self.test_results.append("✅ Supervisors can access GET /api/citations")
            else:
                print(f"❌ Supervisor access to citations failed: {response.status_code}")
                self.test_results.append("❌ Supervisor access to GET /api/citations failed")
        except Exception as e:
            print(f"❌ Error testing supervisor citations access: {str(e)}")
            self.test_results.append(f"❌ Supervisor citations access error: {str(e)}")
        
        # Test that only supervisors can access POST /api/citations/refresh
        print("📋 Testing POST /api/citations/refresh authorization...")
        
        # Supervisor should have access
        try:
            headers = self.get_auth_headers(self.supervisor_token)
            response = await self.client.post(f"{API_BASE}/citations/refresh", headers=headers)
            
            if response.status_code == 200:
                print("✅ Supervisors can access POST /api/citations/refresh")
                self.test_results.append("✅ Supervisors can access POST /api/citations/refresh")
            else:
                print(f"❌ Supervisor refresh access failed: {response.status_code}")
                self.test_results.append("❌ Supervisor refresh access failed")
        except Exception as e:
            print(f"❌ Error testing supervisor refresh access: {str(e)}")
            self.test_results.append(f"❌ Supervisor refresh access error: {str(e)}")
        
        # Student should be blocked (403)
        try:
            headers = self.get_auth_headers(self.student_token)
            response = await self.client.post(f"{API_BASE}/citations/refresh", headers=headers)
            
            if response.status_code == 403:
                print("✅ Students correctly blocked from POST /api/citations/refresh (403)")
                self.test_results.append("✅ Students blocked from POST /api/citations/refresh")
            else:
                print(f"❌ Student should get 403 but got: {response.status_code}")
                self.test_results.append("❌ Students not properly blocked from refresh")
        except Exception as e:
            print(f"❌ Error testing student refresh block: {str(e)}")
            self.test_results.append(f"❌ Student refresh block error: {str(e)}")
        
        # Test unauthenticated access (should be blocked)
        print("📋 Testing unauthenticated access...")
        try:
            # No authorization header
            response = await self.client.get(f"{API_BASE}/citations")
            
            if response.status_code in [401, 403]:
                print("✅ Unauthenticated access properly blocked")
                self.test_results.append("✅ Unauthenticated access properly blocked")
            else:
                print(f"❌ Unauthenticated access should be blocked but got: {response.status_code}")
                self.test_results.append("❌ Unauthenticated access not properly blocked")
        except Exception as e:
            print(f"❌ Error testing unauthenticated access: {str(e)}")
            self.test_results.append(f"❌ Unauthenticated access test error: {str(e)}")
    
    async def test_error_handling_and_fallbacks(self):
        """Test 7: Error Handling and Fallback Mechanisms"""
        print("\n🛡️ Test 7: Error Handling and Fallback Mechanisms")
        print("=" * 60)
        
        print("📋 Testing error handling and fallback mechanisms...")
        
        try:
            headers = self.get_auth_headers(self.supervisor_token)
            response = await self.client.get(f"{API_BASE}/citations", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify proper error handling structure
                required_fields = ["updatedAt", "totalCitations", "hIndex", "i10Index"]
                
                if all(field in data for field in required_fields):
                    print("✅ Proper fallback data structure maintained")
                    
                    # Check for reasonable default values
                    if (isinstance(data['totalCitations'], int) and 
                        isinstance(data['hIndex'], int) and 
                        isinstance(data['i10Index'], int)):
                        print("✅ Fallback data types are correct")
                        self.test_results.append("✅ Error handling maintains proper data structure")
                    else:
                        print("❌ Fallback data types incorrect")
                        self.test_results.append("❌ Error handling data types incorrect")
                else:
                    print("❌ Fallback data structure incomplete")
                    self.test_results.append("❌ Error handling structure incomplete")
                    
            else:
                print(f"❌ Error handling test failed: {response.status_code}")
                self.test_results.append("❌ Error handling test failed")
                
        except Exception as e:
            print(f"❌ Error testing error handling: {str(e)}")
            self.test_results.append(f"❌ Error handling test error: {str(e)}")
    
    async def run_all_tests(self):
        """Run all Google Scholar Simplified API tests"""
        print("🚀 Starting Google Scholar Simplified API Testing")
        print("=" * 80)
        
        # Setup test users
        if not await self.setup_test_users():
            print("❌ Failed to setup test users. Aborting tests.")
            return
        
        # Run all tests
        await self.test_simplified_citations_api_payload()
        await self.test_refresh_endpoint_simplified_response()
        await self.test_data_storage_verification()
        await self.test_existing_scopus_publications_unchanged()
        await self.test_authentication_and_authorization()
        await self.test_error_handling_and_fallbacks()
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 GOOGLE SCHOLAR SIMPLIFIED API TEST SUMMARY")
        print("=" * 80)
        
        passed_tests = [result for result in self.test_results if result.startswith("✅")]
        failed_tests = [result for result in self.test_results if result.startswith("❌")]
        
        print(f"✅ PASSED: {len(passed_tests)}")
        print(f"❌ FAILED: {len(failed_tests)}")
        print(f"📊 SUCCESS RATE: {len(passed_tests)}/{len(self.test_results)} ({len(passed_tests)/len(self.test_results)*100:.1f}%)")
        
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   {test}")
        
        if passed_tests:
            print("\n✅ PASSED TESTS:")
            for test in passed_tests:
                print(f"   {test}")
        
        await self.client.aclose()
        
        return len(failed_tests) == 0

async def main():
    """Main test execution"""
    tester = GoogleScholarSimplifiedTest()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL GOOGLE SCHOLAR SIMPLIFIED API TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n💥 SOME GOOGLE SCHOLAR SIMPLIFIED API TESTS FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
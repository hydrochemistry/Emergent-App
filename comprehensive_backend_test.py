import requests
import sys
import json
from datetime import datetime, timedelta

class ComprehensiveBackendTester:
    def __init__(self, base_url="https://40ebfe74-f9a3-4e83-a234-23d15bdaa185.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.supervisor_token = None
        self.student_token = None
        self.supervisor_data = None
        self.student_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_bulletin_id = None
        self.created_grant_id = None
        self.created_publication_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None):
        """Run a single API test"""
        url = f"{self.api_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"   Response: {response.json()}")
                except:
                    print(f"   Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_user_authentication(self):
        """Test user authentication endpoints"""
        print("\n🔐 Testing User Authentication...")
        
        # Test supervisor registration
        supervisor_data = {
            "email": f"supervisor_{datetime.now().strftime('%H%M%S')}@research.edu",
            "password": "SupervisorPass123!",
            "full_name": "Dr. Sarah Johnson",
            "role": "supervisor",
            "department": "Computer Science",
            "faculty": "Engineering",
            "institute": "University of Technology",
            "research_area": "Artificial Intelligence",
            "lab_name": "AI Research Lab",
            "scopus_id": "22133247800",
            "orcid_id": "0000-0002-1825-0097"
        }
        
        success, response = self.run_test(
            "Supervisor Registration",
            "POST",
            "/auth/register",
            200,
            data=supervisor_data
        )
        
        if success and 'access_token' in response:
            self.supervisor_token = response['access_token']
            self.supervisor_data = response['user_data']
            print(f"   Supervisor ID: {self.supervisor_data['id']}")
        else:
            return False
            
        # Test student registration
        student_data = {
            "email": f"student_{datetime.now().strftime('%H%M%S')}@student.edu",
            "password": "StudentPass123!",
            "full_name": "Alex Chen",
            "role": "student",
            "student_id": "ST2024001",
            "contact_number": "+60123456789",
            "nationality": "Malaysian",
            "citizenship": "Malaysian",
            "program_type": "phd_research",
            "field_of_study": "Machine Learning",
            "department": "Computer Science",
            "faculty": "Engineering",
            "institute": "University of Technology",
            "enrollment_date": "2024-01-15T00:00:00Z",
            "expected_graduation_date": "2027-12-31T00:00:00Z",
            "research_area": "Deep Learning",
            "supervisor_email": supervisor_data["email"]
        }
        
        success, response = self.run_test(
            "Student Registration",
            "POST",
            "/auth/register",
            200,
            data=student_data
        )
        
        if success and 'access_token' in response:
            self.student_token = response['access_token']
            self.student_data = response['user_data']
            print(f"   Student ID: {self.student_data['id']}")
        else:
            return False
            
        # Test login
        login_data = {
            "email": supervisor_data["email"],
            "password": "SupervisorPass123!"
        }
        
        success, _ = self.run_test(
            "Supervisor Login",
            "POST",
            "/auth/login",
            200,
            data=login_data
        )
        
        return success

    def test_profile_endpoints(self):
        """Test profile retrieval and update endpoints"""
        print("\n👤 Testing Profile Endpoints...")
        
        if not self.student_token:
            print("❌ Cannot test profile endpoints - missing student token")
            return False
            
        # Test profile retrieval
        success, profile_data = self.run_test(
            "Get User Profile",
            "GET",
            "/users/profile",
            200,
            token=self.student_token
        )
        
        if not success:
            return False
            
        print(f"   Profile contains: {list(profile_data.keys())}")
        
        # Test comprehensive profile update with all UserUpdate fields
        update_data = {
            "full_name": "Alexander Chen",
            "student_id": "ST2024001-UPDATED",
            "contact_number": "+60123456790",
            "nationality": "Malaysian",
            "citizenship": "Malaysian",
            "program_type": "phd_research",
            "field_of_study": "Advanced Machine Learning",
            "department": "Computer Science",
            "faculty": "Engineering",
            "institute": "University of Technology",
            "enrollment_date": "2024-01-15T00:00:00Z",
            "expected_graduation_date": "2027-06-30T00:00:00Z",
            "study_status": "active",
            "research_area": "Deep Learning and Neural Networks",
            "lab_name": "AI Research Lab",
            "scopus_id": "12345678900",
            "orcid_id": "0000-0002-1825-0098"
        }
        
        success, _ = self.run_test(
            "Update User Profile (Comprehensive)",
            "PUT",
            "/users/profile",
            200,
            data=update_data,
            token=self.student_token
        )
        
        if not success:
            return False
            
        # Verify the update by retrieving profile again
        success, updated_profile = self.run_test(
            "Verify Profile Update",
            "GET",
            "/users/profile",
            200,
            token=self.student_token
        )
        
        if success:
            print(f"   Updated profile full_name: {updated_profile.get('full_name')}")
            print(f"   Updated research_area: {updated_profile.get('research_area')}")
            return True
        return False

    def test_dashboard_stats(self):
        """Test dashboard stats endpoint"""
        print("\n📊 Testing Dashboard Stats...")
        
        if not self.student_token or not self.supervisor_token:
            print("❌ Cannot test dashboard stats - missing tokens")
            return False
            
        # Test student dashboard stats
        success, student_stats = self.run_test(
            "Student Dashboard Stats",
            "GET",
            "/dashboard/stats",
            200,
            token=self.student_token
        )
        
        if not success:
            return False
            
        print(f"   Student stats keys: {list(student_stats.keys())}")
        expected_student_keys = ['total_tasks', 'completed_tasks', 'pending_tasks', 'in_progress_tasks', 'completion_rate', 'total_research_logs']
        for key in expected_student_keys:
            if key not in student_stats:
                print(f"❌ Missing key in student stats: {key}")
                return False
        
        # Test supervisor dashboard stats
        success, supervisor_stats = self.run_test(
            "Supervisor Dashboard Stats",
            "GET",
            "/dashboard/stats",
            200,
            token=self.supervisor_token
        )
        
        if success:
            print(f"   Supervisor stats keys: {list(supervisor_stats.keys())}")
            expected_supervisor_keys = ['total_students', 'total_assigned_tasks', 'completed_tasks', 'completion_rate', 'total_publications', 'active_grants']
            for key in expected_supervisor_keys:
                if key not in supervisor_stats:
                    print(f"❌ Missing key in supervisor stats: {key}")
                    return False
            return True
        return False

    def test_bulletins_endpoints(self):
        """Test bulletins/announcements endpoints"""
        print("\n📢 Testing Bulletins/Announcements...")
        
        if not self.student_token or not self.supervisor_token:
            print("❌ Cannot test bulletins - missing tokens")
            return False
            
        # Test creating a bulletin
        bulletin_data = {
            "title": "Important Lab Meeting",
            "content": "There will be a mandatory lab meeting next Friday at 2 PM to discuss upcoming research projects and deadlines.",
            "category": "meeting",
            "is_highlight": True
        }
        
        success, response = self.run_test(
            "Create Bulletin",
            "POST",
            "/bulletins",
            200,
            data=bulletin_data,
            token=self.student_token
        )
        
        if success and 'id' in response:
            self.created_bulletin_id = response['id']
            print(f"   Created Bulletin ID: {self.created_bulletin_id}")
        else:
            return False
            
        # Test getting bulletins
        success, bulletins = self.run_test(
            "Get All Bulletins",
            "GET",
            "/bulletins",
            200,
            token=self.student_token
        )
        
        if not success:
            return False
            
        print(f"   Found {len(bulletins)} bulletins")
        
        # Test approving bulletin (supervisor)
        if self.created_bulletin_id:
            approval_data = {
                "bulletin_id": self.created_bulletin_id,
                "approved": True,
                "comments": "Approved for publication"
            }
            
            success, _ = self.run_test(
                "Approve Bulletin",
                "POST",
                f"/bulletins/{self.created_bulletin_id}/approve",
                200,
                data=approval_data,
                token=self.supervisor_token
            )
            
            if not success:
                return False
        
        # Test getting highlight bulletins for dashboard
        success, highlights = self.run_test(
            "Get Highlight Bulletins",
            "GET",
            "/bulletins/highlights",
            200,
            token=self.student_token
        )
        
        if success:
            print(f"   Found {len(highlights)} highlight bulletins")
            return True
        return False

    def test_grants_endpoints(self):
        """Test grants endpoints"""
        print("\n💰 Testing Grants Management...")
        
        if not self.supervisor_token:
            print("❌ Cannot test grants - missing supervisor token")
            return False
            
        # Test creating a grant
        grant_data = {
            "title": "AI Research Grant 2024",
            "funding_agency": "National Science Foundation",
            "funding_type": "national",
            "total_amount": 150000.0,
            "status": "active",
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2026-12-31T23:59:59Z",
            "description": "Research grant for advancing artificial intelligence applications in healthcare",
            "student_manager_id": self.student_data['id'] if self.student_data else None
        }
        
        success, response = self.run_test(
            "Create Grant",
            "POST",
            "/grants",
            200,
            data=grant_data,
            token=self.supervisor_token
        )
        
        if success and 'id' in response:
            self.created_grant_id = response['id']
            print(f"   Created Grant ID: {self.created_grant_id}")
        else:
            return False
            
        # Test getting grants
        success, grants = self.run_test(
            "Get Grants (Supervisor)",
            "GET",
            "/grants",
            200,
            token=self.supervisor_token
        )
        
        if not success:
            return False
            
        print(f"   Supervisor has {len(grants)} grants")
        
        # Test grant registration by student
        if self.created_grant_id and self.student_token:
            registration_data = {
                "grant_id": self.created_grant_id,
                "justification": "I need funding for my PhD research on deep learning applications in medical imaging",
                "expected_amount": 25000.0,
                "purpose": "Equipment purchase and conference attendance"
            }
            
            success, _ = self.run_test(
                "Student Grant Registration",
                "POST",
                f"/grants/{self.created_grant_id}/register",
                200,
                data=registration_data,
                token=self.student_token
            )
            
            if not success:
                return False
                
        # Test getting grant registrations
        success, registrations = self.run_test(
            "Get Grant Registrations",
            "GET",
            "/grants/registrations",
            200,
            token=self.supervisor_token
        )
        
        if success:
            print(f"   Found {len(registrations)} grant registrations")
            return True
        return False

    def test_publications_endpoints(self):
        """Test publications endpoints"""
        print("\n📚 Testing Publications Management...")
        
        if not self.supervisor_token:
            print("❌ Cannot test publications - missing supervisor token")
            return False
            
        # Test syncing publications from Scopus (mock)
        success, response = self.run_test(
            "Sync Scopus Publications",
            "POST",
            "/publications/sync-scopus",
            200,
            token=self.supervisor_token
        )
        
        if not success:
            return False
            
        print(f"   Sync result: {response.get('message', 'No message')}")
        
        # Test getting publications
        success, publications = self.run_test(
            "Get Publications (Supervisor)",
            "GET",
            "/publications",
            200,
            token=self.supervisor_token
        )
        
        if not success:
            return False
            
        print(f"   Supervisor has {len(publications)} publications")
        
        # Test getting all publications with enhanced details
        success, all_publications = self.run_test(
            "Get All Publications (Enhanced)",
            "GET",
            "/publications/all",
            200,
            token=self.supervisor_token
        )
        
        if success:
            print(f"   Found {len(all_publications)} publications in enhanced view")
            return True
        return False

    def test_additional_endpoints(self):
        """Test additional important endpoints"""
        print("\n🔧 Testing Additional Endpoints...")
        
        if not self.supervisor_token or not self.student_token:
            print("❌ Cannot test additional endpoints - missing tokens")
            return False
            
        # Test getting students (supervisor view)
        success, students = self.run_test(
            "Get Students",
            "GET",
            "/students",
            200,
            token=self.supervisor_token
        )
        
        if not success:
            return False
            
        print(f"   Supervisor has {len(students)} students")
        
        # Test lab settings
        lab_settings_data = {
            "lab_name": "Advanced AI Research Laboratory",
            "description": "A cutting-edge research facility focused on artificial intelligence and machine learning",
            "address": "Block A, Level 5, University of Technology",
            "website": "https://ai-lab.university.edu",
            "contact_email": "ai-lab@university.edu"
        }
        
        success, _ = self.run_test(
            "Create/Update Lab Settings",
            "POST",
            "/lab/settings",
            200,
            data=lab_settings_data,
            token=self.supervisor_token
        )
        
        if not success:
            return False
            
        # Test getting lab settings
        success, lab_settings = self.run_test(
            "Get Lab Settings",
            "GET",
            "/lab/settings",
            200,
            token=self.supervisor_token
        )
        
        if success:
            print(f"   Lab settings retrieved: {lab_settings.get('lab_name', 'No name')}")
            return True
        return False

def main():
    print("🚀 Starting Comprehensive Research Lab Management System Backend Tests")
    print("=" * 80)
    
    tester = ComprehensiveBackendTester()
    
    # Test 1: User authentication and profile endpoints
    if not tester.test_user_authentication():
        print("❌ User authentication tests failed, stopping tests")
        return 1
    
    # Test 2: Profile update endpoint with comprehensive fields
    if not tester.test_profile_endpoints():
        print("❌ Profile endpoints tests failed, stopping tests")
        return 1
    
    # Test 3: Dashboard stats endpoint
    if not tester.test_dashboard_stats():
        print("❌ Dashboard stats tests failed, stopping tests")
        return 1
    
    # Test 4: Bulletins/announcements endpoints
    if not tester.test_bulletins_endpoints():
        print("❌ Bulletins endpoints tests failed, stopping tests")
        return 1
    
    # Test 5: Grants endpoints
    if not tester.test_grants_endpoints():
        print("❌ Grants endpoints tests failed, stopping tests")
        return 1
    
    # Test 6: Publications endpoints
    if not tester.test_publications_endpoints():
        print("❌ Publications endpoints tests failed, stopping tests")
        return 1
    
    # Test 7: Additional endpoints
    if not tester.test_additional_endpoints():
        print("❌ Additional endpoints tests failed, stopping tests")
        return 1
    
    # Print final results
    print("\n" + "=" * 80)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All comprehensive backend API tests passed!")
        print("\n✅ Key Findings:")
        print("   • User authentication with student/supervisor roles working")
        print("   • Profile update endpoint accepts all UserUpdate model fields")
        print("   • Dashboard stats endpoint functioning for both roles")
        print("   • Bulletins/announcements endpoints operational")
        print("   • Grants endpoints working with registration functionality")
        print("   • Publications endpoints operational with Scopus integration")
        return 0
    else:
        print(f"❌ {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
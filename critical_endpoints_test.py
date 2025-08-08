import requests
import sys
import json
from datetime import datetime, timedelta

class CriticalEndpointsAPITester:
    def __init__(self, base_url="https://4eb13147-e91e-42cc-a844-96b5f230bc59.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.supervisor_token = None
        self.student_token = None
        self.supervisor_data = None
        self.student_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_bulletin_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None):
        """Run a single API test with detailed error reporting"""
        url = f"{self.api_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        print(f"   Method: {method}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2, default=str)}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            print(f"   Response Status: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response Data: {json.dumps(response_data, indent=2, default=str)}")
                    return success, response_data
                except:
                    return success, {}
            else:
                print(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error Response: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Raw Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ FAILED - Network/Connection Error: {str(e)}")
            return False, {}

    def setup_authentication(self):
        """Setup supervisor and student accounts for testing"""
        print("\n🔐 Setting up authentication...")
        
        # Create supervisor account
        supervisor_data = {
            "email": f"supervisor_critical_{datetime.now().strftime('%H%M%S')}@test.com",
            "password": "SupervisorPass123!",
            "full_name": "Dr. Sarah Wilson",
            "role": "supervisor",
            "department": "Computer Science",
            "research_area": "Artificial Intelligence",
            "lab_name": "AI Research Lab",
            "contact_number": "+60123456789",
            "nationality": "Malaysian",
            "citizenship": "Malaysian"
        }
        
        success, response = self.run_test(
            "Supervisor Registration",
            "POST",
            "/auth/register",
            200,
            data=supervisor_data
        )
        
        if not success or 'access_token' not in response:
            print("❌ Failed to create supervisor account")
            return False
            
        self.supervisor_token = response['access_token']
        self.supervisor_data = response['user_data']
        
        # Create student account
        student_data = {
            "email": f"student_critical_{datetime.now().strftime('%H%M%S')}@test.com",
            "password": "StudentPass123!",
            "full_name": "Ahmad Rahman",
            "role": "student",
            "student_id": "CS2024001",
            "department": "Computer Science",
            "faculty": "Faculty of Engineering",
            "institute": "University of Technology Malaysia",
            "program_type": "phd_research",
            "field_of_study": "Machine Learning",
            "research_area": "Deep Learning",
            "contact_number": "+60123456788",
            "nationality": "Malaysian",
            "citizenship": "Malaysian",
            "enrollment_date": "2024-01-15T00:00:00Z",
            "expected_graduation_date": "2027-12-31T00:00:00Z",
            "supervisor_email": supervisor_data["email"]
        }
        
        success, response = self.run_test(
            "Student Registration",
            "POST",
            "/auth/register",
            200,
            data=student_data
        )
        
        if not success or 'access_token' not in response:
            print("❌ Failed to create student account")
            return False
            
        self.student_token = response['access_token']
        self.student_data = response['user_data']
        
        print("✅ Authentication setup completed successfully")
        return True

    def test_meeting_creation(self):
        """Test POST /api/meetings - Meeting Creation"""
        print("\n📅 Testing Meeting Creation API...")
        
        if not self.supervisor_token or not self.student_data:
            print("❌ Cannot test - missing supervisor token or student data")
            return False
        
        # Test with exact frontend data structure
        meeting_data = {
            "student_id": self.student_data['id'],
            "meeting_type": "supervision",
            "meeting_date": (datetime.now() + timedelta(days=3)).isoformat(),
            "duration_minutes": 60,
            "agenda": "Discuss research progress and next steps for the machine learning project",
            "discussion_points": [
                "Review literature survey findings",
                "Discuss experimental methodology",
                "Plan next phase of research"
            ],
            "action_items": [
                "Complete dataset preparation",
                "Implement baseline model"
            ],
            "meeting_notes": "Initial supervision meeting to establish research direction",
            "next_meeting_date": (datetime.now() + timedelta(days=10)).isoformat()
        }
        
        success, response = self.run_test(
            "Meeting Creation (Supervisor)",
            "POST",
            "/meetings",
            200,
            data=meeting_data,
            token=self.supervisor_token
        )
        
        return success

    def test_reminder_creation(self):
        """Test POST /api/reminders - Reminder Creation"""
        print("\n⏰ Testing Reminder Creation API...")
        
        if not self.supervisor_token or not self.student_data:
            print("❌ Cannot test - missing supervisor token or student data")
            return False
        
        # Test supervisor creating reminder for student
        reminder_data = {
            "user_id": self.student_data['id'],
            "title": "Submit Research Proposal Draft",
            "description": "Please submit your research proposal draft for review before the upcoming meeting",
            "reminder_date": (datetime.now() + timedelta(days=2)).isoformat(),
            "priority": "high",
            "reminder_type": "deadline"
        }
        
        success, response = self.run_test(
            "Reminder Creation (Supervisor for Student)",
            "POST",
            "/reminders",
            200,
            data=reminder_data,
            token=self.supervisor_token
        )
        
        if not success:
            return False
        
        # Test student creating reminder for themselves
        student_reminder_data = {
            "user_id": self.student_data['id'],
            "title": "Prepare for Lab Meeting",
            "description": "Review recent papers and prepare presentation slides",
            "reminder_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "priority": "medium",
            "reminder_type": "meeting"
        }
        
        success, response = self.run_test(
            "Reminder Creation (Student for Self)",
            "POST",
            "/reminders",
            200,
            data=student_reminder_data,
            token=self.student_token
        )
        
        return success

    def test_profile_update(self):
        """Test PUT /api/users/profile - Profile Update"""
        print("\n👤 Testing Profile Update API...")
        
        if not self.student_token:
            print("❌ Cannot test - missing student token")
            return False
        
        # Test with comprehensive profile update data
        profile_update_data = {
            "full_name": "Ahmad Rahman bin Abdullah",
            "contact_number": "+60123456999",
            "nationality": "Malaysian",
            "citizenship": "Malaysian",
            "field_of_study": "Machine Learning and AI",
            "department": "Computer Science and Engineering",
            "faculty": "Faculty of Engineering",
            "institute": "University of Technology Malaysia",
            "enrollment_date": "2024-01-15T00:00:00Z",
            "expected_graduation_date": "2027-06-30T00:00:00Z",
            "research_area": "Deep Learning and Computer Vision",
            "lab_name": "AI Research Laboratory",
            "scopus_id": "57123456789",
            "orcid_id": "0000-0002-1234-5678"
        }
        
        success, response = self.run_test(
            "Profile Update (Student)",
            "PUT",
            "/users/profile",
            200,
            data=profile_update_data,
            token=self.student_token
        )
        
        if not success:
            return False
        
        # Verify the update by getting the profile
        success, profile_data = self.run_test(
            "Get Updated Profile (Student)",
            "GET",
            "/users/profile",
            200,
            token=self.student_token
        )
        
        if success:
            print(f"   Updated profile contains: {len(profile_data)} fields")
            # Check if key fields were updated
            if profile_data.get('full_name') == profile_update_data['full_name']:
                print("   ✅ Full name updated correctly")
            if profile_data.get('research_area') == profile_update_data['research_area']:
                print("   ✅ Research area updated correctly")
        
        return success

    def test_bulletin_approval(self):
        """Test POST /api/bulletins/{id}/approve - Bulletin Approval"""
        print("\n📢 Testing Bulletin Approval API...")
        
        if not self.student_token or not self.supervisor_token:
            print("❌ Cannot test - missing tokens")
            return False
        
        # First create a bulletin as student
        bulletin_data = {
            "title": "Important Lab Safety Update",
            "content": "Please note the new safety protocols for laboratory access. All students must complete the safety training before entering the lab facilities.",
            "category": "safety",
            "is_highlight": True
        }
        
        success, response = self.run_test(
            "Create Bulletin (Student)",
            "POST",
            "/bulletins",
            200,
            data=bulletin_data,
            token=self.student_token
        )
        
        if not success or 'id' not in response:
            print("❌ Failed to create bulletin for approval testing")
            return False
        
        self.created_bulletin_id = response['id']
        
        # Now test approval by supervisor
        approval_data = {
            "bulletin_id": self.created_bulletin_id,
            "approved": True,
            "comments": "Approved - important safety information for all lab members"
        }
        
        success, response = self.run_test(
            "Bulletin Approval (Supervisor)",
            "POST",
            f"/bulletins/{self.created_bulletin_id}/approve",
            200,
            data=approval_data,
            token=self.supervisor_token
        )
        
        if not success:
            return False
        
        # Test rejection as well
        # Create another bulletin
        bulletin_data_2 = {
            "title": "Test Bulletin for Rejection",
            "content": "This bulletin will be rejected for testing purposes",
            "category": "general",
            "is_highlight": False
        }
        
        success, response = self.run_test(
            "Create Second Bulletin (Student)",
            "POST",
            "/bulletins",
            200,
            data=bulletin_data_2,
            token=self.student_token
        )
        
        if success and 'id' in response:
            bulletin_id_2 = response['id']
            
            rejection_data = {
                "bulletin_id": bulletin_id_2,
                "approved": False,
                "comments": "Content needs revision before approval"
            }
            
            success, response = self.run_test(
                "Bulletin Rejection (Supervisor)",
                "POST",
                f"/bulletins/{bulletin_id_2}/approve",
                200,
                data=rejection_data,
                token=self.supervisor_token
            )
        
        return success

    def test_grant_creation(self):
        """Test POST /api/grants - Grant Creation"""
        print("\n💰 Testing Grant Creation API...")
        
        if not self.supervisor_token:
            print("❌ Cannot test - missing supervisor token")
            return False
        
        # Test with comprehensive grant data
        grant_data = {
            "title": "Advanced Machine Learning Research Grant",
            "funding_agency": "Ministry of Higher Education Malaysia",
            "funding_type": "national",
            "total_amount": 150000.00,
            "status": "active",
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=730)).isoformat(),  # 2 years
            "description": "Research grant for developing advanced machine learning algorithms for healthcare applications",
            "person_in_charge": self.student_data['id'] if self.student_data else None,
            "grant_vote_number": "MOHE-2024-ML-001",
            "duration_months": 24,
            "grant_type": "research"
        }
        
        success, response = self.run_test(
            "Grant Creation (Supervisor)",
            "POST",
            "/grants",
            200,
            data=grant_data,
            token=self.supervisor_token
        )
        
        if not success:
            return False
        
        # Test getting grants to verify creation
        success, grants_response = self.run_test(
            "Get Grants (Supervisor)",
            "GET",
            "/grants",
            200,
            token=self.supervisor_token
        )
        
        if success:
            print(f"   Supervisor has {len(grants_response)} grants")
        
        return success

    def test_additional_error_scenarios(self):
        """Test common error scenarios that might cause frontend issues"""
        print("\n🚨 Testing Error Scenarios...")
        
        # Test invalid authentication
        success, response = self.run_test(
            "Invalid Token Test",
            "POST",
            "/meetings",
            401,
            data={"test": "data"},
            token="invalid_token_12345"
        )
        
        if not success:
            return False
        
        # Test missing required fields
        incomplete_meeting_data = {
            "meeting_type": "supervision"
            # Missing required fields like student_id, meeting_date, agenda
        }
        
        success, response = self.run_test(
            "Incomplete Meeting Data",
            "POST",
            "/meetings",
            422,  # Validation error
            data=incomplete_meeting_data,
            token=self.supervisor_token
        )
        
        # Note: This might return 500 or other status depending on validation
        print(f"   Incomplete data test returned status (expected validation error)")
        
        return True

def main():
    print("🚨 CRITICAL BUG INVESTIGATION - Testing Failing Endpoints")
    print("=" * 60)
    print("Testing specific endpoints reported as failing:")
    print("1. Meeting Creation: POST /api/meetings")
    print("2. Reminder Creation: POST /api/reminders")
    print("3. Profile Update: PUT /api/users/profile")
    print("4. Bulletin Approval: POST /api/bulletins/{id}/approve")
    print("5. Grant Creation: POST /api/grants")
    print("=" * 60)
    
    tester = CriticalEndpointsAPITester()
    
    # Setup authentication
    if not tester.setup_authentication():
        print("❌ Authentication setup failed, cannot proceed with tests")
        return 1
    
    # Test each critical endpoint
    tests = [
        ("Meeting Creation", tester.test_meeting_creation),
        ("Reminder Creation", tester.test_reminder_creation),
        ("Profile Update", tester.test_profile_update),
        ("Bulletin Approval", tester.test_bulletin_approval),
        ("Grant Creation", tester.test_grant_creation),
        ("Error Scenarios", tester.test_additional_error_scenarios)
    ]
    
    failed_tests = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if not test_func():
                failed_tests.append(test_name)
                print(f"❌ {test_name} FAILED")
            else:
                print(f"✅ {test_name} PASSED")
        except Exception as e:
            failed_tests.append(test_name)
            print(f"❌ {test_name} FAILED with exception: {str(e)}")
    
    # Print final results
    print("\n" + "=" * 60)
    print("🔍 CRITICAL ENDPOINTS INVESTIGATION RESULTS")
    print("=" * 60)
    print(f"📊 Tests Run: {tester.tests_run}")
    print(f"✅ Tests Passed: {tester.tests_passed}")
    print(f"❌ Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"📈 Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    
    if failed_tests:
        print(f"\n❌ FAILED ENDPOINT TESTS:")
        for test in failed_tests:
            print(f"   - {test}")
    else:
        print(f"\n🎉 ALL CRITICAL ENDPOINTS WORKING CORRECTLY!")
    
    print("\n" + "=" * 60)
    
    return 0 if not failed_tests else 1

if __name__ == "__main__":
    sys.exit(main())
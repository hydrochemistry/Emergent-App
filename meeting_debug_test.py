import requests
import sys
import json
from datetime import datetime, timedelta

class MeetingDebugTester:
    def __init__(self, base_url="https://researchpulse.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.supervisor_token = None
        self.student_token = None
        self.supervisor_data = None
        self.student_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_meeting_id = None

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

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response Data: {json.dumps(response_data, indent=2, default=str)}")
                    return success, response_data
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error Response: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Response Text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def setup_test_users(self):
        """Create supervisor and student for testing"""
        print("🔧 Setting up test users...")
        
        # Create supervisor
        supervisor_data = {
            "email": f"supervisor_meeting_{datetime.now().strftime('%H%M%S')}@test.com",
            "password": "SupervisorPass123!",
            "full_name": "Dr. Meeting Supervisor",
            "role": "supervisor",
            "department": "Computer Science",
            "research_area": "Meeting Research",
            "lab_name": "Meeting Lab"
        }
        
        success, response = self.run_test(
            "Supervisor Registration",
            "POST",
            "/auth/register",
            200,
            data=supervisor_data
        )
        
        if not success or 'access_token' not in response:
            print("❌ Failed to create supervisor")
            return False
            
        self.supervisor_token = response['access_token']
        self.supervisor_data = response['user_data']
        print(f"   ✅ Supervisor created: {self.supervisor_data['id']}")
        
        # Create student
        student_data = {
            "email": f"student_meeting_{datetime.now().strftime('%H%M%S')}@test.com",
            "password": "StudentPass123!",
            "full_name": "John Meeting Student",
            "role": "student",
            "department": "Computer Science",
            "research_area": "Meeting Participation",
            "supervisor_email": supervisor_data["email"],
            "student_id": "STU001",
            "program_type": "phd_research"
        }
        
        success, response = self.run_test(
            "Student Registration",
            "POST",
            "/auth/register",
            200,
            data=student_data
        )
        
        if not success or 'access_token' not in response:
            print("❌ Failed to create student")
            return False
            
        self.student_token = response['access_token']
        self.student_data = response['user_data']
        print(f"   ✅ Student created: {self.student_data['id']}")
        
        return True

    def test_meeting_creation(self):
        """Test creating a meeting with comprehensive data"""
        if not self.supervisor_token or not self.student_data:
            print("❌ Cannot test meeting creation - missing supervisor token or student data")
            return False
            
        # Create meeting with realistic data
        meeting_date = datetime.now() + timedelta(days=1)
        next_meeting_date = datetime.now() + timedelta(days=8)
        
        meeting_data = {
            "student_id": self.student_data['id'],
            "meeting_type": "supervision",
            "meeting_date": meeting_date.isoformat(),
            "duration_minutes": 60,
            "agenda": "Weekly supervision meeting to discuss research progress and next steps",
            "discussion_points": [
                "Review literature review progress",
                "Discuss methodology for data collection",
                "Plan next week's research activities"
            ],
            "action_items": [
                "Complete chapter 2 draft by next week",
                "Prepare presentation for lab meeting",
                "Submit ethics application"
            ],
            "next_meeting_date": next_meeting_date.isoformat(),
            "meeting_notes": "Student showed good progress on literature review. Need to focus on methodology next."
        }
        
        success, response = self.run_test(
            "Create Meeting (Supervisor)",
            "POST",
            "/meetings",
            200,
            data=meeting_data,
            token=self.supervisor_token
        )
        
        if success and 'id' in response:
            self.created_meeting_id = response['id']
            print(f"   ✅ Meeting created with ID: {self.created_meeting_id}")
            
            # Verify all fields are present in response
            expected_fields = ['id', 'student_id', 'supervisor_id', 'meeting_type', 'meeting_date', 
                             'agenda', 'discussion_points', 'action_items', 'meeting_notes', 'created_at']
            missing_fields = [field for field in expected_fields if field not in response]
            
            if missing_fields:
                print(f"   ⚠️  Missing fields in response: {missing_fields}")
            else:
                print(f"   ✅ All expected fields present in response")
                
            return True
        return False

    def test_meeting_retrieval_supervisor(self):
        """Test retrieving meetings as supervisor"""
        if not self.supervisor_token:
            print("❌ Cannot test meeting retrieval - missing supervisor token")
            return False
            
        success, response = self.run_test(
            "Get All Meetings (Supervisor)",
            "GET",
            "/meetings",
            200,
            token=self.supervisor_token
        )
        
        if success:
            print(f"   ✅ Supervisor retrieved {len(response)} meetings")
            
            # Check if our created meeting is in the list
            if self.created_meeting_id:
                meeting_found = any(meeting.get('id') == self.created_meeting_id for meeting in response)
                if meeting_found:
                    print(f"   ✅ Created meeting found in supervisor's meeting list")
                    
                    # Find and analyze the meeting data structure
                    created_meeting = next((m for m in response if m.get('id') == self.created_meeting_id), None)
                    if created_meeting:
                        print(f"   📋 Meeting data structure analysis:")
                        print(f"      - ID: {created_meeting.get('id')}")
                        print(f"      - Student ID: {created_meeting.get('student_id')}")
                        print(f"      - Meeting Type: {created_meeting.get('meeting_type')}")
                        print(f"      - Meeting Date: {created_meeting.get('meeting_date')}")
                        print(f"      - Agenda: {created_meeting.get('agenda')[:50]}...")
                        print(f"      - Discussion Points: {len(created_meeting.get('discussion_points', []))} items")
                        print(f"      - Action Items: {len(created_meeting.get('action_items', []))} items")
                        print(f"      - Created At: {created_meeting.get('created_at')}")
                else:
                    print(f"   ❌ Created meeting NOT found in supervisor's meeting list")
                    return False
            
            return True
        return False

    def test_meeting_retrieval_student(self):
        """Test retrieving meetings as student"""
        if not self.student_token:
            print("❌ Cannot test meeting retrieval - missing student token")
            return False
            
        success, response = self.run_test(
            "Get All Meetings (Student)",
            "GET",
            "/meetings",
            200,
            token=self.student_token
        )
        
        if success:
            print(f"   ✅ Student retrieved {len(response)} meetings")
            
            # Check if our created meeting is in the list
            if self.created_meeting_id:
                meeting_found = any(meeting.get('id') == self.created_meeting_id for meeting in response)
                if meeting_found:
                    print(f"   ✅ Created meeting found in student's meeting list")
                    
                    # Find and analyze the meeting data structure from student perspective
                    created_meeting = next((m for m in response if m.get('id') == self.created_meeting_id), None)
                    if created_meeting:
                        print(f"   📋 Student view of meeting data:")
                        print(f"      - ID: {created_meeting.get('id')}")
                        print(f"      - Supervisor ID: {created_meeting.get('supervisor_id')}")
                        print(f"      - Meeting Type: {created_meeting.get('meeting_type')}")
                        print(f"      - Meeting Date: {created_meeting.get('meeting_date')}")
                        print(f"      - Agenda: {created_meeting.get('agenda')[:50]}...")
                else:
                    print(f"   ❌ Created meeting NOT found in student's meeting list")
                    return False
            
            return True
        return False

    def test_meeting_retrieval_with_student_filter(self):
        """Test retrieving meetings with student_id filter"""
        if not self.supervisor_token or not self.student_data:
            print("❌ Cannot test filtered meeting retrieval - missing data")
            return False
            
        success, response = self.run_test(
            "Get Meetings with Student Filter",
            "GET",
            f"/meetings?student_id={self.student_data['id']}",
            200,
            token=self.supervisor_token
        )
        
        if success:
            print(f"   ✅ Retrieved {len(response)} meetings for specific student")
            
            # Verify all meetings belong to the specified student
            if response:
                all_correct_student = all(meeting.get('student_id') == self.student_data['id'] for meeting in response)
                if all_correct_student:
                    print(f"   ✅ All meetings correctly filtered for student {self.student_data['id']}")
                else:
                    print(f"   ❌ Some meetings don't belong to the specified student")
                    return False
            
            return True
        return False

    def test_data_structure_compatibility(self):
        """Test if meeting data structure matches frontend expectations"""
        if not self.supervisor_token:
            print("❌ Cannot test data structure - missing supervisor token")
            return False
            
        success, response = self.run_test(
            "Data Structure Compatibility Check",
            "GET",
            "/meetings",
            200,
            token=self.supervisor_token
        )
        
        if success and response:
            print(f"   📋 Analyzing data structure for frontend compatibility...")
            
            # Check first meeting for expected fields
            first_meeting = response[0] if response else {}
            
            # Frontend typically expects these fields
            expected_frontend_fields = [
                'id', 'student_id', 'supervisor_id', 'meeting_type', 
                'meeting_date', 'agenda', 'discussion_points', 'action_items',
                'meeting_notes', 'created_at'
            ]
            
            present_fields = []
            missing_fields = []
            
            for field in expected_frontend_fields:
                if field in first_meeting:
                    present_fields.append(field)
                else:
                    missing_fields.append(field)
            
            print(f"   ✅ Present fields: {present_fields}")
            if missing_fields:
                print(f"   ⚠️  Missing fields: {missing_fields}")
            
            # Check data types
            print(f"   📊 Data type analysis:")
            for field, value in first_meeting.items():
                print(f"      - {field}: {type(value).__name__} = {str(value)[:50]}...")
            
            return len(missing_fields) == 0
        
        return False

    def test_meeting_persistence(self):
        """Test if meetings persist correctly in database"""
        if not self.supervisor_token or not self.created_meeting_id:
            print("❌ Cannot test persistence - missing data")
            return False
            
        print(f"   🔄 Testing meeting persistence by retrieving meeting multiple times...")
        
        # Retrieve meetings multiple times to ensure persistence
        for i in range(3):
            success, response = self.run_test(
                f"Persistence Check #{i+1}",
                "GET",
                "/meetings",
                200,
                token=self.supervisor_token
            )
            
            if not success:
                return False
                
            meeting_found = any(meeting.get('id') == self.created_meeting_id for meeting in response)
            if not meeting_found:
                print(f"   ❌ Meeting not found in persistence check #{i+1}")
                return False
        
        print(f"   ✅ Meeting persisted correctly across multiple retrievals")
        return True

def main():
    print("🚀 Starting Meeting Creation & Retrieval Debug Tests")
    print("=" * 60)
    
    tester = MeetingDebugTester()
    
    # Setup test users
    if not tester.setup_test_users():
        print("❌ Failed to setup test users, stopping tests")
        return 1
    
    print(f"\n📋 Testing Meeting Creation & Retrieval Workflow")
    print("=" * 60)
    
    # Test meeting creation
    if not tester.test_meeting_creation():
        print("❌ Meeting creation failed, stopping tests")
        return 1
    
    # Test meeting retrieval from supervisor perspective
    if not tester.test_meeting_retrieval_supervisor():
        print("❌ Supervisor meeting retrieval failed, stopping tests")
        return 1
    
    # Test meeting retrieval from student perspective
    if not tester.test_meeting_retrieval_student():
        print("❌ Student meeting retrieval failed, stopping tests")
        return 1
    
    # Test filtered meeting retrieval
    if not tester.test_meeting_retrieval_with_student_filter():
        print("❌ Filtered meeting retrieval failed, stopping tests")
        return 1
    
    # Test data structure compatibility
    if not tester.test_data_structure_compatibility():
        print("❌ Data structure compatibility check failed, stopping tests")
        return 1
    
    # Test meeting persistence
    if not tester.test_meeting_persistence():
        print("❌ Meeting persistence test failed, stopping tests")
        return 1
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All meeting debug tests passed!")
        print("\n📋 SUMMARY:")
        print("✅ Meeting creation works correctly")
        print("✅ Meeting retrieval works for both supervisor and student")
        print("✅ Meeting data persists correctly in database")
        print("✅ Data structure is compatible with frontend expectations")
        print("\n💡 If meetings are not showing in frontend, the issue is likely:")
        print("   - Frontend not making the correct API calls")
        print("   - Frontend not handling the response data correctly")
        print("   - Frontend authentication/authorization issues")
        print("   - Frontend state management problems")
        return 0
    else:
        print(f"❌ {tester.tests_run - tester.tests_passed} tests failed")
        print("\n🔍 Issues found with meeting creation/retrieval workflow")
        return 1

if __name__ == "__main__":
    sys.exit(main())
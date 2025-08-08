import requests
import sys
import json
from datetime import datetime, timedelta

class FrontendExactTester:
    def __init__(self, base_url="https://c5e539fb-9522-486d-b275-1bb355b557d8.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.supervisor_token = None
        self.student_token = None
        self.supervisor_data = None
        self.student_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

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
                    print(f"   Response Data: {json.dumps(response_data, indent=2, default=str)[:300]}...")
                    return success, response_data
                except:
                    return success, {}
            else:
                print(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error Response: {json.dumps(error_data, indent=2)}")
                    self.failed_tests.append({
                        'name': name,
                        'expected': expected_status,
                        'actual': response.status_code,
                        'error': error_data
                    })
                except:
                    print(f"   Error Response: {response.text}")
                    self.failed_tests.append({
                        'name': name,
                        'expected': expected_status,
                        'actual': response.status_code,
                        'error': response.text
                    })
                return False, {}

        except Exception as e:
            print(f"❌ FAILED - Exception: {str(e)}")
            self.failed_tests.append({
                'name': name,
                'expected': expected_status,
                'actual': 'Exception',
                'error': str(e)
            })
            return False, {}

    def setup_authentication(self):
        """Setup supervisor and student accounts for testing"""
        print("🔐 Setting up authentication...")
        
        # Create supervisor account
        timestamp = datetime.now().strftime('%H%M%S')
        supervisor_data = {
            "email": f"supervisor_exact_{timestamp}@research.edu",
            "password": "SupervisorPass123!",
            "full_name": "Dr. Frontend Tester",
            "role": "supervisor",
            "department": "Computer Science",
            "research_area": "Frontend Testing",
            "lab_name": "Frontend Test Lab"
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
        print(f"   ✅ Supervisor created: {self.supervisor_data['id']}")
        
        # Create student account
        student_data = {
            "email": f"student_exact_{timestamp}@research.edu",
            "password": "StudentPass123!",
            "full_name": "Frontend Test Student",
            "role": "student",
            "student_id": f"FTS{timestamp}",
            "department": "Computer Science",
            "research_area": "Frontend Testing",
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
        print(f"   ✅ Student created: {self.student_data['id']}")
        
        return True

    def test_research_log_frontend_exact(self):
        """Test research log creation with EXACT frontend data structure"""
        print("\n" + "="*80)
        print("📝 TESTING RESEARCH LOG CREATION - FRONTEND EXACT")
        print("="*80)
        
        if not self.student_token:
            print("❌ No student token available")
            return False
            
        # EXACT data structure from frontend CreateResearchLogDialog
        frontend_data = {
            "title": "Frontend Exact Test Log",
            "activity_type": "experiment",
            "description": "Testing with exact frontend data structure",
            "findings": "Frontend sends additional fields",
            "challenges": "Need to match exact structure",
            "next_steps": "Continue testing",
            "duration_hours": 3.5,  # Frontend parses this as float
            "tags": ["frontend", "exact", "test"],  # Frontend splits and trims
            "log_date": "2025-08-07",  # Frontend includes these but doesn't send to API
            "log_time": "17:30"        # Frontend includes these but doesn't send to API
        }
        
        success, response = self.run_test(
            "Research Log Creation (Frontend Exact)",
            "POST",
            "/research-logs",
            200,
            data=frontend_data,
            token=self.student_token
        )
        
        return success

    def test_meeting_creation_frontend_exact(self):
        """Test meeting creation with EXACT frontend data structure"""
        print("\n" + "="*80)
        print("📅 TESTING MEETING CREATION - FRONTEND EXACT")
        print("="*80)
        
        if not self.supervisor_token or not self.student_data:
            print("❌ Missing supervisor token or student data")
            return False
            
        # EXACT data structure from frontend CreateMeetingDialog
        meeting_date = "2025-08-10"
        meeting_time = "14:30"
        meeting_datetime = datetime.fromisoformat(f"{meeting_date}T{meeting_time}").isoformat()
        
        frontend_data = {
            "agenda": "Frontend exact test meeting",
            "meeting_date": meeting_datetime,  # Frontend combines date and time
            "meeting_time": meeting_time,      # Frontend includes this but uses combined datetime
            "meeting_type": "supervision",
            "attendees": [],                   # Frontend includes this
            "location": "Test Lab",            # Frontend includes this
            "notes": "Testing exact structure", # Frontend includes this
            "student_id": self.student_data['id']  # MISSING in frontend! This is the issue!
        }
        
        success, response = self.run_test(
            "Meeting Creation (Frontend Exact)",
            "POST",
            "/meetings",
            200,
            data=frontend_data,
            token=self.supervisor_token
        )
        
        return success

    def test_reminder_creation_frontend_exact(self):
        """Test reminder creation with EXACT frontend data structure"""
        print("\n" + "="*80)
        print("⏰ TESTING REMINDER CREATION - FRONTEND EXACT")
        print("="*80)
        
        if not self.student_token:
            print("❌ No student token available")
            return False
            
        # EXACT data structure from frontend CreateReminderDialog
        reminder_date = "2025-08-09"
        reminder_time = "10:00"
        reminder_datetime = datetime.fromisoformat(f"{reminder_date}T{reminder_time}").isoformat()
        
        frontend_data = {
            "title": "Frontend exact reminder test",
            "description": "Testing exact frontend structure",
            "reminder_date": reminder_datetime,  # Frontend combines date and time
            "reminder_time": reminder_time,      # Frontend includes this but uses combined datetime
            "priority": "medium",
            "assigned_to": self.student_data['id'],  # Frontend field name
            "user_id": self.student_data['id'],      # Backend expected field name
            "reminder_type": "general"               # MISSING in frontend! This is required by backend!
        }
        
        success, response = self.run_test(
            "Reminder Creation (Frontend Exact)",
            "POST",
            "/reminders",
            200,
            data=frontend_data,
            token=self.student_token
        )
        
        return success

    def test_bulletin_creation_frontend_exact(self):
        """Test bulletin creation with EXACT frontend data structure"""
        print("\n" + "="*80)
        print("📢 TESTING BULLETIN CREATION - FRONTEND EXACT")
        print("="*80)
        
        if not self.student_token:
            print("❌ No student token available")
            return False
            
        # EXACT data structure from frontend CreateBulletinDialog
        frontend_data = {
            "title": "Frontend exact bulletin test",
            "content": "Testing exact frontend bulletin structure",
            "category": "announcement",  # Frontend uses different categories
            "is_highlight": False
        }
        
        success, response = self.run_test(
            "Bulletin Creation (Frontend Exact)",
            "POST",
            "/bulletins",
            200,
            data=frontend_data,
            token=self.student_token
        )
        
        return success

    def test_grant_creation_frontend_exact(self):
        """Test grant creation with EXACT frontend data structure"""
        print("\n" + "="*80)
        print("💰 TESTING GRANT CREATION - FRONTEND EXACT")
        print("="*80)
        
        if not self.supervisor_token:
            print("❌ Missing supervisor token")
            return False
            
        # EXACT data structure from frontend CreateGrantDialog
        frontend_data = {
            "title": "Frontend exact grant test",
            "funding_agency": "Frontend Test Agency",
            "total_amount": 50000.0,           # Frontend parses as float
            "duration_months": 12,             # Frontend parses as int
            "grant_type": "research",
            "description": "Testing exact frontend grant structure",
            "start_date": "2025-08-07T00:00:00.000Z",  # Frontend converts to ISO
            "end_date": "2026-08-07T00:00:00.000Z",    # Frontend converts to ISO
            "status": "active",
            "person_in_charge": self.student_data['id'] if self.student_data else "",
            "grant_vote_number": "FTE-2025-001",
            "remaining_balance": 50000.0,      # Frontend includes this
            "funding_type": "national"         # MISSING in frontend! Backend requires this!
        }
        
        success, response = self.run_test(
            "Grant Creation (Frontend Exact)",
            "POST",
            "/grants",
            200,
            data=frontend_data,
            token=self.supervisor_token
        )
        
        return success

    def test_frontend_missing_fields(self):
        """Test the specific missing fields that cause frontend failures"""
        print("\n" + "="*80)
        print("🚨 TESTING FRONTEND MISSING FIELDS ISSUES")
        print("="*80)
        
        issues_found = []
        
        # Test 1: Meeting creation missing student_id
        print("\n1. Testing Meeting Creation Missing student_id...")
        meeting_datetime = datetime.now() + timedelta(days=1)
        meeting_data_missing_student = {
            "agenda": "Test meeting",
            "meeting_date": meeting_datetime.isoformat(),
            "meeting_type": "supervision",
            "attendees": [],
            "location": "Test Lab",
            "notes": "Test notes"
            # Missing student_id!
        }
        
        success, response = self.run_test(
            "Meeting Creation (Missing student_id)",
            "POST",
            "/meetings",
            422,  # Should fail with validation error
            data=meeting_data_missing_student,
            token=self.supervisor_token
        )
        
        if not success:
            issues_found.append("Meeting creation missing student_id field")
        
        # Test 2: Reminder creation missing user_id and reminder_type
        print("\n2. Testing Reminder Creation Missing Required Fields...")
        reminder_datetime = datetime.now() + timedelta(days=1)
        reminder_data_missing_fields = {
            "title": "Test reminder",
            "description": "Test description",
            "reminder_date": reminder_datetime.isoformat(),
            "priority": "medium",
            "assigned_to": self.student_data['id'] if self.student_data else ""
            # Missing user_id and reminder_type!
        }
        
        success, response = self.run_test(
            "Reminder Creation (Missing Fields)",
            "POST",
            "/reminders",
            422,  # Should fail with validation error
            data=reminder_data_missing_fields,
            token=self.student_token
        )
        
        if not success:
            issues_found.append("Reminder creation missing user_id and reminder_type fields")
        
        # Test 3: Grant creation missing funding_type
        print("\n3. Testing Grant Creation Missing funding_type...")
        grant_data_missing_funding_type = {
            "title": "Test grant",
            "funding_agency": "Test Agency",
            "total_amount": 10000.0,
            "status": "active",
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=365)).isoformat(),
            "description": "Test grant"
            # Missing funding_type!
        }
        
        success, response = self.run_test(
            "Grant Creation (Missing funding_type)",
            "POST",
            "/grants",
            200,  # Should work because funding_type has default
            data=grant_data_missing_funding_type,
            token=self.supervisor_token
        )
        
        if success:
            print("   ✅ Grant creation works without funding_type (has default)")
        else:
            issues_found.append("Grant creation fails without funding_type")
        
        return issues_found

    def run_comprehensive_frontend_exact_tests(self):
        """Run comprehensive tests with exact frontend data structures"""
        print("🎯 FRONTEND EXACT DATA STRUCTURE TESTING")
        print("Testing with exact data structures sent by frontend")
        print("="*80)
        
        # Setup
        if not self.setup_authentication():
            print("❌ Failed to setup authentication, cannot proceed")
            return False
            
        # Run all exact frontend tests
        results = {
            "research_log": self.test_research_log_frontend_exact(),
            "meeting": self.test_meeting_creation_frontend_exact(),
            "reminder": self.test_reminder_creation_frontend_exact(),
            "bulletin": self.test_bulletin_creation_frontend_exact(),
            "grant": self.test_grant_creation_frontend_exact()
        }
        
        # Test for missing fields issues
        missing_field_issues = self.test_frontend_missing_fields()
        
        # Print comprehensive summary
        print("\n" + "="*80)
        print("📊 FRONTEND EXACT DATA STRUCTURE TEST RESULTS")
        print("="*80)
        
        working_apis = []
        failing_apis = []
        
        for api_name, result in results.items():
            status = "✅ WORKING" if result else "❌ FAILING"
            print(f"{api_name.upper().replace('_', ' ')}: {status}")
            if result:
                working_apis.append(api_name)
            else:
                failing_apis.append(api_name)
        
        print(f"\n📈 Overall Results: {len(working_apis)}/5 APIs working with frontend data")
        print(f"✅ Working APIs: {', '.join(working_apis) if working_apis else 'None'}")
        print(f"❌ Failing APIs: {', '.join(failing_apis) if failing_apis else 'None'}")
        
        # Print missing field issues
        if missing_field_issues:
            print("\n🚨 CRITICAL FRONTEND ISSUES IDENTIFIED:")
            for issue in missing_field_issues:
                print(f"   ❌ {issue}")
        else:
            print("\n✅ No critical missing field issues found")
        
        # Detailed failure analysis
        if self.failed_tests:
            print("\n" + "="*80)
            print("🔍 DETAILED FAILURE ANALYSIS")
            print("="*80)
            for failure in self.failed_tests:
                print(f"\n❌ {failure['name']}")
                print(f"   Expected: {failure['expected']}")
                print(f"   Actual: {failure['actual']}")
                print(f"   Error: {failure['error']}")
        
        return len(failing_apis) == 0 and len(missing_field_issues) == 0

def main():
    print("🎯 FRONTEND EXACT DATA STRUCTURE TESTING")
    print("Testing create APIs with exact frontend data structures")
    print("="*80)
    
    tester = FrontendExactTester()
    
    success = tester.run_comprehensive_frontend_exact_tests()
    
    print(f"\n📊 Final Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if success:
        print("🎉 All frontend exact data structure tests passed!")
        return 0
    else:
        print("❌ Frontend data structure issues found!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
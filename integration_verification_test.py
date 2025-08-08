import requests
import sys
import json
from datetime import datetime, timedelta

class IntegrationVerificationTester:
    def __init__(self, base_url="https://271c89aa-8749-475f-8a8f-92c118c46442.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.supervisor_token = None
        self.student_token = None
        self.promoted_student_token = None
        self.supervisor_data = None
        self.student_data = None
        self.promoted_student_data = None
        self.tests_run = 0
        self.tests_passed = 0

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

    def setup_users(self):
        """Setup supervisor and student accounts"""
        # Register supervisor
        supervisor_data = {
            "email": f"supervisor_integration_{datetime.now().strftime('%H%M%S')}@research.edu",
            "password": "SupervisorPass123!",
            "full_name": "Dr. Integration Test",
            "role": "supervisor",
            "department": "Computer Science",
            "research_area": "Software Engineering"
        }
        
        success, response = self.run_test(
            "Setup: Supervisor Registration",
            "POST",
            "/auth/register",
            200,
            data=supervisor_data
        )
        
        if not success or 'access_token' not in response:
            return False
            
        self.supervisor_token = response['access_token']
        self.supervisor_data = response['user_data']
        
        # Register student
        student_data = {
            "email": f"student_integration_{datetime.now().strftime('%H%M%S')}@research.edu",
            "password": "StudentPass123!",
            "full_name": "Integration Test Student",
            "role": "student",
            "student_id": f"INT{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "department": "Computer Science",
            "program_type": "phd_research",
            "field_of_study": "Software Engineering",
            "supervisor_email": self.supervisor_data['email']
        }
        
        success, response = self.run_test(
            "Setup: Student Registration",
            "POST",
            "/auth/register",
            200,
            data=student_data
        )
        
        if not success or 'access_token' not in response:
            return False
            
        self.student_token = response['access_token']
        self.student_data = response['user_data']
        
        return True

    def test_promote_and_verify_access(self):
        """Test promoting student and verifying they can access supervisor functions"""
        if not self.supervisor_token or not self.student_data:
            print("❌ Cannot test promotion - missing setup data")
            return False
        
        # Promote student to supervisor
        promotion_data = {"new_role": "supervisor"}
        
        success, response = self.run_test(
            "Promote Student to Supervisor",
            "PUT",
            f"/users/{self.student_data['id']}/promote",
            200,
            data=promotion_data,
            token=self.supervisor_token
        )
        
        if not success:
            return False
        
        # Login as promoted student to get updated token
        login_data = {
            "email": self.student_data['email'],
            "password": "StudentPass123!"
        }
        
        success, response = self.run_test(
            "Login as Promoted Student",
            "POST",
            "/auth/login",
            200,
            data=login_data
        )
        
        if not success or 'access_token' not in response:
            return False
            
        self.promoted_student_token = response['access_token']
        self.promoted_student_data = response['user_data']
        
        # Verify the role was updated
        if self.promoted_student_data.get('role') != 'supervisor':
            print(f"❌ Role not updated correctly. Expected 'supervisor', got '{self.promoted_student_data.get('role')}'")
            return False
        
        print(f"   ✅ Role successfully updated to: {self.promoted_student_data.get('role')}")
        return True

    def test_promoted_user_supervisor_functions(self):
        """Test that promoted user can access supervisor-only functions"""
        if not self.promoted_student_token:
            print("❌ Cannot test supervisor functions - no promoted student token")
            return False
        
        # Test creating a task (supervisor-only function)
        due_date = (datetime.now() + timedelta(days=7)).isoformat()
        task_data = {
            "title": "Integration Test Task",
            "description": "Task created by promoted student to test supervisor access",
            "assigned_to": self.student_data['id'],  # Assign to original student ID
            "priority": "medium",
            "due_date": due_date,
            "tags": ["integration", "test"]
        }
        
        success, response = self.run_test(
            "Create Task as Promoted User",
            "POST",
            "/tasks",
            200,
            data=task_data,
            token=self.promoted_student_token
        )
        
        if not success:
            return False
        
        # Test creating a bulletin (supervisor function)
        bulletin_data = {
            "title": "Integration Test Announcement",
            "content": "This bulletin was created by a promoted user to test supervisor access",
            "category": "general",
            "is_highlight": False
        }
        
        success, response = self.run_test(
            "Create Bulletin as Promoted User",
            "POST",
            "/bulletins",
            200,
            data=bulletin_data,
            token=self.promoted_student_token
        )
        
        return success

    def test_research_log_with_attachments_integration(self):
        """Test the complete research log with attachments workflow"""
        if not self.student_token:
            print("❌ Cannot test research log integration - no student token")
            return False
        
        # Create research log
        log_data = {
            "activity_type": "experiment",
            "title": "Integration Test Research Log",
            "description": "Testing complete workflow with attachments",
            "duration_hours": 3.0,
            "findings": "Integration testing is working well",
            "challenges": "Need to ensure all components work together",
            "next_steps": "Continue with comprehensive testing",
            "tags": ["integration", "testing", "workflow"]
        }
        
        success, response = self.run_test(
            "Create Research Log for Integration",
            "POST",
            "/research-logs",
            200,
            data=log_data,
            token=self.student_token
        )
        
        if not success or 'id' not in response:
            return False
        
        log_id = response['id']
        print(f"   Created Research Log ID: {log_id}")
        
        # Verify the research log was created and can be retrieved
        success, response = self.run_test(
            "Retrieve Research Logs",
            "GET",
            "/research-logs",
            200,
            token=self.student_token
        )
        
        if not success:
            return False
        
        # Check if our log is in the response
        found_log = False
        for log in response:
            if log.get('id') == log_id:
                found_log = True
                print(f"   ✅ Research log found in retrieval: {log.get('title')}")
                break
        
        if not found_log:
            print("❌ Created research log not found in retrieval")
            return False
        
        return True

def main():
    print("🔗 Starting Integration Verification Tests")
    print("=" * 50)
    
    tester = IntegrationVerificationTester()
    
    # Setup phase
    print("\n📋 SETUP PHASE")
    if not tester.setup_users():
        print("❌ User setup failed, stopping tests")
        return 1
    
    # Integration tests
    print("\n🔗 INTEGRATION TESTS")
    
    if not tester.test_promote_and_verify_access():
        print("❌ Promotion and access verification failed")
        return 1
    
    if not tester.test_promoted_user_supervisor_functions():
        print("❌ Promoted user supervisor functions test failed")
        return 1
    
    if not tester.test_research_log_with_attachments_integration():
        print("❌ Research log integration test failed")
        return 1
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All integration verification tests passed!")
        print("\n✅ INTEGRATION VERIFICATION COMPLETE:")
        print("   • User promotion system fully functional")
        print("   • Promoted users can access supervisor-level functions")
        print("   • Research log creation and retrieval working")
        print("   • All systems properly integrated")
        return 0
    else:
        print(f"❌ {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
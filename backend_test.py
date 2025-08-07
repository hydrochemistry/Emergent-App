import requests
import sys
import json
from datetime import datetime, timedelta

class ResearchProgressAPITester:
    def __init__(self, base_url="https://4eb13147-e91e-42cc-a844-96b5f230bc59.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.supervisor_token = None
        self.student_token = None
        self.supervisor_data = None
        self.student_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_task_id = None
        self.created_log_id = None

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

    def test_supervisor_registration(self):
        """Test supervisor registration"""
        supervisor_data = {
            "email": f"supervisor_{datetime.now().strftime('%H%M%S')}@test.com",
            "password": "SupervisorPass123!",
            "full_name": "Dr. Jane Smith",
            "role": "supervisor",
            "department": "Computer Science",
            "research_area": "Machine Learning"
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
            return True
        return False

    def test_student_registration(self):
        """Test student registration with supervisor connection"""
        if not self.supervisor_data:
            print("❌ Cannot test student registration - no supervisor data")
            return False
            
        student_data = {
            "email": f"student_{datetime.now().strftime('%H%M%S')}@test.com",
            "password": "StudentPass123!",
            "full_name": "John Doe",
            "role": "student",
            "department": "Computer Science",
            "research_area": "Deep Learning",
            "supervisor_email": self.supervisor_data['email']
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
            return True
        return False

    def test_login(self):
        """Test login for both roles"""
        if not self.supervisor_data or not self.student_data:
            print("❌ Cannot test login - missing user data")
            return False
            
        # Test supervisor login
        supervisor_login = {
            "email": self.supervisor_data['email'],
            "password": "SupervisorPass123!"
        }
        
        success, _ = self.run_test(
            "Supervisor Login",
            "POST",
            "/auth/login",
            200,
            data=supervisor_login
        )
        
        if not success:
            return False
            
        # Test student login
        student_login = {
            "email": self.student_data['email'],
            "password": "StudentPass123!"
        }
        
        success, _ = self.run_test(
            "Student Login",
            "POST",
            "/auth/login",
            200,
            data=student_login
        )
        
        return success

    def test_create_task(self):
        """Test task creation by supervisor"""
        if not self.supervisor_token or not self.student_data:
            print("❌ Cannot test task creation - missing tokens or student data")
            return False
            
        due_date = (datetime.now() + timedelta(days=7)).isoformat()
        task_data = {
            "title": "Literature Review on Neural Networks",
            "description": "Conduct a comprehensive literature review on recent advances in neural networks",
            "assigned_to": self.student_data['id'],
            "priority": "high",
            "due_date": due_date,
            "tags": ["literature", "neural networks", "research"]
        }
        
        success, response = self.run_test(
            "Create Task (Supervisor)",
            "POST",
            "/tasks",
            200,
            data=task_data,
            token=self.supervisor_token
        )
        
        if success and 'id' in response:
            self.created_task_id = response['id']
            print(f"   Created Task ID: {self.created_task_id}")
            return True
        return False

    def test_get_tasks(self):
        """Test getting tasks for both roles"""
        if not self.supervisor_token or not self.student_token:
            print("❌ Cannot test get tasks - missing tokens")
            return False
            
        # Test supervisor getting tasks
        success, response = self.run_test(
            "Get Tasks (Supervisor)",
            "GET",
            "/tasks",
            200,
            token=self.supervisor_token
        )
        
        if not success:
            return False
            
        print(f"   Supervisor sees {len(response)} tasks")
        
        # Test student getting tasks
        success, response = self.run_test(
            "Get Tasks (Student)",
            "GET",
            "/tasks",
            200,
            token=self.student_token
        )
        
        if success:
            print(f"   Student sees {len(response)} tasks")
            return True
        return False

    def test_update_task(self):
        """Test task updates by student"""
        if not self.student_token or not self.created_task_id:
            print("❌ Cannot test task update - missing token or task ID")
            return False
            
        update_data = {
            "status": "in_progress",
            "progress_percentage": 25,
            "comment": "Started working on the literature review"
        }
        
        success, response = self.run_test(
            "Update Task (Student)",
            "PUT",
            f"/tasks/{self.created_task_id}",
            200,
            data=update_data,
            token=self.student_token
        )
        
        return success

    def test_create_research_log(self):
        """Test research log creation by student"""
        if not self.student_token:
            print("❌ Cannot test research log creation - missing student token")
            return False
            
        log_data = {
            "activity_type": "literature_review",
            "title": "Neural Network Architecture Survey",
            "description": "Reviewed 15 papers on modern neural network architectures",
            "duration_hours": 4.5,
            "findings": "Found interesting trends in attention mechanisms",
            "challenges": "Difficulty accessing some paywalled papers",
            "next_steps": "Focus on transformer architectures next",
            "tags": ["literature", "neural networks", "transformers"]
        }
        
        success, response = self.run_test(
            "Create Research Log (Student)",
            "POST",
            "/research-logs",
            200,
            data=log_data,
            token=self.student_token
        )
        
        if success and 'id' in response:
            self.created_log_id = response['id']
            print(f"   Created Research Log ID: {self.created_log_id}")
            return True
        return False

    def test_get_research_logs(self):
        """Test getting research logs for both roles"""
        if not self.supervisor_token or not self.student_token:
            print("❌ Cannot test get research logs - missing tokens")
            return False
            
        # Test student getting their logs
        success, response = self.run_test(
            "Get Research Logs (Student)",
            "GET",
            "/research-logs",
            200,
            token=self.student_token
        )
        
        if not success:
            return False
            
        print(f"   Student sees {len(response)} research logs")
        
        # Test supervisor getting student logs
        success, response = self.run_test(
            "Get Research Logs (Supervisor)",
            "GET",
            "/research-logs",
            200,
            token=self.supervisor_token
        )
        
        if success:
            print(f"   Supervisor sees {len(response)} research logs")
            return True
        return False

    def test_dashboard_stats(self):
        """Test dashboard stats for both roles"""
        if not self.supervisor_token or not self.student_token:
            print("❌ Cannot test dashboard stats - missing tokens")
            return False
            
        # Test student dashboard stats
        success, response = self.run_test(
            "Dashboard Stats (Student)",
            "GET",
            "/dashboard/stats",
            200,
            token=self.student_token
        )
        
        if not success:
            return False
            
        print(f"   Student stats: {response}")
        
        # Test supervisor dashboard stats
        success, response = self.run_test(
            "Dashboard Stats (Supervisor)",
            "GET",
            "/dashboard/stats",
            200,
            token=self.supervisor_token
        )
        
        if success:
            print(f"   Supervisor stats: {response}")
            return True
        return False

    def test_get_students(self):
        """Test supervisor getting their students"""
        if not self.supervisor_token:
            print("❌ Cannot test get students - missing supervisor token")
            return False
            
        success, response = self.run_test(
            "Get Students (Supervisor)",
            "GET",
            "/students",
            200,
            token=self.supervisor_token
        )
        
        if success:
            print(f"   Supervisor has {len(response)} students")
            return True
        return False

    def test_unauthorized_access(self):
        """Test that unauthorized access is properly blocked"""
        # Test accessing tasks without token
        success, _ = self.run_test(
            "Unauthorized Access (No Token)",
            "GET",
            "/tasks",
            403
        )
        
        if not success:
            return False
            
        # Test student trying to create task (should fail)
        if not self.student_token or not self.student_data:
            return True
            
        due_date = (datetime.now() + timedelta(days=7)).isoformat()
        task_data = {
            "title": "Unauthorized Task",
            "description": "This should fail",
            "assigned_to": self.student_data['id'],
            "priority": "low",
            "due_date": due_date
        }
        
        success, _ = self.run_test(
            "Unauthorized Task Creation (Student)",
            "POST",
            "/tasks",
            403,
            data=task_data,
            token=self.student_token
        )
        
        return success

def main():
    print("🚀 Starting Research Progress API Tests")
    print("=" * 50)
    
    tester = ResearchProgressAPITester()
    
    # Run authentication tests
    if not tester.test_supervisor_registration():
        print("❌ Supervisor registration failed, stopping tests")
        return 1
        
    if not tester.test_student_registration():
        print("❌ Student registration failed, stopping tests")
        return 1
        
    if not tester.test_login():
        print("❌ Login tests failed, stopping tests")
        return 1
    
    # Run task management tests
    if not tester.test_create_task():
        print("❌ Task creation failed, stopping tests")
        return 1
        
    if not tester.test_get_tasks():
        print("❌ Get tasks failed, stopping tests")
        return 1
        
    if not tester.test_update_task():
        print("❌ Task update failed, stopping tests")
        return 1
    
    # Run research log tests
    if not tester.test_create_research_log():
        print("❌ Research log creation failed, stopping tests")
        return 1
        
    if not tester.test_get_research_logs():
        print("❌ Get research logs failed, stopping tests")
        return 1
    
    # Run dashboard and student tests
    if not tester.test_dashboard_stats():
        print("❌ Dashboard stats failed, stopping tests")
        return 1
        
    if not tester.test_get_students():
        print("❌ Get students failed, stopping tests")
        return 1
    
    # Run security tests
    if not tester.test_unauthorized_access():
        print("❌ Unauthorized access tests failed, stopping tests")
        return 1
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All backend API tests passed!")
        return 0
    else:
        print(f"❌ {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
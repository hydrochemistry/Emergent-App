import requests
import sys
import json
from datetime import datetime, timedelta

class CriticalCreateAPITester:
    def __init__(self, base_url="https://271c89aa-8749-475f-8a8f-92c118c46442.preview.emergentagent.com"):
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
                    print(f"   Response Data: {json.dumps(response_data, indent=2, default=str)[:500]}...")
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
            "email": f"supervisor_test_{timestamp}@research.edu",
            "password": "SupervisorPass123!",
            "full_name": "Dr. Sarah Wilson",
            "role": "supervisor",
            "department": "Computer Science",
            "research_area": "Artificial Intelligence",
            "lab_name": "AI Research Lab",
            "scopus_id": "12345678900",
            "orcid_id": "0000-0000-0000-0001"
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
            "email": f"student_test_{timestamp}@research.edu",
            "password": "StudentPass123!",
            "full_name": "Alex Johnson",
            "role": "student",
            "student_id": f"STU{timestamp}",
            "department": "Computer Science",
            "research_area": "Machine Learning",
            "supervisor_email": supervisor_data["email"],
            "program_type": "phd_research",
            "field_of_study": "Computer Science",
            "faculty": "Engineering",
            "institute": "University of Research",
            "nationality": "Malaysian",
            "citizenship": "Malaysian",
            "contact_number": "+60123456789"
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

    def test_research_log_creation(self):
        """Test POST /api/research-logs endpoint"""
        print("\n" + "="*60)
        print("🧪 TESTING RESEARCH LOG CREATION API")
        print("="*60)
        
        if not self.student_token:
            print("❌ No student token available")
            return False
            
        # Test with comprehensive research log data
        log_data = {
            "activity_type": "experiment",
            "title": "Neural Network Training Experiment",
            "description": "Conducted experiments on CNN architecture for image classification using CIFAR-10 dataset",
            "duration_hours": 6.5,
            "findings": "Achieved 92% accuracy with ResNet-50 architecture. Batch normalization significantly improved convergence speed.",
            "challenges": "GPU memory limitations required reducing batch size. Overfitting observed after 50 epochs.",
            "next_steps": "Implement data augmentation techniques and experiment with dropout regularization.",
            "tags": ["experiment", "cnn", "image-classification", "resnet"]
        }
        
        success, response = self.run_test(
            "Research Log Creation (Student)",
            "POST",
            "/research-logs",
            200,
            data=log_data,
            token=self.student_token
        )
        
        if success:
            print("✅ Research Log Creation: WORKING")
            return True
        else:
            print("❌ Research Log Creation: FAILED")
            return False

    def test_meeting_creation(self):
        """Test POST /api/meetings endpoint"""
        print("\n" + "="*60)
        print("📅 TESTING MEETING CREATION API")
        print("="*60)
        
        if not self.supervisor_token or not self.student_data:
            print("❌ Missing supervisor token or student data")
            return False
            
        # Test meeting creation by supervisor
        meeting_date = datetime.now() + timedelta(days=3)
        next_meeting_date = datetime.now() + timedelta(days=10)
        
        meeting_data = {
            "student_id": self.student_data['id'],
            "meeting_type": "supervision",
            "meeting_date": meeting_date.isoformat(),
            "duration_minutes": 60,
            "agenda": "Discuss research progress and next steps for neural network experiments",
            "discussion_points": [
                "Review experimental results from CNN training",
                "Discuss challenges with GPU memory limitations",
                "Plan next phase of research"
            ],
            "action_items": [
                "Implement data augmentation techniques",
                "Research dropout regularization methods",
                "Prepare presentation for lab meeting"
            ],
            "next_meeting_date": next_meeting_date.isoformat(),
            "meeting_notes": "Student showing good progress on experimental work"
        }
        
        success, response = self.run_test(
            "Meeting Creation (Supervisor)",
            "POST",
            "/meetings",
            200,
            data=meeting_data,
            token=self.supervisor_token
        )
        
        if success:
            print("✅ Meeting Creation: WORKING")
            return True
        else:
            print("❌ Meeting Creation: FAILED")
            return False

    def test_reminder_creation(self):
        """Test POST /api/reminders endpoint"""
        print("\n" + "="*60)
        print("⏰ TESTING REMINDER CREATION API")
        print("="*60)
        
        if not self.supervisor_token or not self.student_data:
            print("❌ Missing supervisor token or student data")
            return False
            
        # Test reminder creation by supervisor for student
        reminder_date = datetime.now() + timedelta(days=5)
        
        reminder_data = {
            "user_id": self.student_data['id'],
            "title": "Submit Research Progress Report",
            "description": "Monthly research progress report is due. Include experimental results, challenges faced, and next steps.",
            "reminder_date": reminder_date.isoformat(),
            "priority": "high",
            "reminder_type": "submission"
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
            print("❌ Reminder Creation: FAILED")
            return False
            
        # Test self-reminder creation by student
        self_reminder_date = datetime.now() + timedelta(days=2)
        
        self_reminder_data = {
            "user_id": self.student_data['id'],
            "title": "Prepare Lab Meeting Presentation",
            "description": "Prepare slides for weekly lab meeting presentation on CNN experiments",
            "reminder_date": self_reminder_date.isoformat(),
            "priority": "medium",
            "reminder_type": "meeting"
        }
        
        success, response = self.run_test(
            "Self-Reminder Creation (Student)",
            "POST",
            "/reminders",
            200,
            data=self_reminder_data,
            token=self.student_token
        )
        
        if success:
            print("✅ Reminder Creation: WORKING")
            return True
        else:
            print("❌ Reminder Creation: FAILED")
            return False

    def test_bulletin_creation(self):
        """Test POST /api/bulletins endpoint"""
        print("\n" + "="*60)
        print("📢 TESTING BULLETIN/ANNOUNCEMENT CREATION API")
        print("="*60)
        
        if not self.supervisor_token:
            print("❌ Missing supervisor token")
            return False
            
        # Test bulletin creation by supervisor
        bulletin_data = {
            "title": "Important Lab Safety Update",
            "content": "New safety protocols have been implemented in the lab. All students must complete the updated safety training before accessing lab equipment. Training sessions will be held every Tuesday at 2 PM.",
            "category": "safety",
            "is_highlight": True
        }
        
        success, response = self.run_test(
            "Bulletin Creation (Supervisor)",
            "POST",
            "/bulletins",
            200,
            data=bulletin_data,
            token=self.supervisor_token
        )
        
        if not success:
            print("❌ Bulletin Creation: FAILED")
            return False
            
        # Test bulletin creation by student
        student_bulletin_data = {
            "title": "Research Seminar Announcement",
            "content": "Organizing a student research seminar next Friday. All students are invited to present their current work. Please sign up by Wednesday.",
            "category": "academic",
            "is_highlight": False
        }
        
        success, response = self.run_test(
            "Bulletin Creation (Student)",
            "POST",
            "/bulletins",
            200,
            data=student_bulletin_data,
            token=self.student_token
        )
        
        if success:
            print("✅ Bulletin Creation: WORKING")
            return True
        else:
            print("❌ Bulletin Creation: FAILED")
            return False

    def test_grant_creation(self):
        """Test POST /api/grants endpoint"""
        print("\n" + "="*60)
        print("💰 TESTING GRANT CREATION API")
        print("="*60)
        
        if not self.supervisor_token:
            print("❌ Missing supervisor token")
            return False
            
        # Test grant creation by supervisor
        start_date = datetime.now()
        end_date = datetime.now() + timedelta(days=365*2)  # 2 years
        
        grant_data = {
            "title": "AI Research Grant for Neural Network Optimization",
            "funding_agency": "National Science Foundation",
            "funding_type": "national",
            "total_amount": 150000.0,
            "status": "active",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "description": "Research grant focused on developing novel neural network optimization techniques for improved efficiency and accuracy in deep learning models.",
            "student_manager_id": self.student_data['id'] if self.student_data else None,
            "person_in_charge": self.student_data['id'] if self.student_data else None,
            "grant_vote_number": "NSF-2024-AI-001",
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
        
        if success:
            print("✅ Grant Creation: WORKING")
            return True
        else:
            print("❌ Grant Creation: FAILED")
            return False

    def run_all_critical_tests(self):
        """Run all critical create API tests"""
        print("🚨 CRITICAL CREATE API TESTING")
        print("Testing the 5 reported failing endpoints:")
        print("1. Research Log Creation - POST /api/research-logs")
        print("2. Meeting Creation - POST /api/meetings")
        print("3. Reminder Creation - POST /api/reminders")
        print("4. Bulletin Creation - POST /api/bulletins")
        print("5. Grant Creation - POST /api/grants")
        print("="*80)
        
        # Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication setup failed, cannot proceed with tests")
            return False
            
        # Run all critical tests
        results = {
            "research_logs": self.test_research_log_creation(),
            "meetings": self.test_meeting_creation(),
            "reminders": self.test_reminder_creation(),
            "bulletins": self.test_bulletin_creation(),
            "grants": self.test_grant_creation()
        }
        
        # Print summary
        print("\n" + "="*80)
        print("📊 CRITICAL API TEST RESULTS SUMMARY")
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
        
        print(f"\n📈 Overall Results: {len(working_apis)}/5 APIs working")
        print(f"✅ Working APIs: {', '.join(working_apis) if working_apis else 'None'}")
        print(f"❌ Failing APIs: {', '.join(failing_apis) if failing_apis else 'None'}")
        
        # Print detailed failure information
        if self.failed_tests:
            print("\n" + "="*80)
            print("🔍 DETAILED FAILURE ANALYSIS")
            print("="*80)
            for failure in self.failed_tests:
                print(f"\n❌ {failure['name']}")
                print(f"   Expected: {failure['expected']}")
                print(f"   Actual: {failure['actual']}")
                print(f"   Error: {failure['error']}")
        
        return len(failing_apis) == 0

def main():
    print("🚨 CRITICAL BUG INVESTIGATION")
    print("Testing reported failing create/submit APIs")
    print("="*80)
    
    tester = CriticalCreateAPITester()
    
    success = tester.run_all_critical_tests()
    
    print(f"\n📊 Final Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if success:
        print("🎉 All critical create APIs are working!")
        return 0
    else:
        print("❌ Some critical create APIs are failing!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
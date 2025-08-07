import requests
import sys
import json
from datetime import datetime, timedelta

class EnhancedResearchLabAPITester:
    def __init__(self, base_url="https://046e2c53-c2c3-4512-b947-987619959349.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.supervisor_token = None
        self.student_token = None
        self.lab_manager_token = None
        self.supervisor_data = None
        self.student_data = None
        self.lab_manager_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_task_id = None
        self.created_log_id = None
        self.created_meeting_id = None
        self.created_reminder_id = None
        self.created_note_id = None
        self.created_grant_id = None
        self.created_bulletin_id = None

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

    def test_comprehensive_supervisor_registration(self):
        """Test comprehensive supervisor registration with enhanced fields"""
        supervisor_data = {
            "email": f"supervisor_{datetime.now().strftime('%H%M%S')}@test.com",
            "password": "SupervisorPass123!",
            "full_name": "Dr. Jane Smith",
            "role": "supervisor",
            "department": "Computer Science",
            "faculty": "Engineering",
            "institute": "Advanced Computing Institute",
            "research_area": "Machine Learning and AI",
            "lab_name": "AI Research Lab",
            "scopus_id": "22133247800",
            "orcid_id": "0000-0000-0000-0000"
        }
        
        success, response = self.run_test(
            "Comprehensive Supervisor Registration",
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

    def test_comprehensive_student_registration(self):
        """Test comprehensive student registration with all enhanced fields"""
        if not self.supervisor_data:
            print("❌ Cannot test student registration - no supervisor data")
            return False
            
        student_data = {
            "email": f"student_{datetime.now().strftime('%H%M%S')}@test.com",
            "password": "StudentPass123!",
            "full_name": "John Doe",
            "role": "student",
            
            # Enhanced Student Information
            "student_id": "CS2024001",
            "contact_number": "+1234567890",
            "nationality": "Malaysian",
            "citizenship": "Malaysian",
            "program_type": "phd_research",
            "field_of_study": "Artificial Intelligence",
            "department": "Computer Science",
            "faculty": "Engineering",
            "institute": "Advanced Computing Institute",
            "enrollment_date": "2024-01-15",
            "expected_graduation_date": "2027-12-31",
            
            # Existing fields
            "research_area": "Deep Learning",
            "supervisor_email": self.supervisor_data['email']
        }
        
        success, response = self.run_test(
            "Comprehensive Student Registration",
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

    def test_profile_management(self):
        """Test comprehensive profile viewing and updating"""
        if not self.student_token:
            print("❌ Cannot test profile management - missing student token")
            return False
            
        # Test getting profile
        success, response = self.run_test(
            "Get User Profile",
            "GET",
            "/users/profile",
            200,
            token=self.student_token
        )
        
        if not success:
            return False
            
        # Test updating profile
        update_data = {
            "contact_number": "+9876543210",
            "study_status": "active",
            "research_area": "Advanced Deep Learning"
        }
        
        success, _ = self.run_test(
            "Update User Profile",
            "PUT",
            "/users/profile",
            200,
            data=update_data,
            token=self.student_token
        )
        
        return success

    def test_lab_manager_promotion(self):
        """Test promoting student to lab manager"""
        if not self.supervisor_token or not self.student_data:
            print("❌ Cannot test lab manager promotion - missing tokens or data")
            return False
            
        success, _ = self.run_test(
            "Promote Student to Lab Manager",
            "POST",
            f"/users/{self.student_data['id']}/promote-lab-manager",
            200,
            token=self.supervisor_token
        )
        
        if success:
            # Update our local data to reflect the promotion
            self.lab_manager_token = self.student_token
            self.lab_manager_data = self.student_data.copy()
            self.lab_manager_data['role'] = 'lab_manager'
            
        return success

    def test_supervisor_meetings(self):
        """Test supervisor meeting management system"""
        if not self.supervisor_token or not self.student_data:
            print("❌ Cannot test meetings - missing tokens or data")
            return False
            
        # Create a meeting
        meeting_date = (datetime.now() + timedelta(days=3)).isoformat()
        meeting_data = {
            "student_id": self.student_data['id'],
            "meeting_type": "supervision",
            "meeting_date": meeting_date,
            "duration_minutes": 60,
            "agenda": "Discuss research progress and next steps",
            "discussion_points": [
                "Review literature survey progress",
                "Discuss methodology approach",
                "Plan next month activities"
            ],
            "action_items": [
                "Complete chapter 2 draft",
                "Prepare experiment setup",
                "Schedule follow-up meeting"
            ],
            "meeting_notes": "Student showing good progress on literature review"
        }
        
        success, response = self.run_test(
            "Create Supervisor Meeting",
            "POST",
            "/meetings",
            200,
            data=meeting_data,
            token=self.supervisor_token
        )
        
        if success and 'id' in response:
            self.created_meeting_id = response['id']
            print(f"   Created Meeting ID: {self.created_meeting_id}")
        
        if not success:
            return False
            
        # Test getting meetings
        success, response = self.run_test(
            "Get Meetings (Supervisor)",
            "GET",
            "/meetings",
            200,
            token=self.supervisor_token
        )
        
        if success:
            print(f"   Found {len(response)} meetings")
            
        return success

    def test_reminders_system(self):
        """Test enhanced reminders and alerts system"""
        if not self.supervisor_token or not self.student_data:
            print("❌ Cannot test reminders - missing tokens or data")
            return False
            
        # Create a reminder
        reminder_date = (datetime.now() + timedelta(days=5)).isoformat()
        reminder_data = {
            "user_id": self.student_data['id'],
            "title": "Submit Progress Report",
            "description": "Monthly progress report is due next week",
            "reminder_date": reminder_date,
            "priority": "high",
            "reminder_type": "deadline"
        }
        
        success, response = self.run_test(
            "Create Reminder",
            "POST",
            "/reminders",
            200,
            data=reminder_data,
            token=self.supervisor_token
        )
        
        if success and 'id' in response:
            self.created_reminder_id = response['id']
            print(f"   Created Reminder ID: {self.created_reminder_id}")
        
        if not success:
            return False
            
        # Test getting reminders
        success, response = self.run_test(
            "Get Reminders",
            "GET",
            "/reminders",
            200,
            token=self.student_token
        )
        
        if success:
            print(f"   Found {len(response)} reminders")
            
        return success

    def test_supervisor_notes_system(self):
        """Test supervisor notes system"""
        if not self.supervisor_token or not self.student_data:
            print("❌ Cannot test notes - missing tokens or data")
            return False
            
        # Create a supervisor note
        note_data = {
            "student_id": self.student_data['id'],
            "note_type": "supervision",
            "title": "Research Progress Assessment",
            "content": "Student is making excellent progress on the literature review. Recommend focusing on methodology next.",
            "is_private": False
        }
        
        success, response = self.run_test(
            "Create Supervisor Note",
            "POST",
            "/notes",
            200,
            data=note_data,
            token=self.supervisor_token
        )
        
        if success and 'id' in response:
            self.created_note_id = response['id']
            print(f"   Created Note ID: {self.created_note_id}")
        
        if not success:
            return False
            
        # Test getting notes
        success, response = self.run_test(
            "Get Notes (Student View)",
            "GET",
            "/notes",
            200,
            token=self.student_token
        )
        
        if success:
            print(f"   Student can see {len(response)} notes")
            
        return success

    def test_publications_system(self):
        """Test publications management with Scopus integration"""
        if not self.supervisor_token:
            print("❌ Cannot test publications - missing supervisor token")
            return False
            
        # Test Scopus sync (mock)
        success, response = self.run_test(
            "Sync Scopus Publications",
            "POST",
            "/publications/sync-scopus",
            200,
            token=self.supervisor_token
        )
        
        if not success:
            return False
            
        # Test getting all publications
        success, response = self.run_test(
            "Get All Publications",
            "GET",
            "/publications/all",
            200,
            token=self.supervisor_token
        )
        
        if success:
            print(f"   Found {len(response)} publications")
            
        return success

    def test_grants_management(self):
        """Test grant management system"""
        if not self.supervisor_token:
            print("❌ Cannot test grants - missing supervisor token")
            return False
            
        # Create a grant
        start_date = datetime.now().isoformat()
        end_date = (datetime.now() + timedelta(days=365*3)).isoformat()
        
        grant_data = {
            "title": "AI Research Grant 2024",
            "funding_agency": "National Science Foundation",
            "funding_type": "national",
            "total_amount": 500000.0,
            "status": "active",
            "start_date": start_date,
            "end_date": end_date,
            "description": "Research grant for advanced AI algorithms",
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
        
        if not success:
            return False
            
        # Test getting grants
        success, response = self.run_test(
            "Get Grants",
            "GET",
            "/grants",
            200,
            token=self.supervisor_token
        )
        
        if success:
            print(f"   Found {len(response)} grants")
            
        return success

    def test_bulletins_system(self):
        """Test bulletins/announcements system"""
        if not self.student_token:
            print("❌ Cannot test bulletins - missing student token")
            return False
            
        # Create a bulletin
        bulletin_data = {
            "title": "Lab Meeting Announcement",
            "content": "Weekly lab meeting scheduled for Friday at 2 PM",
            "category": "meeting"
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
        
        if not success:
            return False
            
        # Test getting bulletins
        success, response = self.run_test(
            "Get Bulletins",
            "GET",
            "/bulletins",
            200,
            token=self.student_token
        )
        
        if success:
            print(f"   Found {len(response)} bulletins")
            
        return success

    def test_enhanced_dashboard_stats(self):
        """Test comprehensive dashboard statistics"""
        if not self.supervisor_token or not self.student_token:
            print("❌ Cannot test dashboard stats - missing tokens")
            return False
            
        # Test student dashboard stats
        success, response = self.run_test(
            "Enhanced Dashboard Stats (Student)",
            "GET",
            "/dashboard/stats",
            200,
            token=self.student_token
        )
        
        if not success:
            return False
            
        print(f"   Student stats keys: {list(response.keys())}")
        
        # Test supervisor dashboard stats
        success, response = self.run_test(
            "Enhanced Dashboard Stats (Supervisor)",
            "GET",
            "/dashboard/stats",
            200,
            token=self.supervisor_token
        )
        
        if success:
            print(f"   Supervisor stats keys: {list(response.keys())}")
            return True
        return False

    def test_task_endorsement(self):
        """Test task endorsement by supervisor"""
        if not self.supervisor_token or not self.created_task_id:
            print("❌ Cannot test task endorsement - missing token or task ID")
            return False
            
        endorsement_data = {
            "task_id": self.created_task_id,
            "rating": 4,
            "feedback": "Good progress on the literature review. Keep up the excellent work!"
        }
        
        success, _ = self.run_test(
            "Endorse Task",
            "POST",
            f"/tasks/{self.created_task_id}/endorse",
            200,
            data=endorsement_data,
            token=self.supervisor_token
        )
        
        return success

    def test_research_log_endorsement(self):
        """Test research log endorsement by supervisor"""
        if not self.supervisor_token or not self.created_log_id:
            print("❌ Cannot test research log endorsement - missing token or log ID")
            return False
            
        endorsement_data = {
            "log_id": self.created_log_id,
            "endorsed": True,
            "comments": "Excellent research methodology and findings",
            "rating": 5
        }
        
        success, _ = self.run_test(
            "Endorse Research Log",
            "POST",
            f"/research-logs/{self.created_log_id}/endorse",
            200,
            data=endorsement_data,
            token=self.supervisor_token
        )
        
        return success

    def test_basic_functionality(self):
        """Test basic task and research log functionality"""
        # Create task
        if self.supervisor_token and self.student_data:
            due_date = (datetime.now() + timedelta(days=7)).isoformat()
            task_data = {
                "title": "Literature Review on Neural Networks",
                "description": "Conduct a comprehensive literature review",
                "assigned_to": self.student_data['id'],
                "priority": "high",
                "due_date": due_date,
                "tags": ["literature", "neural networks"]
            }
            
            success, response = self.run_test(
                "Create Task",
                "POST",
                "/tasks",
                200,
                data=task_data,
                token=self.supervisor_token
            )
            
            if success and 'id' in response:
                self.created_task_id = response['id']
        
        # Create research log
        if self.student_token:
            log_data = {
                "activity_type": "literature_review",
                "title": "Neural Network Architecture Survey",
                "description": "Reviewed papers on neural network architectures",
                "duration_hours": 4.5,
                "findings": "Found interesting trends in attention mechanisms",
                "tags": ["literature", "neural networks"]
            }
            
            success, response = self.run_test(
                "Create Research Log",
                "POST",
                "/research-logs",
                200,
                data=log_data,
                token=self.student_token
            )
            
            if success and 'id' in response:
                self.created_log_id = response['id']
        
        return True

def main():
    print("🚀 Starting Enhanced Research Lab Management System API Tests")
    print("=" * 70)
    
    tester = EnhancedResearchLabAPITester()
    
    # Test comprehensive registration
    print("\n📝 TESTING COMPREHENSIVE REGISTRATION SYSTEM")
    if not tester.test_comprehensive_supervisor_registration():
        print("❌ Comprehensive supervisor registration failed, stopping tests")
        return 1
        
    if not tester.test_comprehensive_student_registration():
        print("❌ Comprehensive student registration failed, stopping tests")
        return 1
    
    # Test profile management
    print("\n👤 TESTING PROFILE MANAGEMENT")
    if not tester.test_profile_management():
        print("❌ Profile management failed, stopping tests")
        return 1
    
    # Test lab manager promotion
    print("\n👨‍💼 TESTING LAB MANAGER ROLE MANAGEMENT")
    if not tester.test_lab_manager_promotion():
        print("❌ Lab manager promotion failed, stopping tests")
        return 1
    
    # Test basic functionality first
    print("\n📋 TESTING BASIC FUNCTIONALITY")
    if not tester.test_basic_functionality():
        print("❌ Basic functionality failed, stopping tests")
        return 1
    
    # Test supervisor meetings
    print("\n📅 TESTING SUPERVISOR MEETING SYSTEM")
    if not tester.test_supervisor_meetings():
        print("❌ Supervisor meetings failed, stopping tests")
        return 1
    
    # Test reminders system
    print("\n⏰ TESTING REMINDERS & ALERTS SYSTEM")
    if not tester.test_reminders_system():
        print("❌ Reminders system failed, stopping tests")
        return 1
    
    # Test supervisor notes
    print("\n📝 TESTING SUPERVISOR NOTES SYSTEM")
    if not tester.test_supervisor_notes_system():
        print("❌ Supervisor notes system failed, stopping tests")
        return 1
    
    # Test publications system
    print("\n📚 TESTING PUBLICATIONS SYSTEM")
    if not tester.test_publications_system():
        print("❌ Publications system failed, stopping tests")
        return 1
    
    # Test grants management
    print("\n💰 TESTING GRANTS MANAGEMENT")
    if not tester.test_grants_management():
        print("❌ Grants management failed, stopping tests")
        return 1
    
    # Test bulletins system
    print("\n📢 TESTING BULLETINS SYSTEM")
    if not tester.test_bulletins_system():
        print("❌ Bulletins system failed, stopping tests")
        return 1
    
    # Test enhanced dashboard
    print("\n📊 TESTING ENHANCED DASHBOARD")
    if not tester.test_enhanced_dashboard_stats():
        print("❌ Enhanced dashboard failed, stopping tests")
        return 1
    
    # Test endorsement systems
    print("\n⭐ TESTING ENDORSEMENT SYSTEMS")
    if not tester.test_task_endorsement():
        print("❌ Task endorsement failed, stopping tests")
        return 1
        
    if not tester.test_research_log_endorsement():
        print("❌ Research log endorsement failed, stopping tests")
        return 1
    
    # Print final results
    print("\n" + "=" * 70)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All Enhanced Research Lab Management System API tests passed!")
        return 0
    else:
        print(f"❌ {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
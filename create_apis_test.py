import requests
import sys
import json
from datetime import datetime, timedelta

class CreateAPITester:
    def __init__(self, base_url="https://c5e539fb-9522-486d-b275-1bb355b557d8.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.supervisor_token = None
        self.student_token = None
        self.supervisor_data = None
        self.student_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_ids = {}

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None):
        """Run a single API test"""
        url = f"{self.api_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
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

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if 'id' in response_data:
                        print(f"   Created ID: {response_data['id']}")
                    return success, response_data
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Response: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def setup_authentication(self):
        """Set up supervisor and student authentication"""
        print("🔐 Setting up authentication...")
        
        # Register supervisor
        supervisor_data = {
            "email": f"supervisor_{datetime.now().strftime('%H%M%S')}@test.com",
            "password": "SupervisorPass123!",
            "full_name": "Dr. Sarah Johnson",
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
            print("❌ Supervisor registration failed")
            return False
            
        self.supervisor_token = response['access_token']
        self.supervisor_data = response['user_data']
        print(f"   Supervisor ID: {self.supervisor_data['id']}")
        
        # Register student
        student_data = {
            "email": f"student_{datetime.now().strftime('%H%M%S')}@test.com",
            "password": "StudentPass123!",
            "full_name": "Ahmad Rahman",
            "role": "student",
            "student_id": "CS2024001",
            "department": "Computer Science",
            "faculty": "Faculty of Engineering",
            "institute": "Universiti Teknologi Malaysia",
            "program_type": "phd_research",
            "field_of_study": "Machine Learning",
            "research_area": "Deep Learning",
            "contact_number": "+60123456788",
            "nationality": "Malaysian",
            "citizenship": "Malaysian",
            "enrollment_date": "2024-01-15",
            "expected_graduation_date": "2027-12-31",
            "supervisor_email": supervisor_data['email']
        }
        
        success, response = self.run_test(
            "Student Registration",
            "POST",
            "/auth/register",
            200,
            data=student_data
        )
        
        if not success or 'access_token' not in response:
            print("❌ Student registration failed")
            return False
            
        self.student_token = response['access_token']
        self.student_data = response['user_data']
        print(f"   Student ID: {self.student_data['id']}")
        
        return True

    def test_research_log_creation(self):
        """Test Research Log Creation API - POST /api/research-logs"""
        print("\n" + "="*60)
        print("🧪 TESTING RESEARCH LOG CREATION API")
        print("="*60)
        
        if not self.student_token:
            print("❌ Cannot test - missing student token")
            return False
        
        # Test with comprehensive data as mentioned in review request
        log_data = {
            "title": "Machine Learning Experiment Results",
            "activity_type": "experiment",
            "description": "Conducted experiments on neural network performance with various architectures",
            "findings": "Model achieved 89% accuracy on test dataset using ResNet architecture",
            "challenges": "Overfitting issues with small dataset, required extensive data augmentation",
            "next_steps": "Implement regularization techniques and expand dataset",
            "duration_hours": 4.5,
            "tags": ["machine-learning", "neural-networks", "experiments", "resnet"],
        }
        
        success, response = self.run_test(
            "Research Log Creation (Student)",
            "POST",
            "/research-logs",
            200,
            data=log_data,
            token=self.student_token
        )
        
        if success and 'id' in response:
            self.created_ids['research_log'] = response['id']
            print(f"✅ Research Log created successfully with ID: {response['id']}")
            
            # Verify data persistence
            success2, get_response = self.run_test(
                "Verify Research Log Retrieval",
                "GET",
                "/research-logs",
                200,
                token=self.student_token
            )
            
            if success2 and len(get_response) > 0:
                print(f"✅ Research Log data persisted correctly - found {len(get_response)} logs")
                return True
            else:
                print("❌ Research Log data not persisted correctly")
                return False
        
        return success

    def test_meeting_creation(self):
        """Test Meeting Creation API - POST /api/meetings"""
        print("\n" + "="*60)
        print("📅 TESTING MEETING CREATION API")
        print("="*60)
        
        if not self.supervisor_token or not self.student_data:
            print("❌ Cannot test - missing supervisor token or student data")
            return False
        
        # Test with comprehensive data as mentioned in review request
        meeting_date = datetime.now() + timedelta(days=3)
        meeting_data = {
            "student_id": self.student_data['id'],
            "meeting_type": "supervision",
            "meeting_date": meeting_date.isoformat(),
            "duration_minutes": 60,
            "agenda": "Discuss research progress and next steps for machine learning project",
            "discussion_points": [
                "Review current experiment results",
                "Discuss challenges with data collection",
                "Plan next phase of research"
            ],
            "action_items": [
                "Student to prepare literature review summary",
                "Supervisor to provide additional dataset resources",
                "Schedule follow-up meeting in 2 weeks"
            ],
            "meeting_notes": "Initial supervision meeting to establish research direction and expectations"
        }
        
        success, response = self.run_test(
            "Meeting Creation (Supervisor)",
            "POST",
            "/meetings",
            200,
            data=meeting_data,
            token=self.supervisor_token
        )
        
        if success and 'id' in response:
            self.created_ids['meeting'] = response['id']
            print(f"✅ Meeting created successfully with ID: {response['id']}")
            
            # Verify data persistence and role-based access
            success2, get_response = self.run_test(
                "Verify Meeting Retrieval (Supervisor)",
                "GET",
                "/meetings",
                200,
                token=self.supervisor_token
            )
            
            if success2 and len(get_response) > 0:
                print(f"✅ Meeting data persisted correctly - supervisor sees {len(get_response)} meetings")
                
                # Test student access
                success3, student_response = self.run_test(
                    "Verify Meeting Retrieval (Student)",
                    "GET",
                    "/meetings",
                    200,
                    token=self.student_token
                )
                
                if success3:
                    print(f"✅ Student can access meetings - sees {len(student_response)} meetings")
                    return True
                else:
                    print("❌ Student cannot access meetings")
                    return False
            else:
                print("❌ Meeting data not persisted correctly")
                return False
        
        return success

    def test_reminder_creation(self):
        """Test Reminder Creation API - POST /api/reminders"""
        print("\n" + "="*60)
        print("⏰ TESTING REMINDER CREATION API")
        print("="*60)
        
        if not self.supervisor_token or not self.student_data:
            print("❌ Cannot test - missing tokens or student data")
            return False
        
        # Test supervisor creating reminder for student
        reminder_date = datetime.now() + timedelta(days=5)
        reminder_data = {
            "user_id": self.student_data['id'],
            "title": "Submit Research Progress Report",
            "description": "Please submit your monthly research progress report including experiment results and literature review summary",
            "reminder_date": reminder_date.isoformat(),
            "priority": "high",
            "reminder_type": "submission"
        }
        
        success, response = self.run_test(
            "Reminder Creation (Supervisor to Student)",
            "POST",
            "/reminders",
            200,
            data=reminder_data,
            token=self.supervisor_token
        )
        
        if success and 'id' in response:
            self.created_ids['reminder_supervisor'] = response['id']
            print(f"✅ Supervisor-to-Student reminder created with ID: {response['id']}")
        
        # Test student creating reminder for themselves
        self_reminder_data = {
            "user_id": self.student_data['id'],
            "title": "Prepare for Lab Meeting",
            "description": "Prepare presentation slides for weekly lab meeting discussion",
            "reminder_date": (datetime.now() + timedelta(days=2)).isoformat(),
            "priority": "medium",
            "reminder_type": "meeting"
        }
        
        success2, response2 = self.run_test(
            "Reminder Creation (Student Self-Reminder)",
            "POST",
            "/reminders",
            200,
            data=self_reminder_data,
            token=self.student_token
        )
        
        if success2 and 'id' in response2:
            self.created_ids['reminder_student'] = response2['id']
            print(f"✅ Student self-reminder created with ID: {response2['id']}")
            
            # Verify data persistence
            success3, get_response = self.run_test(
                "Verify Reminder Retrieval",
                "GET",
                "/reminders",
                200,
                token=self.student_token
            )
            
            if success3 and len(get_response) >= 2:
                print(f"✅ Reminders persisted correctly - found {len(get_response)} reminders")
                return True
            else:
                print("❌ Reminders not persisted correctly")
                return False
        
        return success and success2

    def test_bulletin_creation(self):
        """Test Bulletin/Announcement Creation API - POST /api/bulletins"""
        print("\n" + "="*60)
        print("📢 TESTING BULLETIN/ANNOUNCEMENT CREATION API")
        print("="*60)
        
        if not self.student_token:
            print("❌ Cannot test - missing student token")
            return False
        
        # Test bulletin creation with comprehensive data
        bulletin_data = {
            "title": "Important Lab Safety Guidelines Update",
            "content": "Please note the updated lab safety guidelines effective immediately. All researchers must complete the new safety training module before accessing lab equipment. The training covers proper handling of chemicals, emergency procedures, and equipment maintenance protocols.",
            "category": "safety",
            "is_highlight": True
        }
        
        success, response = self.run_test(
            "Bulletin Creation (Student)",
            "POST",
            "/bulletins",
            200,
            data=bulletin_data,
            token=self.student_token
        )
        
        if success and 'id' in response:
            self.created_ids['bulletin'] = response['id']
            print(f"✅ Bulletin created successfully with ID: {response['id']}")
            
            # Test supervisor bulletin creation
            supervisor_bulletin_data = {
                "title": "Research Seminar Series Announcement",
                "content": "Join us for the monthly research seminar series featuring guest speakers from leading universities. This month's topic: 'Advances in Quantum Computing Applications'. Date: Next Friday, 2:00 PM in Conference Room A.",
                "category": "event",
                "is_highlight": False
            }
            
            success2, response2 = self.run_test(
                "Bulletin Creation (Supervisor)",
                "POST",
                "/bulletins",
                200,
                data=supervisor_bulletin_data,
                token=self.supervisor_token
            )
            
            if success2 and 'id' in response2:
                self.created_ids['bulletin_supervisor'] = response2['id']
                print(f"✅ Supervisor bulletin created with ID: {response2['id']}")
                
                # Verify data persistence
                success3, get_response = self.run_test(
                    "Verify Bulletin Retrieval",
                    "GET",
                    "/bulletins",
                    200,
                    token=self.supervisor_token
                )
                
                if success3 and len(get_response) >= 2:
                    print(f"✅ Bulletins persisted correctly - found {len(get_response)} bulletins")
                    return True
                else:
                    print("❌ Bulletins not persisted correctly")
                    return False
        
        return success

    def test_grant_creation(self):
        """Test Grant Creation API - POST /api/grants"""
        print("\n" + "="*60)
        print("💰 TESTING GRANT CREATION API")
        print("="*60)
        
        if not self.supervisor_token:
            print("❌ Cannot test - missing supervisor token")
            return False
        
        # Test grant creation with comprehensive data as mentioned in review request
        start_date = datetime.now() + timedelta(days=30)
        end_date = start_date + timedelta(days=365*3)  # 3 years
        
        grant_data = {
            "title": "Advanced Machine Learning Research Initiative",
            "funding_agency": "Ministry of Higher Education Malaysia",
            "total_amount": 250000.00,
            "duration_months": 36,
            "grant_type": "research",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "status": "active",
            "person_in_charge": self.student_data['id'] if self.student_data else None,
            "grant_vote_number": "MOHE-2024-ML-001",
            "description": "Comprehensive research project focusing on advanced machine learning algorithms for healthcare applications, including deep learning models for medical image analysis and natural language processing for clinical data.",
            "funding_type": "national"
        }
        
        success, response = self.run_test(
            "Grant Creation (Supervisor)",
            "POST",
            "/grants",
            200,
            data=grant_data,
            token=self.supervisor_token
        )
        
        if success and 'id' in response:
            self.created_ids['grant'] = response['id']
            print(f"✅ Grant created successfully with ID: {response['id']}")
            
            # Verify data persistence and structure
            success2, get_response = self.run_test(
                "Verify Grant Retrieval",
                "GET",
                "/grants",
                200,
                token=self.supervisor_token
            )
            
            if success2 and len(get_response) > 0:
                grant = get_response[0]
                required_fields = ['title', 'funding_agency', 'total_amount', 'duration_months', 
                                 'grant_type', 'person_in_charge', 'grant_vote_number']
                
                all_fields_present = all(field in grant for field in required_fields)
                
                if all_fields_present:
                    print(f"✅ Grant data structure complete - all required fields present")
                    print(f"   Grant details: {grant['title']} - ${grant['total_amount']}")
                    return True
                else:
                    missing_fields = [field for field in required_fields if field not in grant]
                    print(f"❌ Grant data incomplete - missing fields: {missing_fields}")
                    return False
            else:
                print("❌ Grant data not persisted correctly")
                return False
        
        return success

    def test_authentication_requirements(self):
        """Test that all create APIs properly require authentication"""
        print("\n" + "="*60)
        print("🔒 TESTING AUTHENTICATION REQUIREMENTS")
        print("="*60)
        
        # Test all create endpoints without authentication
        endpoints_to_test = [
            ("/research-logs", {"title": "Test", "activity_type": "experiment", "description": "Test"}),
            ("/meetings", {"student_id": "test", "meeting_type": "supervision", "meeting_date": datetime.now().isoformat(), "agenda": "Test"}),
            ("/reminders", {"user_id": "test", "title": "Test", "description": "Test", "reminder_date": datetime.now().isoformat(), "reminder_type": "general"}),
            ("/bulletins", {"title": "Test", "content": "Test", "category": "general"}),
            ("/grants", {"title": "Test", "funding_agency": "Test", "total_amount": 1000, "status": "active", "start_date": datetime.now().isoformat(), "end_date": datetime.now().isoformat()})
        ]
        
        all_protected = True
        for endpoint, data in endpoints_to_test:
            success, _ = self.run_test(
                f"Unauthorized Access Test - {endpoint}",
                "POST",
                endpoint,
                403,  # Should return 403 Forbidden
                data=data
            )
            if not success:
                all_protected = False
        
        if all_protected:
            print("✅ All create APIs properly require authentication")
            return True
        else:
            print("❌ Some create APIs do not properly require authentication")
            return False

    def run_comprehensive_test(self):
        """Run comprehensive test of all 5 create APIs"""
        print("🚀 STARTING COMPREHENSIVE CREATE API TESTING")
        print("="*80)
        print("Testing the 5 core create APIs that users reported as not working:")
        print("1. Research Log Creation - POST /api/research-logs")
        print("2. Meeting Creation - POST /api/meetings")
        print("3. Reminder Creation - POST /api/reminders")
        print("4. Bulletin/Announcement Creation - POST /api/bulletins")
        print("5. Grant Creation - POST /api/grants")
        print("="*80)
        
        # Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication setup failed - cannot proceed with tests")
            return False
        
        # Test authentication requirements
        auth_test_passed = self.test_authentication_requirements()
        
        # Test each create API
        research_log_passed = self.test_research_log_creation()
        meeting_passed = self.test_meeting_creation()
        reminder_passed = self.test_reminder_creation()
        bulletin_passed = self.test_bulletin_creation()
        grant_passed = self.test_grant_creation()
        
        # Print comprehensive results
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("="*80)
        
        results = [
            ("Authentication Requirements", auth_test_passed),
            ("Research Log Creation API", research_log_passed),
            ("Meeting Creation API", meeting_passed),
            ("Reminder Creation API", reminder_passed),
            ("Bulletin/Announcement Creation API", bulletin_passed),
            ("Grant Creation API", grant_passed)
        ]
        
        for test_name, passed in results:
            status = "✅ WORKING" if passed else "❌ FAILED"
            print(f"{test_name:<40} {status}")
        
        total_passed = sum(1 for _, passed in results if passed)
        total_tests = len(results)
        
        print(f"\nOverall Results: {total_passed}/{total_tests} API groups passed")
        print(f"Individual Tests: {self.tests_passed}/{self.tests_run} tests passed")
        
        if total_passed == total_tests:
            print("\n🎉 ALL CREATE APIs ARE WORKING PERFECTLY!")
            print("The reported issues are NOT caused by backend API failures.")
            print("Issue likely in frontend: JavaScript execution, form validation, or error handling.")
            return True
        else:
            print(f"\n❌ {total_tests - total_passed} API groups have issues")
            return False

def main():
    tester = CreateAPITester()
    success = tester.run_comprehensive_test()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
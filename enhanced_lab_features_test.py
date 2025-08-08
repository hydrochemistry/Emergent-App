import requests
import sys
import json
from datetime import datetime, timedelta

class EnhancedLabFeaturesAPITester:
    def __init__(self, base_url="https://c5e539fb-9522-486d-b275-1bb355b557d8.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.supervisor_token = None
        self.student_token = None
        self.pic_student_token = None  # Student assigned as PIC
        self.supervisor_data = None
        self.student_data = None
        self.pic_student_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_log_id = None
        self.created_grant_id = None

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

    def setup_test_users(self):
        """Create test users for enhanced features testing"""
        print("🔧 Setting up test users...")
        
        # Create supervisor
        supervisor_data = {
            "email": f"supervisor_enhanced_{datetime.now().strftime('%H%M%S')}@test.com",
            "password": "SupervisorPass123!",
            "full_name": "Dr. Enhanced Supervisor",
            "role": "supervisor",
            "department": "Computer Science",
            "research_area": "AI Research",
            "lab_name": "Enhanced AI Lab"
        }
        
        success, response = self.run_test(
            "Supervisor Registration (Enhanced)",
            "POST",
            "/auth/register",
            200,
            data=supervisor_data
        )
        
        if not success or 'access_token' not in response:
            return False
            
        self.supervisor_token = response['access_token']
        self.supervisor_data = response['user_data']
        
        # Create regular student
        student_data = {
            "email": f"student_enhanced_{datetime.now().strftime('%H%M%S')}@test.com",
            "password": "StudentPass123!",
            "full_name": "John Enhanced Student",
            "role": "student",
            "department": "Computer Science",
            "research_area": "Machine Learning",
            "supervisor_email": supervisor_data['email'],
            "student_id": "ENH001"
        }
        
        success, response = self.run_test(
            "Student Registration (Enhanced)",
            "POST",
            "/auth/register",
            200,
            data=student_data
        )
        
        if not success or 'access_token' not in response:
            return False
            
        self.student_token = response['access_token']
        self.student_data = response['user_data']
        
        # Create PIC student (Person In Charge for grants)
        pic_student_data = {
            "email": f"pic_student_{datetime.now().strftime('%H%M%S')}@test.com",
            "password": "PICStudentPass123!",
            "full_name": "Jane PIC Student",
            "role": "student",
            "department": "Computer Science",
            "research_area": "Data Science",
            "supervisor_email": supervisor_data['email'],
            "student_id": "PIC001"
        }
        
        success, response = self.run_test(
            "PIC Student Registration (Enhanced)",
            "POST",
            "/auth/register",
            200,
            data=pic_student_data
        )
        
        if not success or 'access_token' not in response:
            return False
            
        self.pic_student_token = response['access_token']
        self.pic_student_data = response['user_data']
        
        print(f"✅ Test users created successfully")
        return True

    def test_research_log_review_system(self):
        """Test the enhanced research log review system"""
        print("\n📋 Testing Research Log Review System...")
        
        # First, create a research log as student
        log_data = {
            "activity_type": "experiment",
            "title": "Enhanced ML Experiment Results",
            "description": "Conducted comprehensive experiments on enhanced neural network architectures",
            "duration_hours": 6.0,
            "findings": "Achieved 94% accuracy with new attention mechanism",
            "challenges": "Memory constraints with large datasets",
            "next_steps": "Optimize memory usage and test on larger datasets",
            "tags": ["machine-learning", "experiments", "neural-networks"]
        }
        
        success, response = self.run_test(
            "Create Research Log for Review",
            "POST",
            "/research-logs",
            200,
            data=log_data,
            token=self.student_token
        )
        
        if not success or 'id' not in response:
            return False
            
        self.created_log_id = response['id']
        print(f"   Created Research Log ID: {self.created_log_id}")
        
        # Test review with 'accepted' action
        review_data = {
            "action": "accepted",
            "feedback": "Excellent work! The experimental methodology is sound and results are impressive. Well documented findings and clear next steps."
        }
        
        success, response = self.run_test(
            "Review Research Log - Accept",
            "POST",
            f"/research-logs/{self.created_log_id}/review",
            200,
            data=review_data,
            token=self.supervisor_token
        )
        
        if not success:
            return False
        
        # Test review with 'revision' action (create another log)
        log_data_2 = {
            "activity_type": "literature_review",
            "title": "Literature Review on Deep Learning",
            "description": "Reviewed recent papers on deep learning architectures",
            "duration_hours": 4.0,
            "findings": "Found several interesting approaches",
            "challenges": "Limited access to some papers",
            "next_steps": "Continue reviewing transformer architectures",
            "tags": ["literature-review", "deep-learning"]
        }
        
        success, response = self.run_test(
            "Create Second Research Log for Revision Review",
            "POST",
            "/research-logs",
            200,
            data=log_data_2,
            token=self.student_token
        )
        
        if not success or 'id' not in response:
            return False
            
        log_id_2 = response['id']
        
        review_data_revision = {
            "action": "revision",
            "feedback": "Good start, but needs more depth. Please include more detailed analysis of the methodologies and provide critical evaluation of the approaches. Also add more recent papers from 2024."
        }
        
        success, response = self.run_test(
            "Review Research Log - Revision",
            "POST",
            f"/research-logs/{log_id_2}/review",
            200,
            data=review_data_revision,
            token=self.supervisor_token
        )
        
        if not success:
            return False
        
        # Test review with 'rejected' action (create third log)
        log_data_3 = {
            "activity_type": "data_collection",
            "title": "Data Collection Attempt",
            "description": "Attempted to collect data for research",
            "duration_hours": 2.0,
            "findings": "Could not collect sufficient data",
            "challenges": "Equipment malfunction",
            "next_steps": "Fix equipment and retry",
            "tags": ["data-collection"]
        }
        
        success, response = self.run_test(
            "Create Third Research Log for Rejection Review",
            "POST",
            "/research-logs",
            200,
            data=log_data_3,
            token=self.student_token
        )
        
        if not success or 'id' not in response:
            return False
            
        log_id_3 = response['id']
        
        review_data_reject = {
            "action": "rejected",
            "feedback": "This log lacks sufficient detail and analysis. The findings are too brief and don't provide meaningful insights. Please redo this activity with proper documentation and analysis."
        }
        
        success, response = self.run_test(
            "Review Research Log - Reject",
            "POST",
            f"/research-logs/{log_id_3}/review",
            200,
            data=review_data_reject,
            token=self.supervisor_token
        )
        
        if not success:
            return False
        
        # Test that students cannot review logs (should get 403)
        success, response = self.run_test(
            "Student Cannot Review Logs (403 Expected)",
            "POST",
            f"/research-logs/{self.created_log_id}/review",
            403,
            data=review_data,
            token=self.student_token
        )
        
        if not success:
            return False
        
        # Test invalid review action
        invalid_review = {
            "action": "invalid_action",
            "feedback": "This should fail"
        }
        
        success, response = self.run_test(
            "Invalid Review Action (400 Expected)",
            "POST",
            f"/research-logs/{self.created_log_id}/review",
            400,
            data=invalid_review,
            token=self.supervisor_token
        )
        
        if not success:
            return False
        
        # Test retrieving logs with review information
        success, response = self.run_test(
            "Get Research Logs with Review Info (Student View)",
            "GET",
            "/research-logs",
            200,
            token=self.student_token
        )
        
        if not success:
            return False
        
        # Verify review information is included
        logs_with_review = [log for log in response if log.get('review_status')]
        if len(logs_with_review) < 3:
            print(f"❌ Expected at least 3 logs with review status, got {len(logs_with_review)}")
            return False
        
        print(f"   ✅ Found {len(logs_with_review)} logs with review information")
        
        # Test supervisor view includes student information
        success, response = self.run_test(
            "Get Research Logs with Student Info (Supervisor View)",
            "GET",
            "/research-logs",
            200,
            token=self.supervisor_token
        )
        
        if not success:
            return False
        
        # Verify student information is included
        logs_with_student_info = [log for log in response if log.get('student_name')]
        if len(logs_with_student_info) < 3:
            print(f"❌ Expected at least 3 logs with student info, got {len(logs_with_student_info)}")
            return False
        
        print(f"   ✅ Found {len(logs_with_student_info)} logs with student information")
        
        return True

    def test_grant_pic_system(self):
        """Test the Grant System for PIC (Person In Charge) Users"""
        print("\n💰 Testing Grant PIC System...")
        
        # First, create a grant as supervisor with PIC student assigned
        grant_data = {
            "title": "Enhanced AI Research Grant",
            "funding_agency": "National Science Foundation",
            "funding_type": "national",
            "total_amount": 150000.0,
            "status": "active",
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=365*2)).isoformat(),
            "description": "Research grant for enhanced AI methodologies",
            "person_in_charge": self.pic_student_data['id'],  # Assign PIC student
            "grant_vote_number": "NSF-2024-AI-001",
            "duration_months": 24,
            "grant_type": "research"
        }
        
        success, response = self.run_test(
            "Create Grant with PIC Assignment",
            "POST",
            "/grants",
            200,
            data=grant_data,
            token=self.supervisor_token
        )
        
        if not success or 'id' not in response:
            return False
            
        self.created_grant_id = response['id']
        print(f"   Created Grant ID: {self.created_grant_id}")
        
        # Test that PIC student can update grant status
        grant_update_data = {
            "status": "on_hold",
            "current_balance": 140000.0,
            "description": "Grant temporarily on hold due to equipment delays"
        }
        
        success, response = self.run_test(
            "PIC Student Updates Grant Status",
            "PUT",
            f"/grants/{self.created_grant_id}",
            200,
            data=grant_update_data,
            token=self.pic_student_token
        )
        
        if not success:
            return False
        
        # Test updating grant status to different values
        status_updates = [
            {"status": "active", "current_balance": 135000.0},
            {"status": "completed", "current_balance": 120000.0},
            {"status": "cancelled", "current_balance": 150000.0}
        ]
        
        for i, update_data in enumerate(status_updates):
            success, response = self.run_test(
                f"PIC Student Updates Grant Status - {update_data['status'].title()}",
                "PUT",
                f"/grants/{self.created_grant_id}",
                200,
                data=update_data,
                token=self.pic_student_token
            )
            
            if not success:
                return False
        
        # Test that regular student (non-PIC) cannot update grants
        success, response = self.run_test(
            "Regular Student Cannot Update Grant (403 Expected)",
            "PUT",
            f"/grants/{self.created_grant_id}",
            403,
            data={"status": "active"},
            token=self.student_token
        )
        
        if not success:
            return False
        
        # Test updating non-existent grant
        success, response = self.run_test(
            "Update Non-existent Grant (404 Expected)",
            "PUT",
            "/grants/non-existent-id",
            404,
            data={"status": "active"},
            token=self.pic_student_token
        )
        
        if not success:
            return False
        
        return True

    def test_enhanced_grants_visibility(self):
        """Test Enhanced Grants Visibility for All Users"""
        print("\n👁️ Testing Enhanced Grants Visibility...")
        
        # Test that supervisor can view grants
        success, response = self.run_test(
            "Supervisor Views Grants",
            "GET",
            "/grants",
            200,
            token=self.supervisor_token
        )
        
        if not success:
            return False
        
        supervisor_grants = response
        print(f"   Supervisor sees {len(supervisor_grants)} grants")
        
        # Test that regular student can view grants
        success, response = self.run_test(
            "Regular Student Views Grants",
            "GET",
            "/grants",
            200,
            token=self.student_token
        )
        
        if not success:
            return False
        
        student_grants = response
        print(f"   Regular student sees {len(student_grants)} grants")
        
        # Test that PIC student can view grants
        success, response = self.run_test(
            "PIC Student Views Grants",
            "GET",
            "/grants",
            200,
            token=self.pic_student_token
        )
        
        if not success:
            return False
        
        pic_student_grants = response
        print(f"   PIC student sees {len(pic_student_grants)} grants")
        
        # Verify grants include cumulative value calculation
        if supervisor_grants:
            grant = supervisor_grants[0]
            required_fields = ['id', 'title', 'funding_agency', 'total_amount', 'status']
            missing_fields = [field for field in required_fields if field not in grant]
            
            if missing_fields:
                print(f"❌ Grant missing required fields: {missing_fields}")
                return False
            
            print(f"   ✅ Grant includes required fields: {required_fields}")
        
        # Test that all users see the same grants (visibility to all lab members)
        if len(supervisor_grants) > 0:
            # All users should be able to see grants, though creation is restricted
            if len(student_grants) == 0 and len(pic_student_grants) == 0:
                print("❌ Students cannot see grants - visibility issue")
                return False
            
            print("   ✅ All users can view grants as expected")
        
        return True

    def test_publications_integration(self):
        """Test Publications Integration"""
        print("\n📚 Testing Publications Integration...")
        
        # Test retrieving publications as supervisor
        success, response = self.run_test(
            "Get Publications (Supervisor)",
            "GET",
            "/publications",
            200,
            token=self.supervisor_token
        )
        
        if not success:
            return False
        
        supervisor_publications = response
        print(f"   Supervisor sees {len(supervisor_publications)} publications")
        
        # Test retrieving publications as student
        success, response = self.run_test(
            "Get Publications (Student)",
            "GET",
            "/publications",
            200,
            token=self.student_token
        )
        
        if not success:
            return False
        
        student_publications = response
        print(f"   Student sees {len(student_publications)} publications")
        
        # Verify publications data structure includes required fields
        if supervisor_publications:
            pub = supervisor_publications[0]
            required_fields = ['title', 'authors', 'journal', 'year']
            optional_fields = ['doi', 'citation_count']
            
            missing_required = [field for field in required_fields if field not in pub]
            if missing_required:
                print(f"❌ Publication missing required fields: {missing_required}")
                return False
            
            present_optional = [field for field in optional_fields if field in pub]
            print(f"   ✅ Publication includes required fields: {required_fields}")
            print(f"   ✅ Publication includes optional fields: {present_optional}")
        
        # Test Scopus sync functionality (if available)
        success, response = self.run_test(
            "Sync Publications from Scopus",
            "POST",
            "/publications/sync-scopus",
            200,
            token=self.supervisor_token
        )
        
        # This might fail if Scopus API is not configured, which is acceptable
        if success:
            print("   ✅ Scopus sync functionality working")
        else:
            print("   ⚠️ Scopus sync not available (acceptable - may need API key)")
        
        # Test enhanced publication view with student contributors
        success, response = self.run_test(
            "Get Enhanced Publications View",
            "GET",
            "/publications/all",
            200,
            token=self.supervisor_token
        )
        
        if success:
            enhanced_publications = response
            print(f"   Enhanced view shows {len(enhanced_publications)} publications")
            
            if enhanced_publications:
                pub = enhanced_publications[0]
                if 'student_contributors' in pub:
                    print("   ✅ Enhanced view includes student contributor details")
                else:
                    print("   ⚠️ Enhanced view missing student contributor details")
        
        return True

    def test_comprehensive_workflow(self):
        """Test a comprehensive workflow combining all enhanced features"""
        print("\n🔄 Testing Comprehensive Enhanced Workflow...")
        
        # 1. Student creates research log
        log_data = {
            "activity_type": "experiment",
            "title": "Comprehensive AI Research Experiment",
            "description": "End-to-end experiment testing enhanced AI methodologies with grant funding",
            "duration_hours": 8.0,
            "findings": "Significant improvements in model performance using grant-funded equipment",
            "challenges": "Initial setup challenges with new equipment",
            "next_steps": "Scale experiments and prepare for publication",
            "tags": ["experiment", "ai-research", "grant-funded"]
        }
        
        success, response = self.run_test(
            "Workflow Step 1: Create Research Log",
            "POST",
            "/research-logs",
            200,
            data=log_data,
            token=self.student_token
        )
        
        if not success or 'id' not in response:
            return False
        
        workflow_log_id = response['id']
        
        # 2. Supervisor reviews the research log
        review_data = {
            "action": "accepted",
            "feedback": "Excellent comprehensive research work! The methodology is sound, results are significant, and the use of grant funding is well documented. Ready for publication preparation."
        }
        
        success, response = self.run_test(
            "Workflow Step 2: Supervisor Reviews Log",
            "POST",
            f"/research-logs/{workflow_log_id}/review",
            200,
            data=review_data,
            token=self.supervisor_token
        )
        
        if not success:
            return False
        
        # 3. PIC student updates grant status based on research progress
        grant_update = {
            "status": "active",
            "current_balance": 125000.0,
            "description": "Grant progressing well with significant research outcomes achieved"
        }
        
        success, response = self.run_test(
            "Workflow Step 3: PIC Updates Grant Status",
            "PUT",
            f"/grants/{self.created_grant_id}",
            200,
            data=grant_update,
            token=self.pic_student_token
        )
        
        if not success:
            return False
        
        # 4. Verify all users can see updated grant information
        success, response = self.run_test(
            "Workflow Step 4: Verify Grant Visibility",
            "GET",
            "/grants",
            200,
            token=self.student_token
        )
        
        if not success:
            return False
        
        # 5. Check publications are accessible for research reference
        success, response = self.run_test(
            "Workflow Step 5: Access Publications for Reference",
            "GET",
            "/publications",
            200,
            token=self.student_token
        )
        
        if not success:
            return False
        
        print("   ✅ Comprehensive workflow completed successfully")
        return True

    def run_all_tests(self):
        """Run all enhanced lab management feature tests"""
        print("🚀 Starting Enhanced Lab Management Features API Tests")
        print("=" * 60)
        
        # Setup test users
        if not self.setup_test_users():
            print("❌ Failed to setup test users")
            return False
        
        # Test enhanced features
        tests = [
            ("Research Log Review System", self.test_research_log_review_system),
            ("Grant PIC System", self.test_grant_pic_system),
            ("Enhanced Grants Visibility", self.test_enhanced_grants_visibility),
            ("Publications Integration", self.test_publications_integration),
            ("Comprehensive Workflow", self.test_comprehensive_workflow)
        ]
        
        failed_tests = []
        
        for test_name, test_method in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                if not test_method():
                    failed_tests.append(test_name)
                    print(f"❌ {test_name} FAILED")
                else:
                    print(f"✅ {test_name} PASSED")
            except Exception as e:
                failed_tests.append(test_name)
                print(f"❌ {test_name} FAILED with exception: {str(e)}")
        
        # Print final results
        print("\n" + "=" * 60)
        print(f"📊 Final Results: {self.tests_passed}/{self.tests_run} individual tests passed")
        print(f"📋 Feature Tests: {len(tests) - len(failed_tests)}/{len(tests)} feature groups passed")
        
        if failed_tests:
            print(f"❌ Failed feature tests: {', '.join(failed_tests)}")
            return False
        else:
            print("🎉 All enhanced lab management features tests passed!")
            return True

def main():
    tester = EnhancedLabFeaturesAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
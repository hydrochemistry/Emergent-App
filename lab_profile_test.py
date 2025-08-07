import requests
import sys
import json
from datetime import datetime

class LabProfileTester:
    def __init__(self, base_url="https://4eb13147-e91e-42cc-a844-96b5f230bc59.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.supervisor_token = None
        self.student_token = None
        self.supervisor_data = None
        self.student_data = None
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
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)}")
                    return success, response_data
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
        """Create test users for testing"""
        print("🔧 Setting up test users...")
        
        # Create supervisor
        supervisor_data = {
            "email": f"supervisor_lab_{datetime.now().strftime('%H%M%S')}@test.com",
            "password": "SupervisorPass123!",
            "full_name": "Dr. Lab Manager",
            "role": "supervisor",
            "department": "Computer Science",
            "research_area": "Machine Learning",
            "lab_name": "AI Research Lab"
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
            
        # Create student
        student_data = {
            "email": f"student_profile_{datetime.now().strftime('%H%M%S')}@test.com",
            "password": "StudentPass123!",
            "full_name": "John Test Student",
            "role": "student",
            "department": "Computer Science",
            "research_area": "Deep Learning",
            "supervisor_email": supervisor_data['email'],
            "student_id": "CS2024001",
            "contact_number": "123-456-7890",
            "nationality": "Malaysian",
            "citizenship": "Malaysian",
            "program_type": "phd_research",
            "field_of_study": "Artificial Intelligence"
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

    def test_lab_settings_creation(self):
        """Test creating/updating lab settings"""
        if not self.supervisor_token:
            print("❌ Cannot test lab settings - no supervisor token")
            return False
            
        lab_data = {
            "lab_name": "Test Research Lab",
            "description": "Test lab description for comprehensive research",
            "contact_email": "test@lab.edu",
            "website": "https://testlab.edu",
            "address": "123 Research Street, University Campus"
        }
        
        success, response = self.run_test(
            "Create/Update Lab Settings",
            "POST",
            "/lab/settings",
            200,
            data=lab_data,
            token=self.supervisor_token
        )
        
        if success:
            print(f"   Lab settings created/updated successfully")
            # Verify the data was saved correctly
            if 'lab_name' in response and response['lab_name'] == lab_data['lab_name']:
                print(f"   ✅ Lab name saved correctly: {response['lab_name']}")
            else:
                print(f"   ❌ Lab name not saved correctly")
                return False
                
            if 'description' in response and response['description'] == lab_data['description']:
                print(f"   ✅ Description saved correctly")
            else:
                print(f"   ❌ Description not saved correctly")
                return False
                
            return True
        return False

    def test_lab_settings_retrieval(self):
        """Test retrieving lab settings"""
        if not self.supervisor_token:
            print("❌ Cannot test lab settings retrieval - no supervisor token")
            return False
            
        success, response = self.run_test(
            "Get Lab Settings",
            "GET",
            "/lab/settings",
            200,
            token=self.supervisor_token
        )
        
        if success:
            print(f"   Lab settings retrieved successfully")
            # Check if the previously saved data is present
            if response and 'lab_name' in response:
                print(f"   ✅ Lab name retrieved: {response['lab_name']}")
                if response['lab_name'] == "Test Research Lab":
                    print(f"   ✅ Lab name matches saved data")
                    return True
                else:
                    print(f"   ❌ Lab name doesn't match saved data")
                    return False
            else:
                print(f"   ❌ No lab settings found or missing lab_name")
                return False
        return False

    def test_profile_update(self):
        """Test updating user profile"""
        if not self.student_token:
            print("❌ Cannot test profile update - no student token")
            return False
            
        profile_data = {
            "full_name": "Updated Student Name",
            "contact_number": "987-654-3210",
            "department": "Updated Computer Science Department",
            "research_area": "Updated Research Area - Neural Networks",
            "nationality": "Updated Nationality",
            "citizenship": "Updated Citizenship",
            "field_of_study": "Updated Field - Machine Learning"
        }
        
        success, response = self.run_test(
            "Update User Profile",
            "PUT",
            "/users/profile",
            200,
            data=profile_data,
            token=self.student_token
        )
        
        if success:
            print(f"   Profile updated successfully")
            return True
        return False

    def test_profile_retrieval(self):
        """Test retrieving updated profile"""
        if not self.student_token:
            print("❌ Cannot test profile retrieval - no student token")
            return False
            
        success, response = self.run_test(
            "Get User Profile",
            "GET",
            "/users/profile",
            200,
            token=self.student_token
        )
        
        if success:
            print(f"   Profile retrieved successfully")
            # Check if the updated data is present
            expected_updates = {
                "full_name": "Updated Student Name",
                "contact_number": "987-654-3210",
                "department": "Updated Computer Science Department",
                "research_area": "Updated Research Area - Neural Networks"
            }
            
            all_updates_saved = True
            for field, expected_value in expected_updates.items():
                if field in response and response[field] == expected_value:
                    print(f"   ✅ {field} updated correctly: {response[field]}")
                else:
                    print(f"   ❌ {field} not updated correctly. Expected: {expected_value}, Got: {response.get(field, 'NOT FOUND')}")
                    all_updates_saved = False
            
            return all_updates_saved
        return False

    def test_data_persistence(self):
        """Test that data persists across multiple requests"""
        print("\n🔄 Testing data persistence...")
        
        # Test lab settings persistence
        if not self.supervisor_token:
            print("❌ Cannot test lab settings persistence - no supervisor token")
            return False
            
        success, response = self.run_test(
            "Verify Lab Settings Persistence",
            "GET",
            "/lab/settings",
            200,
            token=self.supervisor_token
        )
        
        lab_persistent = False
        if success and response and 'lab_name' in response:
            if response['lab_name'] == "Test Research Lab":
                print(f"   ✅ Lab settings persisted correctly")
                lab_persistent = True
            else:
                print(f"   ❌ Lab settings not persisted correctly")
        
        # Test profile persistence
        if not self.student_token:
            print("❌ Cannot test profile persistence - no student token")
            return False
            
        success, response = self.run_test(
            "Verify Profile Persistence",
            "GET",
            "/users/profile",
            200,
            token=self.student_token
        )
        
        profile_persistent = False
        if success and response and 'full_name' in response:
            if response['full_name'] == "Updated Student Name":
                print(f"   ✅ Profile updates persisted correctly")
                profile_persistent = True
            else:
                print(f"   ❌ Profile updates not persisted correctly")
        
        return lab_persistent and profile_persistent

def main():
    print("🚀 Starting Lab Settings & Profile Update Tests")
    print("=" * 60)
    
    tester = LabProfileTester()
    
    # Setup test users
    if not tester.setup_test_users():
        print("❌ Failed to setup test users, stopping tests")
        return 1
    
    print("\n" + "=" * 60)
    print("🧪 TESTING LAB SETTINGS FUNCTIONALITY")
    print("=" * 60)
    
    # Test lab settings
    if not tester.test_lab_settings_creation():
        print("❌ Lab settings creation failed")
        return 1
        
    if not tester.test_lab_settings_retrieval():
        print("❌ Lab settings retrieval failed")
        return 1
    
    print("\n" + "=" * 60)
    print("👤 TESTING PROFILE UPDATE FUNCTIONALITY")
    print("=" * 60)
    
    # Test profile updates
    if not tester.test_profile_update():
        print("❌ Profile update failed")
        return 1
        
    if not tester.test_profile_retrieval():
        print("❌ Profile retrieval failed")
        return 1
    
    print("\n" + "=" * 60)
    print("💾 TESTING DATA PERSISTENCE")
    print("=" * 60)
    
    # Test data persistence
    if not tester.test_data_persistence():
        print("❌ Data persistence test failed")
        return 1
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All lab settings and profile update tests passed!")
        print("\n✅ CONCLUSION: Both lab settings and profile update functionality are working correctly.")
        print("   - Lab settings can be created/updated and retrieved successfully")
        print("   - Profile updates are saved and persisted correctly")
        print("   - Data persistence is working as expected")
        return 0
    else:
        print(f"❌ {tester.tests_run - tester.tests_passed} tests failed")
        print("\n❌ CONCLUSION: Issues found with lab settings or profile update functionality.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
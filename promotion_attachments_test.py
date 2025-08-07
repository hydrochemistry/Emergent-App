import requests
import sys
import json
import io
import os
from datetime import datetime, timedelta

class PromotionAttachmentsAPITester:
    def __init__(self, base_url="https://4eb13147-e91e-42cc-a844-96b5f230bc59.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.supervisor_token = None
        self.student_token = None
        self.supervisor_data = None
        self.student_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_log_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None, files=None):
        """Run a single API test"""
        url = f"{self.api_url}{endpoint}"
        headers = {}
        if token:
            headers['Authorization'] = f'Bearer {token}'

        # Don't set Content-Type for file uploads
        if not files:
            headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    response = requests.post(url, data=data, files=files, headers=headers)
                else:
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
            "email": f"supervisor_{datetime.now().strftime('%H%M%S')}@research.edu",
            "password": "SupervisorPass123!",
            "full_name": "Dr. Sarah Wilson",
            "role": "supervisor",
            "department": "Computer Science",
            "research_area": "Artificial Intelligence",
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
            return True
        return False

    def test_student_registration(self):
        """Test student registration with supervisor connection"""
        if not self.supervisor_data:
            print("❌ Cannot test student registration - no supervisor data")
            return False
            
        student_data = {
            "email": f"student_{datetime.now().strftime('%H%M%S')}@research.edu",
            "password": "StudentPass123!",
            "full_name": "Alex Johnson",
            "role": "student",
            "student_id": f"STU{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "department": "Computer Science",
            "program_type": "phd_research",
            "field_of_study": "Machine Learning",
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

    def test_user_promotion_lab_manager(self):
        """Test promoting student to lab_manager"""
        if not self.supervisor_token or not self.student_data:
            print("❌ Cannot test promotion - missing tokens or student data")
            return False
            
        promotion_data = {
            "new_role": "lab_manager"
        }
        
        success, response = self.run_test(
            "Promote Student to Lab Manager",
            "PUT",
            f"/users/{self.student_data['id']}/promote",
            200,
            data=promotion_data,
            token=self.supervisor_token
        )
        
        return success

    def test_user_promotion_supervisor(self):
        """Test promoting student to supervisor"""
        if not self.supervisor_token or not self.student_data:
            print("❌ Cannot test promotion - missing tokens or student data")
            return False
            
        promotion_data = {
            "new_role": "supervisor"
        }
        
        success, response = self.run_test(
            "Promote Student to Supervisor",
            "PUT",
            f"/users/{self.student_data['id']}/promote",
            200,
            data=promotion_data,
            token=self.supervisor_token
        )
        
        return success

    def test_user_promotion_admin_should_fail(self):
        """Test that supervisor cannot promote to admin (should fail)"""
        if not self.supervisor_token or not self.student_data:
            print("❌ Cannot test promotion - missing tokens or student data")
            return False
            
        promotion_data = {
            "new_role": "admin"
        }
        
        success, response = self.run_test(
            "Promote Student to Admin (Should Fail)",
            "PUT",
            f"/users/{self.student_data['id']}/promote",
            403,  # Should fail with 403 Forbidden
            data=promotion_data,
            token=self.supervisor_token
        )
        
        return success

    def test_invalid_role_promotion(self):
        """Test promotion with invalid role"""
        if not self.supervisor_token or not self.student_data:
            print("❌ Cannot test promotion - missing tokens or student data")
            return False
            
        promotion_data = {
            "new_role": "invalid_role"
        }
        
        success, response = self.run_test(
            "Promote with Invalid Role (Should Fail)",
            "PUT",
            f"/users/{self.student_data['id']}/promote",
            400,  # Should fail with 400 Bad Request
            data=promotion_data,
            token=self.supervisor_token
        )
        
        return success

    def test_unauthorized_promotion(self):
        """Test that student cannot promote users"""
        if not self.student_token or not self.student_data:
            print("❌ Cannot test unauthorized promotion - missing tokens")
            return False
            
        promotion_data = {
            "new_role": "lab_manager"
        }
        
        success, response = self.run_test(
            "Unauthorized Promotion (Student)",
            "PUT",
            f"/users/{self.student_data['id']}/promote",
            403,  # Should fail with 403 Forbidden
            data=promotion_data,
            token=self.student_token
        )
        
        return success

    def test_create_research_log_for_attachments(self):
        """Create a research log to test attachments"""
        if not self.student_token:
            print("❌ Cannot create research log - missing student token")
            return False
            
        log_data = {
            "activity_type": "experiment",
            "title": "Neural Network Training Experiment",
            "description": "Testing different architectures for image classification",
            "duration_hours": 6.0,
            "findings": "ResNet-50 performed best with 94% accuracy",
            "challenges": "GPU memory limitations with larger batch sizes",
            "next_steps": "Try data augmentation techniques",
            "tags": ["experiment", "neural networks", "image classification"]
        }
        
        success, response = self.run_test(
            "Create Research Log for Attachments",
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

    def test_upload_image_attachment(self):
        """Test uploading an image attachment to research log"""
        if not self.student_token or not self.created_log_id:
            print("❌ Cannot test image upload - missing token or log ID")
            return False

        # Create a small test image file (PNG format)
        image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x12IDATx\x9cc```bPPP\x00\x02D\x00\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
        
        files = {
            'file': ('test_image.png', io.BytesIO(image_content), 'image/png')
        }
        
        data = {
            'research_log_id': self.created_log_id
        }
        
        success, response = self.run_test(
            "Upload Image Attachment",
            "POST",
            "/research-logs/attachments",
            200,
            data=data,
            token=self.student_token,
            files=files
        )
        
        return success

    def test_upload_pdf_attachment(self):
        """Test uploading a PDF attachment to research log"""
        if not self.student_token or not self.created_log_id:
            print("❌ Cannot test PDF upload - missing token or log ID")
            return False

        # Create a minimal PDF content
        pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n174\n%%EOF'
        
        files = {
            'file': ('research_report.pdf', io.BytesIO(pdf_content), 'application/pdf')
        }
        
        data = {
            'research_log_id': self.created_log_id
        }
        
        success, response = self.run_test(
            "Upload PDF Attachment",
            "POST",
            "/research-logs/attachments",
            200,
            data=data,
            token=self.student_token,
            files=files
        )
        
        return success

    def test_upload_large_file_should_fail(self):
        """Test that files larger than 10MB are rejected"""
        if not self.student_token or not self.created_log_id:
            print("❌ Cannot test large file upload - missing token or log ID")
            return False

        # Create a file larger than 10MB (10MB + 1KB)
        large_content = b'x' * (10 * 1024 * 1024 + 1024)
        
        files = {
            'file': ('large_file.txt', io.BytesIO(large_content), 'text/plain')
        }
        
        data = {
            'research_log_id': self.created_log_id
        }
        
        success, response = self.run_test(
            "Upload Large File (Should Fail)",
            "POST",
            "/research-logs/attachments",
            400,  # Should fail with 400 Bad Request
            data=data,
            token=self.student_token,
            files=files
        )
        
        return success

    def test_upload_invalid_file_type(self):
        """Test uploading an executable file (should be allowed but noted)"""
        if not self.student_token or not self.created_log_id:
            print("❌ Cannot test invalid file type - missing token or log ID")
            return False

        # Create a small executable-like file
        exe_content = b'MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00'
        
        files = {
            'file': ('test_program.exe', io.BytesIO(exe_content), 'application/octet-stream')
        }
        
        data = {
            'research_log_id': self.created_log_id
        }
        
        success, response = self.run_test(
            "Upload Executable File",
            "POST",
            "/research-logs/attachments",
            200,  # Should succeed (no file type restrictions in current implementation)
            data=data,
            token=self.student_token,
            files=files
        )
        
        return success

    def test_upload_attachment_invalid_log(self):
        """Test uploading attachment to non-existent research log"""
        if not self.student_token:
            print("❌ Cannot test invalid log upload - missing token")
            return False

        image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde'
        
        files = {
            'file': ('test_image.png', io.BytesIO(image_content), 'image/png')
        }
        
        data = {
            'research_log_id': 'invalid-log-id-12345'
        }
        
        success, response = self.run_test(
            "Upload to Invalid Research Log (Should Fail)",
            "POST",
            "/research-logs/attachments",
            404,  # Should fail with 404 Not Found
            data=data,
            token=self.student_token,
            files=files
        )
        
        return success

    def test_upload_attachment_unauthorized(self):
        """Test uploading attachment without authentication"""
        if not self.created_log_id:
            print("❌ Cannot test unauthorized upload - missing log ID")
            return False

        image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde'
        
        files = {
            'file': ('test_image.png', io.BytesIO(image_content), 'image/png')
        }
        
        data = {
            'research_log_id': self.created_log_id
        }
        
        success, response = self.run_test(
            "Upload Without Authentication (Should Fail)",
            "POST",
            "/research-logs/attachments",
            403,  # Should fail with 403 Forbidden
            data=data,
            files=files
        )
        
        return success

def main():
    print("🚀 Starting User Promotion & Research Log Attachments Tests")
    print("=" * 60)
    
    tester = PromotionAttachmentsAPITester()
    
    # Setup: Register supervisor and student
    print("\n📋 SETUP PHASE")
    if not tester.test_supervisor_registration():
        print("❌ Supervisor registration failed, stopping tests")
        return 1
        
    if not tester.test_student_registration():
        print("❌ Student registration failed, stopping tests")
        return 1

    # Test User Promotion Functionality
    print("\n👑 USER PROMOTION TESTS")
    
    if not tester.test_user_promotion_lab_manager():
        print("❌ Lab manager promotion failed")
        return 1
        
    if not tester.test_user_promotion_supervisor():
        print("❌ Supervisor promotion failed")
        return 1
        
    if not tester.test_user_promotion_admin_should_fail():
        print("❌ Admin promotion restriction test failed")
        return 1
        
    if not tester.test_invalid_role_promotion():
        print("❌ Invalid role promotion test failed")
        return 1
        
    if not tester.test_unauthorized_promotion():
        print("❌ Unauthorized promotion test failed")
        return 1

    # Test Research Log Attachments
    print("\n📎 RESEARCH LOG ATTACHMENTS TESTS")
    
    if not tester.test_create_research_log_for_attachments():
        print("❌ Research log creation failed")
        return 1
        
    if not tester.test_upload_image_attachment():
        print("❌ Image attachment upload failed")
        return 1
        
    if not tester.test_upload_pdf_attachment():
        print("❌ PDF attachment upload failed")
        return 1
        
    if not tester.test_upload_large_file_should_fail():
        print("❌ Large file rejection test failed")
        return 1
        
    if not tester.test_upload_invalid_file_type():
        print("❌ Invalid file type test failed")
        return 1
        
    if not tester.test_upload_attachment_invalid_log():
        print("❌ Invalid log attachment test failed")
        return 1
        
    if not tester.test_upload_attachment_unauthorized():
        print("❌ Unauthorized attachment test failed")
        return 1
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All User Promotion & Research Log Attachments tests passed!")
        print("\n✅ KEY FINDINGS:")
        print("   • User promotion endpoint working correctly")
        print("   • Permission controls functioning (supervisors cannot promote to admin)")
        print("   • Research log attachments accepting various file types")
        print("   • File size validation working (>10MB rejected)")
        print("   • Proper authentication and authorization checks in place")
        return 0
    else:
        print(f"❌ {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
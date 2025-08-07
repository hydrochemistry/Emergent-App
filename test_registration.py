import requests
import json

# Test registration endpoint directly
url = "https://4eb13147-e91e-42cc-a844-96b5f230bc59.preview.emergentagent.com/api/auth/register"

# Simple student registration data
student_data = {
    "email": "teststudent123@example.com",
    "password": "testpassword123",
    "full_name": "Test Student",
    "role": "student",
    "student_id": "STU123",
    "contact_number": "+60123456789",
    "department": "Computer Science",
    "research_area": "Machine Learning"
}

print("Testing student registration...")
print(f"URL: {url}")
print(f"Data: {json.dumps(student_data, indent=2)}")

try:
    response = requests.post(url, json=student_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        print("✅ SUCCESS!")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"❌ FAILED!")
        try:
            error_data = response.json()
            print(f"Error Response: {json.dumps(error_data, indent=2)}")
        except:
            print(f"Error Text: {response.text}")
            
except Exception as e:
    print(f"❌ Exception occurred: {e}")

# Test with supervisor data
print("\n" + "="*50)
print("Testing supervisor registration...")

supervisor_data = {
    "email": "testsupervisor123@example.com", 
    "password": "testpassword123",
    "full_name": "Test Supervisor",
    "role": "supervisor",
    "department": "Computer Science",
    "research_area": "Artificial Intelligence",
    "lab_name": "AI Research Lab"
}

try:
    response = requests.post(url, json=supervisor_data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS!")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"❌ FAILED!")
        try:
            error_data = response.json()
            print(f"Error Response: {json.dumps(error_data, indent=2)}")
        except:
            print(f"Error Text: {response.text}")
            
except Exception as e:
    print(f"❌ Exception occurred: {e}")
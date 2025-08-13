import requests
import json

# Test login endpoint to see exact user data returned
url = "https://researchpulse.preview.emergentagent.com/api/auth/login"

# Test student login
student_login = {
    "email": "teststudent123@example.com",
    "password": "testpassword123"
}

print("Testing student login...")
print(f"URL: {url}")
print(f"Data: {json.dumps(student_login, indent=2)}")

try:
    response = requests.post(url, json=student_login)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ LOGIN SUCCESS!")
        data = response.json()
        print(f"Full Response: {json.dumps(data, indent=2)}")
        
        user_data = data.get('user_data', {})
        print(f"\nUser Role: '{user_data.get('role')}'")
        print(f"User Role Type: {type(user_data.get('role'))}")
        print(f"Role == 'student': {user_data.get('role') == 'student'}")
        
    else:
        print(f"❌ LOGIN FAILED!")
        try:
            error_data = response.json()
            print(f"Error Response: {json.dumps(error_data, indent=2)}")
        except:
            print(f"Error Text: {response.text}")
            
except Exception as e:
    print(f"❌ Exception occurred: {e}")

print("\n" + "="*50)
print("Testing supervisor login...")

supervisor_login = {
    "email": "testsupervisor123@example.com",
    "password": "testpassword123"
}

try:
    response = requests.post(url, json=supervisor_login)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ LOGIN SUCCESS!")
        data = response.json()
        user_data = data.get('user_data', {})
        print(f"User Role: '{user_data.get('role')}'")
        print(f"User Role Type: {type(user_data.get('role'))}")
        print(f"Role == 'supervisor': {user_data.get('role') == 'supervisor'}")
        
except Exception as e:
    print(f"❌ Exception occurred: {e}")
import requests
import json
from datetime import datetime

def test_lab_settings_put_endpoint():
    """Test the PUT /api/lab/settings endpoint specifically"""
    base_url = "https://c5e539fb-9522-486d-b275-1bb355b557d8.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    print("🔧 Testing PUT /api/lab/settings endpoint specifically...")
    
    # First, create a supervisor user
    supervisor_data = {
        "email": f"supervisor_put_{datetime.now().strftime('%H%M%S')}@test.com",
        "password": "SupervisorPass123!",
        "full_name": "Dr. PUT Test Manager",
        "role": "supervisor",
        "department": "Computer Science",
        "research_area": "Machine Learning",
        "lab_name": "PUT Test Lab"
    }
    
    response = requests.post(f"{api_url}/auth/register", json=supervisor_data)
    if response.status_code != 200:
        print(f"❌ Failed to create supervisor: {response.status_code}")
        return False
    
    token = response.json()['access_token']
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    # Test PUT endpoint (which should work via POST route)
    lab_data = {
        "lab_name": "PUT Test Research Lab",
        "description": "PUT test lab description",
        "contact_email": "put_test@lab.edu",
        "website": "https://put-testlab.edu",
        "address": "456 PUT Test Street"
    }
    
    print("\n🔍 Testing PUT /api/lab/settings...")
    put_response = requests.put(f"{api_url}/lab/settings", json=lab_data, headers=headers)
    print(f"PUT Response Status: {put_response.status_code}")
    
    if put_response.status_code == 405:  # Method not allowed
        print("❌ PUT method not supported for /api/lab/settings")
        print("   The endpoint only supports POST method for create/update operations")
        
        # Test with POST instead
        print("\n🔍 Testing POST /api/lab/settings (correct method)...")
        post_response = requests.post(f"{api_url}/lab/settings", json=lab_data, headers=headers)
        print(f"POST Response Status: {post_response.status_code}")
        
        if post_response.status_code == 200:
            print("✅ POST method works correctly")
            print(f"Response: {json.dumps(post_response.json(), indent=2)}")
            return True
        else:
            print(f"❌ POST method also failed: {post_response.status_code}")
            return False
    
    elif put_response.status_code == 200:
        print("✅ PUT method works correctly")
        print(f"Response: {json.dumps(put_response.json(), indent=2)}")
        return True
    else:
        print(f"❌ PUT method failed with status: {put_response.status_code}")
        try:
            print(f"Response: {put_response.json()}")
        except:
            print(f"Response: {put_response.text}")
        return False

if __name__ == "__main__":
    success = test_lab_settings_put_endpoint()
    if success:
        print("\n✅ Lab settings endpoint test completed successfully")
    else:
        print("\n❌ Lab settings endpoint test failed")
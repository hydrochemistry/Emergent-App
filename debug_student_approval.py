#!/usr/bin/env python3

import asyncio
import httpx
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://c5e539fb-9522-486d-b275-1bb355b557d8.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

async def debug_student_approval():
    """Debug student approval status"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Login as supervisor
        supervisor_login = {
            "email": "enhanced.supervisor@research.lab",
            "password": "TestPassword123!"
        }
        
        response = await client.post(f"{API_BASE}/auth/login", json=supervisor_login)
        if response.status_code != 200:
            print(f"❌ Failed to login supervisor: {response.status_code}")
            return
        
        supervisor_data = response.json()
        supervisor_token = supervisor_data["access_token"]
        supervisor_id = supervisor_data["user_data"]["id"]
        supervisor_headers = {"Authorization": f"Bearer {supervisor_token}"}
        
        print(f"✅ Supervisor logged in: {supervisor_id}")
        
        # Login as student
        student_login = {
            "email": "enhanced.student@research.lab",
            "password": "TestPassword123!"
        }
        
        response = await client.post(f"{API_BASE}/auth/login", json=student_login)
        if response.status_code != 200:
            print(f"❌ Failed to login student: {response.status_code}")
            return
        
        student_data = response.json()
        student_token = student_data["access_token"]
        student_id = student_data["user_data"]["id"]
        student_headers = {"Authorization": f"Bearer {student_token}"}
        
        print(f"✅ Student logged in: {student_id}")
        
        # Get student profile to check approval status
        response = await client.get(f"{API_BASE}/users/profile", headers=student_headers)
        if response.status_code == 200:
            profile = response.json()
            print(f"Student approval status: {profile.get('is_approved', 'Not set')}")
            print(f"Student supervisor_id: {profile.get('supervisor_id', 'Not set')}")
            print(f"Student role: {profile.get('role', 'Not set')}")
        else:
            print(f"❌ Failed to get student profile: {response.status_code}")
        
        # Try to create a research log as student
        log_data = {
            "activity_type": "experiment",
            "title": "Debug Test Log",
            "description": "Testing student approval",
            "duration_hours": 1.0
        }
        
        response = await client.post(f"{API_BASE}/research-logs", json=log_data, headers=student_headers)
        print(f"Research log creation status: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.text}")

if __name__ == "__main__":
    asyncio.run(debug_student_approval())
#!/usr/bin/env python3

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

async def approve_student():
    """Manually approve the test student"""
    # MongoDB connection
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    # Find the student
    student = await db.users.find_one({"email": "enhanced.student@research.lab"})
    if not student:
        print("❌ Student not found")
        return
    
    print(f"Found student: {student['full_name']} (ID: {student['id']})")
    print(f"Current approval status: {student.get('is_approved', False)}")
    print(f"Supervisor ID: {student.get('supervisor_id', 'None')}")
    
    # Find the supervisor
    supervisor = await db.users.find_one({"email": "enhanced.supervisor@research.lab"})
    if not supervisor:
        print("❌ Supervisor not found")
        return
    
    print(f"Found supervisor: {supervisor['full_name']} (ID: {supervisor['id']})")
    
    # Update student to be approved
    update_result = await db.users.update_one(
        {"id": student["id"]},
        {"$set": {
            "is_approved": True,
            "approved_by": supervisor["id"],
            "approved_at": datetime.utcnow(),
            "supervisor_id": supervisor["id"]  # Ensure supervisor_id is set
        }}
    )
    
    if update_result.modified_count > 0:
        print("✅ Student approved successfully")
    else:
        print("❌ Failed to approve student")
    
    # Verify the update
    updated_student = await db.users.find_one({"id": student["id"]})
    print(f"Updated approval status: {updated_student.get('is_approved', False)}")
    print(f"Updated supervisor ID: {updated_student.get('supervisor_id', 'None')}")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(approve_student())
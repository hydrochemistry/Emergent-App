from fastapi import FastAPI, APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import jwt
import bcrypt
from enum import Enum
import shutil
import json
import httpx

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create uploads directory
UPLOAD_DIR = ROOT_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Create the main app without a prefix
app = FastAPI()

# Mount static files
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# Enums
class UserRole(str, Enum):
    STUDENT = "student"
    SUPERVISOR = "supervisor"
    LAB_MANAGER = "lab_manager"
    ADMIN = "admin"

class ProgramType(str, Enum):
    MSC_RESEARCH = "msc_research"
    MSC_COURSEWORK = "msc_coursework" 
    PHD_RESEARCH = "phd_research"
    PHD_COURSEWORK = "phd_coursework"

class StudyStatus(str, Enum):
    ACTIVE = "active"
    DEFERRED = "deferred"
    ON_LEAVE = "on_leave"
    GRADUATED = "graduated"

class MeetingType(str, Enum):
    SUPERVISION = "supervision"
    PROGRESS_REVIEW = "progress_review"
    THESIS_DISCUSSION = "thesis_discussion"
    GENERAL = "general"

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class ActivityType(str, Enum):
    EXPERIMENT = "experiment"
    LITERATURE_REVIEW = "literature_review"
    DATA_COLLECTION = "data_collection"
    MEETING = "meeting"
    WRITING = "writing"
    ANALYSIS = "analysis"

class BulletinStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class GrantStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PENDING = "pending"
    CLOSED = "closed"

class FundingType(str, Enum):
    NATIONAL = "national"
    INTERNATIONAL = "international"
    PRIVATE = "private"
    INSTITUTIONAL = "institutional"

# Enhanced Models with comprehensive student information
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    password_hash: str
    full_name: str
    role: UserRole
    
    # Enhanced Student Information
    student_id: Optional[str] = None  # Student ID / Matric Number
    contact_number: Optional[str] = None
    nationality: Optional[str] = None
    citizenship: Optional[str] = None
    program_type: Optional[ProgramType] = None
    field_of_study: Optional[str] = None
    department: Optional[str] = None
    faculty: Optional[str] = None
    institute: Optional[str] = None
    enrollment_date: Optional[datetime] = None
    expected_graduation_date: Optional[datetime] = None
    study_status: StudyStatus = StudyStatus.ACTIVE
    
    # Supervisor and Lab Information
    supervisor_id: Optional[str] = None
    research_area: Optional[str] = None
    lab_name: Optional[str] = None
    lab_logo: Optional[str] = None
    profile_picture: Optional[str] = None
    scopus_id: Optional[str] = None
    orcid_id: Optional[str] = None
    
    # Administrative
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: UserRole
    
    # Enhanced Registration Fields
    student_id: Optional[str] = None
    contact_number: Optional[str] = None
    nationality: Optional[str] = None
    citizenship: Optional[str] = None
    program_type: Optional[ProgramType] = None
    field_of_study: Optional[str] = None
    department: Optional[str] = None
    faculty: Optional[str] = None
    institute: Optional[str] = None
    enrollment_date: Optional[str] = None  # Will be converted to datetime
    expected_graduation_date: Optional[str] = None  # Will be converted to datetime
    
    # Existing fields
    research_area: Optional[str] = None
    supervisor_email: Optional[str] = None
    lab_name: Optional[str] = None
    scopus_id: Optional[str] = None
    orcid_id: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    student_id: Optional[str] = None
    contact_number: Optional[str] = None
    nationality: Optional[str] = None
    citizenship: Optional[str] = None
    program_type: Optional[ProgramType] = None
    field_of_study: Optional[str] = None
    department: Optional[str] = None
    faculty: Optional[str] = None
    institute: Optional[str] = None
    enrollment_date: Optional[str] = None
    expected_graduation_date: Optional[str] = None
    study_status: Optional[StudyStatus] = None
    research_area: Optional[str] = None
    lab_name: Optional[str] = None
    scopus_id: Optional[str] = None
    orcid_id: Optional[str] = None

class SupervisorMeeting(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    supervisor_id: str
    meeting_type: MeetingType
    meeting_date: datetime
    duration_minutes: Optional[int] = None
    agenda: str
    discussion_points: List[str] = []
    action_items: List[str] = []
    next_meeting_date: Optional[datetime] = None
    meeting_notes: Optional[str] = None
    student_feedback: Optional[str] = None
    supervisor_feedback: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MeetingCreate(BaseModel):
    student_id: str
    meeting_type: MeetingType
    meeting_date: datetime
    duration_minutes: Optional[int] = None
    agenda: str
    discussion_points: Optional[List[str]] = []
    action_items: Optional[List[str]] = []
    next_meeting_date: Optional[datetime] = None
    meeting_notes: Optional[str] = None

class Reminder(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    created_by: str  # supervisor or system
    title: str
    description: str
    reminder_date: datetime
    priority: TaskPriority = TaskPriority.MEDIUM
    is_completed: bool = False
    reminder_type: str  # 'deadline', 'meeting', 'submission', 'general'
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ReminderCreate(BaseModel):
    user_id: str
    title: str
    description: str
    reminder_date: datetime
    priority: TaskPriority = TaskPriority.MEDIUM
    reminder_type: str

class SupervisorNote(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    created_by: str  # supervisor_id or 'postgrad_office'
    note_type: str  # 'supervision', 'progress', 'academic', 'administrative'
    title: str
    content: str
    is_private: bool = False  # If true, only visible to supervisors/admin
    created_at: datetime = Field(default_factory=datetime.utcnow)

class NoteCreate(BaseModel):
    student_id: str
    note_type: str
    title: str
    content: str
    is_private: bool = False

class UserLogin(BaseModel):
    email: str
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    department: Optional[str] = None
    research_area: Optional[str] = None
    lab_name: Optional[str] = None
    scopus_id: Optional[str] = None
    orcid_id: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user_data: Dict[str, Any]

class LabSettings(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    lab_name: str
    lab_logo: Optional[str] = None
    description: Optional[str] = None
    supervisor_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    assigned_by: str
    assigned_to: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    progress_percentage: int = 0
    comments: List[str] = []
    tags: List[str] = []
    supervisor_rating: Optional[int] = None
    supervisor_feedback: Optional[str] = None

class TaskCreate(BaseModel):
    title: str
    description: str
    assigned_to: str
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: datetime
    tags: Optional[List[str]] = []

class TaskUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    progress_percentage: Optional[int] = None
    comment: Optional[str] = None

class TaskEndorsement(BaseModel):
    task_id: str
    rating: int = Field(ge=1, le=5)
    feedback: str

class ResearchLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    activity_type: ActivityType
    title: str
    description: str
    date: datetime = Field(default_factory=datetime.utcnow)
    duration_hours: Optional[float] = None
    findings: Optional[str] = None
    challenges: Optional[str] = None
    next_steps: Optional[str] = None
    files: List[str] = []
    tags: List[str] = []
    supervisor_endorsement: Optional[bool] = None
    supervisor_comments: Optional[str] = None
    supervisor_rating: Optional[int] = None

class ResearchLogCreate(BaseModel):
    activity_type: ActivityType
    title: str
    description: str
    duration_hours: Optional[float] = None
    findings: Optional[str] = None
    challenges: Optional[str] = None
    next_steps: Optional[str] = None
    tags: Optional[List[str]] = []

class ResearchLogEndorsement(BaseModel):
    log_id: str
    endorsed: bool
    comments: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)

class Bulletin(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    author_id: str
    status: BulletinStatus = BulletinStatus.PENDING
    category: str
    attachments: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None

class BulletinCreate(BaseModel):
    title: str
    content: str
    category: str

class BulletinApproval(BaseModel):
    bulletin_id: str
    approved: bool
    comments: Optional[str] = None

class Grant(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    funding_agency: str
    funding_type: FundingType
    total_amount: float
    spent_amount: float = 0.0
    balance: float
    status: GrantStatus
    start_date: datetime
    end_date: datetime
    principal_investigator: str  # supervisor_id
    student_manager_id: Optional[str] = None
    description: Optional[str] = None
    milestones: List[Dict[str, Any]] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class GrantCreate(BaseModel):
    title: str
    funding_agency: str
    funding_type: FundingType
    total_amount: float
    status: GrantStatus
    start_date: datetime
    end_date: datetime
    description: Optional[str] = None
    student_manager_id: Optional[str] = None

class Publication(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    authors: List[str]
    journal: str
    year: int
    doi: Optional[str] = None
    scopus_id: Optional[str] = None
    citation_count: int = 0
    student_contributors: List[str] = []  # student_ids
    supervisor_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    retrieved_at: Optional[datetime] = None

class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str
    receiver_id: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    is_read: bool = False

class MessageCreate(BaseModel):
    receiver_id: str
    content: str

# File upload helper
async def save_uploaded_file(file: UploadFile, directory: str) -> str:
    """Save uploaded file and return the file path"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")
    
    # Create directory if it doesn't exist
    upload_path = UPLOAD_DIR / directory
    upload_path.mkdir(exist_ok=True)
    
    # Generate unique filename
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = upload_path / unique_filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return f"/uploads/{directory}/{unique_filename}"

# Helper Functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return User(**user)

# Scopus API integration
async def fetch_scopus_publications(scopus_id: str):
    """Mock Scopus API call - replace with actual integration"""
    # This would be replaced with actual Scopus API integration using the provided ID: 22133247800
    return [
        {
            "title": "Advanced Machine Learning Techniques",
            "authors": ["Dr. John Smith", "Jane Doe"],
            "journal": "Journal of AI Research",
            "year": 2023,
            "doi": "10.1000/123456",
            "scopus_id": "2-s2.0-85123456789",
            "citation_count": 15
        }
    ]

# Auth Routes
@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = hash_password(user_data.password)
    
    user = User(
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role,
        department=user_data.department,
        research_area=user_data.research_area,
        lab_name=user_data.lab_name,
        scopus_id=user_data.scopus_id,
        orcid_id=user_data.orcid_id
    )
    
    # Connect student with supervisor
    if user_data.role == UserRole.STUDENT and user_data.supervisor_email:
        supervisor = await db.users.find_one({"email": user_data.supervisor_email, "role": {"$in": ["supervisor", "lab_manager"]}})
        if supervisor:
            user.supervisor_id = supervisor["id"]
    
    await db.users.insert_one(user.dict())
    
    access_token = create_access_token(data={"sub": user.id})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_data={
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "department": user.department,
            "research_area": user.research_area,
            "lab_name": user.lab_name,
            "profile_picture": user.profile_picture
        }
    )

@api_router.post("/auth/login", response_model=Token)
async def login(login_data: UserLogin):
    user = await db.users.find_one({"email": login_data.email})
    if not user or not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": user["id"]})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_data={
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
            "department": user.get("department"),
            "research_area": user.get("research_area"),
            "lab_name": user.get("lab_name"),
            "profile_picture": user.get("profile_picture")
        }
    )

# Enhanced User Routes
@api_router.put("/users/profile")
async def update_profile(user_update: UserUpdate, current_user: User = Depends(get_current_user)):
    update_data = {k: v for k, v in user_update.dict().items() if v is not None}
    if update_data:
        await db.users.update_one({"id": current_user.id}, {"$set": update_data})
    return {"message": "Profile updated successfully"}

@api_router.post("/users/profile-picture")
async def upload_profile_picture(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    file_path = await save_uploaded_file(file, "profile_pictures")
    await db.users.update_one({"id": current_user.id}, {"$set": {"profile_picture": file_path}})
    
    return {"message": "Profile picture updated", "file_path": file_path}

@api_router.post("/users/promote-to-lab-manager")
async def promote_to_lab_manager(student_id: str, current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.SUPERVISOR:
        raise HTTPException(status_code=403, detail="Only supervisors can promote students")
    
    student = await db.users.find_one({"id": student_id, "supervisor_id": current_user.id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found or not supervised by you")
    
    await db.users.update_one({"id": student_id}, {"$set": {"role": UserRole.LAB_MANAGER}})
    return {"message": "Student promoted to lab manager"}

# Lab Settings Routes
@api_router.post("/lab/settings")
async def create_lab_settings(lab_data: dict, current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.SUPERVISOR, UserRole.LAB_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized to manage lab settings")
    
    lab_settings = LabSettings(
        lab_name=lab_data["lab_name"],
        lab_logo=lab_data.get("lab_logo"),
        description=lab_data.get("description"),
        supervisor_id=current_user.id
    )
    
    await db.lab_settings.insert_one(lab_settings.dict())
    return lab_settings

@api_router.post("/lab/logo")
async def upload_lab_logo(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.SUPERVISOR, UserRole.LAB_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    file_path = await save_uploaded_file(file, "lab_logos")
    
    # Update lab settings
    await db.lab_settings.update_one(
        {"supervisor_id": current_user.supervisor_id or current_user.id},
        {"$set": {"lab_logo": file_path, "updated_at": datetime.utcnow()}},
        upsert=True
    )
    
    return {"message": "Lab logo uploaded", "file_path": file_path}

@api_router.get("/lab/settings")
async def get_lab_settings(current_user: User = Depends(get_current_user)):
    supervisor_id = current_user.supervisor_id or current_user.id
    lab_settings = await db.lab_settings.find_one({"supervisor_id": supervisor_id})
    return lab_settings or {}

# Enhanced Task Routes with Endorsement
@api_router.post("/tasks", response_model=Task)
async def create_task(task_data: TaskCreate, current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.SUPERVISOR, UserRole.LAB_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized to create tasks")
    
    task = Task(
        title=task_data.title,
        description=task_data.description,
        assigned_by=current_user.id,
        assigned_to=task_data.assigned_to,
        priority=task_data.priority,
        due_date=task_data.due_date,
        tags=task_data.tags or []
    )
    
    await db.tasks.insert_one(task.dict())
    return task

@api_router.post("/tasks/{task_id}/endorse")
async def endorse_task(task_id: str, endorsement: TaskEndorsement, current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.SUPERVISOR, UserRole.LAB_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized to endorse tasks")
    
    task = await db.tasks.find_one({"id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    await db.tasks.update_one(
        {"id": task_id},
        {"$set": {
            "supervisor_rating": endorsement.rating,
            "supervisor_feedback": endorsement.feedback
        }}
    )
    
    return {"message": "Task endorsed successfully"}

@api_router.get("/tasks", response_model=List[Task])
async def get_tasks(current_user: User = Depends(get_current_user)):
    if current_user.role == UserRole.STUDENT:
        tasks = await db.tasks.find({"assigned_to": current_user.id}).to_list(1000)
    else:
        tasks = await db.tasks.find({"assigned_by": current_user.id}).to_list(1000)
    
    return [Task(**task) for task in tasks]

@api_router.put("/tasks/{task_id}")
async def update_task(task_id: str, update_data: TaskUpdate, current_user: User = Depends(get_current_user)):
    task = await db.tasks.find_one({"id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if current_user.role == UserRole.STUDENT and task["assigned_to"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    elif current_user.role in [UserRole.SUPERVISOR, UserRole.LAB_MANAGER] and task["assigned_by"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    update_dict = {}
    if update_data.status is not None:
        update_dict["status"] = update_data.status
        if update_data.status == TaskStatus.COMPLETED:
            update_dict["completed_at"] = datetime.utcnow()
            update_dict["progress_percentage"] = 100
    
    if update_data.progress_percentage is not None:
        update_dict["progress_percentage"] = update_data.progress_percentage
    
    if update_data.comment:
        await db.tasks.update_one(
            {"id": task_id},
            {"$push": {"comments": f"{current_user.full_name}: {update_data.comment}"}}
        )
    
    if update_dict:
        await db.tasks.update_one({"id": task_id}, {"$set": update_dict})
    
    updated_task = await db.tasks.find_one({"id": task_id})
    return Task(**updated_task)

# Enhanced Research Log Routes with File Upload and Endorsement
@api_router.post("/research-logs", response_model=ResearchLog)
async def create_research_log(log_data: ResearchLogCreate, current_user: User = Depends(get_current_user)):
    research_log = ResearchLog(
        user_id=current_user.id,
        activity_type=log_data.activity_type,
        title=log_data.title,
        description=log_data.description,
        duration_hours=log_data.duration_hours,
        findings=log_data.findings,
        challenges=log_data.challenges,
        next_steps=log_data.next_steps,
        tags=log_data.tags or []
    )
    
    await db.research_logs.insert_one(research_log.dict())
    return research_log

@api_router.post("/research-logs/{log_id}/files")
async def upload_research_log_files(log_id: str, files: List[UploadFile] = File(...), current_user: User = Depends(get_current_user)):
    log = await db.research_logs.find_one({"id": log_id, "user_id": current_user.id})
    if not log:
        raise HTTPException(status_code=404, detail="Research log not found")
    
    file_paths = []
    for file in files:
        if file.filename:
            file_path = await save_uploaded_file(file, "research_files")
            file_paths.append(file_path)
    
    await db.research_logs.update_one(
        {"id": log_id},
        {"$push": {"files": {"$each": file_paths}}}
    )
    
    return {"message": "Files uploaded successfully", "file_paths": file_paths}

@api_router.post("/research-logs/{log_id}/endorse")
async def endorse_research_log(log_id: str, endorsement: ResearchLogEndorsement, current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.SUPERVISOR, UserRole.LAB_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized to endorse research logs")
    
    await db.research_logs.update_one(
        {"id": log_id},
        {"$set": {
            "supervisor_endorsement": endorsement.endorsed,
            "supervisor_comments": endorsement.comments,
            "supervisor_rating": endorsement.rating
        }}
    )
    
    return {"message": "Research log endorsed successfully"}

@api_router.get("/research-logs", response_model=List[ResearchLog])
async def get_research_logs(current_user: User = Depends(get_current_user)):
    if current_user.role == UserRole.STUDENT:
        logs = await db.research_logs.find({"user_id": current_user.id}).sort("date", -1).to_list(1000)
    else:
        student_ids = []
        students = await db.users.find({"supervisor_id": current_user.id}).to_list(1000)
        student_ids = [student["id"] for student in students]
        logs = await db.research_logs.find({"user_id": {"$in": student_ids}}).sort("date", -1).to_list(1000)
    
    return [ResearchLog(**log) for log in logs]

# Bulletin/News Routes
@api_router.post("/bulletins", response_model=Bulletin)
async def create_bulletin(bulletin_data: BulletinCreate, current_user: User = Depends(get_current_user)):
    bulletin = Bulletin(
        title=bulletin_data.title,
        content=bulletin_data.content,
        author_id=current_user.id,
        category=bulletin_data.category,
        status=BulletinStatus.PENDING
    )
    
    await db.bulletins.insert_one(bulletin.dict())
    return bulletin

@api_router.post("/bulletins/{bulletin_id}/approve")
async def approve_bulletin(bulletin_id: str, approval: BulletinApproval, current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.SUPERVISOR, UserRole.LAB_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized to approve bulletins")
    
    status = BulletinStatus.APPROVED if approval.approved else BulletinStatus.REJECTED
    
    await db.bulletins.update_one(
        {"id": bulletin_id},
        {"$set": {
            "status": status,
            "approved_at": datetime.utcnow(),
            "approved_by": current_user.id
        }}
    )
    
    return {"message": f"Bulletin {status.value} successfully"}

@api_router.get("/bulletins", response_model=List[Bulletin])
async def get_bulletins(status: Optional[BulletinStatus] = None, current_user: User = Depends(get_current_user)):
    query = {}
    if status:
        query["status"] = status
    elif current_user.role == UserRole.STUDENT:
        query["status"] = BulletinStatus.APPROVED
    
    bulletins = await db.bulletins.find(query).sort("created_at", -1).to_list(1000)
    return [Bulletin(**bulletin) for bulletin in bulletins]

# Grant Management Routes
@api_router.post("/grants", response_model=Grant)
async def create_grant(grant_data: GrantCreate, current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.SUPERVISOR, UserRole.LAB_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized to create grants")
    
    grant = Grant(
        title=grant_data.title,
        funding_agency=grant_data.funding_agency,
        funding_type=grant_data.funding_type,
        total_amount=grant_data.total_amount,
        balance=grant_data.total_amount,
        status=grant_data.status,
        start_date=grant_data.start_date,
        end_date=grant_data.end_date,
        principal_investigator=current_user.id,
        student_manager_id=grant_data.student_manager_id,
        description=grant_data.description
    )
    
    await db.grants.insert_one(grant.dict())
    return grant

@api_router.get("/grants", response_model=List[Grant])
async def get_grants(current_user: User = Depends(get_current_user)):
    if current_user.role == UserRole.STUDENT:
        grants = await db.grants.find({"student_manager_id": current_user.id}).to_list(1000)
    else:
        grants = await db.grants.find({"principal_investigator": current_user.id}).to_list(1000)
    
    return [Grant(**grant) for grant in grants]

@api_router.put("/grants/{grant_id}/spend")
async def record_grant_spending(grant_id: str, amount: float, current_user: User = Depends(get_current_user)):
    grant = await db.grants.find_one({"id": grant_id})
    if not grant:
        raise HTTPException(status_code=404, detail="Grant not found")
    
    # Check if user has permission
    if (current_user.role == UserRole.STUDENT and grant["student_manager_id"] != current_user.id) or \
       (current_user.role in [UserRole.SUPERVISOR, UserRole.LAB_MANAGER] and grant["principal_investigator"] != current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to manage this grant")
    
    new_spent = grant["spent_amount"] + amount
    new_balance = grant["total_amount"] - new_spent
    
    await db.grants.update_one(
        {"id": grant_id},
        {"$set": {"spent_amount": new_spent, "balance": new_balance}}
    )
    
    return {"message": "Grant spending recorded", "new_balance": new_balance}

# Publication Routes with Scopus Integration
@api_router.post("/publications/sync-scopus")
async def sync_scopus_publications(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.SUPERVISOR:
        raise HTTPException(status_code=403, detail="Only supervisors can sync publications")
    
    if not current_user.scopus_id:
        raise HTTPException(status_code=400, detail="Scopus ID not configured")
    
    # Fetch publications from Scopus API (mock implementation)
    scopus_publications = await fetch_scopus_publications(current_user.scopus_id)
    
    synced_count = 0
    for pub_data in scopus_publications:
        # Check if publication already exists
        existing = await db.publications.find_one({"scopus_id": pub_data["scopus_id"]})
        
        if not existing:
            publication = Publication(
                title=pub_data["title"],
                authors=pub_data["authors"],
                journal=pub_data["journal"],
                year=pub_data["year"],
                doi=pub_data.get("doi"),
                scopus_id=pub_data["scopus_id"],
                citation_count=pub_data["citation_count"],
                supervisor_id=current_user.id,
                retrieved_at=datetime.utcnow()
            )
            
            await db.publications.insert_one(publication.dict())
            synced_count += 1
    
    return {"message": f"Synced {synced_count} publications from Scopus"}

@api_router.get("/publications", response_model=List[Publication])
async def get_publications(current_user: User = Depends(get_current_user)):
    if current_user.role == UserRole.STUDENT:
        publications = await db.publications.find({"student_contributors": current_user.id}).to_list(1000)
    else:
        publications = await db.publications.find({"supervisor_id": current_user.id}).to_list(1000)
    
    return [Publication(**pub) for pub in publications]

@api_router.post("/publications/{pub_id}/tag-student")
async def tag_student_in_publication(pub_id: str, student_id: str, current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.SUPERVISOR, UserRole.LAB_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    publication = await db.publications.find_one({"id": pub_id})
    if not publication:
        raise HTTPException(status_code=404, detail="Publication not found")
    
    await db.publications.update_one(
        {"id": pub_id},
        {"$addToSet": {"student_contributors": student_id}}
    )
    
    return {"message": "Student tagged in publication"}

# PDF Report Generation Route
@api_router.get("/reports/generate/{report_type}")
async def generate_pdf_report(report_type: str, current_user: User = Depends(get_current_user)):
    # Mock PDF generation - would use libraries like ReportLab or WeasyPrint
    report_data = {
        "user": current_user.dict(),
        "lab_name": current_user.lab_name,
        "generated_at": datetime.utcnow(),
        "report_type": report_type
    }
    
    if report_type == "research_progress":
        logs = await db.research_logs.find({"user_id": current_user.id}).to_list(1000)
        report_data["research_logs"] = logs
    elif report_type == "task_summary":
        tasks = await db.tasks.find({"assigned_to": current_user.id}).to_list(1000)
        report_data["tasks"] = tasks
    elif report_type == "lab_summary" and current_user.role in [UserRole.SUPERVISOR, UserRole.LAB_MANAGER]:
        students = await db.users.find({"supervisor_id": current_user.id}).to_list(1000)
        report_data["students"] = students
    
    # Return mock PDF data for now
    return {"message": "PDF report generated", "report_data": report_data}

# Dashboard Stats
@api_router.get("/dashboard/stats")
async def get_dashboard_stats(current_user: User = Depends(get_current_user)):
    if current_user.role == UserRole.STUDENT:
        total_tasks = await db.tasks.count_documents({"assigned_to": current_user.id})
        completed_tasks = await db.tasks.count_documents({"assigned_to": current_user.id, "status": "completed"})
        pending_tasks = await db.tasks.count_documents({"assigned_to": current_user.id, "status": "pending"})
        in_progress_tasks = await db.tasks.count_documents({"assigned_to": current_user.id, "status": "in_progress"})
        total_logs = await db.research_logs.count_documents({"user_id": current_user.id})
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "in_progress_tasks": in_progress_tasks,
            "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "total_research_logs": total_logs
        }
    else:
        students = await db.users.find({"supervisor_id": current_user.id}).to_list(1000)
        student_ids = [student["id"] for student in students]
        
        total_students = len(students)
        total_assigned_tasks = await db.tasks.count_documents({"assigned_by": current_user.id})
        completed_tasks = await db.tasks.count_documents({"assigned_by": current_user.id, "status": "completed"})
        total_publications = await db.publications.count_documents({"supervisor_id": current_user.id})
        active_grants = await db.grants.count_documents({"principal_investigator": current_user.id, "status": "active"})
        
        return {
            "total_students": total_students,
            "total_assigned_tasks": total_assigned_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": (completed_tasks / total_assigned_tasks * 100) if total_assigned_tasks > 0 else 0,
            "total_publications": total_publications,
            "active_grants": active_grants
        }

# Message Routes
@api_router.post("/messages", response_model=Message)
async def send_message(message_data: MessageCreate, current_user: User = Depends(get_current_user)):
    message = Message(
        sender_id=current_user.id,
        receiver_id=message_data.receiver_id,
        content=message_data.content
    )
    
    await db.messages.insert_one(message.dict())
    return message

@api_router.get("/messages")
async def get_messages(with_user: str, current_user: User = Depends(get_current_user)):
    messages = await db.messages.find({
        "$or": [
            {"sender_id": current_user.id, "receiver_id": with_user},
            {"sender_id": with_user, "receiver_id": current_user.id}
        ]
    }).sort("timestamp", 1).to_list(1000)
    
    return [Message(**msg) for msg in messages]

# Students Routes
@api_router.get("/students")
async def get_students(current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.SUPERVISOR, UserRole.LAB_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    students = await db.users.find({"supervisor_id": current_user.id}).to_list(1000)
    return [{
        "id": student["id"],
        "full_name": student["full_name"],
        "email": student["email"],
        "department": student.get("department"),
        "research_area": student.get("research_area"),
        "profile_picture": student.get("profile_picture")
    } for student in students]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: UserRole
    department: Optional[str] = None
    research_area: Optional[str] = None
    supervisor_email: Optional[str] = None  # For students to connect with supervisor
    lab_name: Optional[str] = None
    lab_logo: Optional[str] = None  # URL or base64 string

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_data: Dict[str, Any]

class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    assigned_by: str  # supervisor_id
    assigned_to: str  # student_id
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    progress_percentage: int = 0
    comments: List[str] = []
    tags: List[str] = []

class TaskCreate(BaseModel):
    title: str
    description: str
    assigned_to: str
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: datetime
    tags: Optional[List[str]] = []

class TaskUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    progress_percentage: Optional[int] = None
    comment: Optional[str] = None

class ResearchLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    activity_type: ActivityType
    title: str
    description: str
    date: datetime = Field(default_factory=datetime.utcnow)
    duration_hours: Optional[float] = None
    findings: Optional[str] = None
    challenges: Optional[str] = None
    next_steps: Optional[str] = None
    files: List[str] = []  # file URLs or references
    tags: List[str] = []

class ResearchLogCreate(BaseModel):
    activity_type: ActivityType
    title: str
    description: str
    duration_hours: Optional[float] = None
    findings: Optional[str] = None
    challenges: Optional[str] = None
    next_steps: Optional[str] = None
    tags: Optional[List[str]] = []

class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str
    receiver_id: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    is_read: bool = False

class MessageCreate(BaseModel):
    receiver_id: str
    content: str

# Helper Functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return User(**user)

# Auth Routes
@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create user
    user = User(
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role,
        department=user_data.department,
        research_area=user_data.research_area,
        lab_name=user_data.lab_name,
        lab_logo=user_data.lab_logo
    )
    
    # If student, try to connect with supervisor
    if user_data.role == UserRole.STUDENT and user_data.supervisor_email:
        supervisor = await db.users.find_one({"email": user_data.supervisor_email, "role": "supervisor"})
        if supervisor:
            user.supervisor_id = supervisor["id"]
    
    # Save user
    await db.users.insert_one(user.dict())
    
    # Create token
    access_token = create_access_token(data={"sub": user.id})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_data={
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "department": user.department,
            "research_area": user.research_area,
            "lab_name": user.lab_name,
            "lab_logo": user.lab_logo
        }
    )

@api_router.post("/auth/login", response_model=Token)
async def login(login_data: UserLogin):
    user = await db.users.find_one({"email": login_data.email})
    if not user or not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": user["id"]})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_data={
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
            "department": user.get("department"),
            "research_area": user.get("research_area")
        }
    )

# Task Routes
@api_router.post("/tasks", response_model=Task)
async def create_task(task_data: TaskCreate, current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.SUPERVISOR:
        raise HTTPException(status_code=403, detail="Only supervisors can create tasks")
    
    task = Task(
        title=task_data.title,
        description=task_data.description,
        assigned_by=current_user.id,
        assigned_to=task_data.assigned_to,
        priority=task_data.priority,
        due_date=task_data.due_date,
        tags=task_data.tags or []
    )
    
    await db.tasks.insert_one(task.dict())
    return task

@api_router.get("/tasks", response_model=List[Task])
async def get_tasks(current_user: User = Depends(get_current_user)):
    if current_user.role == UserRole.STUDENT:
        tasks = await db.tasks.find({"assigned_to": current_user.id}).to_list(1000)
    else:  # Supervisor
        tasks = await db.tasks.find({"assigned_by": current_user.id}).to_list(1000)
    
    return [Task(**task) for task in tasks]

@api_router.put("/tasks/{task_id}")
async def update_task(task_id: str, update_data: TaskUpdate, current_user: User = Depends(get_current_user)):
    task = await db.tasks.find_one({"id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check permissions
    if current_user.role == UserRole.STUDENT and task["assigned_to"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this task")
    elif current_user.role == UserRole.SUPERVISOR and task["assigned_by"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this task")
    
    update_dict = {}
    if update_data.status is not None:
        update_dict["status"] = update_data.status
        if update_data.status == TaskStatus.COMPLETED:
            update_dict["completed_at"] = datetime.utcnow()
            update_dict["progress_percentage"] = 100
    
    if update_data.progress_percentage is not None:
        update_dict["progress_percentage"] = update_data.progress_percentage
    
    if update_data.comment:
        # Add comment to existing comments array
        await db.tasks.update_one(
            {"id": task_id},
            {"$push": {"comments": f"{current_user.full_name}: {update_data.comment}"}}
        )
    
    if update_dict:
        await db.tasks.update_one({"id": task_id}, {"$set": update_dict})
    
    updated_task = await db.tasks.find_one({"id": task_id})
    return Task(**updated_task)

# Research Log Routes
@api_router.post("/research-logs", response_model=ResearchLog)
async def create_research_log(log_data: ResearchLogCreate, current_user: User = Depends(get_current_user)):
    research_log = ResearchLog(
        user_id=current_user.id,
        activity_type=log_data.activity_type,
        title=log_data.title,
        description=log_data.description,
        duration_hours=log_data.duration_hours,
        findings=log_data.findings,
        challenges=log_data.challenges,
        next_steps=log_data.next_steps,
        tags=log_data.tags or []
    )
    
    await db.research_logs.insert_one(research_log.dict())
    return research_log

@api_router.get("/research-logs", response_model=List[ResearchLog])
async def get_research_logs(current_user: User = Depends(get_current_user)):
    if current_user.role == UserRole.STUDENT:
        logs = await db.research_logs.find({"user_id": current_user.id}).sort("date", -1).to_list(1000)
    else:  # Supervisor - can see logs from their students
        student_ids = []
        students = await db.users.find({"supervisor_id": current_user.id}).to_list(1000)
        student_ids = [student["id"] for student in students]
        logs = await db.research_logs.find({"user_id": {"$in": student_ids}}).sort("date", -1).to_list(1000)
    
    return [ResearchLog(**log) for log in logs]

# Message Routes
@api_router.post("/messages", response_model=Message)
async def send_message(message_data: MessageCreate, current_user: User = Depends(get_current_user)):
    message = Message(
        sender_id=current_user.id,
        receiver_id=message_data.receiver_id,
        content=message_data.content
    )
    
    await db.messages.insert_one(message.dict())
    return message

@api_router.get("/messages")
async def get_messages(with_user: str, current_user: User = Depends(get_current_user)):
    messages = await db.messages.find({
        "$or": [
            {"sender_id": current_user.id, "receiver_id": with_user},
            {"sender_id": with_user, "receiver_id": current_user.id}
        ]
    }).sort("timestamp", 1).to_list(1000)
    
    return [Message(**msg) for msg in messages]

# Dashboard Routes
@api_router.get("/dashboard/stats")
async def get_dashboard_stats(current_user: User = Depends(get_current_user)):
    if current_user.role == UserRole.STUDENT:
        total_tasks = await db.tasks.count_documents({"assigned_to": current_user.id})
        completed_tasks = await db.tasks.count_documents({"assigned_to": current_user.id, "status": "completed"})
        pending_tasks = await db.tasks.count_documents({"assigned_to": current_user.id, "status": "pending"})
        in_progress_tasks = await db.tasks.count_documents({"assigned_to": current_user.id, "status": "in_progress"})
        total_logs = await db.research_logs.count_documents({"user_id": current_user.id})
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "in_progress_tasks": in_progress_tasks,
            "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "total_research_logs": total_logs
        }
    else:  # Supervisor
        students = await db.users.find({"supervisor_id": current_user.id}).to_list(1000)
        student_ids = [student["id"] for student in students]
        
        total_students = len(students)
        total_assigned_tasks = await db.tasks.count_documents({"assigned_by": current_user.id})
        completed_tasks = await db.tasks.count_documents({"assigned_by": current_user.id, "status": "completed"})
        
        return {
            "total_students": total_students,
            "total_assigned_tasks": total_assigned_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": (completed_tasks / total_assigned_tasks * 100) if total_assigned_tasks > 0 else 0
        }

# Students Routes (for supervisors)
@api_router.get("/students")
async def get_students(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.SUPERVISOR:
        raise HTTPException(status_code=403, detail="Only supervisors can view students")
    
    students = await db.users.find({"supervisor_id": current_user.id}).to_list(1000)
    return [{
        "id": student["id"],
        "full_name": student["full_name"],
        "email": student["email"],
        "department": student.get("department"),
        "research_area": student.get("research_area")
    } for student in students]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
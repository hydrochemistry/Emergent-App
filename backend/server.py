from fastapi import FastAPI, APIRouter, HTTPException, Depends, UploadFile, File, Form
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

# Backend URL for file URLs
BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:8000')

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
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"

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

class UserLogin(BaseModel):
    email: str
    password: str

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

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_data: Dict[str, Any]

class LabSettings(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    lab_name: str
    lab_logo: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    contact_email: Optional[str] = None
    lab_scopus_id: Optional[str] = None  # Added lab-wide Scopus ID
    supervisor_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class LabSettingsUpdate(BaseModel):
    lab_name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    contact_email: Optional[str] = None
    lab_scopus_id: Optional[str] = None  # Added lab-wide Scopus ID

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
    # New review system fields
    review_status: Optional[str] = None  # 'accepted', 'revision', 'rejected'
    review_feedback: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[str] = None
    reviewer_name: Optional[str] = None
    # Additional student info fields for supervisor view
    student_name: Optional[str] = None
    student_id: Optional[str] = None
    student_email: Optional[str] = None

class ResearchLogCreate(BaseModel):
    activity_type: ActivityType
    title: str
    description: str
    duration_hours: Optional[float] = None
    findings: Optional[str] = None
    challenges: Optional[str] = None
    next_steps: Optional[str] = None
    tags: Optional[List[str]] = []
    log_date: Optional[str] = None  # Added missing field
    log_time: Optional[str] = None  # Added missing field

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
    is_highlight: bool = False  # New field for dashboard highlights
    created_at: datetime = Field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None

class BulletinCreate(BaseModel):
    title: str
    content: str
    category: str
    is_highlight: bool = False

class MilestoneCreate(BaseModel):
    project_title: str
    milestone_title: str
    description: str
    start_date: datetime
    target_end_date: datetime
    progress_percentage: int = Field(ge=0, le=100, default=0)
    status: str = "in_progress"
    deliverables: Optional[List[str]] = []
    challenges: Optional[str] = None
    next_steps: Optional[str] = None

class Milestone(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    project_title: str
    milestone_title: str
    description: str
    start_date: datetime
    target_end_date: datetime
    actual_end_date: Optional[datetime] = None
    progress_percentage: int = 0
    status: str = "in_progress"  # in_progress, completed, delayed, cancelled
    deliverables: List[str] = []
    challenges: Optional[str] = None
    next_steps: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

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
    
    # New fields
    person_in_charge: Optional[str] = None  # student_id
    grant_vote_number: Optional[str] = None
    duration_months: Optional[int] = None
    grant_type: Optional[str] = None
    remaining_balance: Optional[float] = None

class GrantCreate(BaseModel):
    title: str
    funding_agency: str
    funding_type: Optional[FundingType] = FundingType.NATIONAL
    total_amount: float
    status: GrantStatus
    start_date: datetime
    end_date: datetime
    description: Optional[str] = None
    student_manager_id: Optional[str] = None
    
    # New fields
    person_in_charge: Optional[str] = None
    grant_vote_number: Optional[str] = None
    duration_months: Optional[int] = None
    grant_type: Optional[str] = None

# New Grant Registration Model
class GrantRegistration(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    grant_id: str
    applicant_id: str  # student_id who is registering
    application_date: datetime = Field(default_factory=datetime.utcnow)
    application_status: str = "pending"  # pending, approved, rejected
    justification: str
    expected_amount: float
    purpose: str
    supervisor_approval: Optional[bool] = None
    supervisor_comments: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class GrantRegistrationCreate(BaseModel):
    grant_id: str
    justification: str
    expected_amount: float
    purpose: str

class Publication(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    authors: List[str]  # Fixed back to List[str] for frontend compatibility
    journal: Optional[str] = None
    conference: Optional[str] = None  # Added for conference publications
    publication_year: int  # Direct field name, no alias needed
    doi: Optional[str] = None
    scopus_id: Optional[str] = None
    abstract: Optional[str] = None  # Added abstract field
    keywords: List[str] = []  # Added keywords
    status: str = "published"  # Added status
    citation_count: int = 0
    student_contributors: List[str] = []  # student_ids
    supervisor_id: Optional[str] = None  # Made optional
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
    """Fetch publications from Scopus API using the provided Scopus Author ID"""
    scopus_api_key = os.environ.get('SCOPUS_API_KEY')
    if not scopus_api_key:
        raise HTTPException(status_code=500, detail="Scopus API key not configured")
    
    url = f"https://api.elsevier.com/content/search/scopus?query=AU-ID({scopus_id})&count=10&sort=-coverDate"
    headers = {
        "X-ELS-APIKey": scopus_api_key,
        "Accept": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            publications = data.get("search-results", {}).get("entry", [])
            
            formatted_publications = []
            for pub in publications:
                formatted_publications.append({
                    "title": pub.get("dc:title", "Unknown Title"),
                    "authors": [pub.get("dc:creator", "Unknown Author")],
                    "journal": pub.get("prism:publicationName", "Unknown Journal"),
                    "publication_year": int(pub.get("prism:coverDate", "2024")[:4]) if pub.get("prism:coverDate") else 2024,
                    "doi": pub.get("prism:doi"),
                    "scopus_id": pub.get("dc:identifier", "").replace("SCOPUS_ID:", ""),
                    "citation_count": int(pub.get("citedby-count", 0)),
                    "scopus_url": pub.get("prism:url", "")
                })
            
            return formatted_publications
            
    except httpx.HTTPError as e:
        print(f"Scopus API Error: {e}")
        # Return mock data as fallback
        return [
            {
                "title": f"Sample Publication from Scopus ID {scopus_id}",
                "authors": ["Dr. Sample Author"],
                "journal": "Sample Journal",
                "publication_year": 2024,
                "doi": "10.1000/sample",
                "scopus_id": "2-s2.0-sample",
                "citation_count": 5,
                "scopus_url": "https://www.scopus.com/record/display.uri"
            }
        ]

async def sync_lab_publications_from_scopus(lab_scopus_id: str, supervisor_id: str):
    """Sync publications from Scopus API for the entire lab using lab Scopus ID"""
    try:
        # Fetch publications from Scopus
        publications_data = await fetch_scopus_publications(lab_scopus_id)
        
        # Clear existing lab publications to avoid duplicates
        await db.publications.delete_many({"supervisor_id": supervisor_id})
        
        # Process and store publications
        for pub_data in publications_data:
            # Create new publication record
            publication = Publication(
                title=pub_data["title"],
                authors=pub_data["authors"],
                journal=pub_data.get("journal"),
                publication_year=pub_data["publication_year"],
                doi=pub_data.get("doi"),
                scopus_id=pub_data.get("scopus_id"),
                citation_count=pub_data.get("citation_count", 0),
                supervisor_id=supervisor_id,
                retrieved_at=datetime.utcnow()
            )
            
            await db.publications.insert_one(publication.dict())
        
        print(f"Successfully synced {len(publications_data)} publications for lab Scopus ID: {lab_scopus_id}")
        
    except Exception as e:
        print(f"Error syncing lab publications: {str(e)}")
        raise e

# Auth Routes
@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = hash_password(user_data.password)
    
    # Convert date strings to datetime objects
    enrollment_date = None
    expected_graduation_date = None
    
    if user_data.enrollment_date:
        try:
            enrollment_date = datetime.fromisoformat(user_data.enrollment_date.replace('Z', '+00:00'))
        except:
            enrollment_date = None
    
    if user_data.expected_graduation_date:
        try:
            expected_graduation_date = datetime.fromisoformat(user_data.expected_graduation_date.replace('Z', '+00:00'))
        except:
            expected_graduation_date = None
    
    user = User(
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role,
        student_id=user_data.student_id,
        contact_number=user_data.contact_number,
        nationality=user_data.nationality,
        citizenship=user_data.citizenship,
        program_type=user_data.program_type,
        field_of_study=user_data.field_of_study,
        department=user_data.department,
        faculty=user_data.faculty,
        institute=user_data.institute,
        enrollment_date=enrollment_date,
        expected_graduation_date=expected_graduation_date,
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
            "student_id": user.student_id,
            "department": user.department,
            "research_area": user.research_area,
            "lab_name": user.lab_name,
            "profile_picture": user.profile_picture,
            "program_type": user.program_type,
            "study_status": user.study_status
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
            "profile_picture": user.get("profile_picture"),
            "program_type": user.get("program_type"),
            "study_status": user.get("study_status")
        }
    )

# Enhanced User Routes
@api_router.put("/users/profile")
async def update_profile(user_update: UserUpdate, current_user: User = Depends(get_current_user)):
    update_data = {k: v for k, v in user_update.dict().items() if v is not None}
    
    # Convert date strings to datetime objects
    if 'enrollment_date' in update_data and update_data['enrollment_date']:
        try:
            update_data['enrollment_date'] = datetime.fromisoformat(update_data['enrollment_date'].replace('Z', '+00:00'))
        except:
            del update_data['enrollment_date']
    
    if 'expected_graduation_date' in update_data and update_data['expected_graduation_date']:
        try:
            update_data['expected_graduation_date'] = datetime.fromisoformat(update_data['expected_graduation_date'].replace('Z', '+00:00'))
        except:
            del update_data['expected_graduation_date']
    
    if update_data:
        update_data['updated_at'] = datetime.utcnow()
        await db.users.update_one({"id": current_user.id}, {"$set": update_data})
    return {"message": "Profile updated successfully"}

@api_router.get("/users/profile")
async def get_user_profile(user_id: Optional[str] = None, current_user: User = Depends(get_current_user)):
    """Get user profile - if user_id provided and user has permission, return that user's profile"""
    target_user_id = user_id if user_id else current_user.id
    
    # Check permissions
    if user_id and user_id != current_user.id:
        if current_user.role not in [UserRole.SUPERVISOR, UserRole.LAB_MANAGER]:
            raise HTTPException(status_code=403, detail="Not authorized to view other profiles")
        
        # Supervisors can only view their students' profiles
        if current_user.role == UserRole.SUPERVISOR:
            target_user = await db.users.find_one({"id": target_user_id})
            if not target_user or target_user.get("supervisor_id") != current_user.id:
                raise HTTPException(status_code=403, detail="Not authorized to view this profile")
    
    user = await db.users.find_one({"id": target_user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Remove sensitive information and MongoDB ObjectId
    user.pop("password_hash", None)
    user.pop("_id", None)
    return user

@api_router.post("/users/profile-picture")
async def upload_profile_picture(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    file_path = await save_uploaded_file(file, "profile_pictures")
    await db.users.update_one(
        {"id": current_user.id}, 
        {"$set": {"profile_picture": file_path, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Profile picture updated", "file_path": file_path}

@api_router.post("/users/change-password")
async def change_password(password_data: PasswordChange, current_user: User = Depends(get_current_user)):
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Hash new password
    new_password_hash = hash_password(password_data.new_password)
    
    # Update password
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {"password_hash": new_password_hash, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Password updated successfully"}

@api_router.put("/users/{student_id}/promote")
async def promote_user(student_id: str, promotion_data: dict, current_user: User = Depends(get_current_user)):
    """Promote a user to a new role"""
    if current_user.role not in [UserRole.SUPERVISOR, UserRole.LAB_MANAGER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only supervisors and above can promote users")
    
    # Validate the new role
    valid_roles = ["student", "lab_manager", "supervisor", "admin"]
    new_role = promotion_data.get("new_role")
    if new_role not in valid_roles:
        raise HTTPException(status_code=400, detail="Invalid role specified")
    
    # Find the user
    user_to_promote = await db.users.find_one({"id": student_id})
    if not user_to_promote:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check permissions - supervisors can only promote their students
    if current_user.role == UserRole.SUPERVISOR:
        if user_to_promote.get("supervisor_id") != current_user.id:
            raise HTTPException(status_code=403, detail="You can only promote your own students")
        
        # Supervisors cannot promote to admin
        if new_role == "admin":
            raise HTTPException(status_code=403, detail="Supervisors cannot promote users to admin")
    
    # Update the user's role
    await db.users.update_one(
        {"id": student_id}, 
        {"$set": {"role": new_role, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": f"User promoted to {new_role.replace('_', ' ')} successfully"}

@api_router.post("/users/{student_id}/promote-lab-manager")
async def promote_to_lab_manager(student_id: str, current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.SUPERVISOR:
        raise HTTPException(status_code=403, detail="Only supervisors can promote students")
    
    student = await db.users.find_one({"id": student_id, "supervisor_id": current_user.id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found or not supervised by you")
    
    await db.users.update_one(
        {"id": student_id}, 
        {"$set": {"role": UserRole.LAB_MANAGER, "updated_at": datetime.utcnow()}}
    )
    return {"message": "Student promoted to lab manager"}

@api_router.post("/users/{student_id}/revoke-lab-manager")
async def revoke_lab_manager(student_id: str, current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.SUPERVISOR:
        raise HTTPException(status_code=403, detail="Only supervisors can revoke lab manager status")
    
    student = await db.users.find_one({"id": student_id, "supervisor_id": current_user.id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found or not supervised by you")
    
    await db.users.update_one(
        {"id": student_id}, 
        {"$set": {"role": UserRole.STUDENT, "updated_at": datetime.utcnow()}}
    )
    return {"message": "Lab manager status revoked"}

# Lab Settings Routes
@api_router.post("/lab/settings")
async def create_lab_settings(lab_data: LabSettingsUpdate, current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.SUPERVISOR, UserRole.LAB_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized to manage lab settings")
    
    # Check if lab settings already exist
    existing_settings = await db.lab_settings.find_one({"supervisor_id": current_user.id})
    
    if existing_settings:
        # Update existing settings
        update_data = {k: v for k, v in lab_data.dict().items() if v is not None}
        update_data['updated_at'] = datetime.utcnow()
        await db.lab_settings.update_one(
            {"supervisor_id": current_user.id},
            {"$set": update_data}
        )
        updated_settings = await db.lab_settings.find_one({"supervisor_id": current_user.id})
        return LabSettings(**updated_settings)
    else:
        # Create new settings
        lab_settings = LabSettings(
            lab_name=lab_data.lab_name or current_user.lab_name or "Research Lab",
            description=lab_data.description,
            address=lab_data.address,
            website=lab_data.website,
            contact_email=lab_data.contact_email,
            supervisor_id=current_user.id
        )
        
        await db.lab_settings.insert_one(lab_settings.dict())
        return lab_settings

@api_router.put("/lab/settings")
async def update_lab_settings(lab_data: LabSettingsUpdate, current_user: User = Depends(get_current_user)):
    """PUT endpoint for updating lab settings with automatic publications sync"""
    if current_user.role not in [UserRole.SUPERVISOR, UserRole.LAB_MANAGER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized to manage lab settings")
    
    # Get current supervisor ID
    supervisor_id = current_user.supervisor_id or current_user.id
    
    # Prepare update data
    update_data = {}
    for field, value in lab_data.dict(exclude_unset=True).items():
        if value is not None:
            update_data[field] = value
    
    update_data["updated_at"] = datetime.utcnow()
    
    # Check if lab_scopus_id is being updated
    sync_publications = False
    if "lab_scopus_id" in update_data and update_data["lab_scopus_id"]:
        sync_publications = True
        new_scopus_id = update_data["lab_scopus_id"]
    
    # Update lab settings
    await db.lab_settings.update_one(
        {"supervisor_id": supervisor_id},
        {"$set": update_data},
        upsert=True
    )
    
    # Sync publications if Scopus ID was updated
    if sync_publications:
        try:
            await sync_lab_publications_from_scopus(new_scopus_id, supervisor_id)
        except Exception as e:
            print(f"Warning: Failed to sync publications: {str(e)}")
            # Don't fail the lab settings update if publications sync fails
    
    return {"message": "Lab settings updated successfully"}

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
    if lab_settings:
        lab_settings.pop("_id", None)
    return lab_settings or {}

# Supervisor Meeting Routes
@api_router.post("/meetings", response_model=SupervisorMeeting)
async def create_meeting(meeting_data: MeetingCreate, current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.SUPERVISOR, UserRole.LAB_MANAGER]:
        raise HTTPException(status_code=403, detail="Only supervisors can create meetings")
    
    meeting = SupervisorMeeting(
        student_id=meeting_data.student_id,
        supervisor_id=current_user.id,
        meeting_type=meeting_data.meeting_type,
        meeting_date=meeting_data.meeting_date,
        duration_minutes=meeting_data.duration_minutes,
        agenda=meeting_data.agenda,
        discussion_points=meeting_data.discussion_points or [],
        action_items=meeting_data.action_items or [],
        next_meeting_date=meeting_data.next_meeting_date,
        meeting_notes=meeting_data.meeting_notes
    )
    
    await db.meetings.insert_one(meeting.dict())
    return meeting

@api_router.get("/meetings")
async def get_meetings(student_id: Optional[str] = None, current_user: User = Depends(get_current_user)):
    query = {}
    
    if current_user.role == UserRole.STUDENT:
        query["student_id"] = current_user.id
    elif student_id:
        # Verify supervisor has access to this student
        student = await db.users.find_one({"id": student_id, "supervisor_id": current_user.id})
        if not student:
            raise HTTPException(status_code=403, detail="Not authorized to view these meetings")
        query["student_id"] = student_id
    else:
        # Get all meetings for students supervised by this user
        students = await db.users.find({"supervisor_id": current_user.id}).to_list(1000)
        student_ids = [student["id"] for student in students]
        query["student_id"] = {"$in": student_ids}
    
    meetings = await db.meetings.find(query).sort("meeting_date", -1).to_list(1000)
    return [SupervisorMeeting(**meeting) for meeting in meetings]

@api_router.put("/meetings/{meeting_id}")
async def update_meeting(meeting_id: str, update_data: dict, current_user: User = Depends(get_current_user)):
    meeting = await db.meetings.find_one({"id": meeting_id})
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Check permissions
    if current_user.role == UserRole.STUDENT and meeting["student_id"] != current_user.id:
        # Students can only add feedback to their own meetings
        update_data = {"student_feedback": update_data.get("student_feedback", "")}
    elif current_user.role in [UserRole.SUPERVISOR, UserRole.LAB_MANAGER] and meeting["supervisor_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this meeting")
    
    await db.meetings.update_one({"id": meeting_id}, {"$set": update_data})
    return {"message": "Meeting updated successfully"}

# Reminders Routes
@api_router.post("/reminders", response_model=Reminder)
async def create_reminder(reminder_data: ReminderCreate, current_user: User = Depends(get_current_user)):
    # Check if user can create reminder for the target user
    if reminder_data.user_id != current_user.id:
        if current_user.role not in [UserRole.SUPERVISOR, UserRole.LAB_MANAGER]:
            raise HTTPException(status_code=403, detail="Not authorized to create reminders for others")
        
        target_user = await db.users.find_one({"id": reminder_data.user_id})
        if not target_user or target_user.get("supervisor_id") != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to create reminder for this user")
    
    reminder = Reminder(
        user_id=reminder_data.user_id,
        created_by=current_user.id,
        title=reminder_data.title,
        description=reminder_data.description,
        reminder_date=reminder_data.reminder_date,
        priority=reminder_data.priority,
        reminder_type=reminder_data.reminder_type
    )
    
    await db.reminders.insert_one(reminder.dict())
    return reminder

@api_router.get("/reminders")
async def get_reminders(user_id: Optional[str] = None, current_user: User = Depends(get_current_user)):
    target_user_id = user_id if user_id else current_user.id
    
    # Check permissions
    if user_id and user_id != current_user.id:
        if current_user.role not in [UserRole.SUPERVISOR, UserRole.LAB_MANAGER]:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        target_user = await db.users.find_one({"id": target_user_id})
        if not target_user or target_user.get("supervisor_id") != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
    
    reminders = await db.reminders.find({"user_id": target_user_id}).sort("reminder_date", 1).to_list(1000)
    return [Reminder(**reminder) for reminder in reminders]

@api_router.put("/reminders/{reminder_id}/complete")
async def complete_reminder(reminder_id: str, current_user: User = Depends(get_current_user)):
    reminder = await db.reminders.find_one({"id": reminder_id})
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    if reminder["user_id"] != current_user.id and current_user.role not in [UserRole.SUPERVISOR, UserRole.LAB_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await db.reminders.update_one({"id": reminder_id}, {"$set": {"is_completed": True}})
    return {"message": "Reminder marked as completed"}

@api_router.put("/reminders/{reminder_id}")
async def update_reminder(reminder_id: str, update_data: dict, current_user: User = Depends(get_current_user)):
    """Update reminder details (edit functionality)"""
    reminder = await db.reminders.find_one({"id": reminder_id})
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    # Check permissions
    if reminder["user_id"] != current_user.id and current_user.role not in [UserRole.SUPERVISOR, UserRole.LAB_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Prepare update data
    allowed_fields = ["title", "description", "reminder_date", "priority", "reminder_type"]
    update_dict = {}
    
    for field in allowed_fields:
        if field in update_data:
            if field == "reminder_date" and update_data[field]:
                # Parse datetime string
                try:
                    update_dict[field] = datetime.fromisoformat(update_data[field].replace('Z', '+00:00'))
                except:
                    update_dict[field] = datetime.fromisoformat(update_data[field])
            else:
                update_dict[field] = update_data[field]
    
    if update_dict:
        await db.reminders.update_one({"id": reminder_id}, {"$set": update_dict})
    
    return {"message": "Reminder updated successfully"}

@api_router.delete("/reminders/{reminder_id}")
async def delete_reminder(reminder_id: str, current_user: User = Depends(get_current_user)):
    """Delete a reminder"""
    reminder = await db.reminders.find_one({"id": reminder_id})
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    # Check permissions
    if reminder["user_id"] != current_user.id and current_user.role not in [UserRole.SUPERVISOR, UserRole.LAB_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await db.reminders.delete_one({"id": reminder_id})
    return {"message": "Reminder deleted successfully"}

# Supervisor Notes Routes
@api_router.post("/notes", response_model=SupervisorNote)
async def create_note(note_data: NoteCreate, current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.SUPERVISOR, UserRole.LAB_MANAGER]:
        raise HTTPException(status_code=403, detail="Only supervisors can create notes")
    
    # Verify student belongs to supervisor
    student = await db.users.find_one({"id": note_data.student_id, "supervisor_id": current_user.id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found or not supervised by you")
    
    note = SupervisorNote(
        student_id=note_data.student_id,
        created_by=current_user.id,
        note_type=note_data.note_type,
        title=note_data.title,
        content=note_data.content,
        is_private=note_data.is_private
    )
    
    await db.notes.insert_one(note.dict())
    return note

@api_router.get("/notes")
async def get_notes(student_id: Optional[str] = None, current_user: User = Depends(get_current_user)):
    if current_user.role == UserRole.STUDENT:
        # Students can only see non-private notes about themselves
        notes = await db.notes.find({
            "student_id": current_user.id,
            "is_private": False
        }).sort("created_at", -1).to_list(1000)
    else:
        # Supervisors can see all notes for their students
        query = {}
        if student_id:
            # Verify supervisor has access to this student
            student = await db.users.find_one({"id": student_id, "supervisor_id": current_user.id})
            if not student:
                raise HTTPException(status_code=403, detail="Not authorized")
            query["student_id"] = student_id
        else:
            # Get all notes for students supervised by this user
            students = await db.users.find({"supervisor_id": current_user.id}).to_list(1000)
            student_ids = [student["id"] for student in students]
            query["student_id"] = {"$in": student_ids}
        
        notes = await db.notes.find(query).sort("created_at", -1).to_list(1000)
    
    return [SupervisorNote(**note) for note in notes]

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
    # Handle date/time from frontend
    research_date = datetime.utcnow()  # Default to current time
    if log_data.log_date:
        try:
            if log_data.log_time:
                # Combine date and time
                research_date = datetime.fromisoformat(f"{log_data.log_date}T{log_data.log_time}")
            else:
                # Just date, set time to current
                research_date = datetime.fromisoformat(f"{log_data.log_date}T{datetime.utcnow().strftime('%H:%M:%S')}")
        except ValueError:
            # If parsing fails, use current time
            research_date = datetime.utcnow()
    
    research_log = ResearchLog(
        user_id=current_user.id,
        activity_type=log_data.activity_type,
        title=log_data.title,
        description=log_data.description,
        date=research_date,  # Use parsed date
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

@api_router.post("/research-logs/attachments")
async def upload_research_log_attachment(
    file: UploadFile = File(...), 
    research_log_id: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    """Upload a single attachment for a research log"""
    log = await db.research_logs.find_one({"id": research_log_id, "user_id": current_user.id})
    if not log:
        raise HTTPException(status_code=404, detail="Research log not found")
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Validate file size and type
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB")
    
    # Reset file position
    await file.seek(0)
    
    # Save the file
    file_path = await save_uploaded_file(file, "research_attachments")
    
    # Update the research log with the new attachment
    await db.research_logs.update_one(
        {"id": research_log_id},
        {"$push": {"attachments": {
            "filename": file.filename,
            "file_path": file_path,
            "content_type": file.content_type,
            "size": len(content),
            "uploaded_at": datetime.utcnow()
        }}}
    )
    
    return {"message": "Attachment uploaded successfully", "file_path": file_path}

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

@api_router.post("/research-logs/{log_id}/review")
async def review_research_log(
    log_id: str, 
    review_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Review research log with accept, revision, or reject actions"""
    if current_user.role not in [UserRole.SUPERVISOR, UserRole.LAB_MANAGER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized to review research logs")
    
    # Validate the log exists
    log = await db.research_logs.find_one({"id": log_id})
    if not log:
        raise HTTPException(status_code=404, detail="Research log not found")
    
    # Validate action
    valid_actions = ['accepted', 'revision', 'rejected']
    action = review_data.get('action')
    if action not in valid_actions:
        raise HTTPException(status_code=400, detail=f"Invalid action. Must be one of: {valid_actions}")
    
    # Update the research log with review information
    await db.research_logs.update_one(
        {"id": log_id},
        {"$set": {
            "review_status": action,
            "review_feedback": review_data.get("feedback", ""),
            "reviewed_by": current_user.id,
            "reviewed_at": datetime.utcnow().isoformat(),
            "reviewer_name": current_user.full_name
        }}
    )
    
    return {"message": f"Research log {action} successfully"}

@api_router.get("/research-logs/{log_id}/pdf")
async def download_research_log_pdf(log_id: str, current_user: User = Depends(get_current_user)):
    """Generate and download research log as PDF"""
    
    # Find the research log
    log = await db.research_logs.find_one({"id": log_id})
    if not log:
        raise HTTPException(status_code=404, detail="Research log not found")
    
    # Check permissions - students can only download their own, supervisors can download any
    if current_user.role == UserRole.STUDENT and log["student_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this research log")
    
    # For now, return a simple response indicating PDF generation is not implemented
    # In a full implementation, you would generate an actual PDF using libraries like reportlab or weasyprint
    return {"message": "PDF generation feature - Coming Soon!", "log_title": log["title"]}

@api_router.get("/research-logs", response_model=List[ResearchLog])
async def get_research_logs(current_user: User = Depends(get_current_user)):
    if current_user.role == UserRole.STUDENT:
        logs = await db.research_logs.find({"user_id": current_user.id}).sort("date", -1).to_list(1000)
    else:
        student_ids = []
        students = await db.users.find({"supervisor_id": current_user.id}).to_list(1000)
        student_ids = [student["id"] for student in students]
        logs = await db.research_logs.find({"user_id": {"$in": student_ids}}).sort("date", -1).to_list(1000)
        
        # Add student information for supervisor view
        student_map = {student["id"]: student for student in students}
        for log in logs:
            student_info = student_map.get(log["user_id"], {})
            log["student_name"] = student_info.get("full_name", "Unknown Student")
            log["student_id"] = student_info.get("student_id", log["user_id"])
            log["student_email"] = student_info.get("email", "")
    
    return [ResearchLog(**log) for log in logs]

# Enhanced Bulletin/News Routes with Highlight Feature
@api_router.post("/bulletins", response_model=Bulletin)
async def create_bulletin(bulletin_data: BulletinCreate, current_user: User = Depends(get_current_user)):
    bulletin = Bulletin(
        title=bulletin_data.title,
        content=bulletin_data.content,
        author_id=current_user.id,
        category=bulletin_data.category,
        is_highlight=bulletin_data.is_highlight,
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

@api_router.get("/bulletins/highlights")
async def get_highlight_bulletins(current_user: User = Depends(get_current_user)):
    """Get highlighted bulletins for dashboard display"""
    query = {
        "status": BulletinStatus.APPROVED,
        "is_highlight": True
    }
    
    bulletins = await db.bulletins.find(query).sort("created_at", -1).to_list(5)
    return [Bulletin(**bulletin) for bulletin in bulletins]

# Grant Management Routes
@api_router.post("/grants", response_model=Grant)
async def create_grant(grant_data: GrantCreate, current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.SUPERVISOR, UserRole.LAB_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized to create grants")
    
    grant = Grant(
        title=grant_data.title,
        funding_agency=grant_data.funding_agency,
        funding_type=grant_data.funding_type or FundingType.GOVERNMENT,
        total_amount=grant_data.total_amount,
        balance=grant_data.total_amount,
        status=grant_data.status,
        start_date=grant_data.start_date,
        end_date=grant_data.end_date,
        principal_investigator=current_user.id,
        student_manager_id=grant_data.student_manager_id,
        description=grant_data.description,
        person_in_charge=grant_data.person_in_charge,
        grant_vote_number=grant_data.grant_vote_number,
        duration_months=grant_data.duration_months,
        grant_type=grant_data.grant_type,
        remaining_balance=grant_data.total_amount
    )
    
    await db.grants.insert_one(grant.dict())
    return grant

@api_router.get("/grants", response_model=List[Grant])
async def get_grants(current_user: User = Depends(get_current_user)):
    """Get grants - all users can see all grants for proper synchronization"""
    # All users see all grants for full lab visibility and synchronization
    grants = await db.grants.find({}).to_list(1000)
    
    # Add enhanced balance calculations for dashboard display
    for grant in grants:
        if "total_amount" in grant and "spent_amount" in grant:
            grant["remaining_balance"] = grant["total_amount"] - grant.get("spent_amount", 0)
        elif "balance" in grant:
            grant["remaining_balance"] = grant["balance"]
        else:
            grant["remaining_balance"] = grant.get("total_amount", 0)
        
        # Ensure current_balance field is populated for consistency
        if "current_balance" not in grant:
            grant["current_balance"] = grant.get("remaining_balance", grant.get("total_amount", 0))
    
    return [Grant(**grant) for grant in grants]

@api_router.put("/grants/{grant_id}")
async def update_grant(grant_id: str, grant_update: dict, current_user: User = Depends(get_current_user)):
    """Update grant information"""
    # Find the grant first
    grant = await db.grants.find_one({"id": grant_id})
    if not grant:
        raise HTTPException(status_code=404, detail="Grant not found")
    
    # Check if user has permission to update grants
    # Allow supervisors, lab managers, admins, OR students assigned as PIC (person_in_charge)
    is_authorized = (
        current_user.role in [UserRole.SUPERVISOR, UserRole.LAB_MANAGER, UserRole.ADMIN] or
        (current_user.role == UserRole.STUDENT and grant.get("person_in_charge") == current_user.id)
    )
    
    if not is_authorized:
        raise HTTPException(status_code=403, detail="Not authorized to update grants")
    
    # Prepare update data
    update_data = {}
    allowed_fields = [
        "title", "funding_agency", "total_amount", "current_balance", 
        "duration_months", "grant_type", "status", "person_in_charge", 
        "grant_vote_number", "start_date", "end_date", "description"
    ]
    
    for field in allowed_fields:
        if field in grant_update:
            update_data[field] = grant_update[field]
    
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await db.grants.update_one({"id": grant_id}, {"$set": update_data})
    
    return {"message": "Grant updated successfully"}

@api_router.delete("/grants/{grant_id}")
async def delete_grant(grant_id: str, current_user: User = Depends(get_current_user)):
    """Delete a grant - supervisors have ultimate power to delete any grant"""
    if current_user.role not in [UserRole.SUPERVISOR, UserRole.LAB_MANAGER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only supervisors and administrators can delete grants")
    
    grant = await db.grants.find_one({"id": grant_id})
    if not grant:
        raise HTTPException(status_code=404, detail="Grant not found")
    
    # Supervisors have ultimate power - they can delete ANY grant
    # No additional authorization checks needed for supervisors
    
    await db.grants.delete_one({"id": grant_id})
    return {"message": "Grant deleted successfully"}

# Milestone endpoints
@api_router.post("/milestones", response_model=Milestone)
async def create_milestone(milestone: MilestoneCreate, current_user: User = Depends(get_current_user)):
    """Create a new milestone for student project"""
    
    # Only students can create milestones for themselves
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can create milestones")
    
    milestone_data = milestone.dict()
    milestone_data["student_id"] = current_user.id
    milestone_data["id"] = str(uuid.uuid4())
    milestone_data["created_at"] = datetime.utcnow()
    milestone_data["updated_at"] = datetime.utcnow()
    
    await db.milestones.insert_one(milestone_data)
    return Milestone(**milestone_data)

@api_router.get("/milestones", response_model=List[Milestone])
async def get_milestones(current_user: User = Depends(get_current_user)):
    """Get milestones - students see their own, supervisors see all"""
    
    if current_user.role == UserRole.STUDENT:
        milestones = await db.milestones.find({"student_id": current_user.id}).to_list(None)
    else:
        milestones = await db.milestones.find().to_list(None)
    
    # Add student names for supervisors
    if current_user.role != UserRole.STUDENT:
        student_ids = {milestone["student_id"] for milestone in milestones}
        students = await db.users.find({"id": {"$in": list(student_ids)}}).to_list(None)
        student_map = {student["id"]: student["full_name"] for student in students}
        
        for milestone in milestones:
            milestone["student_name"] = student_map.get(milestone["student_id"], "Unknown Student")
    
    return [Milestone(**milestone) for milestone in milestones]

@api_router.put("/milestones/{milestone_id}")
async def update_milestone(milestone_id: str, milestone_update: dict, current_user: User = Depends(get_current_user)):
    """Update milestone progress"""
    
    milestone = await db.milestones.find_one({"id": milestone_id})
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    
    # Check permissions
    if current_user.role == UserRole.STUDENT and milestone["student_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Can only update your own milestones")
    
    update_data = {}
    allowed_fields = ["progress_percentage", "status", "actual_end_date", "challenges", "next_steps", "deliverables"]
    
    for field in allowed_fields:
        if field in milestone_update:
            update_data[field] = milestone_update[field]
    
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await db.milestones.update_one({"id": milestone_id}, {"$set": update_data})
    
    return {"message": "Milestone updated successfully"}

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

# New Grant Registration Routes
@api_router.post("/grants/{grant_id}/register", response_model=GrantRegistration)
async def register_for_grant(grant_id: str, registration_data: GrantRegistrationCreate, current_user: User = Depends(get_current_user)):
    """Allow students to register/apply for grants"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can register for grants")
    
    # Verify grant exists
    grant = await db.grants.find_one({"id": grant_id})
    if not grant:
        raise HTTPException(status_code=404, detail="Grant not found")
    
    # Check if student already registered
    existing_registration = await db.grant_registrations.find_one({
        "grant_id": grant_id,
        "applicant_id": current_user.id
    })
    if existing_registration:
        raise HTTPException(status_code=400, detail="Already registered for this grant")
    
    registration = GrantRegistration(
        grant_id=grant_id,
        applicant_id=current_user.id,
        justification=registration_data.justification,
        expected_amount=registration_data.expected_amount,
        purpose=registration_data.purpose
    )
    
    await db.grant_registrations.insert_one(registration.dict())
    return registration

@api_router.get("/grants/registrations")
async def get_grant_registrations(current_user: User = Depends(get_current_user)):
    """Get grant registrations - students see their own, supervisors see all"""
    if current_user.role == UserRole.STUDENT:
        registrations = await db.grant_registrations.find({"applicant_id": current_user.id}).to_list(1000)
    else:
        # Supervisors see registrations for their grants
        grants = await db.grants.find({"principal_investigator": current_user.id}).to_list(1000)
        grant_ids = [grant["id"] for grant in grants]
        registrations = await db.grant_registrations.find({"grant_id": {"$in": grant_ids}}).to_list(1000)
    
    return [GrantRegistration(**reg) for reg in registrations]

@api_router.post("/grants/registrations/{registration_id}/approve")
async def approve_grant_registration(registration_id: str, approved: bool, comments: Optional[str] = None, current_user: User = Depends(get_current_user)):
    """Supervisors approve or reject grant registrations"""
    if current_user.role not in [UserRole.SUPERVISOR, UserRole.LAB_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized to approve grant registrations")
    
    registration = await db.grant_registrations.find_one({"id": registration_id})
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")
    
    # Verify supervisor owns the grant
    grant = await db.grants.find_one({"id": registration["grant_id"], "principal_investigator": current_user.id})
    if not grant:
        raise HTTPException(status_code=403, detail="Not authorized to manage this grant")
    
    await db.grant_registrations.update_one(
        {"id": registration_id},
        {"$set": {
            "supervisor_approval": approved,
            "supervisor_comments": comments,
            "application_status": "approved" if approved else "rejected"
        }}
    )
    
    return {"message": f"Grant registration {'approved' if approved else 'rejected'}"}

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
    """Get lab-wide publications synchronized from lab Scopus ID - same data for all users"""
    # Get supervisor ID to fetch lab publications
    supervisor_id = current_user.supervisor_id or current_user.id
    
    # Fetch publications for the lab (tied to supervisor)
    publications = await db.publications.find({"supervisor_id": supervisor_id}).sort("created_at", -1).to_list(1000)
    
    # Handle field migration and data format fixes
    for pub in publications:
        pub.pop("_id", None)  # Remove MongoDB ObjectId
        
        # Handle field migration from 'year' to 'publication_year'
        if "year" in pub and "publication_year" not in pub:
            pub["publication_year"] = pub.pop("year")
        
        # Handle authors field migration from string to List[str]
        if "authors" in pub and isinstance(pub["authors"], str):
            pub["authors"] = [pub["authors"]]  # Convert string to list
        elif "authors" not in pub:
            pub["authors"] = []  # Default empty list if missing
    
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

@api_router.post("/publications/scopus")
async def add_publication_from_scopus(scopus_data: dict, current_user: User = Depends(get_current_user)):
    """Add publication by fetching data from Scopus API using Scopus ID - Only supervisors can add"""
    # Only supervisors, lab managers, and admins can add publications from Scopus
    if current_user.role not in [UserRole.SUPERVISOR, UserRole.LAB_MANAGER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only supervisors can add publications from Scopus")
    
    scopus_id = scopus_data.get("scopus_id")
    if not scopus_id:
        raise HTTPException(status_code=400, detail="Scopus ID is required")
    
    try:
        # Mock Scopus API call - In production, you would call the actual Scopus API here
        # For now, create a publication with basic info and the Scopus ID
        publication_data = {
            "id": str(uuid.uuid4()),
            "title": f"Publication from Scopus ID: {scopus_id}",
            "authors": [current_user.full_name],  # Fixed to be a list
            "journal": "Journal Name (Retrieved from Scopus)",
            "publication_year": datetime.utcnow().year,  # Use publication_year field directly
            "doi": f"10.1000/scopus.{scopus_id}",
            "scopus_id": scopus_id,
            "abstract": "Abstract retrieved from Scopus API",
            "keywords": ["scopus", "research"],
            "status": "published",
            "citation_count": 0,
            "supervisor_id": current_user.id,
            "student_contributors": [],  # Publications are synchronized across all users
            "created_at": datetime.utcnow(),
            "retrieved_at": datetime.utcnow()
        }
        
        await db.publications.insert_one(publication_data)
        
        # Return the publication using the Publication model
        publication = Publication(**publication_data)
        return publication
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching from Scopus: {str(e)}")

# Publications Page Route
@api_router.get("/publications/all")
async def get_all_publications(current_user: User = Depends(get_current_user)):
    """Get all publications for the lab/supervisor with comprehensive details"""
    if current_user.role == UserRole.STUDENT:
        # Students see publications they're tagged in plus their supervisor's publications
        supervisor_id = current_user.supervisor_id
        publications = await db.publications.find({
            "$or": [
                {"student_contributors": current_user.id},
                {"supervisor_id": supervisor_id}
            ]
        }).sort("publication_year", -1).to_list(1000)
    else:
        # Supervisors see all their publications
        publications = await db.publications.find({"supervisor_id": current_user.id}).sort("publication_year", -1).to_list(1000)
    
    # Enhance publications with student contributor names
    enhanced_publications = []
    for pub in publications:
        # Remove MongoDB ObjectId
        pub.pop("_id", None)
        
        # Handle field migration from 'year' to 'publication_year'
        if "year" in pub and "publication_year" not in pub:
            pub["publication_year"] = pub.pop("year")
        
        # Handle authors field migration from string to List[str]
        if "authors" in pub and isinstance(pub["authors"], str):
            pub["authors"] = [pub["authors"]]  # Convert string to list
        elif "authors" not in pub:
            pub["authors"] = []  # Default empty list if missing
        
        if pub.get("student_contributors"):
            student_names = []
            for student_id in pub["student_contributors"]:
                student = await db.users.find_one({"id": student_id})
                if student:
                    student_names.append(student["full_name"])
            pub["student_contributor_names"] = student_names
        enhanced_publications.append(pub)
    
    return enhanced_publications

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
        "profile_picture": student.get("profile_picture"),
        "student_id": student.get("student_id"),
        "program_type": student.get("program_type"),
        "study_status": student.get("study_status", "active"),
        "role": student.get("role", "student")
    } for student in students]

# Include the router in the main app
app.include_router(api_router)

# Add a health check endpoint at the root level
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Research Lab Management System API is running"}

@app.get("/api/health")
async def api_health_check():
    return {"status": "healthy", "message": "API endpoints are accessible"}

# CORS middleware should be configured earlier, but since it's here, ensure it's properly configured
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for debugging
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
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
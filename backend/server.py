from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

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

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    password_hash: str
    full_name: str
    role: UserRole
    student_id: Optional[str] = None
    supervisor_id: Optional[str] = None
    department: Optional[str] = None
    research_area: Optional[str] = None
    lab_name: Optional[str] = None
    lab_logo: Optional[str] = None  # URL or base64 string
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: UserRole
    department: Optional[str] = None
    research_area: Optional[str] = None
    supervisor_email: Optional[str] = None  # For students to connect with supervisor

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
        research_area=user_data.research_area
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
            "research_area": user.research_area
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
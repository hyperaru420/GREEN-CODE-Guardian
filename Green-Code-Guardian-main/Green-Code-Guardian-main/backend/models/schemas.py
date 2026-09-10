from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User Models
class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    created_at: datetime

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Token Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Metrics Models
class MetricsData(BaseModel):
    project_id: str
    cpu_usage: float
    memory_usage: float
    execution_time: float
    disk_usage: float
    network_usage: Optional[float] = 0.0
    timestamp: Optional[datetime] = None

class MetricsResponse(MetricsData):
    id: str

# Project Models
class ProjectCreate(BaseModel):
    project_name: str
    region: Optional[str] = "us-east"

class ProjectResponse(BaseModel):
    id: str
    project_name: str
    cpu_usage: float
    memory_usage: float
    execution_time: float
    carbon_emissions: float
    green_score: float
    timestamp: datetime
    region: str

# Carbon Models
class CarbonEstimate(BaseModel):
    project_id: str
    energy_consumed: float
    carbon_emissions: float
    region: str
    carbon_intensity: float
    timestamp: datetime

# Green Score
class GreenScoreResponse(BaseModel):
    project_id: str
    score: float
    grade: str
    color: str
    breakdown: dict
    timestamp: datetime

# AI Suggestion Models
class Suggestion(BaseModel):
    category: str
    title: str
    description: str
    severity: str  # low, medium, high
    estimated_savings: float
    code_example: Optional[str] = None

class SuggestionsResponse(BaseModel):
    project_id: str
    suggestions: List[Suggestion]
    total_potential_savings: float
    generated_at: datetime

# Certificate Models
class CertificateCreate(BaseModel):
    project_name: str
    project_id: Optional[str] = None

class CertificateResponse(BaseModel):
    certificate_id: str
    project_name: str
    carbon_value: float
    green_score: float


# Webhook Models
class GitHubPushPayload(BaseModel):
    repository: dict
    ref: str
    commits: List[dict]

class WebhookEvent(BaseModel):
    source: str  # github, gitlab, custom
    event_type: str
    repo: str
    timestamp: Optional[datetime] = None

class WebhookResponse(BaseModel):
    status: str
    webhook_id: str
    event_type: str
    repo: str


# Notification Models
class NotificationPreference(BaseModel):
    email_notifications: Optional[bool] = True
    slack_notifications: Optional[bool] = False
    carbon_threshold_alerts: Optional[bool] = True
    achievement_notifications: Optional[bool] = True
    daily_digest: Optional[bool] = False
    carbon_threshold: Optional[float] = 100.0

class Notification(BaseModel):
    user_id: str
    type: str  # carbon_alert, achievement, digest, etc
    message: str
    created_at: Optional[datetime] = None
    read: Optional[bool] = False


# Team Models
class TeamCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    owner_id: str
    public: Optional[bool] = False

class TeamMember(BaseModel):
    id: str
    name: str
    email: str
    role: str  # owner, member

class TeamResponse(BaseModel):
    team_id: str
    name: str
    description: str
    owner_id: str
    members: List[TeamMember]
    created_at: datetime
    blockchain_hash: Optional[str] = None
    date: datetime
    optimization_status: str

from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from enum import Enum
from models import IndustryType, ComplianceStandard
import uuid

# User and Authentication Models
class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    VIEWER = "viewer"

class TenantPlan(str, Enum):
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole = UserRole.VIEWER
    tenant_id: str
    is_active: bool = True
    is_verified: bool = False
    is_superuser: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    profile_picture: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    preferences: dict = Field(default_factory=dict)

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: UserRole = UserRole.VIEWER
    department: Optional[str] = None
    phone: Optional[str] = None

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRole] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    preferences: Optional[dict] = None

class Tenant(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    domain: str  # e.g., "acme-corp"
    plan: TenantPlan = TenantPlan.PROFESSIONAL
    industry: IndustryType
    employee_count: int
    annual_revenue: float
    headquarters_location: str
    compliance_standards: List[ComplianceStandard] = []
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    subscription_expires: Optional[datetime] = None
    max_users: int = 10
    current_users: int = 0
    features_enabled: List[str] = Field(default_factory=list)
    settings: dict = Field(default_factory=dict)

class TenantCreate(BaseModel):
    name: str
    domain: str
    industry: IndustryType
    employee_count: int
    annual_revenue: float
    headquarters_location: str
    plan: TenantPlan = TenantPlan.PROFESSIONAL
    compliance_standards: List[ComplianceStandard] = []

class SSOProvider(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    provider_type: str  # "saml", "oidc", "oauth2"
    provider_name: str  # "Azure AD", "Okta", "Google Workspace"
    is_active: bool = True
    configuration: dict  # Provider-specific config
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Permission and Role Models
class Permission(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    resource: str  # "companies", "emissions", "marketplace", etc.
    action: str    # "read", "write", "delete", "admin"
    description: str

class RolePermissions(BaseModel):
    role: UserRole
    permissions: List[Permission]

# Audit and Security Models
class AuditLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    user_id: str
    action: str
    resource: str
    resource_id: Optional[str] = None
    details: dict = Field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = "success"  # success, failed, warning

class SecuritySettings(BaseModel):
    tenant_id: str
    password_policy: dict = Field(default_factory=lambda: {
        "min_length": 8,
        "require_uppercase": True,
        "require_lowercase": True,
        "require_numbers": True,
        "require_special_chars": True,
        "max_age_days": 90
    })
    session_timeout_minutes: int = 480  # 8 hours
    max_failed_attempts: int = 5
    lockout_duration_minutes: int = 30
    require_mfa: bool = False
    allowed_ip_ranges: List[str] = Field(default_factory=list)
    sso_required: bool = False

# API Key Models for Integrations
class APIKey(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    name: str
    key_hash: str  # Hashed version of the API key
    permissions: List[str]
    is_active: bool = True
    created_by: str  # user_id
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    usage_count: int = 0

# Feature flag system
class FeatureFlag(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    is_enabled: bool = False
    tenant_ids: List[str] = Field(default_factory=list)  # If empty, applies to all
    user_roles: List[UserRole] = Field(default_factory=list)  # If empty, applies to all roles
    plan_types: List[TenantPlan] = Field(default_factory=list)  # If empty, applies to all plans
    percentage_rollout: int = 100  # 0-100 percentage
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
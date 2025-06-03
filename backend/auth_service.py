from typing import Optional, Dict, List
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorCollection
import hashlib
import secrets
import logging
from auth_models import User, Tenant, UserRole, AuditLog, APIKey, SecuritySettings
import os

logger = logging.getLogger(__name__)

class AuthenticationService:
    """Enterprise authentication and authorization service"""
    
    def __init__(self, db):
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.SECRET_KEY = os.getenv("JWT_SECRET_KEY", "climabill-secret-key-change-in-production")
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        self.REFRESH_TOKEN_EXPIRE_DAYS = 7
        
        # Collections
        self.users: AsyncIOMotorCollection = db.users
        self.tenants: AsyncIOMotorCollection = db.tenants
        self.audit_logs: AsyncIOMotorCollection = db.audit_logs
        self.api_keys: AsyncIOMotorCollection = db.api_keys
        self.security_settings: AsyncIOMotorCollection = db.security_settings
        
        # Default permissions by role
        self.role_permissions = {
            UserRole.ADMIN: [
                "companies:admin", "emissions:admin", "marketplace:admin", 
                "supply_chain:admin", "compliance:admin", "users:admin"
            ],
            UserRole.MANAGER: [
                "companies:write", "emissions:write", "marketplace:write",
                "supply_chain:write", "compliance:write", "users:read"
            ],
            UserRole.ANALYST: [
                "companies:read", "emissions:write", "marketplace:read",
                "supply_chain:read", "compliance:read"
            ],
            UserRole.VIEWER: [
                "companies:read", "emissions:read", "marketplace:read",
                "supply_chain:read", "compliance:read"
            ]
        }
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plaintext password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt
    
    def create_refresh_token(self, data: dict):
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt
    
    async def authenticate_user(self, email: str, password: str, tenant_domain: str) -> Optional[Dict]:
        """Authenticate user with email, password, and tenant"""
        try:
            # Get tenant
            tenant = await self.tenants.find_one({"domain": tenant_domain, "is_active": True})
            if not tenant:
                await self.log_security_event(None, "failed_login", "tenant_not_found", 
                                            {"tenant_domain": tenant_domain})
                return None
            
            # Get user
            user = await self.users.find_one({
                "email": email, 
                "tenant_id": tenant["id"], 
                "is_active": True
            })
            
            if not user:
                await self.log_security_event(tenant["id"], "failed_login", "user_not_found", 
                                            {"email": email})
                return None
            
            # Check password
            if not self.verify_password(password, user["hashed_password"]):
                await self.log_security_event(tenant["id"], "failed_login", "invalid_password", 
                                            {"user_id": user["id"]})
                return None
            
            # Update last login
            await self.users.update_one(
                {"id": user["id"]},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            
            await self.log_security_event(tenant["id"], "successful_login", "user_authenticated", 
                                        {"user_id": user["id"]})
            
            return {"user": user, "tenant": tenant}
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    async def get_current_user(self, token: str) -> Optional[Dict]:
        """Get current user from JWT token"""
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            user_id: str = payload.get("sub")
            tenant_id: str = payload.get("tenant_id")
            
            if user_id is None or tenant_id is None:
                return None
            
            user = await self.users.find_one({"id": user_id, "is_active": True})
            tenant = await self.tenants.find_one({"id": tenant_id, "is_active": True})
            
            if user is None or tenant is None:
                return None
            
            return {"user": user, "tenant": tenant}
            
        except JWTError:
            return None
    
    async def create_user(self, user_data: Dict, tenant_id: str, created_by: str) -> Dict:
        """Create a new user in the tenant"""
        # Check if user already exists
        existing_user = await self.users.find_one({
            "email": user_data["email"],
            "tenant_id": tenant_id
        })
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists in this tenant"
            )
        
        # Hash password
        hashed_password = self.get_password_hash(user_data["password"])
        
        # Create user document
        user = {
            "id": user_data.get("id", secrets.token_urlsafe(16)),
            "email": user_data["email"],
            "first_name": user_data["first_name"],
            "last_name": user_data["last_name"],
            "role": user_data.get("role", UserRole.VIEWER),
            "tenant_id": tenant_id,
            "hashed_password": hashed_password,
            "is_active": True,
            "is_verified": False,
            "is_superuser": False,
            "created_at": datetime.utcnow(),
            "department": user_data.get("department"),
            "phone": user_data.get("phone"),
            "preferences": {}
        }
        
        await self.users.insert_one(user)
        
        # Remove password from response
        user.pop("hashed_password", None)
        
        await self.log_audit_event(tenant_id, created_by, "create_user", "users", user["id"])
        
        return user
    
    async def check_permission(self, user: Dict, resource: str, action: str) -> bool:
        """Check if user has permission for resource action"""
        user_role = UserRole(user["role"])
        required_permission = f"{resource}:{action}"
        user_permissions = self.role_permissions.get(user_role, [])
        
        # Check exact permission or admin permission
        return (required_permission in user_permissions or 
                f"{resource}:admin" in user_permissions or
                "admin" in user_permissions)
    
    async def require_permission(self, user: Dict, resource: str, action: str):
        """Raise exception if user doesn't have permission"""
        if not await self.check_permission(user, resource, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions for {resource}:{action}"
            )
    
    async def create_api_key(self, tenant_id: str, user_id: str, name: str, permissions: List[str]) -> Dict:
        """Create an API key for programmatic access"""
        # Generate API key
        api_key = f"cb_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        api_key_doc = {
            "id": secrets.token_urlsafe(16),
            "tenant_id": tenant_id,
            "name": name,
            "key_hash": key_hash,
            "permissions": permissions,
            "is_active": True,
            "created_by": user_id,
            "created_at": datetime.utcnow(),
            "usage_count": 0
        }
        
        await self.api_keys.insert_one(api_key_doc)
        
        await self.log_audit_event(tenant_id, user_id, "create_api_key", "api_keys", api_key_doc["id"])
        
        # Return the actual key only once
        api_key_doc["api_key"] = api_key
        api_key_doc.pop("key_hash")
        
        return api_key_doc
    
    async def authenticate_api_key(self, api_key: str) -> Optional[Dict]:
        """Authenticate request using API key"""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        api_key_doc = await self.api_keys.find_one({
            "key_hash": key_hash,
            "is_active": True
        })
        
        if not api_key_doc:
            return None
        
        # Update usage
        await self.api_keys.update_one(
            {"id": api_key_doc["id"]},
            {
                "$set": {"last_used": datetime.utcnow()},
                "$inc": {"usage_count": 1}
            }
        )
        
        # Get tenant
        tenant = await self.tenants.find_one({"id": api_key_doc["tenant_id"]})
        
        return {
            "api_key": api_key_doc,
            "tenant": tenant,
            "permissions": api_key_doc["permissions"]
        }
    
    async def log_audit_event(self, tenant_id: str, user_id: str, action: str, 
                            resource: str, resource_id: Optional[str] = None, 
                            details: Optional[Dict] = None, request: Optional[Request] = None):
        """Log audit event for compliance and security"""
        audit_log = {
            "id": secrets.token_urlsafe(16),
            "tenant_id": tenant_id,
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "resource_id": resource_id,
            "details": details or {},
            "timestamp": datetime.utcnow(),
            "status": "success"
        }
        
        if request:
            audit_log["ip_address"] = request.client.host if request.client else None
            audit_log["user_agent"] = request.headers.get("user-agent")
        
        await self.audit_logs.insert_one(audit_log)
    
    async def log_security_event(self, tenant_id: Optional[str], event_type: str, 
                                event_details: str, metadata: Dict = None):
        """Log security-related events"""
        security_log = {
            "id": secrets.token_urlsafe(16),
            "tenant_id": tenant_id,
            "user_id": None,
            "action": event_type,
            "resource": "security",
            "resource_id": None,
            "details": {
                "event_details": event_details,
                "metadata": metadata or {}
            },
            "timestamp": datetime.utcnow(),
            "status": "warning" if "failed" in event_type else "info"
        }
        
        await self.audit_logs.insert_one(security_log)
    
    async def get_tenant_security_settings(self, tenant_id: str) -> Dict:
        """Get security settings for tenant"""
        settings = await self.security_settings.find_one({"tenant_id": tenant_id})
        
        if not settings:
            # Create default settings
            default_settings = {
                "tenant_id": tenant_id,
                "password_policy": {
                    "min_length": 8,
                    "require_uppercase": True,
                    "require_lowercase": True,
                    "require_numbers": True,
                    "require_special_chars": True,
                    "max_age_days": 90
                },
                "session_timeout_minutes": 480,
                "max_failed_attempts": 5,
                "lockout_duration_minutes": 30,
                "require_mfa": False,
                "allowed_ip_ranges": [],
                "sso_required": False
            }
            
            await self.security_settings.insert_one(default_settings)
            return default_settings
        
        return settings

# Dependency functions for FastAPI
security = HTTPBearer()

async def get_current_user_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthenticationService = None
) -> Dict:
    """FastAPI dependency to get current authenticated user"""
    if not auth_service:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service not available"
        )
    
    user_data = await auth_service.get_current_user(credentials.credentials)
    
    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_data

def require_role(required_role: UserRole):
    """Decorator to require specific role"""
    def role_checker(current_user: Dict = Depends(get_current_user_dependency)):
        user_role = UserRole(current_user["user"]["role"])
        role_hierarchy = {
            UserRole.VIEWER: 0,
            UserRole.ANALYST: 1,
            UserRole.MANAGER: 2,
            UserRole.ADMIN: 3
        }
        
        if role_hierarchy[user_role] < role_hierarchy[required_role]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_role.value} role or higher"
            )
        
        return current_user
    
    return role_checker

def require_permission(resource: str, action: str):
    """Decorator to require specific permission"""
    def permission_checker(
        current_user: Dict = Depends(get_current_user_dependency),
        auth_service: AuthenticationService = None
    ):
        if not auth_service:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service not available"
            )
        
        if not auth_service.check_permission(current_user["user"], resource, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions for {resource}:{action}"
            )
        
        return current_user
    
    return permission_checker
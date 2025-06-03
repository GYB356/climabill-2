"""
Security Service for ClimaBill - Comprehensive security hardening
Includes rate limiting, audit logging, input validation, and API key authentication
"""

import logging
import hashlib
import secrets
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import re
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
import ipaddress
from user_agents import parse

logger = logging.getLogger(__name__)

class SecurityService:
    """Comprehensive security service for ClimaBill"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.audit_logs: AsyncIOMotorCollection = db.audit_logs
        self.api_keys: AsyncIOMotorCollection = db.api_keys
        self.rate_limit_cache: Dict[str, Dict] = {}
        
        # Security configurations
        self.MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
        self.MAX_STRING_LENGTH = 10000
        self.SUSPICIOUS_PATTERNS = [
            r'<script[^>]*>.*?</script>',  # XSS
            r'javascript:',  # JavaScript injection
            r'on\w+\s*=',  # Event handlers
            r'union\s+select',  # SQL injection
            r'insert\s+into',  # SQL injection
            r'delete\s+from',  # SQL injection
            r'drop\s+table',  # SQL injection
            r'\$\{.*\}',  # Template injection
            r'<%.*%>',  # Template injection
        ]
        
        # Rate limiting configurations per endpoint type
        self.RATE_LIMITS = {
            "auth": {"requests": 5, "window": 300},  # 5 requests per 5 minutes for auth
            "api": {"requests": 100, "window": 60},  # 100 requests per minute for API
            "ai": {"requests": 10, "window": 60},    # 10 AI requests per minute
            "upload": {"requests": 5, "window": 300}  # 5 uploads per 5 minutes
        }
    
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check for forwarded headers first (common in proxy setups)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        if hasattr(request.client, "host"):
            return request.client.host
        
        return "unknown"
    
    def detect_endpoint_type(self, path: str) -> str:
        """Determine endpoint type for rate limiting"""
        if "/auth/" in path:
            return "auth"
        elif "/ai/" in path:
            return "ai"
        elif "/upload" in path:
            return "upload"
        else:
            return "api"
    
    async def check_rate_limit(self, request: Request) -> bool:
        """Check if request exceeds rate limits"""
        client_ip = self.get_client_ip(request)
        endpoint_type = self.detect_endpoint_type(request.url.path)
        
        rate_config = self.RATE_LIMITS.get(endpoint_type, self.RATE_LIMITS["api"])
        
        # Create cache key
        cache_key = f"{client_ip}:{endpoint_type}"
        current_time = datetime.utcnow()
        
        # Check in-memory cache first
        if cache_key in self.rate_limit_cache:
            cache_entry = self.rate_limit_cache[cache_key]
            
            # Clean old requests outside the window
            window_start = current_time - timedelta(seconds=rate_config["window"])
            cache_entry["requests"] = [
                req_time for req_time in cache_entry["requests"] 
                if req_time > window_start
            ]
            
            # Check if limit exceeded
            if len(cache_entry["requests"]) >= rate_config["requests"]:
                await self.log_security_event(
                    request=request,
                    event_type="RATE_LIMIT_EXCEEDED",
                    details={
                        "endpoint_type": endpoint_type,
                        "current_requests": len(cache_entry["requests"]),
                        "limit": rate_config["requests"],
                        "window_seconds": rate_config["window"]
                    }
                )
                return False
            
            # Add current request
            cache_entry["requests"].append(current_time)
        else:
            # Initialize cache entry
            self.rate_limit_cache[cache_key] = {
                "requests": [current_time]
            }
        
        return True
    
    def validate_input_string(self, value: str, field_name: str) -> str:
        """Validate and sanitize string input"""
        if not isinstance(value, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Field '{field_name}' must be a string"
            )
        
        # Check length
        if len(value) > self.MAX_STRING_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Field '{field_name}' exceeds maximum length of {self.MAX_STRING_LENGTH}"
            )
        
        # Check for suspicious patterns
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Field '{field_name}' contains potentially malicious content"
                )
        
        # Basic HTML entity encoding for safety
        value = value.replace("&", "&amp;")
        value = value.replace("<", "&lt;")
        value = value.replace(">", "&gt;")
        value = value.replace("\"", "&quot;")
        value = value.replace("'", "&#x27;")
        
        return value.strip()
    
    def validate_email(self, email: str) -> str:
        """Validate email format"""
        email = self.validate_input_string(email, "email")
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        return email.lower()
    
    def validate_numeric_input(self, value: Any, field_name: str, min_val: Optional[float] = None, max_val: Optional[float] = None) -> float:
        """Validate numeric input"""
        try:
            num_value = float(value)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Field '{field_name}' must be a valid number"
            )
        
        if min_val is not None and num_value < min_val:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Field '{field_name}' must be at least {min_val}"
            )
        
        if max_val is not None and num_value > max_val:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Field '{field_name}' must be at most {max_val}"
            )
        
        return num_value
    
    async def validate_request_size(self, request: Request) -> bool:
        """Check if request size is within limits"""
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > self.MAX_REQUEST_SIZE:
                    await self.log_security_event(
                        request=request,
                        event_type="OVERSIZED_REQUEST",
                        details={"content_length": size, "max_allowed": self.MAX_REQUEST_SIZE}
                    )
                    return False
            except ValueError:
                return False
        
        return True
    
    async def log_security_event(self, request: Request, event_type: str, details: Dict[str, Any], severity: str = "warning"):
        """Log security-related events"""
        try:
            client_ip = self.get_client_ip(request)
            user_agent = request.headers.get("user-agent", "unknown")
            
            # Parse user agent for additional context
            parsed_ua = parse(user_agent)
            
            audit_entry = {
                "timestamp": datetime.utcnow(),
                "event_type": event_type,
                "severity": severity,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "browser": f"{parsed_ua.browser.family} {parsed_ua.browser.version_string}" if parsed_ua.browser else "unknown",
                "os": f"{parsed_ua.os.family} {parsed_ua.os.version_string}" if parsed_ua.os else "unknown",
                "request_path": request.url.path,
                "request_method": request.method,
                "headers": dict(request.headers),
                "details": details
            }
            
            # Add tenant context if available
            if hasattr(request.state, "tenant_context"):
                audit_entry["tenant_id"] = request.state.tenant_context["tenant_id"]
                audit_entry["user_id"] = request.state.tenant_context["user_id"]
            
            await self.audit_logs.insert_one(audit_entry)
            
            # Log to application logger as well
            logger.warning(f"Security Event [{event_type}]: {client_ip} - {details}")
            
        except Exception as e:
            # Don't let audit logging break the application
            logger.error(f"Failed to log security event: {e}")
    
    async def log_access_event(self, request: Request, response_status: int, response_time_ms: float):
        """Log successful access events for audit trail"""
        try:
            client_ip = self.get_client_ip(request)
            
            audit_entry = {
                "timestamp": datetime.utcnow(),
                "event_type": "API_ACCESS",
                "severity": "info",
                "client_ip": client_ip,
                "request_path": request.url.path,
                "request_method": request.method,
                "response_status": response_status,
                "response_time_ms": response_time_ms,
                "user_agent": request.headers.get("user-agent", "unknown")
            }
            
            # Add tenant context if available
            if hasattr(request.state, "tenant_context"):
                audit_entry["tenant_id"] = request.state.tenant_context["tenant_id"]
                audit_entry["user_id"] = request.state.tenant_context["user_id"]
            
            await self.audit_logs.insert_one(audit_entry)
            
        except Exception as e:
            logger.error(f"Failed to log access event: {e}")
    
    async def generate_api_key(self, name: str, tenant_id: str, user_id: str, permissions: List[str]) -> Dict[str, str]:
        """Generate a new API key for programmatic access"""
        # Generate secure API key
        api_key = "cb_" + secrets.token_urlsafe(32)
        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Store API key details
        key_record = {
            "id": secrets.token_urlsafe(16),
            "name": name,
            "api_key_hash": api_key_hash,
            "tenant_id": tenant_id,
            "created_by": user_id,
            "permissions": permissions,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "last_used": None,
            "usage_count": 0
        }
        
        await self.api_keys.insert_one(key_record)
        
        return {
            "api_key": api_key,
            "key_id": key_record["id"],
            "name": name,
            "permissions": permissions
        }
    
    async def validate_api_key(self, api_key: str) -> Optional[Dict]:
        """Validate API key and return associated metadata"""
        if not api_key.startswith("cb_"):
            return None
        
        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        key_record = await self.api_keys.find_one({
            "api_key_hash": api_key_hash,
            "is_active": True
        })
        
        if key_record:
            # Update usage statistics
            await self.api_keys.update_one(
                {"_id": key_record["_id"]},
                {
                    "$set": {"last_used": datetime.utcnow()},
                    "$inc": {"usage_count": 1}
                }
            )
            
            return key_record
        
        return None
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers to add to responses"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https:; connect-src 'self' https:; frame-ancestors 'none';",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

# Security middleware
class SecurityMiddleware:
    """Middleware for comprehensive security checks"""
    
    def __init__(self, security_service: SecurityService):
        self.security_service = security_service
    
    async def __call__(self, request: Request, call_next):
        start_time = datetime.utcnow()
        
        # Skip security checks for certain paths
        skip_paths = ["/docs", "/redoc", "/openapi.json", "/health"]
        if any(request.url.path.startswith(path) for path in skip_paths):
            response = await call_next(request)
            return response
        
        try:
            # Check request size
            if not await self.security_service.validate_request_size(request):
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="Request too large"
                )
            
            # Check rate limits
            if not await self.security_service.check_rate_limit(request):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )
            
            # Process request
            response = await call_next(request)
            
            # Add security headers
            security_headers = self.security_service.get_security_headers()
            for header, value in security_headers.items():
                response.headers[header] = value
            
            # Log successful access
            end_time = datetime.utcnow()
            response_time_ms = (end_time - start_time).total_seconds() * 1000
            
            await self.security_service.log_access_event(
                request, response.status_code, response_time_ms
            )
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            await self.security_service.log_security_event(
                request=request,
                event_type="SECURITY_MIDDLEWARE_ERROR",
                details={"error": str(e)},
                severity="error"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Security check failed"
            )

# API Key authentication
class APIKeyAuth:
    """API key authentication for programmatic access"""
    
    def __init__(self, security_service: SecurityService):
        self.security_service = security_service
    
    async def __call__(self, request: Request) -> Optional[Dict]:
        """Validate API key from request headers"""
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return None
        
        key_record = await self.security_service.validate_api_key(api_key)
        if not key_record:
            await self.security_service.log_security_event(
                request=request,
                event_type="INVALID_API_KEY",
                details={"api_key_prefix": api_key[:10] + "..."},
                severity="warning"
            )
            return None
        
        return key_record

# Dependency injection helpers
async def get_security_service(db) -> SecurityService:
    """FastAPI dependency to get security service"""
    return SecurityService(db)

def require_permission(required_permission: str):
    """Decorator to require specific permission for API key access"""
    def permission_checker(api_key_data: Optional[Dict] = Depends(APIKeyAuth)):
        if not api_key_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Valid API key required"
            )
        
        if required_permission not in api_key_data.get("permissions", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{required_permission}' required"
            )
        
        return api_key_data
    
    return permission_checker
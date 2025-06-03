from typing import Dict, Optional, List, Any
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from datetime import datetime
import logging
from auth_models import Tenant, TenantPlan, User
from jose import JWTError, jwt
import os

logger = logging.getLogger(__name__)

class MultiTenancyService:
    """
    Multi-tenancy service providing tenant isolation at the document level.
    All database operations are automatically scoped to the current tenant.
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.SECRET_KEY = os.getenv("JWT_SECRET_KEY", "climabill-secret-key-change-in-production")
        self.ALGORITHM = "HS256"
        
        # Core collections
        self.tenants: AsyncIOMotorCollection = db.tenants
        self.users: AsyncIOMotorCollection = db.users
        
        # Business collections - all will be tenant-scoped
        self.companies: AsyncIOMotorCollection = db.companies
        self.emissions: AsyncIOMotorCollection = db.emissions
        self.suppliers: AsyncIOMotorCollection = db.suppliers
        self.marketplace_listings: AsyncIOMotorCollection = db.marketplace_listings
        self.compliance_reports: AsyncIOMotorCollection = db.compliance_reports
        self.carbon_credits: AsyncIOMotorCollection = db.carbon_credits
        self.supply_chain_events: AsyncIOMotorCollection = db.supply_chain_events
        self.ai_chat_sessions: AsyncIOMotorCollection = db.ai_chat_sessions
        self.ai_chat_messages: AsyncIOMotorCollection = db.ai_chat_messages
        self.blockchain_transactions: AsyncIOMotorCollection = db.blockchain_transactions
        
    async def extract_tenant_from_token(self, token: str) -> Optional[Dict]:
        """Extract tenant information from JWT token"""
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            tenant_id = payload.get("tenant_id")
            user_id = payload.get("sub")
            
            if not tenant_id or not user_id:
                return None
                
            # Fetch tenant and user information
            tenant = await self.tenants.find_one({"id": tenant_id, "is_active": True})
            user = await self.users.find_one({"id": user_id, "tenant_id": tenant_id, "is_active": True})
            
            if not tenant or not user:
                return None
                
            return {
                "tenant": tenant,
                "user": user,
                "tenant_id": tenant_id,
                "user_id": user_id
            }
            
        except JWTError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
        except Exception as e:
            logger.error(f"Error extracting tenant from token: {e}")
            return None
    
    async def get_tenant_context(self, request: Request) -> Dict:
        """Get tenant context from request"""
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header"
            )
        
        token = auth_header.split(" ")[1]
        tenant_context = await self.extract_tenant_from_token(token)
        
        if not tenant_context:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token or tenant not found"
            )
        
        return tenant_context
    
    def add_tenant_filter(self, query: Dict, tenant_id: str) -> Dict:
        """Add tenant_id filter to any MongoDB query"""
        if query is None:
            query = {}
        query["tenant_id"] = tenant_id
        return query
    
    def add_tenant_to_document(self, document: Dict, tenant_id: str) -> Dict:
        """Add tenant_id to any document before insertion"""
        if document is None:
            document = {}
        document["tenant_id"] = tenant_id
        return document
    
    # Tenant-scoped database operations
    async def find_one_scoped(self, collection: AsyncIOMotorCollection, 
                             query: Dict, tenant_id: str) -> Optional[Dict]:
        """Find one document scoped to tenant"""
        scoped_query = self.add_tenant_filter(query, tenant_id)
        return await collection.find_one(scoped_query)
    
    async def find_many_scoped(self, collection: AsyncIOMotorCollection, 
                              query: Dict, tenant_id: str, 
                              limit: Optional[int] = None,
                              skip: Optional[int] = None,
                              sort: Optional[List] = None) -> List[Dict]:
        """Find multiple documents scoped to tenant"""
        scoped_query = self.add_tenant_filter(query, tenant_id)
        cursor = collection.find(scoped_query)
        
        if sort:
            cursor = cursor.sort(sort)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
            
        return await cursor.to_list(length=limit)
    
    async def insert_one_scoped(self, collection: AsyncIOMotorCollection, 
                               document: Dict, tenant_id: str) -> Dict:
        """Insert document with tenant scope"""
        scoped_document = self.add_tenant_to_document(document, tenant_id)
        result = await collection.insert_one(scoped_document)
        scoped_document["_id"] = result.inserted_id
        return scoped_document
    
    async def insert_many_scoped(self, collection: AsyncIOMotorCollection, 
                                documents: List[Dict], tenant_id: str) -> List[Dict]:
        """Insert multiple documents with tenant scope"""
        scoped_documents = [self.add_tenant_to_document(doc.copy(), tenant_id) for doc in documents]
        result = await collection.insert_many(scoped_documents)
        for i, doc in enumerate(scoped_documents):
            doc["_id"] = result.inserted_ids[i]
        return scoped_documents
    
    async def update_one_scoped(self, collection: AsyncIOMotorCollection, 
                               query: Dict, update: Dict, tenant_id: str) -> Dict:
        """Update one document scoped to tenant"""
        scoped_query = self.add_tenant_filter(query, tenant_id)
        result = await collection.update_one(scoped_query, update)
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}
    
    async def update_many_scoped(self, collection: AsyncIOMotorCollection, 
                                query: Dict, update: Dict, tenant_id: str) -> Dict:
        """Update multiple documents scoped to tenant"""
        scoped_query = self.add_tenant_filter(query, tenant_id)
        result = await collection.update_many(scoped_query, update)
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}
    
    async def delete_one_scoped(self, collection: AsyncIOMotorCollection, 
                               query: Dict, tenant_id: str) -> Dict:
        """Delete one document scoped to tenant"""
        scoped_query = self.add_tenant_filter(query, tenant_id)
        result = await collection.delete_one(scoped_query)
        return {"deleted_count": result.deleted_count}
    
    async def delete_many_scoped(self, collection: AsyncIOMotorCollection, 
                                query: Dict, tenant_id: str) -> Dict:
        """Delete multiple documents scoped to tenant"""
        scoped_query = self.add_tenant_filter(query, tenant_id)
        result = await collection.delete_many(scoped_query)
        return {"deleted_count": result.deleted_count}
    
    async def count_scoped(self, collection: AsyncIOMotorCollection, 
                          query: Dict, tenant_id: str) -> int:
        """Count documents scoped to tenant"""
        scoped_query = self.add_tenant_filter(query, tenant_id)
        return await collection.count_documents(scoped_query)
    
    async def aggregate_scoped(self, collection: AsyncIOMotorCollection, 
                              pipeline: List[Dict], tenant_id: str) -> List[Dict]:
        """Run aggregation pipeline scoped to tenant"""
        # Add tenant filter as the first stage of the pipeline
        tenant_match = {"$match": {"tenant_id": tenant_id}}
        scoped_pipeline = [tenant_match] + pipeline
        
        cursor = collection.aggregate(scoped_pipeline)
        return await cursor.to_list(length=None)
    
    # Tenant management operations
    async def create_tenant(self, tenant_data: Dict) -> Dict:
        """Create a new tenant"""
        tenant = {
            "id": tenant_data.get("id"),
            "name": tenant_data["name"],
            "domain": tenant_data["domain"],
            "plan": tenant_data.get("plan", TenantPlan.PROFESSIONAL),
            "industry": tenant_data["industry"],
            "employee_count": tenant_data["employee_count"],
            "annual_revenue": tenant_data["annual_revenue"],
            "headquarters_location": tenant_data["headquarters_location"],
            "compliance_standards": tenant_data.get("compliance_standards", []),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "max_users": tenant_data.get("max_users", 10),
            "current_users": 0,
            "features_enabled": tenant_data.get("features_enabled", [
                "carbon_tracking", "ai_chat", "marketplace", "compliance", "supply_chain"
            ]),
            "settings": tenant_data.get("settings", {})
        }
        
        result = await self.tenants.insert_one(tenant)
        tenant["_id"] = result.inserted_id
        return tenant
    
    async def get_tenant_by_domain(self, domain: str) -> Optional[Dict]:
        """Get tenant by domain"""
        return await self.tenants.find_one({"domain": domain, "is_active": True})
    
    async def get_tenant_by_id(self, tenant_id: str) -> Optional[Dict]:
        """Get tenant by ID"""
        return await self.tenants.find_one({"id": tenant_id, "is_active": True})
    
    async def validate_tenant_access(self, user_id: str, tenant_id: str) -> bool:
        """Validate that user has access to tenant"""
        user = await self.users.find_one({
            "id": user_id,
            "tenant_id": tenant_id,
            "is_active": True
        })
        return user is not None
    
    async def get_tenant_stats(self, tenant_id: str) -> Dict:
        """Get statistics for a tenant"""
        stats = {
            "total_users": await self.users.count_documents({"tenant_id": tenant_id, "is_active": True}),
            "total_companies": await self.count_scoped(self.companies, {}, tenant_id),
            "total_emissions": await self.count_scoped(self.emissions, {}, tenant_id),
            "total_suppliers": await self.count_scoped(self.suppliers, {}, tenant_id),
            "total_marketplace_listings": await self.count_scoped(self.marketplace_listings, {}, tenant_id),
            "total_compliance_reports": await self.count_scoped(self.compliance_reports, {}, tenant_id),
            "active_ai_sessions": await self.count_scoped(self.ai_chat_sessions, {"status": "active"}, tenant_id)
        }
        return stats

# Middleware for automatic tenant context injection
class TenantContextMiddleware:
    """Middleware to inject tenant context into request state"""
    
    def __init__(self, multitenancy_service: MultiTenancyService):
        self.multitenancy_service = multitenancy_service
    
    async def __call__(self, request: Request, call_next):
        # Skip tenant validation for certain endpoints
        skip_paths = [
            "/docs", "/redoc", "/openapi.json", "/health", 
            "/api/auth/login", "/api/auth/register"
        ]
        
        if any(request.url.path.startswith(path) for path in skip_paths):
            response = await call_next(request)
            return response
        
        try:
            # Extract tenant context and add to request state
            tenant_context = await self.multitenancy_service.get_tenant_context(request)
            request.state.tenant_context = tenant_context
            
        except HTTPException:
            # Let the endpoint handle the authentication error
            pass
        except Exception as e:
            logger.error(f"Error in tenant middleware: {e}")
        
        response = await call_next(request)
        return response

# Dependency injection helpers
async def get_tenant_context(request: Request) -> Dict:
    """FastAPI dependency to get tenant context from request state"""
    if not hasattr(request.state, "tenant_context"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No tenant context found"
        )
    return request.state.tenant_context

async def get_current_tenant(tenant_context: Dict = Depends(get_tenant_context)) -> Dict:
    """FastAPI dependency to get current tenant"""
    return tenant_context["tenant"]

async def get_current_user(tenant_context: Dict = Depends(get_tenant_context)) -> Dict:
    """FastAPI dependency to get current user"""
    return tenant_context["user"]

async def get_tenant_id(tenant_context: Dict = Depends(get_tenant_context)) -> str:
    """FastAPI dependency to get current tenant ID"""
    return tenant_context["tenant_id"]
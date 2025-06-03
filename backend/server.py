from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

# Add current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import our models and services
from models import *
from data_service import CarbonDataService
from ai_service import CarbonAIService
from carbon_calculator import CarbonCalculator

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Import blockchain, compliance, auth and multi-tenancy services
from blockchain_service import BlockchainService
from compliance_service import ComplianceService
from auth_service import AuthenticationService, get_current_user_dependency, require_permission
from multitenancy_service import MultiTenancyService, TenantContextMiddleware, get_tenant_context, get_current_tenant, get_current_user, get_tenant_id
from auth_models import User, Tenant, UserCreate, UserUpdate, TenantCreate, UserRole

# Initialize services
carbon_service = CarbonDataService(db)
ai_service = CarbonAIService()
calculator = CarbonCalculator()
blockchain_service = BlockchainService()
compliance_service = ComplianceService(db)
auth_service = AuthenticationService(db)
multitenancy_service = MultiTenancyService(db)

# Create the main app without a prefix
app = FastAPI(title="ClimaBill API", description="Carbon Intelligence and Billing Management Platform", version="1.0.0")

# Add tenant context middleware
tenant_middleware = TenantContextMiddleware(multitenancy_service)
app.middleware("http")(tenant_middleware)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Dependency to get services
async def get_carbon_service():
    return carbon_service

async def get_ai_service():
    return ai_service

async def get_auth_service():
    return auth_service

async def get_multitenancy_service():
    return multitenancy_service

# Health check endpoint (no authentication required)
@api_router.get("/")
async def root():
    return {"message": "ClimaBill API is running", "version": "1.0.0"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Authentication Endpoints (no tenant validation required)
@api_router.post("/auth/login")
async def login(
    email: str,
    password: str,
    multitenancy: MultiTenancyService = Depends(get_multitenancy_service)
):
    """Login with email and password, returns JWT token"""
    import hashlib
    from jose import jwt
    
    # Hash the provided password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    # Find user by email and password
    user = await multitenancy.users.find_one({
        "email": email,
        "hashed_password": hashed_password,
        "is_active": True
    })
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Get tenant information
    tenant = await multitenancy.get_tenant_by_id(user["tenant_id"])
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tenant not found or inactive"
        )
    
    # Create JWT token
    payload = {
        "sub": user["id"],
        "tenant_id": user["tenant_id"],
        "role": user["role"],
        "exp": datetime.utcnow() + timedelta(days=30),
        "iat": datetime.utcnow()
    }
    
    token = jwt.encode(payload, multitenancy.SECRET_KEY, algorithm="HS256")
    
    # Update last login
    await multitenancy.users.update_one(
        {"id": user["id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "role": user["role"]
        },
        "tenant": {
            "id": tenant["id"],
            "name": tenant["name"],
            "domain": tenant["domain"],
            "plan": tenant["plan"]
        }
    }

@api_router.get("/auth/me")
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    current_tenant: dict = Depends(get_current_tenant)
):
    """Get current user and tenant information"""
    return {
        "user": {
            "id": current_user["id"],
            "email": current_user["email"],
            "first_name": current_user["first_name"],
            "last_name": current_user["last_name"],
            "role": current_user["role"]
        },
        "tenant": {
            "id": current_tenant["id"],
            "name": current_tenant["name"],
            "domain": current_tenant["domain"],
            "plan": current_tenant["plan"],
            "industry": current_tenant["industry"]
        }
    }

# Company Management Endpoints
@api_router.post("/companies", response_model=Company)
async def create_company(
    company_data: CompanyCreate,
    tenant_id: str = Depends(get_tenant_id),
    service: CarbonDataService = Depends(get_carbon_service),
    multitenancy: MultiTenancyService = Depends(get_multitenancy_service)
):
    """Create a new company profile"""
    try:
        # Use tenant-scoped creation
        company_dict = company_data.dict()
        company = await multitenancy.insert_one_scoped(
            multitenancy.companies, company_dict, tenant_id
        )
        return Company(**company)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/companies/{company_id}", response_model=Company)
async def get_company(
    company_id: str,
    tenant_id: str = Depends(get_tenant_id),
    multitenancy: MultiTenancyService = Depends(get_multitenancy_service)
):
    """Get company profile"""
    company = await multitenancy.find_one_scoped(
        multitenancy.companies, {"id": company_id}, tenant_id
    )
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return Company(**company)

@api_router.get("/companies", response_model=List[Company])
async def list_companies(
    tenant_id: str = Depends(get_tenant_id),
    multitenancy: MultiTenancyService = Depends(get_multitenancy_service)
):
    """List all companies"""
    companies = await multitenancy.find_many_scoped(
        multitenancy.companies, {}, tenant_id, limit=100
    )
    # Remove MongoDB _id field to avoid serialization issues
    for company in companies:
        company.pop('_id', None)
    return [Company(**company) for company in companies]

# Emission Data Endpoints
@api_router.post("/companies/{company_id}/emissions", response_model=EmissionRecord)
async def add_emission_record(
    company_id: str,
    record_data: EmissionRecordCreate,
    tenant_id: str = Depends(get_tenant_id),
    service: CarbonDataService = Depends(get_carbon_service),
    multitenancy: MultiTenancyService = Depends(get_multitenancy_service)
):
    """Add emission record for a company"""
    try:
        # Verify company belongs to tenant
        company = await multitenancy.find_one_scoped(
            multitenancy.companies, {"id": company_id}, tenant_id
        )
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Add emission record with tenant scope
        record_dict = record_data.dict()
        record_dict["company_id"] = company_id
        record = await multitenancy.insert_one_scoped(
            multitenancy.emissions, record_dict, tenant_id
        )
        return EmissionRecord(**record)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/companies/{company_id}/emissions/summary")
async def get_emissions_summary(
    company_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    tenant_id: str = Depends(get_tenant_id),
    multitenancy: MultiTenancyService = Depends(get_multitenancy_service)
):
    """Get emissions summary for a company"""
    # Verify company belongs to tenant
    company = await multitenancy.find_one_scoped(
        multitenancy.companies, {"id": company_id}, tenant_id
    )
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    if not start_date:
        start_date = (datetime.utcnow() - timedelta(days=365)).isoformat()
    if not end_date:
        end_date = datetime.utcnow().isoformat()
    
    start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    
    # Get tenant-scoped emissions summary
    pipeline = [
        {"$match": {"company_id": company_id, "recorded_date": {"$gte": start_dt, "$lte": end_dt}}},
        {"$group": {
            "_id": None,
            "total_co2e": {"$sum": "$total_co2e"},
            "scope1_total": {"$sum": "$scope1_emissions"},
            "scope2_total": {"$sum": "$scope2_emissions"},
            "scope3_total": {"$sum": "$scope3_emissions"},
            "record_count": {"$sum": 1}
        }}
    ]
    
    summary_data = await multitenancy.aggregate_scoped(
        multitenancy.emissions, pipeline, tenant_id
    )
    
    if not summary_data:
        return {
            "total_co2e": 0,
            "scope1_total": 0,
            "scope2_total": 0,
            "scope3_total": 0,
            "record_count": 0
        }
    
    return summary_data[0]

@api_router.get("/companies/{company_id}/emissions/trend")
async def get_emissions_trend(
    company_id: str,
    months: int = 12,
    tenant_id: str = Depends(get_tenant_id),
    multitenancy: MultiTenancyService = Depends(get_multitenancy_service)
):
    """Get emissions trend data"""
    # Verify company belongs to tenant
    company = await multitenancy.find_one_scoped(
        multitenancy.companies, {"id": company_id}, tenant_id
    )
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    start_date = datetime.utcnow() - timedelta(days=months * 30)
    
    pipeline = [
        {"$match": {"company_id": company_id, "recorded_date": {"$gte": start_date}}},
        {"$group": {
            "_id": {
                "year": {"$year": "$recorded_date"},
                "month": {"$month": "$recorded_date"}
            },
            "total_co2e": {"$sum": "$total_co2e"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id.year": 1, "_id.month": 1}}
    ]
    
    trend_data = await multitenancy.aggregate_scoped(
        multitenancy.emissions, pipeline, tenant_id
    )
    
    return trend_data

@api_router.get("/companies/{company_id}/emissions/sources/top")
async def get_top_emission_sources(
    company_id: str,
    limit: int = 5,
    tenant_id: str = Depends(get_tenant_id),
    multitenancy: MultiTenancyService = Depends(get_multitenancy_service)
):
    """Get top emission sources"""
    # Verify company belongs to tenant
    company = await multitenancy.find_one_scoped(
        multitenancy.companies, {"id": company_id}, tenant_id
    )
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    pipeline = [
        {"$match": {"company_id": company_id}},
        {"$group": {
            "_id": "$emission_source",
            "total_co2e": {"$sum": "$total_co2e"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"total_co2e": -1}},
        {"$limit": limit}
    ]
    
    sources_data = await multitenancy.aggregate_scoped(
        multitenancy.emissions, pipeline, tenant_id
    )
    
    return sources_data

# AI Carbon Intelligence Endpoints
@api_router.post("/companies/{company_id}/ai/query")
async def process_ai_query(
    company_id: str,
    query_request: AIQueryRequest,
    service: CarbonDataService = Depends(get_carbon_service),
    ai_svc: CarbonAIService = Depends(get_ai_service)
):
    """Process natural language queries about carbon data"""
    try:
        # Get company data for context
        company = await db.companies.find_one({"id": company_id})
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Get recent emissions data
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=365)
        emissions_summary = await service.get_company_emissions_summary(company_id, start_date, end_date)
        emissions_trend = await service.get_emissions_trend(company_id, 12)
        top_sources = await service.get_top_emission_sources(company_id)
        
        # Prepare context data (convert datetime objects to strings)
        company_data = {
            **company,
            "recent_emissions": emissions_summary,
            "emissions_trend": emissions_trend,
            "emission_sources": top_sources,
            "created_at": company.get('created_at', datetime.utcnow()).isoformat() if isinstance(company.get('created_at'), datetime) else str(company.get('created_at', ''))
        }
        
        # Process query with AI
        response = await ai_svc.process_natural_language_query(
            company_data, 
            query_request.query_text
        )
        
        # Save query and response
        ai_query = AIQuery(
            company_id=company_id,
            user_id=query_request.user_id,
            query_text=query_request.query_text,
            response_text=response,
            query_type="analytics"
        )
        await db.ai_queries.insert_one(ai_query.dict())
        
        return {"query": query_request.query_text, "response": response, "query_id": ai_query.id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI query processing failed: {str(e)}")

@api_router.post("/companies/{company_id}/ai/forecast")
async def generate_emissions_forecast(
    company_id: str,
    horizon_months: int = 12,
    service: CarbonDataService = Depends(get_carbon_service),
    ai_svc: CarbonAIService = Depends(get_ai_service)
):
    """Generate AI-powered emissions forecast"""
    try:
        company = await db.companies.find_one({"id": company_id})
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Get historical data
        historical_records = await db.emission_records.find({"company_id": company_id}).to_list(1000)
        
        # Generate forecast
        forecast = await ai_svc.generate_emission_forecast(historical_records, company, horizon_months)
        
        # Save forecast
        await db.carbon_forecasts.insert_one(forecast.dict())
        
        return forecast
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast generation failed: {str(e)}")

@api_router.post("/companies/{company_id}/ai/recommendations")
async def generate_reduction_recommendations(
    company_id: str,
    service: CarbonDataService = Depends(get_carbon_service),
    ai_svc: CarbonAIService = Depends(get_ai_service)
):
    """Generate AI-powered carbon reduction recommendations"""
    try:
        company = await db.companies.find_one({"id": company_id})
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Get current emissions data
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=365)
        emissions_data = await service.get_company_emissions_summary(company_id, start_date, end_date)
        
        # Generate recommendations
        recommendations = await ai_svc.generate_reduction_recommendations(company, emissions_data)
        
        return {"recommendations": recommendations}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendations generation failed: {str(e)}")

# Carbon Calculation Models
class ElectricityCalculationRequest(BaseModel):
    kwh_consumed: float
    region: str = "us_average"
    renewable_percentage: float = 0

class FuelCalculationRequest(BaseModel):
    fuel_type: str
    quantity: float
    unit: str = "liters"

class TravelCalculationRequest(BaseModel):
    trips: List[Dict[str, Any]]

# Carbon Calculation Endpoints
@api_router.post("/calculate/electricity")
async def calculate_electricity_emissions(request: ElectricityCalculationRequest):
    """Calculate emissions from electricity consumption"""
    result = calculator.calculate_electricity_emissions(
        request.kwh_consumed, 
        request.region, 
        request.renewable_percentage
    )
    return result

@api_router.post("/calculate/fuel")
async def calculate_fuel_emissions(request: FuelCalculationRequest):
    """Calculate emissions from fuel combustion"""
    result = calculator.calculate_fuel_emissions(
        request.fuel_type, 
        request.quantity, 
        request.unit
    )
    return result

@api_router.post("/calculate/travel")
async def calculate_travel_emissions(request: TravelCalculationRequest):
    """Calculate emissions from business travel"""
    result = calculator.calculate_business_travel_emissions(request.trips)
    return result

# Dashboard and Analytics Endpoints
@api_router.get("/companies/{company_id}/dashboard")
async def get_dashboard_data(
    company_id: str,
    period_months: int = 12,
    service: CarbonDataService = Depends(get_carbon_service)
):
    """Get complete dashboard data"""
    try:
        dashboard_data = await service.get_dashboard_data(company_id, period_months)
        return dashboard_data.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard data retrieval failed: {str(e)}")

@api_router.get("/companies/{company_id}/targets/progress")
async def get_target_progress(
    company_id: str,
    service: CarbonDataService = Depends(get_carbon_service)
):
    """Get progress towards carbon reduction targets"""
    progress = await service.calculate_progress_to_targets(company_id)
    return progress

@api_router.get("/companies/{company_id}/financial-impact")
async def get_financial_impact(
    company_id: str,
    service: CarbonDataService = Depends(get_carbon_service)
):
    """Get financial impact of carbon initiatives"""
    impact = await service.get_financial_impact_summary(company_id)
    return impact

# Carbon Targets Management
@api_router.post("/companies/{company_id}/targets", response_model=CarbonTarget)
async def create_carbon_target(
    company_id: str,
    target_data: CarbonTargetCreate
):
    """Create a carbon reduction target"""
    target = CarbonTarget(**target_data.dict(), company_id=company_id)
    await db.carbon_targets.insert_one(target.dict())
    return target

@api_router.get("/companies/{company_id}/targets", response_model=List[CarbonTarget])
async def get_company_targets(company_id: str):
    """Get all carbon targets for a company"""
    targets = await db.carbon_targets.find({"company_id": company_id}).to_list(100)
    return [CarbonTarget(**target) for target in targets]

# Reduction Initiatives Management
@api_router.post("/companies/{company_id}/initiatives", response_model=CarbonReductionInitiative)
async def create_reduction_initiative(
    company_id: str,
    initiative_data: CarbonReductionInitiativeCreate
):
    """Create a carbon reduction initiative"""
    initiative = CarbonReductionInitiative(**initiative_data.dict(), company_id=company_id)
    await db.reduction_initiatives.insert_one(initiative.dict())
    return initiative

@api_router.get("/companies/{company_id}/initiatives", response_model=List[CarbonReductionInitiative])
async def get_company_initiatives(company_id: str):
    """Get all reduction initiatives for a company"""
    initiatives = await db.reduction_initiatives.find({"company_id": company_id}).to_list(100)
    return [CarbonReductionInitiative(**initiative) for initiative in initiatives]

# Industry Benchmarking
@api_router.get("/benchmarks/{industry}")
async def get_industry_benchmark(industry: str, employee_count: int):
    """Get industry benchmarking data"""
    benchmark = calculator.get_industry_benchmark(industry, employee_count)
    return benchmark

# Blockchain Carbon Offset Marketplace Endpoints
@api_router.get("/marketplace/projects")
async def get_offset_projects(
    project_type: Optional[str] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None
):
    """Get available carbon offset projects"""
    filters = {}
    if project_type:
        filters["project_type"] = project_type
    if max_price:
        filters["max_price"] = max_price
    if min_rating:
        filters["min_rating"] = min_rating
    
    listings = blockchain_service.get_marketplace_listings(filters)
    return {"projects": listings}

@api_router.post("/marketplace/purchase")
async def purchase_carbon_offsets(purchase_data: dict):
    """Purchase carbon offset credits"""
    try:
        listing_id = purchase_data["listing_id"]
        credits_amount = purchase_data["credits_amount"]
        company_id = purchase_data["company_id"]
        
        # Generate a mock buyer address for demo
        buyer_address = f"0x{company_id[:40].replace('-', '0').lower()}"
        
        purchase_result = blockchain_service.purchase_carbon_credits(
            listing_id, credits_amount, buyer_address
        )
        
        # Create certificate record in database
        certificate = CarbonCertificate(
            certificate_id=purchase_result["purchase_id"],
            project_id=listing_id,
            company_id=company_id,
            credits_amount=credits_amount,
            purchase_price=purchase_result["total_cost"],
            purchase_date=datetime.fromisoformat(purchase_result["purchase_date"]),
            blockchain_address=buyer_address,
            transaction_hash=purchase_result["transaction_hash"]
        )
        
        await db.carbon_certificates.insert_one(certificate.dict())
        
        return purchase_result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.post("/marketplace/retire")
async def retire_carbon_credits(retirement_data: dict):
    """Retire carbon credits (permanent removal from circulation)"""
    try:
        certificate_id = retirement_data["certificate_id"]
        credits_amount = retirement_data["credits_amount"]
        retirement_reason = retirement_data["retirement_reason"]
        company_id = retirement_data["company_id"]
        
        # Find certificate
        certificate = await db.carbon_certificates.find_one({"certificate_id": certificate_id, "company_id": company_id})
        if not certificate:
            raise HTTPException(status_code=404, detail="Certificate not found")
        
        retirement_result = blockchain_service.retire_carbon_credits(
            certificate_id, credits_amount, retirement_reason
        )
        
        # Update certificate status
        await db.carbon_certificates.update_one(
            {"certificate_id": certificate_id},
            {
                "$set": {
                    "retirement_status": "retired",
                    "retirement_date": datetime.utcnow(),
                    "retirement_reason": retirement_reason
                }
            }
        )
        
        return retirement_result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/companies/{company_id}/certificates")
async def get_company_certificates(company_id: str):
    """Get all carbon certificates owned by a company"""
    certificates = await db.carbon_certificates.find({"company_id": company_id}).to_list(100)
    return [CarbonCertificate(**cert) for cert in certificates]

@api_router.get("/marketplace/verify/{certificate_id}")
async def verify_carbon_certificate(certificate_id: str):
    """Verify the authenticity of a carbon certificate"""
    verification = blockchain_service.verify_offset_authenticity(certificate_id)
    return verification

# Supply Chain Carbon Visibility Endpoints
@api_router.post("/companies/{company_id}/suppliers", response_model=Supplier)
async def add_supplier(company_id: str, supplier_data: dict):
    """Add a new supplier to the supply chain"""
    supplier = Supplier(**supplier_data, company_id=company_id)
    await db.suppliers.insert_one(supplier.dict())
    return supplier

@api_router.get("/companies/{company_id}/suppliers", response_model=List[Supplier])
async def get_company_suppliers(company_id: str):
    """Get all suppliers for a company"""
    suppliers = await db.suppliers.find({"company_id": company_id}).to_list(100)
    return [Supplier(**supplier) for supplier in suppliers]

@api_router.post("/companies/{company_id}/supply-chain-emissions")
async def add_supply_chain_emission(company_id: str, emission_data: dict):
    """Add supply chain emission data"""
    emission = SupplyChainEmission(**emission_data, company_id=company_id)
    await db.supply_chain_emissions.insert_one(emission.dict())
    return emission

@api_router.get("/companies/{company_id}/supply-chain-emissions")
async def get_supply_chain_emissions(company_id: str):
    """Get supply chain emissions for a company"""
    emissions = await db.supply_chain_emissions.find({"company_id": company_id}).to_list(100)
    return emissions

@api_router.get("/companies/{company_id}/supply-chain/dashboard")
async def get_supply_chain_dashboard(company_id: str):
    """Get supply chain carbon visibility dashboard data"""
    try:
        # Get suppliers
        suppliers = await db.suppliers.find({"company_id": company_id}).to_list(100)
        
        # Get supply chain emissions
        emissions = await db.supply_chain_emissions.find({"company_id": company_id}).to_list(100)
        
        # Calculate metrics
        total_suppliers = len(suppliers)
        verified_suppliers = len([s for s in suppliers if s.get("verification_status") == "verified"])
        avg_carbon_score = sum(s.get("carbon_score", 0) for s in suppliers) / max(total_suppliers, 1)
        
        total_supply_chain_emissions = sum(e.get("co2_equivalent_kg", 0) for e in emissions)
        
        # Supplier scoring distribution
        score_ranges = {"0-25": 0, "26-50": 0, "51-75": 0, "76-100": 0}
        for supplier in suppliers:
            score = supplier.get("carbon_score", 0)
            if score <= 25:
                score_ranges["0-25"] += 1
            elif score <= 50:
                score_ranges["26-50"] += 1
            elif score <= 75:
                score_ranges["51-75"] += 1
            else:
                score_ranges["76-100"] += 1
        
        dashboard_data = {
            "total_suppliers": total_suppliers,
            "verified_suppliers": verified_suppliers,
            "verification_rate": (verified_suppliers / max(total_suppliers, 1)) * 100,
            "average_carbon_score": avg_carbon_score,
            "total_supply_chain_emissions": total_supply_chain_emissions,
            "score_distribution": score_ranges,
            "top_performing_suppliers": [{
                "id": str(s.get("_id", s.get("id", ""))),
                "supplier_name": s.get("supplier_name", "Unknown"),
                "industry": s.get("industry", "Unknown"),
                "carbon_score": s.get("carbon_score", 0)
            } for s in sorted(suppliers, key=lambda x: x.get("carbon_score", 0), reverse=True)[:5]],
            "suppliers_needing_attention": [{
                "id": str(s.get("_id", s.get("id", ""))),
                "supplier_name": s.get("supplier_name", "Unknown"),
                "industry": s.get("industry", "Unknown"),
                "carbon_score": s.get("carbon_score", 0)
            } for s in suppliers if s.get("carbon_score", 0) < 50]
        }
        
        return dashboard_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard data retrieval failed: {str(e)}")

@api_router.post("/companies/{company_id}/supply-chain/targets")
async def create_supply_chain_target(company_id: str, target_data: dict):
    """Create supply chain carbon reduction target"""
    target = SupplyChainTarget(**target_data, company_id=company_id)
    await db.supply_chain_targets.insert_one(target.dict())
    return target

@api_router.get("/companies/{company_id}/supply-chain/targets")
async def get_supply_chain_targets(company_id: str):
    """Get supply chain targets for a company"""
    targets = await db.supply_chain_targets.find({"company_id": company_id}).to_list(100)
    return targets

# Compliance Automation Endpoints
@api_router.get("/companies/{company_id}/compliance/dashboard")
async def get_compliance_dashboard(company_id: str):
    """Get compliance status dashboard for all standards"""
    try:
        dashboard = await compliance_service.get_compliance_dashboard(company_id)
        return dashboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/companies/{company_id}/compliance/report/{standard}")
async def generate_compliance_report(
    company_id: str,
    standard: str,
    year: Optional[int] = None
):
    """Generate automated compliance report for specified standard"""
    try:
        if year is None:
            year = datetime.utcnow().year
        
        report = await compliance_service.generate_compliance_report(company_id, standard, year)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/compliance/standards")
async def get_available_standards():
    """Get list of available compliance standards"""
    return {
        "standards": [
            {
                "code": "eu_csrd",
                "name": "EU Corporate Sustainability Reporting Directive",
                "description": "Mandatory sustainability reporting for large EU companies",
                "deadline": "Annual by April 30"
            },
            {
                "code": "sec_climate",
                "name": "SEC Climate Disclosure Rules",
                "description": "Climate-related financial risk disclosures for US public companies",
                "deadline": "Annual with 10-K filing"
            },
            {
                "code": "ghg_protocol",
                "name": "GHG Protocol Corporate Standard",
                "description": "Global standard for corporate greenhouse gas accounting",
                "deadline": "Annual"
            },
            {
                "code": "tcfd",
                "name": "TCFD Recommendations",
                "description": "Climate-related financial disclosures framework",
                "deadline": "Annual"
            }
        ]
    }

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
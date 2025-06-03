from fastapi import FastAPI, APIRouter, HTTPException, Depends
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

# Initialize services
carbon_service = CarbonDataService(db)
ai_service = CarbonAIService()
calculator = CarbonCalculator()

# Create the main app without a prefix
app = FastAPI(title="ClimaBill API", description="Carbon Intelligence and Billing Management Platform", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Dependency to get services
async def get_carbon_service():
    return carbon_service

async def get_ai_service():
    return ai_service

# Health check endpoint
@api_router.get("/")
async def root():
    return {"message": "ClimaBill API is running", "version": "1.0.0"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Company Management Endpoints
@api_router.post("/companies", response_model=Company)
async def create_company(
    company_data: CompanyCreate,
    service: CarbonDataService = Depends(get_carbon_service)
):
    """Create a new company profile"""
    try:
        company = await service.create_company(company_data)
        return company
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/companies/{company_id}", response_model=Company)
async def get_company(company_id: str):
    """Get company profile"""
    company = await db.companies.find_one({"id": company_id})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return Company(**company)

@api_router.get("/companies", response_model=List[Company])
async def list_companies():
    """List all companies"""
    companies = await db.companies.find().to_list(100)
    return [Company(**company) for company in companies]

# Emission Data Endpoints
@api_router.post("/companies/{company_id}/emissions", response_model=EmissionRecord)
async def add_emission_record(
    company_id: str,
    record_data: EmissionRecordCreate,
    service: CarbonDataService = Depends(get_carbon_service)
):
    """Add emission record for a company"""
    try:
        record = await service.add_emission_record(company_id, record_data)
        return record
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/companies/{company_id}/emissions/summary")
async def get_emissions_summary(
    company_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    service: CarbonDataService = Depends(get_carbon_service)
):
    """Get emissions summary for a company"""
    if not start_date:
        start_date = (datetime.utcnow() - timedelta(days=365)).isoformat()
    if not end_date:
        end_date = datetime.utcnow().isoformat()
    
    start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    
    summary = await service.get_company_emissions_summary(company_id, start_dt, end_dt)
    return summary

@api_router.get("/companies/{company_id}/emissions/trend")
async def get_emissions_trend(
    company_id: str,
    months: int = 12,
    service: CarbonDataService = Depends(get_carbon_service)
):
    """Get emissions trend data"""
    trend = await service.get_emissions_trend(company_id, months)
    return trend

@api_router.get("/companies/{company_id}/emissions/sources/top")
async def get_top_emission_sources(
    company_id: str,
    limit: int = 5,
    service: CarbonDataService = Depends(get_carbon_service)
):
    """Get top emission sources"""
    sources = await service.get_top_emission_sources(company_id, limit)
    return sources

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
        
        # Prepare context data
        company_data = {
            **company,
            "recent_emissions": emissions_summary,
            "emissions_trend": emissions_trend,
            "emission_sources": top_sources
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

# Carbon Calculation Endpoints
@api_router.post("/calculate/electricity")
async def calculate_electricity_emissions(
    kwh_consumed: float,
    region: str = "us_average",
    renewable_percentage: float = 0
):
    """Calculate emissions from electricity consumption"""
    result = calculator.calculate_electricity_emissions(kwh_consumed, region, renewable_percentage)
    return result

@api_router.post("/calculate/fuel")
async def calculate_fuel_emissions(
    fuel_type: str,
    quantity: float,
    unit: str = "liters"
):
    """Calculate emissions from fuel combustion"""
    result = calculator.calculate_fuel_emissions(fuel_type, quantity, unit)
    return result

@api_router.post("/calculate/travel")
async def calculate_travel_emissions(trips: List[Dict[str, Any]]):
    """Calculate emissions from business travel"""
    result = calculator.calculate_business_travel_emissions(trips)
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
    target_name: str,
    baseline_year: int,
    target_year: int,
    baseline_emissions: float,
    target_reduction_percentage: float,
    scope_coverage: List[EmissionScope]
):
    """Create a carbon reduction target"""
    target = CarbonTarget(
        company_id=company_id,
        target_name=target_name,
        baseline_year=baseline_year,
        target_year=target_year,
        baseline_emissions=baseline_emissions,
        target_reduction_percentage=target_reduction_percentage,
        scope_coverage=scope_coverage
    )
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
    initiative_name: str,
    description: str,
    implementation_cost: float,
    annual_savings: float,
    annual_co2_reduction: float,
    roi_percentage: float,
    implementation_date: datetime,
    status: str = "planned"
):
    """Create a carbon reduction initiative"""
    initiative = CarbonReductionInitiative(
        company_id=company_id,
        initiative_name=initiative_name,
        description=description,
        implementation_cost=implementation_cost,
        annual_savings=annual_savings,
        annual_co2_reduction=annual_co2_reduction,
        roi_percentage=roi_percentage,
        implementation_date=implementation_date,
        status=status
    )
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
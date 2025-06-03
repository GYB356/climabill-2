from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

# Enums for data validation
class EmissionScope(str, Enum):
    SCOPE_1 = "scope_1"  # Direct emissions
    SCOPE_2 = "scope_2"  # Indirect emissions from energy
    SCOPE_3 = "scope_3"  # Other indirect emissions

class IndustryType(str, Enum):
    SAAS = "saas"
    FINTECH = "fintech"
    ECOMMERCE = "ecommerce"
    MANUFACTURING = "manufacturing"
    HEALTHCARE = "healthcare"
    CONSULTING = "consulting"

class ComplianceStandard(str, Enum):
    EU_CSRD = "eu_csrd"
    SEC_CLIMATE = "sec_climate"
    GHG_PROTOCOL = "ghg_protocol"
    TCFD = "tcfd"

# Core Models
class Company(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    industry: IndustryType
    employee_count: int
    annual_revenue: float  # in USD
    headquarters_location: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    compliance_standards: List[ComplianceStandard] = []

class EmissionSource(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_id: str
    source_name: str
    source_type: str  # e.g., "electricity", "fuel", "travel", "office"
    scope: EmissionScope
    description: Optional[str] = None

class EmissionRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_id: str
    source_id: str
    period_start: datetime
    period_end: datetime
    co2_equivalent_kg: float
    activity_data: Dict[str, Any]  # Flexible data for different sources
    emission_factor: float
    data_quality: str = "estimated"  # estimated, measured, calculated
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CarbonTarget(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_id: str
    target_name: str
    baseline_year: int
    target_year: int
    baseline_emissions: float  # kg CO2eq
    target_reduction_percentage: float
    scope_coverage: List[EmissionScope]
    status: str = "active"  # active, achieved, revised
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CarbonReductionInitiative(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_id: str
    initiative_name: str
    description: str
    implementation_cost: float  # USD
    annual_savings: float  # USD
    annual_co2_reduction: float  # kg CO2eq
    roi_percentage: float
    implementation_date: datetime
    status: str = "planned"  # planned, in_progress, completed
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AIQuery(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_id: str
    user_id: Optional[str] = None
    query_text: str
    response_text: str
    query_type: str  # analytics, forecasting, recommendations
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class CarbonForecast(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_id: str
    forecast_date: datetime
    forecast_horizon_months: int
    predicted_emissions: Dict[str, float]  # scope -> emissions
    confidence_interval: Dict[str, List[float]]  # scope -> [min, max]
    assumptions: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Request/Response Models
class CompanyCreate(BaseModel):
    name: str
    industry: IndustryType
    employee_count: int
    annual_revenue: float
    headquarters_location: str
    compliance_standards: List[ComplianceStandard] = []

class EmissionRecordCreate(BaseModel):
    source_id: str
    period_start: datetime
    period_end: datetime
    co2_equivalent_kg: float
    activity_data: Dict[str, Any]
    emission_factor: float
    data_quality: str = "estimated"

class AIQueryRequest(BaseModel):
    company_id: str
    query_text: str
    user_id: Optional[str] = None

class CarbonDashboardData(BaseModel):
    company_id: str
    period_start: datetime
    period_end: datetime
    total_emissions: Dict[str, float]  # scope -> emissions
    emissions_trend: List[Dict[str, Any]]
    top_emission_sources: List[Dict[str, Any]]
    reduction_opportunities: List[Dict[str, Any]]
    financial_impact: Dict[str, float]
    compliance_status: Dict[str, str]
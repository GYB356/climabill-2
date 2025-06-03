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

# Blockchain and Carbon Offset Models
class OffsetProject(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_name: str
    project_type: str  # Forest Conservation, Renewable Energy, etc.
    location: str
    developer: str
    description: str
    verification_standard: str  # VCS, Gold Standard, ACR
    methodology: str
    vintage_year: int
    total_credits: float
    available_credits: float
    price_per_credit: float
    rating: float = 0.0
    additional_benefits: List[str] = []
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CarbonCertificate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    certificate_id: str
    project_id: str
    company_id: str
    credits_amount: float
    purchase_price: float
    purchase_date: datetime
    blockchain_address: str
    transaction_hash: str
    verification_status: str = "verified"
    retirement_status: str = "active"  # active, retired
    retirement_date: Optional[datetime] = None
    retirement_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class OffsetPurchase(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_id: str
    project_id: str
    credits_purchased: float
    total_cost: float
    purchase_date: datetime
    transaction_hash: str
    certificate_id: str
    status: str = "completed"
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Supply Chain Models
class Supplier(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_id: str  # The company this supplier belongs to
    supplier_name: str
    industry: str
    location: str
    contact_email: str
    annual_revenue: float
    employee_count: int
    carbon_score: float = 0.0  # 0-100 scoring
    verification_status: str = "pending"  # pending, verified, flagged
    partnership_level: str = "basic"  # basic, preferred, strategic
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SupplyChainEmission(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_id: str
    supplier_id: str
    emission_type: str  # upstream, downstream
    scope: EmissionScope
    co2_equivalent_kg: float
    activity_description: str
    reporting_period_start: datetime
    reporting_period_end: datetime
    data_quality: str = "estimated"  # estimated, measured, calculated
    verification_level: str = "supplier_reported"  # supplier_reported, third_party_verified
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SupplyChainTarget(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_id: str
    target_name: str
    target_type: str = "supply_chain_reduction"
    baseline_year: int
    target_year: int
    reduction_percentage: float
    scope_coverage: List[EmissionScope]
    participating_suppliers: List[str]  # List of supplier IDs
    progress_percentage: float = 0.0
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow)
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

class CarbonTargetCreate(BaseModel):
    target_name: str
    baseline_year: int
    target_year: int
    baseline_emissions: float
    target_reduction_percentage: float
    scope_coverage: List[EmissionScope]

class CarbonReductionInitiativeCreate(BaseModel):
    initiative_name: str
    description: str
    implementation_cost: float
    annual_savings: float
    annual_co2_reduction: float
    roi_percentage: float
    implementation_date: datetime
    status: str = "planned"

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
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from models import *
from carbon_calculator import CarbonCalculator
import json

class CarbonDataService:
    """Service layer for carbon data operations and analytics"""
    
    def __init__(self, db):
        self.db = db
        self.calculator = CarbonCalculator()
        
        # Collections
        self.companies: AsyncIOMotorCollection = db.companies
        self.emission_sources: AsyncIOMotorCollection = db.emission_sources
        self.emission_records: AsyncIOMotorCollection = db.emission_records
        self.carbon_targets: AsyncIOMotorCollection = db.carbon_targets
        self.reduction_initiatives: AsyncIOMotorCollection = db.reduction_initiatives
        self.ai_queries: AsyncIOMotorCollection = db.ai_queries
        self.carbon_forecasts: AsyncIOMotorCollection = db.carbon_forecasts
    
    async def create_company(self, company_data: CompanyCreate) -> Company:
        """Create a new company profile"""
        company = Company(**company_data.dict())
        await self.companies.insert_one(company.dict())
        
        # Create default emission sources for the company
        await self._create_default_emission_sources(company.id, company.industry)
        
        return company
    
    async def _create_default_emission_sources(self, company_id: str, industry: IndustryType):
        """Create default emission sources based on industry type"""
        default_sources = {
            IndustryType.SAAS: [
                {"name": "Office Electricity", "type": "electricity", "scope": EmissionScope.SCOPE_2},
                {"name": "Employee Commuting", "type": "commuting", "scope": EmissionScope.SCOPE_3},
                {"name": "Business Travel", "type": "travel", "scope": EmissionScope.SCOPE_3},
                {"name": "Cloud Services", "type": "cloud", "scope": EmissionScope.SCOPE_3},
                {"name": "Office Heating", "type": "heating", "scope": EmissionScope.SCOPE_1},
            ],
            IndustryType.MANUFACTURING: [
                {"name": "Production Electricity", "type": "electricity", "scope": EmissionScope.SCOPE_2},
                {"name": "Industrial Processes", "type": "production", "scope": EmissionScope.SCOPE_1},
                {"name": "Raw Materials", "type": "materials", "scope": EmissionScope.SCOPE_3},
                {"name": "Transportation", "type": "logistics", "scope": EmissionScope.SCOPE_3},
                {"name": "Waste Management", "type": "waste", "scope": EmissionScope.SCOPE_3},
            ]
        }
        
        sources = default_sources.get(industry, default_sources[IndustryType.SAAS])
        
        for source_data in sources:
            source = EmissionSource(
                company_id=company_id,
                source_name=source_data["name"],
                source_type=source_data["type"],
                scope=source_data["scope"]
            )
            await self.emission_sources.insert_one(source.dict())
    
    async def add_emission_record(self, company_id: str, record_data: EmissionRecordCreate) -> EmissionRecord:
        """Add a new emission record"""
        record = EmissionRecord(company_id=company_id, **record_data.dict())
        await self.emission_records.insert_one(record.dict())
        return record
    
    async def get_company_emissions_summary(self, company_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get comprehensive emissions summary for a company"""
        pipeline = [
            {
                "$match": {
                    "company_id": company_id,
                    "period_start": {"$gte": start_date},
                    "period_end": {"$lte": end_date}
                }
            },
            {
                "$lookup": {
                    "from": "emission_sources",
                    "localField": "source_id",
                    "foreignField": "id",
                    "as": "source_info"
                }
            },
            {
                "$unwind": "$source_info"
            },
            {
                "$group": {
                    "_id": {
                        "scope": "$source_info.scope",
                        "source_type": "$source_info.source_type"
                    },
                    "total_emissions": {"$sum": "$co2_equivalent_kg"},
                    "record_count": {"$sum": 1}
                }
            }
        ]
        
        results = await self.emission_records.aggregate(pipeline).to_list(100)
        
        # Process results into structured format
        scope_totals = {"scope_1": 0, "scope_2": 0, "scope_3": 0}
        source_breakdown = {}
        
        for result in results:
            scope = result["_id"]["scope"]
            source_type = result["_id"]["source_type"]
            emissions = result["total_emissions"]
            
            scope_totals[scope] += emissions
            source_breakdown[source_type] = emissions
        
        total_emissions = sum(scope_totals.values())
        
        return {
            "company_id": company_id,
            "period_start": start_date,
            "period_end": end_date,
            "total_emissions_kg": total_emissions,
            "scope_breakdown": scope_totals,
            "source_breakdown": source_breakdown,
            "emissions_intensity": total_emissions / 1000,  # tonnes CO2eq
        }
    
    async def get_emissions_trend(self, company_id: str, months: int = 12) -> List[Dict[str, Any]]:
        """Get monthly emissions trend data"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=months * 30)
        
        pipeline = [
            {
                "$match": {
                    "company_id": company_id,
                    "period_start": {"$gte": start_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$period_start"},
                        "month": {"$month": "$period_start"}
                    },
                    "total_emissions": {"$sum": "$co2_equivalent_kg"},
                    "record_count": {"$sum": 1}
                }
            },
            {
                "$sort": {"_id.year": 1, "_id.month": 1}
            }
        ]
        
        results = await self.emission_records.aggregate(pipeline).to_list(100)
        
        trend_data = []
        for result in results:
            trend_data.append({
                "year": result["_id"]["year"],
                "month": result["_id"]["month"],
                "emissions_kg": result["total_emissions"],
                "emissions_tonnes": result["total_emissions"] / 1000
            })
        
        return trend_data
    
    async def get_top_emission_sources(self, company_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top emission sources by volume"""
        pipeline = [
            {
                "$match": {"company_id": company_id}
            },
            {
                "$lookup": {
                    "from": "emission_sources",
                    "localField": "source_id",
                    "foreignField": "id",
                    "as": "source_info"
                }
            },
            {
                "$unwind": "$source_info"
            },
            {
                "$group": {
                    "_id": "$source_id",
                    "source_name": {"$first": "$source_info.source_name"},
                    "source_type": {"$first": "$source_info.source_type"},
                    "scope": {"$first": "$source_info.scope"},
                    "total_emissions": {"$sum": "$co2_equivalent_kg"},
                    "record_count": {"$sum": 1}
                }
            },
            {
                "$sort": {"total_emissions": -1}
            },
            {
                "$limit": limit
            }
        ]
        
        results = await self.emission_sources.aggregate(pipeline).to_list(limit)
        return results
    
    async def calculate_progress_to_targets(self, company_id: str) -> List[Dict[str, Any]]:
        """Calculate progress towards carbon reduction targets"""
        targets = await self.carbon_targets.find({"company_id": company_id, "status": "active"}).to_list(100)
        
        progress_data = []
        for target in targets:
            # Get current year emissions
            current_year = datetime.utcnow().year
            year_start = datetime(current_year, 1, 1)
            year_end = datetime(current_year, 12, 31)
            
            current_emissions = await self.get_company_emissions_summary(company_id, year_start, year_end)
            
            # Calculate progress
            baseline_emissions = target["baseline_emissions"]
            target_emissions = baseline_emissions * (1 - target["target_reduction_percentage"] / 100)
            current_total = current_emissions["total_emissions_kg"]
            
            progress_percentage = ((baseline_emissions - current_total) / (baseline_emissions - target_emissions)) * 100
            progress_percentage = max(0, min(100, progress_percentage))  # Clamp between 0-100%
            
            progress_data.append({
                "target_id": target["id"],
                "target_name": target["target_name"],
                "baseline_emissions": baseline_emissions,
                "target_emissions": target_emissions,
                "current_emissions": current_total,
                "progress_percentage": progress_percentage,
                "target_year": target["target_year"],
                "on_track": progress_percentage >= ((current_year - target["baseline_year"]) / (target["target_year"] - target["baseline_year"]) * 100)
            })
        
        return progress_data
    
    async def get_financial_impact_summary(self, company_id: str) -> Dict[str, Any]:
        """Calculate financial impact of carbon initiatives and costs"""
        # Get all reduction initiatives
        initiatives = await self.reduction_initiatives.find({"company_id": company_id}).to_list(100)
        
        total_investment = sum(init["implementation_cost"] for init in initiatives)
        total_annual_savings = sum(init["annual_savings"] for init in initiatives)
        total_co2_reduction = sum(init["annual_co2_reduction"] for init in initiatives)
        
        # Calculate carbon costs
        current_year = datetime.utcnow().year
        year_start = datetime(current_year, 1, 1)
        year_end = datetime(current_year, 12, 31)
        
        current_emissions = await self.get_company_emissions_summary(company_id, year_start, year_end)
        carbon_cost = self.calculator.calculate_carbon_cost(current_emissions["total_emissions_kg"])
        
        # Calculate ROI
        if total_investment > 0:
            annual_roi = (total_annual_savings / total_investment) * 100
        else:
            annual_roi = 0
        
        # Calculate payback period
        if total_annual_savings > 0:
            payback_period = total_investment / total_annual_savings
        else:
            payback_period = float('inf')
        
        # Handle inf values for JSON serialization
        if payback_period == float('inf'):
            payback_period = 999.0  # Use a large number instead of infinity
        
        return {
            "total_carbon_investment": total_investment,
            "annual_cost_savings": total_annual_savings,
            "annual_co2_reduction": total_co2_reduction,
            "current_annual_carbon_cost": carbon_cost["total_carbon_cost"],
            "annual_roi_percentage": annual_roi,
            "payback_period_years": total_investment / total_annual_savings if total_annual_savings > 0 else float('inf'),
            "carbon_reduction_value": self.calculator.calculate_reduction_value(total_co2_reduction)["total_financial_value"]
        }
    
    async def get_dashboard_data(self, company_id: str, period_months: int = 12) -> CarbonDashboardData:
        """Get complete dashboard data for the frontend"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_months * 30)
        
        # Get all dashboard components
        emissions_summary = await self.get_company_emissions_summary(company_id, start_date, end_date)
        emissions_trend = await self.get_emissions_trend(company_id, period_months)
        top_sources = await self.get_top_emission_sources(company_id)
        target_progress = await self.calculate_progress_to_targets(company_id)
        financial_impact = await self.get_financial_impact_summary(company_id)
        
        # Get company for compliance status
        company = await self.companies.find_one({"id": company_id})
        compliance_status = {}
        if company:
            for standard in company.get("compliance_standards", []):
                # Simple compliance check - in practice this would be more sophisticated
                compliance_status[standard] = "compliant" if emissions_summary["total_emissions_kg"] < 100000 else "attention_needed"
        
        return CarbonDashboardData(
            company_id=company_id,
            period_start=start_date,
            period_end=end_date,
            total_emissions=emissions_summary["scope_breakdown"],
            emissions_trend=emissions_trend,
            top_emission_sources=top_sources,
            reduction_opportunities=target_progress,
            financial_impact=financial_impact,
            compliance_status=compliance_status
        )
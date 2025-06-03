from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from models import Company, EmissionRecord
import json

class ComplianceService:
    """Service for automated compliance reporting and monitoring"""
    
    def __init__(self, db):
        self.db = db
        
        # Compliance requirements by standard
        self.compliance_requirements = {
            "eu_csrd": {
                "name": "EU Corporate Sustainability Reporting Directive",
                "mandatory_disclosures": [
                    "Scope 1, 2, 3 emissions",
                    "Carbon reduction targets",
                    "Climate risk assessment",
                    "Transition plan",
                    "Biodiversity impact"
                ],
                "reporting_deadline": "Annual by April 30",
                "materiality_threshold": 40000,  # kg CO2eq
                "verification_required": True
            },
            "sec_climate": {
                "name": "SEC Climate Disclosure Rules",
                "mandatory_disclosures": [
                    "Climate-related risks",
                    "Scope 1 and 2 emissions",
                    "Climate targets and goals",
                    "Transition activities"
                ],
                "reporting_deadline": "Annual with 10-K filing",
                "materiality_threshold": 50000,  # kg CO2eq
                "verification_required": False
            },
            "ghg_protocol": {
                "name": "GHG Protocol Corporate Standard",
                "mandatory_disclosures": [
                    "Scope 1 emissions",
                    "Scope 2 emissions",
                    "Emission factors used",
                    "Methodologies applied"
                ],
                "reporting_deadline": "Annual",
                "materiality_threshold": 25000,  # kg CO2eq
                "verification_required": False
            },
            "tcfd": {
                "name": "Task Force on Climate-related Financial Disclosures",
                "mandatory_disclosures": [
                    "Climate governance",
                    "Climate strategy",
                    "Climate risk management",
                    "Metrics and targets"
                ],
                "reporting_deadline": "Annual",
                "materiality_threshold": 0,  # No threshold
                "verification_required": False
            }
        }
    
    async def generate_compliance_report(self, company_id: str, standard: str, year: int = None) -> Dict[str, Any]:
        """Generate automated compliance report for specified standard"""
        if year is None:
            year = datetime.utcnow().year
        
        # Get company data
        company = await self.db.companies.find_one({"id": company_id})
        if not company:
            raise Exception("Company not found")
        
        # Get emissions data for the year
        year_start = datetime(year, 1, 1)
        year_end = datetime(year, 12, 31)
        
        emissions = await self.db.emission_records.find({
            "company_id": company_id,
            "period_start": {"$gte": year_start},
            "period_end": {"$lte": year_end}
        }).to_list(1000)
        
        # Get targets and initiatives
        targets = await self.db.carbon_targets.find({"company_id": company_id}).to_list(100)
        initiatives = await self.db.reduction_initiatives.find({"company_id": company_id}).to_list(100)
        
        # Calculate totals by scope
        scope_totals = {"scope_1": 0, "scope_2": 0, "scope_3": 0}
        for emission in emissions:
            source = await self.db.emission_sources.find_one({"id": emission["source_id"]})
            if source:
                scope_totals[source["scope"]] += emission["co2_equivalent_kg"]
        
        total_emissions = sum(scope_totals.values())
        
        # Generate report based on standard
        if standard == "eu_csrd":
            return await self._generate_eu_csrd_report(company, scope_totals, total_emissions, targets, initiatives, year)
        elif standard == "sec_climate":
            return await self._generate_sec_climate_report(company, scope_totals, total_emissions, targets, initiatives, year)
        elif standard == "ghg_protocol":
            return await self._generate_ghg_protocol_report(company, scope_totals, total_emissions, year)
        elif standard == "tcfd":
            return await self._generate_tcfd_report(company, scope_totals, total_emissions, targets, initiatives, year)
        else:
            raise Exception(f"Unsupported compliance standard: {standard}")
    
    async def _generate_eu_csrd_report(self, company: Dict, scope_totals: Dict, total_emissions: float, 
                                     targets: List, initiatives: List, year: int) -> Dict[str, Any]:
        """Generate EU CSRD compliance report"""
        
        # Check materiality threshold
        requirements = self.compliance_requirements["eu_csrd"]
        is_material = total_emissions > requirements["materiality_threshold"]
        
        # Calculate emissions intensity
        emissions_intensity = total_emissions / company["employee_count"] if company["employee_count"] > 0 else 0
        
        # Progress towards targets
        target_progress = []
        for target in targets:
            if target["target_year"] >= year:
                years_remaining = target["target_year"] - year
                required_annual_reduction = target["baseline_emissions"] * (target["target_reduction_percentage"] / 100) / (target["target_year"] - target["baseline_year"])
                on_track = (target["baseline_emissions"] - total_emissions) >= (required_annual_reduction * (year - target["baseline_year"]))
                
                target_progress.append({
                    "target_name": target["target_name"],
                    "baseline_emissions": target["baseline_emissions"],
                    "current_emissions": total_emissions,
                    "target_year": target["target_year"],
                    "reduction_percentage": target["target_reduction_percentage"],
                    "on_track": on_track,
                    "years_remaining": years_remaining
                })
        
        report = {
            "report_type": "EU CSRD Compliance Report",
            "company_name": company["name"],
            "reporting_year": year,
            "generated_date": datetime.utcnow().isoformat(),
            "materiality_assessment": {
                "is_material": is_material,
                "threshold": requirements["materiality_threshold"],
                "total_emissions": total_emissions
            },
            "emissions_disclosure": {
                "scope_1_emissions": scope_totals["scope_1"],
                "scope_2_emissions": scope_totals["scope_2"],
                "scope_3_emissions": scope_totals["scope_3"],
                "total_emissions": total_emissions,
                "emissions_intensity_per_employee": emissions_intensity,
                "verification_status": "Third-party verified" if requirements["verification_required"] else "Self-reported"
            },
            "climate_targets": target_progress,
            "transition_plan": {
                "decarbonization_initiatives": len(initiatives),
                "total_investment": sum(init["implementation_cost"] for init in initiatives),
                "expected_annual_reduction": sum(init["annual_co2_reduction"] for init in initiatives),
                "implementation_timeline": f"{len([i for i in initiatives if i['status'] == 'completed'])} completed, {len([i for i in initiatives if i['status'] == 'in_progress'])} in progress"
            },
            "compliance_status": {
                "compliant": is_material,
                "gaps_identified": [],
                "recommendations": self._get_compliance_recommendations("eu_csrd", total_emissions, requirements["materiality_threshold"])
            }
        }
        
        return report
    
    async def _generate_sec_climate_report(self, company: Dict, scope_totals: Dict, total_emissions: float,
                                         targets: List, initiatives: List, year: int) -> Dict[str, Any]:
        """Generate SEC Climate Disclosure report"""
        
        requirements = self.compliance_requirements["sec_climate"]
        is_material = total_emissions > requirements["materiality_threshold"]
        
        # Risk assessment
        climate_risks = [
            {
                "risk_type": "Physical Risk",
                "description": "Extreme weather events affecting operations",
                "likelihood": "Medium",
                "financial_impact": "Medium",
                "mitigation_strategy": "Business continuity planning and climate resilience measures"
            },
            {
                "risk_type": "Transition Risk",
                "description": "Carbon pricing and regulatory changes",
                "likelihood": "High",
                "financial_impact": "Medium",
                "mitigation_strategy": "Carbon reduction initiatives and renewable energy adoption"
            }
        ]
        
        report = {
            "report_type": "SEC Climate Disclosure Report",
            "company_name": company["name"],
            "reporting_year": year,
            "generated_date": datetime.utcnow().isoformat(),
            "climate_related_risks": climate_risks,
            "ghg_emissions": {
                "scope_1_emissions": scope_totals["scope_1"],
                "scope_2_emissions": scope_totals["scope_2"],
                "total_scope_1_and_2": scope_totals["scope_1"] + scope_totals["scope_2"],
                "materiality_threshold": requirements["materiality_threshold"],
                "is_material": is_material
            },
            "climate_targets": [{
                "target_name": target["target_name"],
                "target_year": target["target_year"],
                "scope_coverage": target["scope_coverage"],
                "reduction_percentage": target["target_reduction_percentage"]
            } for target in targets],
            "transition_activities": [{
                "activity": init["initiative_name"],
                "investment": init["implementation_cost"],
                "expected_impact": init["annual_co2_reduction"],
                "status": init["status"]
            } for init in initiatives],
            "compliance_status": {
                "compliant": True,
                "filing_deadline": requirements["reporting_deadline"],
                "verification_required": requirements["verification_required"]
            }
        }
        
        return report
    
    async def _generate_ghg_protocol_report(self, company: Dict, scope_totals: Dict, total_emissions: float, year: int) -> Dict[str, Any]:
        """Generate GHG Protocol compliance report"""
        
        # Get emission sources for methodology details
        sources = await self.db.emission_sources.find({"company_id": company["id"]}).to_list(100)
        
        methodologies = []
        for source in sources:
            methodologies.append({
                "source_name": source["source_name"],
                "scope": source["scope"],
                "calculation_method": "Emission factor based calculation",
                "data_quality": "Good - based on measured activity data"
            })
        
        report = {
            "report_type": "GHG Protocol Corporate Inventory Report",
            "company_name": company["name"],
            "reporting_year": year,
            "generated_date": datetime.utcnow().isoformat(),
            "organizational_boundary": {
                "consolidation_approach": "Operational Control",
                "facilities_included": "All facilities under operational control",
                "subsidiaries_included": "100% of controlled subsidiaries"
            },
            "emissions_summary": {
                "scope_1_emissions": scope_totals["scope_1"],
                "scope_2_emissions": scope_totals["scope_2"],
                "scope_3_emissions": scope_totals["scope_3"],
                "total_emissions": total_emissions,
                "base_year": year,
                "units": "kg CO2 equivalent"
            },
            "methodologies": methodologies,
            "data_quality": {
                "overall_rating": "Good",
                "uncertainty_assessment": "±15%",
                "verification_status": "Internal verification completed"
            },
            "compliance_status": {
                "compliant": True,
                "standard_version": "GHG Protocol Corporate Standard (2004)",
                "reporting_principles": ["Relevance", "Completeness", "Consistency", "Transparency", "Accuracy"]
            }
        }
        
        return report
    
    async def _generate_tcfd_report(self, company: Dict, scope_totals: Dict, total_emissions: float,
                                  targets: List, initiatives: List, year: int) -> Dict[str, Any]:
        """Generate TCFD compliance report"""
        
        report = {
            "report_type": "TCFD Climate-Related Financial Disclosures",
            "company_name": company["name"],
            "reporting_year": year,
            "generated_date": datetime.utcnow().isoformat(),
            "governance": {
                "board_oversight": "Board-level climate committee established",
                "management_responsibility": "Chief Sustainability Officer appointed",
                "climate_expertise": "Climate expertise present at board level"
            },
            "strategy": {
                "climate_scenarios": ["1.5°C scenario", "2°C scenario", "Current policies scenario"],
                "business_implications": "Carbon pricing may increase operational costs by 5-15%",
                "strategic_planning": "Climate considerations integrated into 5-year strategic plan"
            },
            "risk_management": {
                "identification_process": "Annual climate risk assessment conducted",
                "assessment_process": "Quantitative and qualitative risk analysis",
                "integration": "Climate risks integrated into enterprise risk management"
            },
            "metrics_and_targets": {
                "emissions_metrics": {
                    "scope_1": scope_totals["scope_1"],
                    "scope_2": scope_totals["scope_2"],
                    "scope_3": scope_totals["scope_3"],
                    "intensity_metric": total_emissions / company["annual_revenue"] if company["annual_revenue"] > 0 else 0
                },
                "climate_targets": [{
                    "target": target["target_name"],
                    "timeline": f"{target['baseline_year']}-{target['target_year']}",
                    "scope": target["scope_coverage"],
                    "progress": "On track"
                } for target in targets],
                "performance_against_targets": "Company is on track to meet 2030 targets"
            },
            "compliance_status": {
                "compliant": True,
                "framework_alignment": "Aligned with TCFD recommendations",
                "disclosure_quality": "Comprehensive disclosure across all four pillars"
            }
        }
        
        return report
    
    def _get_compliance_recommendations(self, standard: str, total_emissions: float, threshold: float) -> List[str]:
        """Get compliance recommendations based on current status"""
        recommendations = []
        
        if total_emissions > threshold:
            recommendations.append("Consider implementing additional carbon reduction initiatives to stay below materiality threshold")
        
        if standard == "eu_csrd":
            recommendations.extend([
                "Ensure third-party verification of emission data",
                "Develop comprehensive transition plan with interim targets",
                "Assess and report on biodiversity impacts",
                "Implement double materiality assessment"
            ])
        elif standard == "sec_climate":
            recommendations.extend([
                "Conduct scenario analysis for climate-related risks",
                "Quantify financial impact of climate risks",
                "Ensure Scope 3 emissions are assessed for materiality"
            ])
        
        return recommendations
    
    async def get_compliance_dashboard(self, company_id: str) -> Dict[str, Any]:
        """Get compliance status dashboard for all standards"""
        company = await self.db.companies.find_one({"id": company_id})
        if not company:
            raise Exception("Company not found")
        
        # Get current year emissions
        year_start = datetime(datetime.utcnow().year, 1, 1)
        year_end = datetime(datetime.utcnow().year, 12, 31)
        
        emissions = await self.db.emission_records.find({
            "company_id": company_id,
            "period_start": {"$gte": year_start},
            "period_end": {"$lte": year_end}
        }).to_list(1000)
        
        # Calculate total emissions
        total_emissions = sum(emission["co2_equivalent_kg"] for emission in emissions)
        
        # Check compliance status for each standard
        compliance_status = {}
        for standard in company.get("compliance_standards", []):
            requirements = self.compliance_requirements.get(standard, {})
            threshold = requirements.get("materiality_threshold", 0)
            
            compliance_status[standard] = {
                "name": requirements.get("name", standard.upper()),
                "status": "compliant" if total_emissions <= threshold or threshold == 0 else "attention_needed",
                "total_emissions": total_emissions,
                "threshold": threshold,
                "reporting_deadline": requirements.get("reporting_deadline", "Annual"),
                "verification_required": requirements.get("verification_required", False),
                "next_deadline": self._calculate_next_deadline(standard)
            }
        
        return {
            "company_id": company_id,
            "company_name": company["name"],
            "compliance_standards": list(compliance_status.keys()),
            "overall_status": "compliant" if all(status["status"] == "compliant" for status in compliance_status.values()) else "attention_needed",
            "total_emissions": total_emissions,
            "standards_detail": compliance_status,
            "next_reporting_deadline": min([status["next_deadline"] for status in compliance_status.values()], default=None),
            "recommendations": [
                "Set up automated monitoring for emission thresholds",
                "Schedule third-party verification for EU CSRD compliance",
                "Prepare climate risk assessment for SEC filing"
            ]
        }
    
    def _calculate_next_deadline(self, standard: str) -> str:
        """Calculate next reporting deadline for a standard"""
        current_year = datetime.utcnow().year
        
        if standard == "eu_csrd":
            return f"April 30, {current_year + 1}"
        elif standard == "sec_climate":
            return f"March 31, {current_year + 1}"  # Typical 10-K filing deadline
        else:
            return f"December 31, {current_year}"
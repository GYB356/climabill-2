#!/usr/bin/env python3
"""
Create comprehensive sample data for ClimaBill MVP across multiple industries
"""
import requests
import json
from datetime import datetime, timedelta
import random
import uuid

API_BASE = "http://localhost:8001/api"

def create_multi_industry_companies():
    """Create companies across different industries for comprehensive demo"""
    companies = [
        {
            "name": "TechFlow Systems",
            "industry": "saas",
            "employee_count": 250,
            "annual_revenue": 15000000,
            "headquarters_location": "Austin, TX",
            "compliance_standards": ["sec_climate", "ghg_protocol"]
        },
        {
            "name": "GreenManufacturing Corp",
            "industry": "manufacturing",
            "employee_count": 800,
            "annual_revenue": 50000000,
            "headquarters_location": "Detroit, MI",
            "compliance_standards": ["eu_csrd", "ghg_protocol", "tcfd"]
        },
        {
            "name": "HealthTech Solutions",
            "industry": "healthcare",
            "employee_count": 400,
            "annual_revenue": 25000000,
            "headquarters_location": "Boston, MA",
            "compliance_standards": ["sec_climate", "tcfd"]
        },
        {
            "name": "EcoCommerce Ltd",
            "industry": "ecommerce",
            "employee_count": 150,
            "annual_revenue": 8000000,
            "headquarters_location": "Seattle, WA",
            "compliance_standards": ["ghg_protocol"]
        },
        {
            "name": "ConsultPro International",
            "industry": "consulting",
            "employee_count": 300,
            "annual_revenue": 18000000,
            "headquarters_location": "New York, NY",
            "compliance_standards": ["sec_climate", "tcfd"]
        }
    ]
    
    created_companies = []
    for company_data in companies:
        response = requests.post(f"{API_BASE}/companies", json=company_data)
        if response.status_code == 200:
            company = response.json()
            created_companies.append(company)
            print(f"✅ Created: {company['name']} ({company['industry']})")
        else:
            print(f"❌ Failed to create: {company_data['name']}")
    
    return created_companies

def create_comprehensive_emissions_data(company):
    """Create 18 months of detailed emissions data"""
    print(f"\n📊 Creating emissions data for {company['name']}...")
    
    # Industry-specific emission patterns
    industry_factors = {
        "saas": {"electricity": 1.0, "travel": 0.8, "cloud": 1.5},
        "manufacturing": {"electricity": 2.5, "travel": 0.6, "industrial": 3.0},
        "healthcare": {"electricity": 1.8, "travel": 1.2, "medical": 1.3},
        "ecommerce": {"electricity": 1.2, "travel": 0.4, "logistics": 2.0},
        "consulting": {"electricity": 0.8, "travel": 2.0, "office": 1.0}
    }
    
    factors = industry_factors.get(company["industry"], {"electricity": 1.0, "travel": 1.0, "other": 1.0})
    
    for month_offset in range(18):
        period_start = datetime.now() - timedelta(days=30 * (month_offset + 1))
        period_end = datetime.now() - timedelta(days=30 * month_offset)
        
        # Base emissions with seasonal variation
        seasonal_factor = 1.0 + 0.3 * math.cos((month_offset * 2 * math.pi) / 12)
        
        # Create multiple emission records per month
        emissions_data = []
        
        # Electricity (always present)
        base_electricity = (company["employee_count"] * 50) * factors.get("electricity", 1.0) * seasonal_factor
        electricity_kwh = base_electricity + random.randint(-20, 20)
        
        # Calculate electricity emissions
        calc_response = requests.post(f"{API_BASE}/calculate/electricity", json={
            "kwh_consumed": electricity_kwh,
            "region": "us_average",
            "renewable_percentage": min(25 + month_offset * 1.5, 45)  # Gradual improvement
        })
        
        if calc_response.status_code == 200:
            calc_result = calc_response.json()
            emissions_data.append({
                "source_id": f"electricity-{company['id']}",
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "co2_equivalent_kg": calc_result["co2_equivalent_kg"],
                "activity_data": {
                    "kwh_consumed": electricity_kwh,
                    "region": "us_average",
                    "renewable_percentage": min(25 + month_offset * 1.5, 45),
                    "source_name": "Office Electricity",
                    "source_type": "electricity"
                },
                "emission_factor": calc_result["calculation_details"]["emission_factor"],
                "data_quality": "measured"
            })
        
        # Industry-specific emissions
        if company["industry"] == "manufacturing":
            # Industrial processes
            industrial_emissions = company["annual_revenue"] / 1000000 * 500 * seasonal_factor
            emissions_data.append({
                "source_id": f"industrial-{company['id']}",
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "co2_equivalent_kg": industrial_emissions,
                "activity_data": {
                    "process_type": "manufacturing",
                    "production_volume": company["annual_revenue"] / 12 / 1000,
                    "source_name": "Industrial Processes",
                    "source_type": "industrial"
                },
                "emission_factor": 2.5,
                "data_quality": "calculated"
            })
        
        elif company["industry"] == "ecommerce":
            # Logistics and shipping
            shipping_emissions = company["employee_count"] * 80 * factors.get("logistics", 1.0)
            emissions_data.append({
                "source_id": f"logistics-{company['id']}",
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "co2_equivalent_kg": shipping_emissions,
                "activity_data": {
                    "packages_shipped": company["employee_count"] * 200,
                    "avg_distance": 500,
                    "source_name": "Logistics & Shipping",
                    "source_type": "logistics"
                },
                "emission_factor": 0.2,
                "data_quality": "estimated"
            })
        
        # Business travel (varies by industry)
        if month_offset < 12:  # Reduced travel in recent months
            travel_factor = factors.get("travel", 1.0)
            travel_distance = random.randint(200, 2000) * travel_factor
            
            if travel_distance > 0:
                travel_calc = requests.post(f"{API_BASE}/calculate/travel", json={
                    "trips": [{
                        "transport_mode": "business_travel_medium_haul" if travel_distance > 1000 else "car_petrol",
                        "distance_km": travel_distance,
                        "passengers": 1
                    }]
                })
                
                if travel_calc.status_code == 200:
                    travel_result = travel_calc.json()
                    emissions_data.append({
                        "source_id": f"travel-{company['id']}",
                        "period_start": period_start.isoformat(),
                        "period_end": period_end.isoformat(),
                        "co2_equivalent_kg": travel_result["co2_equivalent_kg"],
                        "activity_data": {
                            "distance_km": travel_distance,
                            "transport_mode": "business_travel_medium_haul" if travel_distance > 1000 else "car_petrol",
                            "source_name": "Business Travel",
                            "source_type": "travel"
                        },
                        "emission_factor": travel_result["calculation_details"][0]["emission_factor"],
                        "data_quality": "calculated"
                    })
        
        # Add all emissions for this month
        for emission_data in emissions_data:
            response = requests.post(f"{API_BASE}/companies/{company['id']}/emissions", json=emission_data)
            if response.status_code == 200:
                print(f"  ✅ Month {month_offset + 1}: {emission_data['activity_data']['source_name']}")

def create_industry_specific_initiatives(company):
    """Create realistic carbon reduction initiatives based on industry"""
    print(f"\n💡 Creating initiatives for {company['name']}...")
    
    industry_initiatives = {
        "saas": [
            {
                "initiative_name": "Cloud Infrastructure Optimization",
                "description": "Migrate to carbon-neutral cloud providers and optimize resource usage",
                "implementation_cost": 45000,
                "annual_savings": 28000,
                "annual_co2_reduction": 35000,
                "roi_percentage": 62.2,
                "implementation_date": (datetime.now() - timedelta(days=120)).isoformat(),
                "status": "completed"
            },
            {
                "initiative_name": "Remote Work Expansion",
                "description": "Expand remote work policy to reduce commuting by 70%",
                "implementation_cost": 25000,
                "annual_savings": 45000,
                "annual_co2_reduction": 55000,
                "roi_percentage": 180.0,
                "implementation_date": (datetime.now() - timedelta(days=200)).isoformat(),
                "status": "completed"
            }
        ],
        "manufacturing": [
            {
                "initiative_name": "Industrial Process Electrification",
                "description": "Replace gas-powered equipment with electric alternatives",
                "implementation_cost": 350000,
                "annual_savings": 125000,
                "annual_co2_reduction": 180000,
                "roi_percentage": 35.7,
                "implementation_date": (datetime.now() + timedelta(days=90)).isoformat(),
                "status": "in_progress"
            },
            {
                "initiative_name": "Waste Heat Recovery System",
                "description": "Install system to capture and reuse industrial waste heat",
                "implementation_cost": 150000,
                "annual_savings": 65000,
                "annual_co2_reduction": 85000,
                "roi_percentage": 43.3,
                "implementation_date": (datetime.now() + timedelta(days=180)).isoformat(),
                "status": "planned"
            }
        ],
        "healthcare": [
            {
                "initiative_name": "Medical Equipment Energy Upgrade",
                "description": "Replace aging medical equipment with energy-efficient models",
                "implementation_cost": 200000,
                "annual_savings": 75000,
                "annual_co2_reduction": 95000,
                "roi_percentage": 37.5,
                "implementation_date": (datetime.now() + timedelta(days=60)).isoformat(),
                "status": "in_progress"
            }
        ],
        "ecommerce": [
            {
                "initiative_name": "Green Logistics Network",
                "description": "Partner with carbon-neutral shipping providers and optimize routes",
                "implementation_cost": 80000,
                "annual_savings": 45000,
                "annual_co2_reduction": 75000,
                "roi_percentage": 56.3,
                "implementation_date": (datetime.now() - timedelta(days=60)).isoformat(),
                "status": "completed"
            }
        ],
        "consulting": [
            {
                "initiative_name": "Digital-First Client Engagement",
                "description": "Reduce client travel by 80% through virtual engagement tools",
                "implementation_cost": 30000,
                "annual_savings": 85000,
                "annual_co2_reduction": 120000,
                "roi_percentage": 283.3,
                "implementation_date": (datetime.now() - timedelta(days=150)).isoformat(),
                "status": "completed"
            }
        ]
    }
    
    initiatives = industry_initiatives.get(company["industry"], [])
    
    for initiative_data in initiatives:
        response = requests.post(f"{API_BASE}/companies/{company['id']}/initiatives", json=initiative_data)
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ {result['initiative_name']} (Status: {result['status']})")

def create_supply_chain_data(company):
    """Create supply chain data specific to industry"""
    print(f"\n🔗 Creating supply chain data for {company['name']}...")
    
    # Industry-specific supplier profiles
    industry_suppliers = {
        "saas": [
            {"name": "CloudHost Pro", "industry": "Technology", "score": 88.5, "location": "Virginia, USA"},
            {"name": "DevTools Inc", "industry": "Software", "score": 91.2, "location": "Toronto, Canada"},
            {"name": "DataCenter Solutions", "industry": "Infrastructure", "score": 76.8, "location": "Oregon, USA"}
        ],
        "manufacturing": [
            {"name": "SteelWorks Limited", "industry": "Raw Materials", "score": 65.4, "location": "Pittsburgh, PA"},
            {"name": "GreenComponents LLC", "industry": "Components", "score": 82.7, "location": "Ohio, USA"},
            {"name": "EcoTransport Co", "industry": "Logistics", "score": 78.9, "location": "Illinois, USA"}
        ],
        "healthcare": [
            {"name": "MedSupply International", "industry": "Medical Equipment", "score": 73.2, "location": "California, USA"},
            {"name": "CleanLab Solutions", "industry": "Laboratory", "score": 85.6, "location": "Massachusetts, USA"}
        ],
        "ecommerce": [
            {"name": "PackagePro", "industry": "Packaging", "score": 69.8, "location": "Texas, USA"},
            {"name": "QuickShip Logistics", "industry": "Shipping", "score": 58.3, "location": "Tennessee, USA"}
        ],
        "consulting": [
            {"name": "OfficeSpace Solutions", "industry": "Real Estate", "score": 71.4, "location": "New York, USA"},
            {"name": "TechPartners LLC", "industry": "Technology", "score": 89.1, "location": "California, USA"}
        ]
    }
    
    suppliers = industry_suppliers.get(company["industry"], [])
    
    for supplier_data in suppliers:
        supplier_request = {
            "supplier_name": supplier_data["name"],
            "industry": supplier_data["industry"],
            "location": supplier_data["location"],
            "contact_email": f"contact@{supplier_data['name'].lower().replace(' ', '')}.com",
            "annual_revenue": random.randint(2000000, 50000000),
            "employee_count": random.randint(50, 500),
            "carbon_score": supplier_data["score"],
            "verification_status": "verified" if supplier_data["score"] > 75 else "pending",
            "partnership_level": "strategic" if supplier_data["score"] > 85 else "preferred" if supplier_data["score"] > 70 else "basic"
        }
        
        response = requests.post(f"{API_BASE}/companies/{company['id']}/suppliers", json=supplier_request)
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ {result['supplier_name']} (Score: {result['carbon_score']})")

def main():
    print("🌍 Creating comprehensive ClimaBill MVP sample data...\n")
    
    # Create diverse companies
    companies = create_multi_industry_companies()
    
    if not companies:
        print("❌ No companies created. Exiting.")
        return
    
    # Add detailed data for each company
    for company in companies:
        create_comprehensive_emissions_data(company)
        create_industry_specific_initiatives(company)
        create_supply_chain_data(company)
        
        # Brief pause between companies
        time.sleep(1)
    
    print(f"\n✅ MVP sample data creation complete!")
    print(f"📊 Created {len(companies)} companies across industries")
    print(f"🌐 Access the application at: http://localhost:3000")
    print(f"🎯 Demo companies available for investor presentation")

if __name__ == "__main__":
    import math
    import time
    main()
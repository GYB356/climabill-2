#!/usr/bin/env python3
"""
Enhanced sample data generation script for ClimaBill
Creates comprehensive demo data for investor presentation
"""
import requests
import json
from datetime import datetime, timedelta
import random
import uuid

API_BASE = "http://localhost:8001/api"

def create_comprehensive_company():
    """Create a comprehensive company with rich data"""
    company_data = {
        "name": "EcoTech Solutions",
        "industry": "saas",
        "employee_count": 150,
        "annual_revenue": 5000000,
        "headquarters_location": "San Francisco, CA",
        "compliance_standards": ["eu_csrd", "sec_climate", "ghg_protocol"]
    }
    
    response = requests.post(f"{API_BASE}/companies", json=company_data)
    if response.status_code == 200:
        company = response.json()
        print(f"✅ Created company: {company['name']} (ID: {company['id']})")
        return company['id']
    else:
        print(f"❌ Failed to create company: {response.text}")
        return None

def add_comprehensive_emissions(company_id):
    """Add comprehensive emission data for the last 12 months"""
    print("\n📊 Adding comprehensive emission data...")
    
    # Generate emission records for the last 12 months
    for month_offset in range(12):
        period_start = datetime.now() - timedelta(days=30 * (month_offset + 1))
        period_end = datetime.now() - timedelta(days=30 * month_offset)
        
        # Electricity emissions (monthly variation)
        electricity_kwh = random.randint(8000, 15000) + (month_offset * 200)  # Growing usage
        calc_response = requests.post(f"{API_BASE}/calculate/electricity", json={
            "kwh_consumed": electricity_kwh,
            "region": "us_average",
            "renewable_percentage": min(30 + month_offset * 2, 50)  # Increasing renewable %
        })
        
        if calc_response.status_code == 200:
            calc_result = calc_response.json()
            
            emission_record = {
                "source_id": "electricity-office-main",
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "co2_equivalent_kg": calc_result["co2_equivalent_kg"],
                "activity_data": {
                    "kwh_consumed": electricity_kwh,
                    "region": "us_average",
                    "renewable_percentage": min(30 + month_offset * 2, 50),
                    "source_name": "Office Electricity",
                    "source_type": "electricity"
                },
                "emission_factor": calc_result["calculation_details"]["emission_factor"],
                "data_quality": "measured"
            }
            
            response = requests.post(f"{API_BASE}/companies/{company_id}/emissions", json=emission_record)
            if response.status_code == 200:
                print(f"  ✅ Added electricity emissions for month {month_offset + 1}: {calc_result['co2_equivalent_kg']:.2f} kg CO2eq")
        
        # Business travel emissions
        if month_offset < 8:  # Reduced travel in recent months
            travel_distance = random.randint(500, 3000)
            travel_calc = requests.post(f"{API_BASE}/calculate/travel", json={
                "trips": [{
                    "transport_mode": "business_travel_medium_haul",
                    "distance_km": travel_distance,
                    "passengers": 1
                }]
            })
            
            if travel_calc.status_code == 200:
                travel_result = travel_calc.json()
                
                travel_record = {
                    "source_id": "business-travel-flights",
                    "period_start": period_start.isoformat(),
                    "period_end": period_end.isoformat(),
                    "co2_equivalent_kg": travel_result["co2_equivalent_kg"],
                    "activity_data": {
                        "transport_mode": "business_travel_medium_haul",
                        "distance_km": travel_distance,
                        "passengers": 1,
                        "source_name": "Business Travel",
                        "source_type": "travel"
                    },
                    "emission_factor": travel_result["calculation_details"][0]["emission_factor"],
                    "data_quality": "calculated"
                }
                
                requests.post(f"{API_BASE}/companies/{company_id}/emissions", json=travel_record)
                print(f"  ✅ Added travel emissions for month {month_offset + 1}: {travel_result['co2_equivalent_kg']:.2f} kg CO2eq")

def add_carbon_targets(company_id):
    """Add comprehensive carbon reduction targets"""
    print("\n🎯 Adding carbon reduction targets...")
    
    targets = [
        {
            "target_name": "2030 Net Zero Commitment",
            "baseline_year": 2023,
            "target_year": 2030,
            "baseline_emissions": 50000,
            "target_reduction_percentage": 100,
            "scope_coverage": ["scope_1", "scope_2", "scope_3"]
        },
        {
            "target_name": "2025 Interim Target",
            "baseline_year": 2023,
            "target_year": 2025,
            "baseline_emissions": 50000,
            "target_reduction_percentage": 40,
            "scope_coverage": ["scope_1", "scope_2"]
        },
        {
            "target_name": "Renewable Energy Goal",
            "baseline_year": 2023,
            "target_year": 2026,
            "baseline_emissions": 20000,
            "target_reduction_percentage": 80,
            "scope_coverage": ["scope_2"]
        }
    ]
    
    for target in targets:
        response = requests.post(f"{API_BASE}/companies/{company_id}/targets", json=target)
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Added target: {result['target_name']}")
        else:
            print(f"  ❌ Failed to add target: {response.text}")

def add_reduction_initiatives(company_id):
    """Add comprehensive carbon reduction initiatives"""
    print("\n💡 Adding carbon reduction initiatives...")
    
    initiatives = [
        {
            "initiative_name": "LED Lighting Upgrade",
            "description": "Replace all office lighting with energy-efficient LED bulbs and smart controls",
            "implementation_cost": 25000,
            "annual_savings": 8500,
            "annual_co2_reduction": 15000,
            "roi_percentage": 34.0,
            "implementation_date": (datetime.now() - timedelta(days=180)).isoformat(),
            "status": "completed"
        },
        {
            "initiative_name": "Remote Work Policy Expansion",
            "description": "Implement hybrid remote work to reduce commuting emissions by 60%",
            "implementation_cost": 15000,
            "annual_savings": 25000,
            "annual_co2_reduction": 45000,
            "roi_percentage": 166.7,
            "implementation_date": (datetime.now() - timedelta(days=90)).isoformat(),
            "status": "completed"
        },
        {
            "initiative_name": "100% Renewable Energy Contract",
            "description": "Switch to verified 100% renewable energy provider with RECs",
            "implementation_cost": 45000,
            "annual_savings": 18000,
            "annual_co2_reduction": 85000,
            "roi_percentage": 40.0,
            "implementation_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "status": "in_progress"
        },
        {
            "initiative_name": "Employee Carbon Awareness Program",
            "description": "Training and incentive program to reduce individual carbon footprints",
            "implementation_cost": 12000,
            "annual_savings": 5000,
            "annual_co2_reduction": 8000,
            "roi_percentage": 41.7,
            "implementation_date": (datetime.now() + timedelta(days=60)).isoformat(),
            "status": "planned"
        },
        {
            "initiative_name": "Green Cloud Migration",
            "description": "Migrate to carbon-neutral cloud providers and optimize resource usage",
            "implementation_cost": 35000,
            "annual_savings": 22000,
            "annual_co2_reduction": 35000,
            "roi_percentage": 62.9,
            "implementation_date": (datetime.now() + timedelta(days=120)).isoformat(),
            "status": "planned"
        },
        {
            "initiative_name": "Sustainable Commuting Incentives",
            "description": "Electric vehicle charging stations and public transport subsidies",
            "implementation_cost": 55000,
            "annual_savings": 12000,
            "annual_co2_reduction": 25000,
            "roi_percentage": 21.8,
            "implementation_date": (datetime.now() + timedelta(days=180)).isoformat(),
            "status": "planned"
        }
    ]
    
    for initiative in initiatives:
        response = requests.post(f"{API_BASE}/companies/{company_id}/initiatives", json=initiative)
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Added initiative: {result['initiative_name']} (Status: {result['status']})")
        else:
            print(f"  ❌ Failed to add initiative: {response.text}")

def test_ai_integration(company_id):
    """Test AI integration with sample queries"""
    print("\n🤖 Testing AI integration...")
    
    sample_queries = [
        "What is our current carbon footprint and how does it compare to industry benchmarks?",
        "What are our top 3 emission sources and what reduction opportunities do you recommend?",
        "Calculate the ROI for switching to 100% renewable energy",
        "How much can we save by implementing all our planned initiatives?"
    ]
    
    for query in sample_queries:
        response = requests.post(f"{API_BASE}/companies/{company_id}/ai/query", json={
            "company_id": company_id,
            "query_text": query
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ AI Query successful: '{query[:50]}...'")
            if "quota" not in result['response'].lower():
                print(f"     Response: {result['response'][:100]}...")
            else:
                print(f"     Response: AI quota exceeded (expected)")
        else:
            print(f"  ❌ AI Query failed: {response.text}")

def generate_forecasts(company_id):
    """Generate AI-powered forecasts"""
    print("\n📈 Generating emissions forecasts...")
    
    response = requests.post(f"{API_BASE}/companies/{company_id}/ai/forecast", json={
        "horizon_months": 12
    })
    
    if response.status_code == 200:
        result = response.json()
        print(f"  ✅ Generated forecast for 12 months")
        print(f"     Predicted total emissions: {sum(result['predicted_emissions'].values()):.2f} kg CO2eq")
    else:
        print(f"  ❌ Forecast generation failed: {response.text}")

def create_additional_companies():
    """Create additional companies for benchmarking"""
    print("\n🏢 Creating additional companies for benchmarking...")
    
    companies = [
        {
            "name": "TechFlow Systems",
            "industry": "saas",
            "employee_count": 200,
            "annual_revenue": 8000000,
            "headquarters_location": "Austin, TX",
            "compliance_standards": ["ghg_protocol"]
        },
        {
            "name": "GreenData Corp",
            "industry": "saas", 
            "employee_count": 75,
            "annual_revenue": 2500000,
            "headquarters_location": "Seattle, WA",
            "compliance_standards": ["eu_csrd"]
        },
        {
            "name": "CloudVision Inc",
            "industry": "saas",
            "employee_count": 300,
            "annual_revenue": 12000000,
            "headquarters_location": "New York, NY",
            "compliance_standards": ["sec_climate", "ghg_protocol"]
        }
    ]
    
    created_companies = []
    for company_data in companies:
        response = requests.post(f"{API_BASE}/companies", json=company_data)
        if response.status_code == 200:
            company = response.json()
            created_companies.append(company['id'])
            print(f"  ✅ Created: {company['name']}")
    
    return created_companies

def main():
    print("🌍 Creating comprehensive demo data for ClimaBill investor presentation...")
    
    # Create main company
    company_id = create_comprehensive_company()
    if not company_id:
        return
    
    # Add comprehensive data
    add_comprehensive_emissions(company_id)
    add_carbon_targets(company_id)
    add_reduction_initiatives(company_id)
    
    # Test AI features
    test_ai_integration(company_id)
    generate_forecasts(company_id)
    
    # Create additional companies for benchmarking
    additional_companies = create_additional_companies()
    
    print(f"\n✅ Comprehensive demo data created successfully!")
    print(f"🎯 Main Company ID: {company_id}")
    print(f"📊 Additional Companies: {len(additional_companies)}")
    print(f"🌐 Access the application at: http://localhost:3000")
    print(f"📈 Dashboard URL: http://localhost:3000/dashboard")
    print(f"🤖 AI Chat URL: http://localhost:3000/ai-chat")
    
    # Test dashboard endpoint
    print(f"\n📊 Testing dashboard data...")
    dashboard_response = requests.get(f"{API_BASE}/companies/{company_id}/dashboard")
    if dashboard_response.status_code == 200:
        dashboard_data = dashboard_response.json()
        total_emissions = sum(dashboard_data['total_emissions'].values())
        print(f"✅ Dashboard loaded - Total emissions: {total_emissions:.2f} kg CO2eq")
        print(f"📈 Emissions trend data points: {len(dashboard_data['emissions_trend'])}")
        print(f"💰 Financial impact data: ${dashboard_data['financial_impact']['annual_cost_savings']:,.2f} annual savings")
    else:
        print(f"❌ Dashboard test failed: {dashboard_response.text}")

if __name__ == "__main__":
    main()
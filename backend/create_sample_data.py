#!/usr/bin/env python3
"""
Sample data generation script for ClimaBill
"""
import requests
import json
from datetime import datetime, timedelta
import random

API_BASE = "http://localhost:8001/api"

# Sample company data
company_data = {
    "name": "EcoTech Solutions",
    "industry": "saas",
    "employee_count": 150,
    "annual_revenue": 5000000,
    "headquarters_location": "San Francisco, CA",
    "compliance_standards": ["eu_csrd", "sec_climate"]
}

def create_company():
    """Create a sample company"""
    response = requests.post(f"{API_BASE}/companies", json=company_data)
    if response.status_code == 200:
        company = response.json()
        print(f"✅ Created company: {company['name']} (ID: {company['id']})")
        return company['id']
    else:
        print(f"❌ Failed to create company: {response.text}")
        return None

def add_sample_emissions(company_id):
    """Add sample emission data"""
    # Sample emission records
    emission_records = [
        {
            "source_id": "sample-electricity-source",
            "period_start": (datetime.now() - timedelta(days=30)).isoformat(),
            "period_end": datetime.now().isoformat(),
            "co2_equivalent_kg": random.randint(1000, 5000),
            "activity_data": {
                "kwh_consumed": random.randint(5000, 15000),
                "region": "us_average",
                "renewable_percentage": random.randint(10, 30)
            },
            "emission_factor": 0.385,
            "data_quality": "estimated"
        },
        {
            "source_id": "sample-travel-source", 
            "period_start": (datetime.now() - timedelta(days=30)).isoformat(),
            "period_end": datetime.now().isoformat(),
            "co2_equivalent_kg": random.randint(500, 2000),
            "activity_data": {
                "transport_mode": "business_travel_medium_haul",
                "distance_km": random.randint(1000, 5000),
                "passengers": 1
            },
            "emission_factor": 0.102,
            "data_quality": "calculated"
        }
    ]
    
    for record in emission_records:
        response = requests.post(f"{API_BASE}/companies/{company_id}/emissions", json=record)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Added emission record: {result['co2_equivalent_kg']} kg CO2eq")
        else:
            print(f"❌ Failed to add emission record: {response.text}")

def add_sample_initiatives(company_id):
    """Add sample carbon reduction initiatives"""
    initiatives = [
        {
            "company_id": company_id,
            "initiative_name": "LED Lighting Upgrade",
            "description": "Replace all office lighting with energy-efficient LED bulbs",
            "implementation_cost": 15000,
            "annual_savings": 3500,
            "annual_co2_reduction": 12000,
            "roi_percentage": 23.3,
            "implementation_date": datetime.now().isoformat(),
            "status": "completed"
        },
        {
            "company_id": company_id,
            "initiative_name": "Remote Work Policy",
            "description": "Implement hybrid remote work to reduce commuting emissions",
            "implementation_cost": 5000,
            "annual_savings": 8000,
            "annual_co2_reduction": 25000,
            "roi_percentage": 160,
            "implementation_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "status": "planned"
        },
        {
            "company_id": company_id,
            "initiative_name": "Renewable Energy Contract",
            "description": "Switch to 100% renewable energy provider",
            "implementation_cost": 25000,
            "annual_savings": 12000,
            "annual_co2_reduction": 45000,
            "roi_percentage": 48,
            "implementation_date": (datetime.now() + timedelta(days=60)).isoformat(),
            "status": "in_progress"
        }
    ]
    
    for initiative in initiatives:
        response = requests.post(f"{API_BASE}/companies/{company_id}/initiatives", json=initiative)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Added initiative: {result['initiative_name']}")
        else:
            print(f"❌ Failed to add initiative: {response.text}")

def main():
    print("🌍 Creating sample data for ClimaBill...")
    
    # Create company
    company_id = create_company()
    if not company_id:
        return
    
    # Add sample data
    print("\n📊 Adding sample emission data...")
    add_sample_emissions(company_id)
    
    print("\n💡 Adding sample initiatives...")
    add_sample_initiatives(company_id)
    
    print(f"\n✅ Sample data created successfully!")
    print(f"Company ID: {company_id}")
    print(f"Access the dashboard at: http://localhost:3000")

if __name__ == "__main__":
    main()
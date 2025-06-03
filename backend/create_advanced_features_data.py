#!/usr/bin/env python3
"""
Create sample data for blockchain marketplace and supply chain features
"""
import requests
import json
from datetime import datetime, timedelta
import random

API_BASE = "http://localhost:8001/api"

def create_sample_supply_chain_data(company_id):
    """Create sample supply chain data"""
    print("\n🔗 Creating supply chain sample data...")
    
    # Sample suppliers
    suppliers = [
        {
            "supplier_name": "EcoMaterials Corp",
            "industry": "Raw Materials",
            "location": "Portland, OR",
            "contact_email": "contact@ecomaterials.com",
            "annual_revenue": 25000000,
            "employee_count": 200,
            "carbon_score": 85.2,
            "verification_status": "verified",
            "partnership_level": "strategic"
        },
        {
            "supplier_name": "GreenLogistics LLC",
            "industry": "Transportation",
            "location": "Denver, CO",
            "contact_email": "info@greenlogistics.com",
            "annual_revenue": 15000000,
            "employee_count": 150,
            "carbon_score": 72.8,
            "verification_status": "verified",
            "partnership_level": "preferred"
        },
        {
            "supplier_name": "CloudTech Solutions",
            "industry": "Technology",
            "location": "Austin, TX",
            "contact_email": "sales@cloudtech.com",
            "annual_revenue": 8000000,
            "employee_count": 80,
            "carbon_score": 91.5,
            "verification_status": "verified",
            "partnership_level": "strategic"
        },
        {
            "supplier_name": "TradPrint Services",
            "industry": "Manufacturing",
            "location": "Cleveland, OH",
            "contact_email": "orders@tradprint.com",
            "annual_revenue": 3000000,
            "employee_count": 45,
            "carbon_score": 45.2,
            "verification_status": "pending",
            "partnership_level": "basic"
        },
        {
            "supplier_name": "FastShip Express",
            "industry": "Logistics",
            "location": "Memphis, TN",
            "contact_email": "support@fastship.com",
            "annual_revenue": 12000000,
            "employee_count": 300,
            "carbon_score": 38.7,
            "verification_status": "flagged",
            "partnership_level": "basic"
        }
    ]
    
    created_suppliers = []
    for supplier_data in suppliers:
        response = requests.post(f"{API_BASE}/companies/{company_id}/suppliers", json=supplier_data)
        if response.status_code == 200:
            supplier = response.json()
            created_suppliers.append(supplier)
            print(f"  ✅ Added supplier: {supplier['supplier_name']} (Score: {supplier['carbon_score']})")
        else:
            print(f"  ❌ Failed to add supplier: {response.text}")
    
    # Sample supply chain emissions
    emission_activities = [
        {
            "activity_description": "Raw material transportation from EcoMaterials",
            "emission_type": "upstream",
            "scope": "scope_3",
            "co2_equivalent_kg": 15000,
            "data_quality": "calculated"
        },
        {
            "activity_description": "Product delivery via GreenLogistics",
            "emission_type": "downstream",
            "scope": "scope_3", 
            "co2_equivalent_kg": 8500,
            "data_quality": "measured"
        },
        {
            "activity_description": "Cloud infrastructure from CloudTech",
            "emission_type": "upstream",
            "scope": "scope_2",
            "co2_equivalent_kg": 3200,
            "data_quality": "calculated"
        },
        {
            "activity_description": "Printed materials from TradPrint",
            "emission_type": "upstream",
            "scope": "scope_3",
            "co2_equivalent_kg": 2800,
            "data_quality": "estimated"
        },
        {
            "activity_description": "Express shipping via FastShip",
            "emission_type": "downstream",
            "scope": "scope_3",
            "co2_equivalent_kg": 12000,
            "data_quality": "supplier_reported"
        }
    ]
    
    for i, emission_data in enumerate(emission_activities):
        if i < len(created_suppliers):
            emission_data["supplier_id"] = created_suppliers[i]["id"]
            
            response = requests.post(f"{API_BASE}/companies/{company_id}/supply-chain-emissions", json=emission_data)
            if response.status_code == 200:
                print(f"  ✅ Added emission data: {emission_data['activity_description']}")
            else:
                print(f"  ❌ Failed to add emission data: {response.text}")

def create_sample_marketplace_purchases(company_id):
    """Create sample marketplace purchases"""
    print("\n⛓️ Creating sample marketplace purchases...")
    
    # Get available projects
    response = requests.get(f"{API_BASE}/marketplace/projects")
    if response.status_code != 200:
        print("  ❌ Failed to get marketplace projects")
        return
    
    projects = response.json()["projects"]
    
    # Make some sample purchases
    purchases = [
        {"listing_id": "LIST-001", "credits": 500, "reason": "Q4 carbon neutrality goal"},
        {"listing_id": "LIST-002", "credits": 750, "reason": "Annual sustainability commitment"},
        {"listing_id": "LIST-003", "credits": 200, "reason": "Product launch carbon offset"}
    ]
    
    for purchase in purchases:
        # Purchase credits
        purchase_response = requests.post(f"{API_BASE}/marketplace/purchase", json={
            "listing_id": purchase["listing_id"],
            "credits_amount": purchase["credits"],
            "company_id": company_id
        })
        
        if purchase_response.status_code == 200:
            result = purchase_response.json()
            print(f"  ✅ Purchased {purchase['credits']} credits for ${result['total_cost']:.2f}")
            
            # Retire some credits immediately
            retire_amount = purchase["credits"] // 2
            if retire_amount > 0:
                retire_response = requests.post(f"{API_BASE}/marketplace/retire", json={
                    "certificate_id": result["purchase_id"],
                    "credits_amount": retire_amount,
                    "retirement_reason": purchase["reason"],
                    "company_id": company_id
                })
                
                if retire_response.status_code == 200:
                    print(f"    ✅ Retired {retire_amount} credits for: {purchase['reason']}")
                else:
                    print(f"    ❌ Failed to retire credits: {retire_response.text}")
        else:
            print(f"  ❌ Failed to purchase credits: {purchase_response.text}")

def test_new_apis(company_id):
    """Test the new API endpoints"""
    print("\n🧪 Testing new API endpoints...")
    
    # Test supply chain dashboard
    response = requests.get(f"{API_BASE}/companies/{company_id}/supply-chain/dashboard")
    if response.status_code == 200:
        dashboard = response.json()
        print(f"  ✅ Supply chain dashboard - {dashboard['total_suppliers']} suppliers, avg score: {dashboard['average_carbon_score']:.1f}")
    else:
        print(f"  ❌ Supply chain dashboard failed: {response.text}")
    
    # Test marketplace projects
    response = requests.get(f"{API_BASE}/marketplace/projects?project_type=Forest Conservation")
    if response.status_code == 200:
        projects = response.json()
        print(f"  ✅ Marketplace projects - {len(projects['projects'])} forest conservation projects found")
    else:
        print(f"  ❌ Marketplace projects failed: {response.text}")
    
    # Test certificates
    response = requests.get(f"{API_BASE}/companies/{company_id}/certificates")
    if response.status_code == 200:
        certificates = response.json()
        total_credits = sum(cert['credits_amount'] for cert in certificates)
        print(f"  ✅ Carbon certificates - {len(certificates)} certificates, {total_credits} total credits")
    else:
        print(f"  ❌ Certificates endpoint failed: {response.text}")

def main():
    print("🌍 Creating sample data for new ClimaBill features...")
    
    # Use the existing company ID from previous demo data
    company_id = "8b4b1648-31af-4859-9b2d-bd3eb6fa6043"  # Update this with actual company ID
    
    # Get companies to find the right ID
    response = requests.get(f"{API_BASE}/companies")
    if response.status_code == 200:
        companies = response.json()
        if companies:
            company_id = companies[0]["id"]  # Use the first company
            print(f"🎯 Using company: {companies[0]['name']} (ID: {company_id})")
        else:
            print("❌ No companies found. Please run create_enhanced_demo_data.py first")
            return
    else:
        print("❌ Failed to fetch companies")
        return
    
    # Create sample data
    create_sample_supply_chain_data(company_id)
    create_sample_marketplace_purchases(company_id)
    
    # Test the new APIs
    test_new_apis(company_id)
    
    print(f"\n✅ Sample data for new features created successfully!")
    print(f"🌐 Access the application at: http://localhost:3000")
    print(f"⛓️ Test Carbon Marketplace: http://localhost:3000/marketplace")
    print(f"🔗 Test Supply Chain: http://localhost:3000/supply-chain")

if __name__ == "__main__":
    main()
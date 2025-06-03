#!/usr/bin/env python3
"""
Create sample tenant data for testing multi-tenancy in ClimaBill.
Creates two test tenants (Alpha and Beta) with isolated sample data.
"""

import asyncio
import os
import uuid
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from multitenancy_service import MultiTenancyService
from auth_models import TenantPlan, UserRole
import hashlib
from jose import jwt

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "climabill_database")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "climabill-secret-key-change-in-production")

async def create_sample_tenants():
    """Create sample tenant data"""
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    multitenancy = MultiTenancyService(db)
    
    print("🏢 Creating sample tenants...")
    
    # Tenant Alpha - Technology Company
    tenant_alpha_id = str(uuid.uuid4())
    alpha_tenant = await multitenancy.create_tenant({
        "id": tenant_alpha_id,
        "name": "Alpha Tech Solutions",
        "domain": "alpha-tech.com",
        "plan": TenantPlan.ENTERPRISE,
        "industry": "Technology",
        "employee_count": 500,
        "annual_revenue": 50000000,
        "headquarters_location": "San Francisco, CA",
        "compliance_standards": ["ISO 14001", "CDP", "SBTi"],
        "max_users": 50,
        "features_enabled": [
            "carbon_tracking", "ai_chat", "marketplace", "compliance", 
            "supply_chain", "blockchain", "advanced_analytics"
        ]
    })
    
    # Tenant Beta - Manufacturing Company  
    tenant_beta_id = str(uuid.uuid4())
    beta_tenant = await multitenancy.create_tenant({
        "id": tenant_beta_id,
        "name": "Beta Manufacturing Corp",
        "domain": "beta-manufacturing.com", 
        "plan": TenantPlan.PROFESSIONAL,
        "industry": "Manufacturing",
        "employee_count": 1200,
        "annual_revenue": 150000000,
        "headquarters_location": "Detroit, MI",
        "compliance_standards": ["ISO 14001", "EPA", "CARB"],
        "max_users": 25,
        "features_enabled": [
            "carbon_tracking", "ai_chat", "marketplace", "compliance", "supply_chain"
        ]
    })
    
    print(f"✅ Created tenant Alpha: {tenant_alpha_id}")
    print(f"✅ Created tenant Beta: {tenant_beta_id}")
    
    # Create users for each tenant
    print("\n👥 Creating sample users...")
    
    # Alpha users
    alpha_admin_id = str(uuid.uuid4())
    alpha_admin = {
        "id": alpha_admin_id,
        "email": "admin@alpha-tech.com",
        "first_name": "Alice",
        "last_name": "Alpha",
        "role": UserRole.ADMIN,
        "tenant_id": tenant_alpha_id,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "last_login": datetime.utcnow(),
        "hashed_password": hashlib.sha256("admin123".encode()).hexdigest()
    }
    
    alpha_user_id = str(uuid.uuid4())
    alpha_user = {
        "id": alpha_user_id,
        "email": "user@alpha-tech.com",
        "first_name": "Alan",
        "last_name": "Analyst",
        "role": UserRole.ANALYST,
        "tenant_id": tenant_alpha_id,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "last_login": datetime.utcnow(),
        "hashed_password": hashlib.sha256("user123".encode()).hexdigest()
    }
    
    # Beta users
    beta_admin_id = str(uuid.uuid4())
    beta_admin = {
        "id": beta_admin_id,
        "email": "admin@beta-manufacturing.com",
        "first_name": "Bob",
        "last_name": "Beta",
        "role": UserRole.ADMIN,
        "tenant_id": tenant_beta_id,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "last_login": datetime.utcnow(),
        "hashed_password": hashlib.sha256("admin123".encode()).hexdigest()
    }
    
    beta_user_id = str(uuid.uuid4())
    beta_user = {
        "id": beta_user_id,
        "email": "user@beta-manufacturing.com",
        "first_name": "Betty",
        "last_name": "Manager",
        "role": UserRole.MANAGER,
        "tenant_id": tenant_beta_id,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "last_login": datetime.utcnow(),
        "hashed_password": hashlib.sha256("user123".encode()).hexdigest()
    }
    
    # Insert users
    await multitenancy.users.insert_many([alpha_admin, alpha_user, beta_admin, beta_user])
    
    print(f"✅ Created Alpha admin: {alpha_admin_id}")
    print(f"✅ Created Alpha user: {alpha_user_id}")
    print(f"✅ Created Beta admin: {beta_admin_id}")
    print(f"✅ Created Beta user: {beta_user_id}")
    
    # Create companies for each tenant
    print("\n🏢 Creating sample companies...")
    
    # Alpha companies
    alpha_company_id = str(uuid.uuid4())
    alpha_company = {
        "id": alpha_company_id,
        "name": "Alpha Tech Solutions HQ",
        "industry": "saas",  # Use enum value
        "employee_count": 500,
        "annual_revenue": 50000000.0,
        "headquarters_location": "San Francisco, CA",
        "created_at": datetime.utcnow(),
        "compliance_standards": ["ghg_protocol", "tcfd"]
    }
    
    alpha_subsidiary_id = str(uuid.uuid4())
    alpha_subsidiary = {
        "id": alpha_subsidiary_id,
        "name": "Alpha Data Centers",
        "industry": "saas",  # Use enum value
        "employee_count": 150,
        "annual_revenue": 15000000.0,
        "headquarters_location": "Austin, TX",
        "created_at": datetime.utcnow(),
        "compliance_standards": ["ghg_protocol"]
    }
    
    # Beta companies
    beta_company_id = str(uuid.uuid4())
    beta_company = {
        "id": beta_company_id,
        "name": "Beta Manufacturing Plant 1",
        "industry": "manufacturing",  # Use enum value
        "employee_count": 1200,
        "annual_revenue": 150000000.0,
        "headquarters_location": "Detroit, MI",
        "created_at": datetime.utcnow(),
        "compliance_standards": ["ghg_protocol", "eu_csrd"]
    }
    
    beta_facility_id = str(uuid.uuid4())
    beta_facility = {
        "id": beta_facility_id,
        "name": "Beta Distribution Center",
        "industry": "manufacturing",  # Use enum value
        "employee_count": 200,
        "annual_revenue": 25000000.0,
        "headquarters_location": "Chicago, IL",
        "created_at": datetime.utcnow(),
        "compliance_standards": ["ghg_protocol"]
    }
    
    # Insert companies with tenant scope
    await multitenancy.insert_many_scoped(
        multitenancy.companies,
        [alpha_company, alpha_subsidiary],
        tenant_alpha_id
    )
    
    await multitenancy.insert_many_scoped(
        multitenancy.companies,
        [beta_company, beta_facility], 
        tenant_beta_id
    )
    
    print(f"✅ Created Alpha companies: {alpha_company_id}, {alpha_subsidiary_id}")
    print(f"✅ Created Beta companies: {beta_company_id}, {beta_facility_id}")
    
    # Create emission records
    print("\n🌱 Creating sample emission records...")
    
    base_date = datetime.utcnow() - timedelta(days=365)
    
    # Alpha emission records
    alpha_emissions = []
    for i in range(12):  # 12 months of data
        record_date = base_date + timedelta(days=i * 30)
        
        # Alpha HQ emissions
        alpha_emissions.append({
            "id": str(uuid.uuid4()),
            "company_id": alpha_company_id,
            "facility_name": "San Francisco HQ",
            "emission_source": "Electricity",
            "scope1_emissions": 10.5 + (i * 0.5),
            "scope2_emissions": 25.3 + (i * 1.2),
            "scope3_emissions": 45.7 + (i * 2.1),
            "total_co2e": 81.5 + (i * 3.8),
            "recorded_date": record_date,
            "verification_status": "verified" if i % 3 == 0 else "pending",
            "notes": f"Monthly electricity consumption data for {record_date.strftime('%B %Y')}"
        })
        
        # Alpha Data Center emissions
        alpha_emissions.append({
            "id": str(uuid.uuid4()),
            "company_id": alpha_subsidiary_id,
            "facility_name": "Austin Data Center",
            "emission_source": "Data Center Operations",
            "scope1_emissions": 5.2 + (i * 0.3),
            "scope2_emissions": 85.4 + (i * 4.2),
            "scope3_emissions": 12.1 + (i * 0.8),
            "total_co2e": 102.7 + (i * 5.3),
            "recorded_date": record_date,
            "verification_status": "verified" if i % 2 == 0 else "pending",
            "notes": f"Data center power and cooling for {record_date.strftime('%B %Y')}"
        })
    
    # Beta emission records  
    beta_emissions = []
    for i in range(12):  # 12 months of data
        record_date = base_date + timedelta(days=i * 30)
        
        # Beta Manufacturing emissions
        beta_emissions.append({
            "id": str(uuid.uuid4()),
            "company_id": beta_company_id,
            "facility_name": "Detroit Manufacturing Plant",
            "emission_source": "Manufacturing",
            "scope1_emissions": 150.5 + (i * 8.3),
            "scope2_emissions": 85.3 + (i * 4.5),
            "scope3_emissions": 220.7 + (i * 12.1),
            "total_co2e": 456.5 + (i * 24.9),
            "recorded_date": record_date,
            "verification_status": "verified" if i % 3 == 0 else "pending",
            "notes": f"Manufacturing processes and energy for {record_date.strftime('%B %Y')}"
        })
        
        # Beta Distribution emissions
        beta_emissions.append({
            "id": str(uuid.uuid4()),
            "company_id": beta_facility_id,
            "facility_name": "Chicago Distribution Center",
            "emission_source": "Transportation",
            "scope1_emissions": 45.2 + (i * 2.1),
            "scope2_emissions": 25.4 + (i * 1.2),
            "scope3_emissions": 95.1 + (i * 4.8),
            "total_co2e": 165.7 + (i * 8.1),
            "recorded_date": record_date,
            "verification_status": "verified" if i % 4 == 0 else "pending",
            "notes": f"Logistics and transportation for {record_date.strftime('%B %Y')}"
        })
    
    # Insert emissions with tenant scope
    await multitenancy.insert_many_scoped(
        multitenancy.emissions,
        alpha_emissions,
        tenant_alpha_id
    )
    
    await multitenancy.insert_many_scoped(
        multitenancy.emissions,
        beta_emissions,
        tenant_beta_id
    )
    
    print(f"✅ Created {len(alpha_emissions)} emission records for Alpha")
    print(f"✅ Created {len(beta_emissions)} emission records for Beta")
    
    # Generate JWT tokens for testing
    print("\n🔐 Generating JWT tokens for testing...")
    
    def generate_token(user_id: str, tenant_id: str, role: str):
        payload = {
            "sub": user_id,
            "tenant_id": tenant_id,
            "role": role,
            "exp": datetime.utcnow() + timedelta(days=30),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")
    
    alpha_admin_token = generate_token(alpha_admin_id, tenant_alpha_id, "admin")
    alpha_user_token = generate_token(alpha_user_id, tenant_alpha_id, "user")
    beta_admin_token = generate_token(beta_admin_id, tenant_beta_id, "admin")
    beta_user_token = generate_token(beta_user_id, tenant_beta_id, "user")
    
    print(f"\n📋 TENANT ALPHA (Tech Company):")
    print(f"   Tenant ID: {tenant_alpha_id}")
    print(f"   Admin Token: {alpha_admin_token}")
    print(f"   User Token: {alpha_user_token}")
    print(f"   Companies: {alpha_company_id}, {alpha_subsidiary_id}")
    
    print(f"\n📋 TENANT BETA (Manufacturing):")
    print(f"   Tenant ID: {tenant_beta_id}")
    print(f"   Admin Token: {beta_admin_token}")
    print(f"   User Token: {beta_user_token}")
    print(f"   Companies: {beta_company_id}, {beta_facility_id}")
    
    # Test tenant isolation
    print("\n🔍 Testing tenant isolation...")
    
    # Count data for each tenant
    alpha_stats = await multitenancy.get_tenant_stats(tenant_alpha_id)
    beta_stats = await multitenancy.get_tenant_stats(tenant_beta_id)
    
    print(f"Alpha tenant stats: {alpha_stats}")
    print(f"Beta tenant stats: {beta_stats}")
    
    # Verify isolation - try to fetch Beta's companies using Alpha's tenant_id
    alpha_scoped_beta_companies = await multitenancy.find_many_scoped(
        multitenancy.companies, {"id": beta_company_id}, tenant_alpha_id
    )
    
    if not alpha_scoped_beta_companies:
        print("✅ Tenant isolation working: Alpha cannot see Beta's companies")
    else:
        print("❌ Tenant isolation failed: Alpha can see Beta's companies")
    
    print("\n🎉 Sample tenant data created successfully!")
    print("\nYou can now test the multi-tenant API using the tokens above.")
    print("Example: curl -H 'Authorization: Bearer <token>' http://localhost:8001/api/companies")
    
    # Save test data to file for easy reference
    with open("/app/backend/tenant_test_data.txt", "w") as f:
        f.write("CLIMABILL MULTI-TENANT TEST DATA\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"TENANT ALPHA (Technology)\n")
        f.write(f"Tenant ID: {tenant_alpha_id}\n")
        f.write(f"Admin Token: {alpha_admin_token}\n")
        f.write(f"User Token: {alpha_user_token}\n")
        f.write(f"Companies: {alpha_company_id}, {alpha_subsidiary_id}\n\n")
        f.write(f"TENANT BETA (Manufacturing)\n") 
        f.write(f"Tenant ID: {tenant_beta_id}\n")
        f.write(f"Admin Token: {beta_admin_token}\n")
        f.write(f"User Token: {beta_user_token}\n")
        f.write(f"Companies: {beta_company_id}, {beta_facility_id}\n\n")
        f.write("Test commands:\n")
        f.write(f"curl -H 'Authorization: Bearer {alpha_admin_token}' http://localhost:8001/api/companies\n")
        f.write(f"curl -H 'Authorization: Bearer {beta_admin_token}' http://localhost:8001/api/companies\n")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_sample_tenants())
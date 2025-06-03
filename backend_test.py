
import requests
import sys
import json
from datetime import datetime, timedelta
import uuid
import time

# Test tokens for Alpha and Beta tenants
ALPHA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MDFjOThjMC01ZmFlLTQzYTItOTFlNy0xMzUxODYyYzU1NDYiLCJ0ZW5hbnRfaWQiOiJiNDNjMTg1NC1kNTg3LTRmMTAtYmZiNS03ZWI4YjU3MmI0MTYiLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3NTE1NzY0NzIsImlhdCI6MTc0ODk4NDQ3Mn0.7zW_W3xhVnXoH84CDxNpc0UVIcxhKHdyCkwZmYlIRKs"
BETA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjOTBkMDQyNC02MWYyLTQ0ZjUtYWEwZi1iYTYwNzk1MTFlYjAiLCJ0ZW5hbnRfaWQiOiJhYWQ1MGY3Ny0wMzdkLTRiYTUtOGJmMC1lNTgyMWE3N2JhM2MiLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3NTE1NzY0NzIsImlhdCI6MTc0ODk4NDQ3Mn0.r_S01gVQIL-xqrnpAaUHwT_uqw3m1TxNX4I1Q9W-ZyU"

# Company IDs for Alpha and Beta tenants
ALPHA_COMPANY_IDS = [
    "ff6eb712-e0fe-442e-a0af-9abac69fa731",
    "ea5ba40a-82de-413f-b091-32873cfd0d00"
]

BETA_COMPANY_IDS = [
    "b27132cf-2c61-4945-a0b8-34b615aa7678",
    "82b61da9-af82-43a0-b206-db48f087c7fa"
]

# Sample credentials for login testing
ALPHA_ADMIN_CREDS = {"email": "admin@alpha-tech.com", "password": "admin123"}
ALPHA_USER_CREDS = {"email": "user@alpha-tech.com", "password": "user123"}
BETA_ADMIN_CREDS = {"email": "admin@beta-manufacturing.com", "password": "admin123"}
BETA_USER_CREDS = {"email": "user@beta-manufacturing.com", "password": "user123"}

class ClimaBillAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.company_id = None
        self.source_id = None
        self.initiative_id = None
        self.target_id = None
        
        # Multi-tenant testing properties
        self.alpha_token = ALPHA_TOKEN
        self.beta_token = BETA_TOKEN
        self.alpha_company_ids = ALPHA_COMPANY_IDS
        self.beta_company_ids = BETA_COMPANY_IDS
        
        # Store new company IDs created during testing
        self.alpha_new_company_id = None
        self.beta_new_company_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        else:
            # Ensure Content-Type is set
            if 'Content-Type' not in headers:
                headers['Content-Type'] = 'application/json'
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Status: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"Error details: {json.dumps(error_detail, indent=2)}")
                except:
                    print(f"Response text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    # Multi-tenant Authentication Tests
    def test_login_alpha_admin(self):
        """Test login with Alpha admin credentials"""
        return self.run_test(
            "Login with Alpha Admin Credentials", 
            "POST", 
            "auth/login", 
            200, 
            params=ALPHA_ADMIN_CREDS
        )

    def test_login_beta_admin(self):
        """Test login with Beta admin credentials"""
        return self.run_test(
            "Login with Beta Admin Credentials", 
            "POST", 
            "auth/login", 
            200, 
            params=BETA_ADMIN_CREDS
        )

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        return self.run_test(
            "Login with Invalid Credentials", 
            "POST", 
            "auth/login", 
            401, 
            params={"email": "invalid@example.com", "password": "wrongpassword"}
        )

    def test_get_current_user_alpha(self):
        """Test getting current user info with Alpha token"""
        headers = {"Authorization": f"Bearer {self.alpha_token}"}
        return self.run_test(
            "Get Current User with Alpha Token", 
            "GET", 
            "auth/me", 
            200, 
            headers=headers
        )

    def test_get_current_user_beta(self):
        """Test getting current user info with Beta token"""
        headers = {"Authorization": f"Bearer {self.beta_token}"}
        return self.run_test(
            "Get Current User with Beta Token", 
            "GET", 
            "auth/me", 
            200, 
            headers=headers
        )

    def test_get_current_user_invalid_token(self):
        """Test getting current user info with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        return self.run_test(
            "Get Current User with Invalid Token", 
            "GET", 
            "auth/me", 
            401, 
            headers=headers
        )

    # Multi-tenant Company Endpoints Tests
    def test_list_companies_alpha(self):
        """Test listing companies for Alpha tenant"""
        headers = {"Authorization": f"Bearer {self.alpha_token}"}
        success, response = self.run_test(
            "List Companies for Alpha Tenant", 
            "GET", 
            "companies", 
            200, 
            headers=headers
        )
        
        if success:
            # Verify that only Alpha companies are returned
            company_ids = [company["id"] for company in response]
            for company_id in company_ids:
                if company_id in self.beta_company_ids:
                    print(f"❌ Security issue: Alpha tenant can see Beta company {company_id}")
                    return False, response
            
            print("✅ Verified: Alpha tenant can only see Alpha companies")
        
        return success, response

    def test_list_companies_beta(self):
        """Test listing companies for Beta tenant"""
        headers = {"Authorization": f"Bearer {self.beta_token}"}
        success, response = self.run_test(
            "List Companies for Beta Tenant", 
            "GET", 
            "companies", 
            200, 
            headers=headers
        )
        
        if success:
            # Verify that only Beta companies are returned
            company_ids = [company["id"] for company in response]
            for company_id in company_ids:
                if company_id in self.alpha_company_ids:
                    print(f"❌ Security issue: Beta tenant can see Alpha company {company_id}")
                    return False, response
            
            print("✅ Verified: Beta tenant can only see Beta companies")
        
        return success, response

    def test_get_company_alpha(self):
        """Test getting a specific company for Alpha tenant"""
        company_id = self.alpha_company_ids[0]
        headers = {"Authorization": f"Bearer {self.alpha_token}"}
        return self.run_test(
            "Get Company for Alpha Tenant", 
            "GET", 
            f"companies/{company_id}", 
            200, 
            headers=headers
        )

    def test_get_company_beta(self):
        """Test getting a specific company for Beta tenant"""
        company_id = self.beta_company_ids[0]
        headers = {"Authorization": f"Bearer {self.beta_token}"}
        return self.run_test(
            "Get Company for Beta Tenant", 
            "GET", 
            f"companies/{company_id}", 
            200, 
            headers=headers
        )

    def test_cross_tenant_company_access_alpha_to_beta(self):
        """Test Alpha tenant trying to access Beta company"""
        company_id = self.beta_company_ids[0]
        headers = {"Authorization": f"Bearer {self.alpha_token}"}
        return self.run_test(
            "Cross-Tenant Access: Alpha -> Beta Company", 
            "GET", 
            f"companies/{company_id}", 
            404, 
            headers=headers
        )

    def test_cross_tenant_company_access_beta_to_alpha(self):
        """Test Beta tenant trying to access Alpha company"""
        company_id = self.alpha_company_ids[0]
        headers = {"Authorization": f"Bearer {self.beta_token}"}
        return self.run_test(
            "Cross-Tenant Access: Beta -> Alpha Company", 
            "GET", 
            f"companies/{company_id}", 
            404, 
            headers=headers
        )

    def test_create_company_alpha(self):
        """Test creating a new company for Alpha tenant"""
        company_data = {
            "name": f"Alpha Test Company {uuid.uuid4()}",
            "industry": "saas",
            "employee_count": 150,
            "annual_revenue": 5000000,
            "headquarters_location": "San Francisco, CA",
            "compliance_standards": ["ghg_protocol"]
        }
        headers = {"Authorization": f"Bearer {self.alpha_token}"}
        success, response = self.run_test(
            "Create Company for Alpha Tenant", 
            "POST", 
            "companies", 
            200, 
            data=company_data,
            headers=headers
        )
        
        if success:
            self.alpha_new_company_id = response["id"]
            print(f"Created Alpha company with ID: {self.alpha_new_company_id}")
        
        return success, response

    def test_create_company_beta(self):
        """Test creating a new company for Beta tenant"""
        company_data = {
            "name": f"Beta Test Company {uuid.uuid4()}",
            "industry": "manufacturing",
            "employee_count": 500,
            "annual_revenue": 25000000,
            "headquarters_location": "Chicago, IL",
            "compliance_standards": ["eu_csrd"]
        }
        headers = {"Authorization": f"Bearer {self.beta_token}"}
        success, response = self.run_test(
            "Create Company for Beta Tenant", 
            "POST", 
            "companies", 
            200, 
            data=company_data,
            headers=headers
        )
        
        if success:
            self.beta_new_company_id = response["id"]
            print(f"Created Beta company with ID: {self.beta_new_company_id}")
        
        return success, response

    # Multi-tenant Emission Endpoints Tests
    def test_create_emission_record_alpha(self):
        """Test creating an emission record for Alpha company"""
        if not self.alpha_new_company_id:
            print("❌ No Alpha company ID available for testing")
            return False, {}
            
        emission_data = {
            "source_id": f"mock-source-id-alpha-{uuid.uuid4()}",
            "period_start": (datetime.utcnow() - timedelta(days=30)).isoformat(),
            "period_end": datetime.utcnow().isoformat(),
            "co2_equivalent_kg": 1500.75,
            "activity_data": {
                "electricity_kwh": 5000,
                "renewable_percentage": 20
            },
            "emission_factor": 0.5,
            "data_quality": "measured"
        }
        headers = {"Authorization": f"Bearer {self.alpha_token}"}
        return self.run_test(
            "Create Emission Record for Alpha Company", 
            "POST", 
            f"companies/{self.alpha_new_company_id}/emissions", 
            200, 
            data=emission_data,
            headers=headers
        )

    def test_create_emission_record_beta(self):
        """Test creating an emission record for Beta company"""
        if not self.beta_new_company_id:
            print("❌ No Beta company ID available for testing")
            return False, {}
            
        emission_data = {
            "source_id": f"mock-source-id-beta-{uuid.uuid4()}",
            "period_start": (datetime.utcnow() - timedelta(days=30)).isoformat(),
            "period_end": datetime.utcnow().isoformat(),
            "co2_equivalent_kg": 2500.50,
            "activity_data": {
                "electricity_kwh": 8000,
                "renewable_percentage": 10
            },
            "emission_factor": 0.6,
            "data_quality": "measured"
        }
        headers = {"Authorization": f"Bearer {self.beta_token}"}
        return self.run_test(
            "Create Emission Record for Beta Company", 
            "POST", 
            f"companies/{self.beta_new_company_id}/emissions", 
            200, 
            data=emission_data,
            headers=headers
        )

    def test_get_emissions_summary_alpha(self):
        """Test getting emissions summary for Alpha company"""
        if not self.alpha_new_company_id:
            print("❌ No Alpha company ID available for testing")
            return False, {}
            
        headers = {"Authorization": f"Bearer {self.alpha_token}"}
        return self.run_test(
            "Get Emissions Summary for Alpha Company", 
            "GET", 
            f"companies/{self.alpha_new_company_id}/emissions/summary", 
            200, 
            headers=headers
        )

    def test_get_emissions_summary_beta(self):
        """Test getting emissions summary for Beta company"""
        if not self.beta_new_company_id:
            print("❌ No Beta company ID available for testing")
            return False, {}
            
        headers = {"Authorization": f"Bearer {self.beta_token}"}
        return self.run_test(
            "Get Emissions Summary for Beta Company", 
            "GET", 
            f"companies/{self.beta_new_company_id}/emissions/summary", 
            200, 
            headers=headers
        )

    def test_get_emissions_trend_alpha(self):
        """Test getting emissions trend for Alpha company"""
        if not self.alpha_new_company_id:
            print("❌ No Alpha company ID available for testing")
            return False, {}
            
        headers = {"Authorization": f"Bearer {self.alpha_token}"}
        return self.run_test(
            "Get Emissions Trend for Alpha Company", 
            "GET", 
            f"companies/{self.alpha_new_company_id}/emissions/trend", 
            200, 
            headers=headers
        )

    def test_get_emissions_trend_beta(self):
        """Test getting emissions trend for Beta company"""
        if not self.beta_new_company_id:
            print("❌ No Beta company ID available for testing")
            return False, {}
            
        headers = {"Authorization": f"Bearer {self.beta_token}"}
        return self.run_test(
            "Get Emissions Trend for Beta Company", 
            "GET", 
            f"companies/{self.beta_new_company_id}/emissions/trend", 
            200, 
            headers=headers
        )

    def test_get_top_emission_sources_alpha(self):
        """Test getting top emission sources for Alpha company"""
        if not self.alpha_new_company_id:
            print("❌ No Alpha company ID available for testing")
            return False, {}
            
        headers = {"Authorization": f"Bearer {self.alpha_token}"}
        return self.run_test(
            "Get Top Emission Sources for Alpha Company", 
            "GET", 
            f"companies/{self.alpha_new_company_id}/emissions/sources/top", 
            200, 
            headers=headers
        )

    def test_get_top_emission_sources_beta(self):
        """Test getting top emission sources for Beta company"""
        if not self.beta_new_company_id:
            print("❌ No Beta company ID available for testing")
            return False, {}
            
        headers = {"Authorization": f"Bearer {self.beta_token}"}
        return self.run_test(
            "Get Top Emission Sources for Beta Company", 
            "GET", 
            f"companies/{self.beta_new_company_id}/emissions/sources/top", 
            200, 
            headers=headers
        )

    def test_cross_tenant_emissions_access_alpha_to_beta(self):
        """Test Alpha tenant trying to access Beta company emissions"""
        if not self.beta_new_company_id:
            print("❌ No Beta company ID available for testing")
            return False, {}
            
        headers = {"Authorization": f"Bearer {self.alpha_token}"}
        return self.run_test(
            "Cross-Tenant Access: Alpha -> Beta Emissions", 
            "GET", 
            f"companies/{self.beta_new_company_id}/emissions/summary", 
            404, 
            headers=headers
        )

    def test_cross_tenant_emissions_access_beta_to_alpha(self):
        """Test Beta tenant trying to access Alpha company emissions"""
        if not self.alpha_new_company_id:
            print("❌ No Alpha company ID available for testing")
            return False, {}
            
        headers = {"Authorization": f"Bearer {self.beta_token}"}
        return self.run_test(
            "Cross-Tenant Access: Beta -> Alpha Emissions", 
            "GET", 
            f"companies/{self.alpha_new_company_id}/emissions/summary", 
            404, 
            headers=headers
        )

    # Error Handling Tests
    def test_missing_auth_header(self):
        """Test API response with missing Authorization header"""
        return self.run_test(
            "Missing Authorization Header", 
            "GET", 
            "companies", 
            401
        )

    def test_malformed_request(self):
        """Test API response with malformed request"""
        headers = {"Authorization": f"Bearer {self.alpha_token}", "Content-Type": "application/json"}
        # We'll use a custom request here to send invalid JSON
        url = f"{self.base_url}/api/companies"
        
        self.tests_run += 1
        print(f"\n🔍 Testing Malformed Request...")
        
        try:
            response = requests.post(url, data="This is not valid JSON", headers=headers)
            
            # Either 400 (Bad Request) or 422 (Unprocessable Entity) is acceptable
            success = response.status_code in [400, 422]
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                return True, {}
            else:
                print(f"❌ Failed - Status: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"Error details: {json.dumps(error_detail, indent=2)}")
                except:
                    print(f"Response text: {response.text}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_invalid_company_id(self):
        """Test API response with invalid company ID"""
        headers = {"Authorization": f"Bearer {self.alpha_token}"}
        return self.run_test(
            "Invalid Company ID", 
            "GET", 
            "companies/invalid-uuid-format", 
            404, 
            headers=headers
        )

    def test_ai_query(self):
        """Test AI query endpoint"""
        if not self.company_id:
            print("❌ No company ID available for testing")
            return False, {}
            
        query_data = {
            "company_id": self.company_id,
            "query_text": "What are our total emissions for the last quarter?",
            "user_id": "test_user"
        }
        
        return self.run_test(
            "AI Query", 
            "POST", 
            f"companies/{self.company_id}/ai/query", 
            200, 
            data=query_data
        )

    def test_emissions_forecast(self):
        """Test emissions forecast endpoint"""
        if not self.company_id:
            print("❌ No company ID available for testing")
            return False, {}
            
        return self.run_test(
            "Emissions Forecast", 
            "POST", 
            f"companies/{self.company_id}/ai/forecast", 
            200,
            data={"horizon_months": 6}
        )

    def test_reduction_recommendations(self):
        """Test reduction recommendations endpoint"""
        if not self.company_id:
            print("❌ No company ID available for testing")
            return False, {}
            
        return self.run_test(
            "Reduction Recommendations", 
            "POST", 
            f"companies/{self.company_id}/ai/recommendations", 
            200
        )

    def test_calculate_electricity_emissions(self):
        """Test electricity emissions calculation"""
        data = {
            "kwh_consumed": 1000, 
            "region": "us_average", 
            "renewable_percentage": 20
        }
        return self.run_test(
            "Calculate Electricity Emissions", 
            "POST", 
            "calculate/electricity", 
            200,
            data=data
        )

    def test_calculate_fuel_emissions(self):
        """Test fuel emissions calculation"""
        data = {
            "fuel_type": "gasoline", 
            "quantity": 100, 
            "unit": "liters"
        }
        return self.run_test(
            "Calculate Fuel Emissions", 
            "POST", 
            "calculate/fuel", 
            200,
            data=data
        )

    def test_calculate_travel_emissions(self):
        """Test travel emissions calculation"""
        data = {
            "trips": [
                {
                    "mode": "flight",
                    "distance_km": 1000,
                    "passengers": 1,
                    "class": "economy"
                },
                {
                    "mode": "car",
                    "distance_km": 500,
                    "vehicle_type": "medium"
                }
            ]
        }
        
        return self.run_test(
            "Calculate Travel Emissions", 
            "POST", 
            "calculate/travel", 
            200,
            data=data
        )

    def test_get_dashboard_data(self):
        """Test getting dashboard data"""
        if not self.company_id:
            print("❌ No company ID available for testing")
            return False, {}
            
        return self.run_test(
            "Get Dashboard Data", 
            "GET", 
            f"companies/{self.company_id}/dashboard", 
            200,
            params={"period_months": 12}
        )

    def test_create_carbon_target(self):
        """Test creating a carbon target"""
        if not self.company_id:
            print("❌ No company ID available for testing")
            return False, {}
            
        target_data = {
            "target_name": "2030 Net Zero",
            "baseline_year": 2023,
            "target_year": 2030,
            "baseline_emissions": 5000,
            "target_reduction_percentage": 50,
            "scope_coverage": ["scope_1", "scope_2"]
        }
        
        success, response = self.run_test(
            "Create Carbon Target", 
            "POST", 
            f"companies/{self.company_id}/targets", 
            200, 
            data=target_data
        )
        
        if success:
            self.target_id = response.get("id")
            print(f"Created carbon target with ID: {self.target_id}")
        
        return success, response

    def test_get_company_targets(self):
        """Test getting company targets"""
        if not self.company_id:
            print("❌ No company ID available for testing")
            return False, {}
            
        return self.run_test(
            "Get Company Targets", 
            "GET", 
            f"companies/{self.company_id}/targets", 
            200
        )

    def test_create_reduction_initiative(self):
        """Test creating a reduction initiative"""
        if not self.company_id:
            print("❌ No company ID available for testing")
            return False, {}
            
        initiative_data = {
            "initiative_name": "Solar Panel Installation",
            "description": "Install solar panels on office roof",
            "implementation_cost": 50000,
            "annual_savings": 12000,
            "annual_co2_reduction": 15000,
            "roi_percentage": 24,
            "implementation_date": datetime.utcnow().isoformat(),
            "status": "planned"
        }
        
        success, response = self.run_test(
            "Create Reduction Initiative", 
            "POST", 
            f"companies/{self.company_id}/initiatives", 
            200, 
            data=initiative_data
        )
        
        if success:
            self.initiative_id = response.get("id")
            print(f"Created reduction initiative with ID: {self.initiative_id}")
        
        return success, response

    def test_get_company_initiatives(self):
        """Test getting company initiatives"""
        if not self.company_id:
            print("❌ No company ID available for testing")
            return False, {}
            
        return self.run_test(
            "Get Company Initiatives", 
            "GET", 
            f"companies/{self.company_id}/initiatives", 
            200
        )

    def test_get_target_progress(self):
        """Test getting target progress"""
        if not self.company_id:
            print("❌ No company ID available for testing")
            return False, {}
            
        return self.run_test(
            "Get Target Progress", 
            "GET", 
            f"companies/{self.company_id}/targets/progress", 
            200
        )

    def test_get_financial_impact(self):
        """Test getting financial impact"""
        if not self.company_id:
            print("❌ No company ID available for testing")
            return False, {}
            
        return self.run_test(
            "Get Financial Impact", 
            "GET", 
            f"companies/{self.company_id}/financial-impact", 
            200
        )

    def test_marketplace_projects(self):
        """Test getting marketplace projects"""
        return self.run_test(
            "Get Marketplace Projects", 
            "GET", 
            "marketplace/projects", 
            200
        )
        
    def test_marketplace_purchase(self):
        """Test purchasing carbon offsets"""
        if not self.company_id:
            print("❌ No company ID available for testing")
            return False, {}
            
        purchase_data = {
            "listing_id": "project-123",
            "credits_amount": 10,
            "company_id": self.company_id
        }
        
        return self.run_test(
            "Purchase Carbon Offsets", 
            "POST", 
            "marketplace/purchase", 
            200, 
            data=purchase_data
        )
        
    def test_get_company_certificates(self):
        """Test getting company certificates"""
        if not self.company_id:
            print("❌ No company ID available for testing")
            return False, {}
            
        return self.run_test(
            "Get Company Certificates", 
            "GET", 
            f"companies/{self.company_id}/certificates", 
            200
        )
        
    def test_add_supplier(self):
        """Test adding a supplier"""
        if not self.company_id:
            print("❌ No company ID available for testing")
            return False, {}
            
        supplier_data = {
            "supplier_name": f"Test Supplier {uuid.uuid4()}",
            "industry": "manufacturing",
            "location": "Detroit, MI",
            "contact_email": "supplier@example.com",
            "annual_revenue": 5000000,
            "employee_count": 100,
            "carbon_score": 75.5,
            "verification_status": "verified",
            "partnership_level": "preferred"
        }
        
        return self.run_test(
            "Add Supplier", 
            "POST", 
            f"companies/{self.company_id}/suppliers", 
            200, 
            data=supplier_data
        )
        
    def test_get_company_suppliers(self):
        """Test getting company suppliers"""
        if not self.company_id:
            print("❌ No company ID available for testing")
            return False, {}
            
        return self.run_test(
            "Get Company Suppliers", 
            "GET", 
            f"companies/{self.company_id}/suppliers", 
            200
        )
        
    def test_get_supply_chain_dashboard(self):
        """Test getting supply chain dashboard"""
        if not self.company_id:
            print("❌ No company ID available for testing")
            return False, {}
            
        return self.run_test(
            "Get Supply Chain Dashboard", 
            "GET", 
            f"companies/{self.company_id}/supply-chain/dashboard", 
            200
        )
        
    def test_get_compliance_dashboard(self):
        """Test getting compliance dashboard"""
        if not self.company_id:
            print("❌ No company ID available for testing")
            return False, {}
            
        return self.run_test(
            "Get Compliance Dashboard", 
            "GET", 
            f"companies/{self.company_id}/compliance/dashboard", 
            200
        )
        
    def test_get_industry_benchmark(self):
        """Test getting industry benchmark"""
        return self.run_test(
            "Get Industry Benchmark", 
            "GET", 
            "benchmarks/saas", 
            200,
            params={"employee_count": 50}
        )

    def test_get_compliance_standards(self):
        """Test getting compliance standards"""
        return self.run_test(
            "Get Compliance Standards", 
            "GET", 
            "compliance/standards", 
            200
        )
        
    def run_multi_tenant_tests(self):
        """Run all multi-tenant API tests"""
        print("🚀 Starting ClimaBill Multi-Tenant API Tests")
        
        # Authentication Tests
        self.test_login_alpha_admin()
        self.test_login_beta_admin()
        self.test_login_invalid_credentials()
        self.test_get_current_user_alpha()
        self.test_get_current_user_beta()
        self.test_get_current_user_invalid_token()
        
        # Company Endpoints Tests
        self.test_list_companies_alpha()
        self.test_list_companies_beta()
        self.test_get_company_alpha()
        self.test_get_company_beta()
        self.test_cross_tenant_company_access_alpha_to_beta()
        self.test_cross_tenant_company_access_beta_to_alpha()
        self.test_create_company_alpha()
        self.test_create_company_beta()
        
        # Emission Endpoints Tests
        self.test_create_emission_record_alpha()
        self.test_create_emission_record_beta()
        self.test_get_emissions_summary_alpha()
        self.test_get_emissions_summary_beta()
        self.test_get_emissions_trend_alpha()
        self.test_get_emissions_trend_beta()
        self.test_get_top_emission_sources_alpha()
        self.test_get_top_emission_sources_beta()
        self.test_cross_tenant_emissions_access_alpha_to_beta()
        self.test_cross_tenant_emissions_access_beta_to_alpha()
        
        # Error Handling Tests
        self.test_missing_auth_header()
        self.test_malformed_request()
        self.test_invalid_company_id()
        
        # Print results
        print(f"\n📊 Multi-Tenant Tests passed: {self.tests_passed}/{self.tests_run} ({(self.tests_passed/self.tests_run)*100:.1f}%)")
        
        return self.tests_passed == self.tests_run

def main():
    # Get the backend URL from the frontend .env file
    backend_url = "https://2af63da8-69f3-449e-9a45-00a182941828.preview.emergentagent.com"
    
    # Create tester instance
    tester = ClimaBillAPITester(backend_url)
    
    # Run all tests
    success = tester.run_all_tests()
    
    # Return exit code based on test results
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

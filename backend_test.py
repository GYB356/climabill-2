
import requests
import sys
import json
from datetime import datetime, timedelta
import uuid
import time

class ClimaBillAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.company_id = None
        self.source_id = None
        self.initiative_id = None
        self.target_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
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

    def test_health_check(self):
        """Test API health check endpoint"""
        return self.run_test("Health Check", "GET", "health", 200)

    def test_create_company(self):
        """Test company creation"""
        company_data = {
            "name": f"Test Company {uuid.uuid4()}",
            "industry": "saas",
            "employee_count": 50,
            "annual_revenue": 1000000,
            "headquarters_location": "San Francisco, CA",
            "compliance_standards": ["ghg_protocol"]
        }
        success, response = self.run_test(
            "Create Company", 
            "POST", 
            "companies", 
            200, 
            data=company_data
        )
        if success:
            self.company_id = response.get("id")
            print(f"Created company with ID: {self.company_id}")
        return success, response

    def test_get_company(self):
        """Test getting company details"""
        if not self.company_id:
            print("❌ No company ID available for testing")
            return False, {}
        return self.run_test(
            "Get Company", 
            "GET", 
            f"companies/{self.company_id}", 
            200
        )

    def test_list_companies(self):
        """Test listing all companies"""
        return self.run_test("List Companies", "GET", "companies", 200)

    def test_add_emission_source(self):
        """Test adding an emission source"""
        if not self.company_id:
            print("❌ No company ID available for testing")
            return False, {}
            
        # This is a custom test since there's no direct API for creating sources
        # We'll create a source through an emission record
        emission_data = {
            "source_id": str(uuid.uuid4()),  # Generate a new source ID
            "period_start": (datetime.utcnow() - timedelta(days=30)).isoformat(),
            "period_end": datetime.utcnow().isoformat(),
            "co2_equivalent_kg": 1000.5,
            "activity_data": {
                "kwh_consumed": 5000,
                "source_name": "Office Electricity",
                "source_type": "electricity",
                "scope": "scope_2"
            },
            "emission_factor": 0.2,
            "data_quality": "measured"
        }
        
        self.source_id = emission_data["source_id"]
        
        success, response = self.run_test(
            "Add Emission Record with New Source", 
            "POST", 
            f"companies/{self.company_id}/emissions", 
            200, 
            data=emission_data
        )
        
        if success:
            print(f"Created emission record with source ID: {self.source_id}")
        
        return success, response

    def test_get_emissions_summary(self):
        """Test getting emissions summary"""
        if not self.company_id:
            print("❌ No company ID available for testing")
            return False, {}
            
        return self.run_test(
            "Get Emissions Summary", 
            "GET", 
            f"companies/{self.company_id}/emissions/summary", 
            200
        )

    def test_get_emissions_trend(self):
        """Test getting emissions trend"""
        if not self.company_id:
            print("❌ No company ID available for testing")
            return False, {}
            
        return self.run_test(
            "Get Emissions Trend", 
            "GET", 
            f"companies/{self.company_id}/emissions/trend", 
            200,
            params={"months": 6}
        )

    def test_get_top_emission_sources(self):
        """Test getting top emission sources"""
        if not self.company_id:
            print("❌ No company ID available for testing")
            return False, {}
            
        return self.run_test(
            "Get Top Emission Sources", 
            "GET", 
            f"companies/{self.company_id}/emissions/sources/top", 
            200,
            params={"limit": 3}
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
        travel_data = [
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
        
        return self.run_test(
            "Calculate Travel Emissions", 
            "POST", 
            "calculate/travel", 
            200,
            data=travel_data
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

    def test_get_industry_benchmark(self):
        """Test getting industry benchmark"""
        return self.run_test(
            "Get Industry Benchmark", 
            "GET", 
            "benchmarks/saas", 
            200,
            params={"employee_count": 50}
        )

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting ClimaBill API Tests")
        
        # Basic health check
        self.test_health_check()
        
        # Company management
        self.test_create_company()
        self.test_get_company()
        self.test_list_companies()
        
        # Emissions data
        self.test_add_emission_source()
        self.test_get_emissions_summary()
        self.test_get_emissions_trend()
        self.test_get_top_emission_sources()
        
        # AI features
        self.test_ai_query()
        self.test_emissions_forecast()
        self.test_reduction_recommendations()
        
        # Carbon calculations
        self.test_calculate_electricity_emissions()
        self.test_calculate_fuel_emissions()
        self.test_calculate_travel_emissions()
        
        # Dashboard and analytics
        self.test_get_dashboard_data()
        
        # Carbon targets
        self.test_create_carbon_target()
        self.test_get_company_targets()
        self.test_get_target_progress()
        
        # Reduction initiatives
        self.test_create_reduction_initiative()
        self.test_get_company_initiatives()
        self.test_get_financial_impact()
        
        # Benchmarking
        self.test_get_industry_benchmark()
        
        # Print results
        print(f"\n📊 Tests passed: {self.tests_passed}/{self.tests_run} ({(self.tests_passed/self.tests_run)*100:.1f}%)")
        
        return self.tests_passed == self.tests_run

def main():
    # Get the backend URL from the frontend .env file
    backend_url = "https://0ce4d86b-7397-4bc2-ac0a-a1db46ac1241.preview.emergentagent.com"
    
    # Create tester instance
    tester = ClimaBillAPITester(backend_url)
    
    # Run all tests
    success = tester.run_all_tests()
    
    # Return exit code based on test results
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

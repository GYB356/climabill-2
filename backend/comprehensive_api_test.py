#!/usr/bin/env python3
"""
Comprehensive API test suite for ClimaBill MVP validation
"""
import requests
import json
from datetime import datetime, timedelta
import time

class ClimaBillAPITester:
    def __init__(self):
        self.base_url = "http://localhost:8001/api"
        self.company_id = None
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
        
    def run_test(self, test_name, test_func):
        """Run a test and record results"""
        self.total_tests += 1
        try:
            result = test_func()
            if result:
                self.test_results[test_name] = "✅ PASS"
                self.passed_tests += 1
                print(f"✅ {test_name}: PASS")
            else:
                self.test_results[test_name] = "❌ FAIL"
                print(f"❌ {test_name}: FAIL")
        except Exception as e:
            self.test_results[test_name] = f"❌ ERROR: {str(e)}"
            print(f"❌ {test_name}: ERROR - {str(e)}")
    
    def test_health_endpoints(self):
        """Test basic health endpoints"""
        response = requests.get(f"{self.base_url}/")
        return response.status_code == 200 and "ClimaBill API is running" in response.text
    
    def test_company_creation(self):
        """Test company creation"""
        company_data = {
            "name": "Test Company MVP",
            "industry": "saas",
            "employee_count": 100,
            "annual_revenue": 5000000,
            "headquarters_location": "San Francisco, CA",
            "compliance_standards": ["eu_csrd", "sec_climate"]
        }
        response = requests.post(f"{self.base_url}/companies", json=company_data)
        if response.status_code == 200:
            self.company_id = response.json()["id"]
            return True
        return False
    
    def test_emissions_calculation(self):
        """Test emissions calculations"""
        # Test electricity calculation
        calc_data = {
            "kwh_consumed": 1000,
            "region": "us_average",
            "renewable_percentage": 20
        }
        response = requests.post(f"{self.base_url}/calculate/electricity", json=calc_data)
        return response.status_code == 200 and "co2_equivalent_kg" in response.json()
    
    def test_emissions_tracking(self):
        """Test emissions record creation"""
        if not self.company_id:
            return False
            
        emission_data = {
            "source_id": "test-source-id",
            "period_start": datetime.utcnow().isoformat(),
            "period_end": datetime.utcnow().isoformat(),
            "co2_equivalent_kg": 1500.0,
            "activity_data": {"test": "data"},
            "emission_factor": 0.385,
            "data_quality": "estimated"
        }
        response = requests.post(f"{self.base_url}/companies/{self.company_id}/emissions", json=emission_data)
        return response.status_code == 200
    
    def test_dashboard_data(self):
        """Test dashboard data retrieval"""
        if not self.company_id:
            return False
            
        response = requests.get(f"{self.base_url}/companies/{self.company_id}/dashboard")
        return response.status_code == 200 and "total_emissions" in response.json()
    
    def test_ai_query(self):
        """Test AI query functionality"""
        if not self.company_id:
            return False
            
        query_data = {
            "company_id": self.company_id,
            "query_text": "What is our carbon footprint?"
        }
        response = requests.post(f"{self.base_url}/companies/{self.company_id}/ai/query", json=query_data)
        return response.status_code == 200 and "response" in response.json()
    
    def test_ai_forecast(self):
        """Test AI forecasting"""
        if not self.company_id:
            return False
            
        response = requests.post(f"{self.base_url}/companies/{self.company_id}/ai/forecast", 
                               json={"horizon_months": 6})
        return response.status_code == 200 and "predicted_emissions" in response.json()
    
    def test_marketplace_projects(self):
        """Test marketplace project listings"""
        response = requests.get(f"{self.base_url}/marketplace/projects")
        return response.status_code == 200 and "projects" in response.json()
    
    def test_marketplace_purchase(self):
        """Test marketplace purchase"""
        if not self.company_id:
            return False
            
        purchase_data = {
            "listing_id": "LIST-001",
            "credits_amount": 10,
            "company_id": self.company_id
        }
        response = requests.post(f"{self.base_url}/marketplace/purchase", json=purchase_data)
        return response.status_code == 200 and "purchase_id" in response.json()
    
    def test_supply_chain_suppliers(self):
        """Test supplier management"""
        if not self.company_id:
            return False
            
        supplier_data = {
            "supplier_name": "Test Supplier",
            "industry": "Technology",
            "location": "San Jose, CA",
            "contact_email": "test@supplier.com",
            "annual_revenue": 1000000,
            "employee_count": 50,
            "carbon_score": 75.0,
            "verification_status": "verified",
            "partnership_level": "preferred"
        }
        response = requests.post(f"{self.base_url}/companies/{self.company_id}/suppliers", json=supplier_data)
        return response.status_code == 200
    
    def test_supply_chain_dashboard(self):
        """Test supply chain dashboard"""
        if not self.company_id:
            return False
            
        response = requests.get(f"{self.base_url}/companies/{self.company_id}/supply-chain/dashboard")
        return response.status_code == 200 and "total_suppliers" in response.json()
    
    def test_compliance_dashboard(self):
        """Test compliance dashboard"""
        if not self.company_id:
            return False
            
        response = requests.get(f"{self.base_url}/companies/{self.company_id}/compliance/dashboard")
        return response.status_code == 200 and "compliance_standards" in response.json()
    
    def test_compliance_report(self):
        """Test compliance report generation"""
        if not self.company_id:
            return False
            
        response = requests.get(f"{self.base_url}/companies/{self.company_id}/compliance/report/eu_csrd")
        return response.status_code == 200 and "report_type" in response.json()
    
    def test_financial_impact(self):
        """Test financial impact calculations"""
        if not self.company_id:
            return False
            
        response = requests.get(f"{self.base_url}/companies/{self.company_id}/financial-impact")
        return response.status_code == 200 and "total_carbon_investment" in response.json()
    
    def test_initiatives_management(self):
        """Test carbon reduction initiatives"""
        if not self.company_id:
            return False
            
        initiative_data = {
            "initiative_name": "Test Initiative",
            "description": "Test carbon reduction initiative",
            "implementation_cost": 10000,
            "annual_savings": 5000,
            "annual_co2_reduction": 2000,
            "roi_percentage": 50.0,
            "implementation_date": datetime.utcnow().isoformat(),
            "status": "planned"
        }
        response = requests.post(f"{self.base_url}/companies/{self.company_id}/initiatives", json=initiative_data)
        return response.status_code == 200
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🧪 Running ClimaBill MVP Comprehensive API Test Suite\n")
        
        # Core functionality tests
        self.run_test("Health Check", self.test_health_endpoints)
        self.run_test("Company Creation", self.test_company_creation)
        self.run_test("Emissions Calculation", self.test_emissions_calculation)
        self.run_test("Emissions Tracking", self.test_emissions_tracking)
        self.run_test("Dashboard Data", self.test_dashboard_data)
        
        # AI features tests
        self.run_test("AI Query Processing", self.test_ai_query)
        self.run_test("AI Forecast Generation", self.test_ai_forecast)
        
        # Marketplace tests
        self.run_test("Marketplace Projects", self.test_marketplace_projects)
        self.run_test("Marketplace Purchase", self.test_marketplace_purchase)
        
        # Supply chain tests
        self.run_test("Supplier Management", self.test_supply_chain_suppliers)
        self.run_test("Supply Chain Dashboard", self.test_supply_chain_dashboard)
        
        # Compliance tests
        self.run_test("Compliance Dashboard", self.test_compliance_dashboard)
        self.run_test("Compliance Report", self.test_compliance_report)
        
        # Financial tests
        self.run_test("Financial Impact", self.test_financial_impact)
        self.run_test("Initiatives Management", self.test_initiatives_management)
        
        # Print final results
        print(f"\n📊 Test Results Summary:")
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed Tests: {self.passed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        
        if self.passed_tests == self.total_tests:
            print("\n🎉 ALL TESTS PASSED - MVP IS READY!")
        else:
            print(f"\n⚠️  {self.total_tests - self.passed_tests} tests failed - needs attention")
        
        return self.passed_tests / self.total_tests

if __name__ == "__main__":
    tester = ClimaBillAPITester()
    success_rate = tester.run_all_tests()
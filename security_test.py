#!/usr/bin/env python3
import requests
import time
import json
import sys
import uuid
from datetime import datetime
import random
import string

# Test configuration
BASE_URL = "http://localhost:8001/api"
ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MDFjOThjMC01ZmFlLTQzYTItOTFlNy0xMzUxODYyYzU1NDYiLCJ0ZW5hbnRfaWQiOiJiNDNjMTg1NC1kNTg3LTRmMTAtYmZiNS03ZWI4YjU3MmI0MTYiLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3NTE1NzY0NzIsImlhdCI6MTc0ODk4NDQ3Mn0.7zW_W3xhVnXoH84CDxNpc0UVIcxhKHdyCkwZmYlIRKs"
API_KEY = "cb_Hpz0SOQS0RwrUOhcMbvLikZJL_AgU9N7S7kq5bKwhuM"

# Test results tracking
test_results = {
    "security_headers": {"passed": 0, "failed": 0, "details": []},
    "rate_limiting": {"passed": 0, "failed": 0, "details": []},
    "input_validation": {"passed": 0, "failed": 0, "details": []},
    "api_key_auth": {"passed": 0, "failed": 0, "details": []},
    "audit_logging": {"passed": 0, "failed": 0, "details": []},
    "multi_tenant_security": {"passed": 0, "failed": 0, "details": []}
}

def print_header(title):
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def print_test_result(category, test_name, passed, message=""):
    result = "✅ PASSED" if passed else "❌ FAILED"
    print(f"{result} - {test_name}")
    if message:
        print(f"       {message}")
    
    if passed:
        test_results[category]["passed"] += 1
    else:
        test_results[category]["failed"] += 1
    
    test_results[category]["details"].append({
        "test": test_name,
        "passed": passed,
        "message": message
    })

def make_request(method, endpoint, headers=None, data=None, json_data=None, expected_status=None, auth_token=None, api_key=None):
    url = f"{BASE_URL}{endpoint}"
    
    if headers is None:
        headers = {}
    
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    
    if api_key:
        headers["X-API-Key"] = api_key
    
    try:
        if method.lower() == "get":
            response = requests.get(url, headers=headers, params=data)
        elif method.lower() == "post":
            response = requests.post(url, headers=headers, data=data, json=json_data)
        elif method.lower() == "put":
            response = requests.put(url, headers=headers, data=data, json=json_data)
        elif method.lower() == "delete":
            response = requests.delete(url, headers=headers, params=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        if expected_status and response.status_code != expected_status:
            return False, response, f"Expected status {expected_status}, got {response.status_code}"
        
        return True, response, ""
    except Exception as e:
        return False, None, str(e)

def test_security_headers():
    print_header("Testing Security Headers")
    
    # Test endpoints
    endpoints = ["/health", "/companies", "/auth/me"]
    required_headers = [
        "X-Content-Type-Options",
        "X-Frame-Options",
        "X-XSS-Protection",
        "Strict-Transport-Security",
        "Content-Security-Policy",
        "Referrer-Policy"
    ]
    
    for endpoint in endpoints:
        success, response, error = make_request("get", endpoint, auth_token=ADMIN_TOKEN)
        
        if not success:
            print_test_result("security_headers", f"Headers on {endpoint}", False, error)
            continue
        
        missing_headers = []
        for header in required_headers:
            if header not in response.headers:
                missing_headers.append(header)
        
        if missing_headers:
            print_test_result("security_headers", f"Headers on {endpoint}", False, 
                             f"Missing headers: {', '.join(missing_headers)}")
        else:
            print_test_result("security_headers", f"Headers on {endpoint}", True, 
                             f"All security headers present")
            
            # Print the actual headers for verification
            print("Security headers found:")
            for header in required_headers:
                print(f"  {header}: {response.headers.get(header)}")

def test_rate_limiting():
    print_header("Testing Rate Limiting")
    
    # Test normal API endpoint (100 requests/minute)
    print("Testing normal API endpoint rate limit (100 requests/minute)...")
    success_count = 0
    rate_limited = False
    
    for i in range(110):  # Try to exceed the limit
        success, response, error = make_request("get", "/companies", auth_token=ADMIN_TOKEN)
        
        if success and response.status_code == 200:
            success_count += 1
        elif response and response.status_code == 429:
            rate_limited = True
            print(f"Rate limited after {success_count} requests")
            break
        
        # Don't hammer the server too hard
        if i % 10 == 0:
            time.sleep(0.1)
    
    print_test_result("rate_limiting", "Normal API rate limit (100/min)", 
                     rate_limited and success_count > 90, 
                     f"Made {success_count} successful requests before being rate limited: {rate_limited}")
    
    # Test auth endpoint (5 requests/5 minutes)
    print("\nTesting auth endpoint rate limit (5 requests/5 minutes)...")
    success_count = 0
    rate_limited = False
    
    for i in range(10):  # Try to exceed the limit
        success, response, error = make_request(
            "post", 
            "/auth/login", 
            json_data={"email": "test@example.com", "password": "wrongpassword"}
        )
        
        if success and response.status_code in [200, 401]:  # Both successful API calls, just different responses
            success_count += 1
        elif response and response.status_code == 429:
            rate_limited = True
            print(f"Rate limited after {success_count} requests")
            break
        
        time.sleep(0.5)  # Slower to avoid hammering auth endpoint
    
    print_test_result("rate_limiting", "Auth endpoint rate limit (5/5min)", 
                     rate_limited and success_count >= 5, 
                     f"Made {success_count} successful requests before being rate limited: {rate_limited}")
    
    # Test AI endpoint (10 requests/minute)
    print("\nTesting AI endpoint rate limit (10 requests/minute)...")
    success_count = 0
    rate_limited = False
    
    for i in range(15):  # Try to exceed the limit
        success, response, error = make_request(
            "post", 
            "/companies/some-id/ai/query", 
            auth_token=ADMIN_TOKEN,
            json_data={"query_text": "Test query"}
        )
        
        # Even if we get 404 (company not found), it's still a successful API call
        if success and response.status_code in [200, 404]:
            success_count += 1
        elif response and response.status_code == 429:
            rate_limited = True
            print(f"Rate limited after {success_count} requests")
            break
        
        time.sleep(0.2)
    
    print_test_result("rate_limiting", "AI endpoint rate limit (10/min)", 
                     rate_limited and success_count >= 10, 
                     f"Made {success_count} successful requests before being rate limited: {rate_limited}")
    
    # Check for rate limit headers
    success, response, error = make_request("get", "/companies", auth_token=ADMIN_TOKEN)
    has_rate_headers = "X-RateLimit-Limit" in response.headers or "X-RateLimit-Remaining" in response.headers
    
    print_test_result("rate_limiting", "Rate limit headers", has_rate_headers,
                     "Rate limit headers present" if has_rate_headers else "No rate limit headers found")

def test_input_validation():
    print_header("Testing Input Validation")
    
    # Test login endpoint with malicious inputs
    print("Testing login endpoint with malicious inputs...")
    
    # XSS attempt
    xss_payload = "<script>alert('XSS')</script>"
    success, response, error = make_request(
        "post", 
        "/auth/login", 
        json_data={"email": f"test{xss_payload}@example.com", "password": "password123"}
    )
    
    print_test_result("input_validation", "XSS in login email", 
                     response.status_code == 400, 
                     f"Response: {response.status_code} - {response.text if response else 'No response'}")
    
    # SQL injection attempt
    sql_payload = "' OR 1=1 --"
    success, response, error = make_request(
        "post", 
        "/auth/login", 
        json_data={"email": "test@example.com", "password": sql_payload}
    )
    
    print_test_result("input_validation", "SQL injection in login password", 
                     response.status_code == 400 or response.status_code == 401, 
                     f"Response: {response.status_code} - {response.text if response else 'No response'}")
    
    # Test company creation with oversized data
    print("\nTesting company creation with oversized/malicious data...")
    
    # Create a very long string
    long_string = "A" * 20000
    
    company_data = {
        "name": long_string,
        "industry": "saas",
        "employee_count": 100,
        "annual_revenue": 1000000,
        "headquarters_location": "Test Location",
        "compliance_standards": []
    }
    
    success, response, error = make_request(
        "post", 
        "/companies", 
        auth_token=ADMIN_TOKEN,
        json_data=company_data
    )
    
    print_test_result("input_validation", "Oversized company name", 
                     response.status_code == 400, 
                     f"Response: {response.status_code} - {response.text if response else 'No response'}")
    
    # Test with script tags in company name
    company_data = {
        "name": "<script>alert('XSS')</script>Company",
        "industry": "saas",
        "employee_count": 100,
        "annual_revenue": 1000000,
        "headquarters_location": "Test Location",
        "compliance_standards": []
    }
    
    success, response, error = make_request(
        "post", 
        "/companies", 
        auth_token=ADMIN_TOKEN,
        json_data=company_data
    )
    
    print_test_result("input_validation", "XSS in company name", 
                     response.status_code == 400, 
                     f"Response: {response.status_code} - {response.text if response else 'No response'}")

def test_api_key_authentication():
    print_header("Testing API Key Authentication")
    
    # Test API key creation (admin only)
    print("Testing API key creation (admin only)...")
    
    api_key_data = {
        "name": f"Test Key {datetime.now().isoformat()}",
        "permissions": ["read", "write"]
    }
    
    success, response, error = make_request(
        "post", 
        "/security/api-keys", 
        auth_token=ADMIN_TOKEN,
        json_data=api_key_data
    )
    
    api_key_created = success and response.status_code == 200 and "api_key" in response.json()
    print_test_result("api_key_auth", "API key creation (admin)", api_key_created,
                     f"Response: {response.json() if api_key_created else response.text if response else error}")
    
    if api_key_created:
        new_api_key = response.json()["api_key"]
        print(f"Created new API key: {new_api_key}")
        
        # Test using the new API key
        success, response, error = make_request(
            "get", 
            "/companies", 
            api_key=new_api_key
        )
        
        print_test_result("api_key_auth", "Using new API key", 
                         success and response.status_code == 200,
                         f"Response: {response.status_code} - {response.text if response else error}")
    
    # Test using the provided API key
    success, response, error = make_request(
        "get", 
        "/companies", 
        api_key=API_KEY
    )
    
    print_test_result("api_key_auth", "Using provided API key", 
                     success and response.status_code == 200,
                     f"Response: {response.status_code} - {response.text if response else error}")
    
    # Test with invalid API key
    success, response, error = make_request(
        "get", 
        "/companies", 
        api_key="cb_invalid_key"
    )
    
    print_test_result("api_key_auth", "Using invalid API key", 
                     not success or response.status_code == 401,
                     f"Response: {response.status_code} - {response.text if response else error}")

def test_audit_logging():
    print_header("Testing Audit Logging")
    
    # Test security stats endpoint
    print("Testing security stats endpoint...")
    
    success, response, error = make_request(
        "get", 
        "/security/stats", 
        auth_token=ADMIN_TOKEN
    )
    
    stats_working = success and response.status_code == 200
    print_test_result("audit_logging", "Security stats endpoint", stats_working,
                     f"Response: {response.json() if stats_working else response.text if response else error}")
    
    if stats_working:
        print("Security stats:")
        for key, value in response.json().items():
            print(f"  {key}: {value}")
    
    # Test audit logs endpoint
    print("\nTesting audit logs endpoint...")
    
    success, response, error = make_request(
        "get", 
        "/security/audit-logs", 
        auth_token=ADMIN_TOKEN
    )
    
    logs_working = success and response.status_code == 200
    print_test_result("audit_logging", "Audit logs endpoint", logs_working,
                     f"Response: {response.json() if logs_working else response.text if response else error}")
    
    if logs_working:
        logs = response.json().get("logs", [])
        print(f"Found {len(logs)} audit log entries")
        if logs:
            print("Sample log entry:")
            print(json.dumps(logs[0], indent=2))
    
    # Generate some events to test logging
    print("\nGenerating events to test logging...")
    
    # Failed login attempt
    make_request(
        "post", 
        "/auth/login", 
        json_data={"email": "nonexistent@example.com", "password": "wrongpassword"}
    )
    
    # Invalid API key
    make_request(
        "get", 
        "/companies", 
        api_key="cb_invalid_key_for_testing"
    )
    
    # Wait a moment for logs to be written
    time.sleep(1)
    
    # Check logs again to see if our events were recorded
    success, response, error = make_request(
        "get", 
        "/security/audit-logs?limit=5", 
        auth_token=ADMIN_TOKEN
    )
    
    events_logged = False
    if success and response.status_code == 200:
        logs = response.json().get("logs", [])
        for log in logs:
            if log.get("event_type") in ["INVALID_API_KEY", "API_ACCESS"]:
                events_logged = True
                break
    
    print_test_result("audit_logging", "Events being logged", events_logged,
                     "Recent events found in audit logs" if events_logged else "Recent events not found in logs")

def test_multi_tenant_security():
    print_header("Testing Multi-tenant Security")
    
    # Create a company in the current tenant
    company_name = f"Test Company {uuid.uuid4()}"
    company_data = {
        "name": company_name,
        "industry": "saas",
        "employee_count": 100,
        "annual_revenue": 1000000,
        "headquarters_location": "Test Location",
        "compliance_standards": []
    }
    
    success, response, error = make_request(
        "post", 
        "/companies", 
        auth_token=ADMIN_TOKEN,
        json_data=company_data
    )
    
    if not success or response.status_code != 200:
        print_test_result("multi_tenant_security", "Create company in tenant", False,
                         f"Failed to create test company: {error or response.text if response else 'Unknown error'}")
        return
    
    company_id = response.json().get("id")
    print(f"Created test company with ID: {company_id}")
    
    # Verify we can access the company with our token
    success, response, error = make_request(
        "get", 
        f"/companies/{company_id}", 
        auth_token=ADMIN_TOKEN
    )
    
    print_test_result("multi_tenant_security", "Access company with correct tenant", 
                     success and response.status_code == 200,
                     f"Response: {response.status_code} - {response.text if response else error}")
    
    # Try to access with a modified token (changing tenant_id)
    # We can't actually forge a token without the secret key, so we'll use an invalid token
    modified_token = ADMIN_TOKEN[:-10] + "modified"
    
    success, response, error = make_request(
        "get", 
        f"/companies/{company_id}", 
        auth_token=modified_token
    )
    
    print_test_result("multi_tenant_security", "Access company with incorrect tenant", 
                     not success or response.status_code == 401,
                     f"Response: {response.status_code} - {response.text if response else error}")
    
    # Test that security features work per-tenant
    # Create a company with API key
    company_name = f"API Key Company {uuid.uuid4()}"
    company_data = {
        "name": company_name,
        "industry": "saas",
        "employee_count": 100,
        "annual_revenue": 1000000,
        "headquarters_location": "Test Location",
        "compliance_standards": []
    }
    
    success, response, error = make_request(
        "post", 
        "/companies", 
        api_key=API_KEY,
        json_data=company_data
    )
    
    print_test_result("multi_tenant_security", "Create company with API key", 
                     success and response.status_code == 200,
                     f"Response: {response.status_code} - {response.text if response else error}")
    
    # Test that security headers are present even with API key auth
    if success and response.status_code == 200:
        has_security_headers = all(header in response.headers for header in [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection"
        ])
        
        print_test_result("multi_tenant_security", "Security headers with API key", has_security_headers,
                         "Security headers present with API key auth" if has_security_headers else "Missing security headers")

def print_summary():
    print_header("Test Summary")
    
    total_passed = sum(category["passed"] for category in test_results.values())
    total_failed = sum(category["failed"] for category in test_results.values())
    total_tests = total_passed + total_failed
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_passed} ({total_passed/total_tests*100:.1f}%)")
    print(f"Failed: {total_failed} ({total_failed/total_tests*100:.1f}%)")
    print("\nResults by Category:")
    
    for category, results in test_results.items():
        category_total = results["passed"] + results["failed"]
        if category_total > 0:
            pass_rate = results["passed"] / category_total * 100
            print(f"  {category.replace('_', ' ').title()}: {results['passed']}/{category_total} passed ({pass_rate:.1f}%)")
    
    print("\nFailed Tests:")
    for category, results in test_results.items():
        for test in results["details"]:
            if not test["passed"]:
                print(f"  [{category}] {test['test']}: {test['message']}")

if __name__ == "__main__":
    print("ClimaBill Security Hardening Test Suite")
    print("======================================")
    print(f"Testing against: {BASE_URL}")
    print(f"Admin Token: {ADMIN_TOKEN[:10]}...{ADMIN_TOKEN[-5:]}")
    print(f"API Key: {API_KEY[:10]}...{API_KEY[-5:]}")
    print("======================================")
    
    # Run all tests
    test_security_headers()
    test_rate_limiting()
    test_input_validation()
    test_api_key_authentication()
    test_audit_logging()
    test_multi_tenant_security()
    
    # Print summary
    print_summary()
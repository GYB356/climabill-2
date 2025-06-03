#!/usr/bin/env python3
import sys
import os

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Test imports
try:
    from models import Company, CompanyCreate
    print("✅ Models imported successfully")
except Exception as e:
    print(f"❌ Models import failed: {e}")

try:
    from carbon_calculator import CarbonCalculator
    print("✅ Carbon Calculator imported successfully")
except Exception as e:
    print(f"❌ Carbon Calculator import failed: {e}")

try:
    from data_service import CarbonDataService
    print("✅ Data Service imported successfully") 
except Exception as e:
    print(f"❌ Data Service import failed: {e}")

try:
    from ai_service import CarbonAIService
    print("✅ AI Service imported successfully")
except Exception as e:
    print(f"❌ AI Service import failed: {e}")

print("All import tests completed!")
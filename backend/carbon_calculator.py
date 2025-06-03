from typing import Dict, List, Any
from datetime import datetime
import json

class CarbonCalculator:
    """Carbon footprint calculation engine with industry-standard emission factors"""
    
    def __init__(self):
        # EPA and DEFRA emission factors (kg CO2eq per unit)
        self.emission_factors = {
            # Electricity (by region/grid mix)
            "electricity_us_average": 0.385,  # kg CO2eq/kWh
            "electricity_renewable": 0.012,   # kg CO2eq/kWh
            "electricity_coal": 0.820,        # kg CO2eq/kWh
            "electricity_natural_gas": 0.350, # kg CO2eq/kWh
            
            # Fuel combustion
            "natural_gas": 0.185,             # kg CO2eq/kWh
            "gasoline": 2.31,                 # kg CO2eq/liter
            "diesel": 2.68,                   # kg CO2eq/liter
            "jet_fuel": 2.52,                 # kg CO2eq/liter
            
            # Transportation
            "business_travel_short_haul": 0.158,  # kg CO2eq/km (flights <500km)
            "business_travel_medium_haul": 0.102, # kg CO2eq/km (flights 500-1500km)
            "business_travel_long_haul": 0.089,   # kg CO2eq/km (flights >1500km)
            "car_petrol": 0.168,                  # kg CO2eq/km
            "car_diesel": 0.165,                  # kg CO2eq/km
            "car_electric": 0.047,                # kg CO2eq/km
            "train": 0.033,                       # kg CO2eq/km
            "bus": 0.082,                         # kg CO2eq/km
            
            # Office and facilities
            "office_paper": 0.9,                  # kg CO2eq/kg paper
            "waste_landfill": 0.94,               # kg CO2eq/kg waste
            "waste_recycled": 0.21,               # kg CO2eq/kg waste
            "water_supply": 0.149,                # kg CO2eq/m3
            "server_cloud": 0.5,                  # kg CO2eq/GB data
            
            # Industry-specific factors
            "saas_data_center": 0.1,              # kg CO2eq/GB processed
            "manufacturing_steel": 1.85,          # kg CO2eq/kg steel
            "manufacturing_aluminum": 8.24,       # kg CO2eq/kg aluminum
            "manufacturing_plastic": 1.8,         # kg CO2eq/kg plastic
        }
        
        # Industry benchmarks (annual tonnes CO2eq per employee)
        self.industry_benchmarks = {
            "saas": 4.2,
            "fintech": 5.8,
            "ecommerce": 6.5,
            "manufacturing": 15.3,
            "healthcare": 8.7,
            "consulting": 3.9
        }
    
    def calculate_electricity_emissions(self, kwh_consumed: float, region: str = "us_average", renewable_percentage: float = 0) -> Dict[str, Any]:
        """Calculate emissions from electricity consumption"""
        grid_factor = self.emission_factors.get(f"electricity_{region}", self.emission_factors["electricity_us_average"])
        renewable_factor = self.emission_factors["electricity_renewable"]
        
        # Weighted average based on renewable percentage
        effective_factor = (grid_factor * (1 - renewable_percentage/100)) + (renewable_factor * (renewable_percentage/100))
        
        total_emissions = kwh_consumed * effective_factor
        
        return {
            "co2_equivalent_kg": total_emissions,
            "scope": "scope_2",
            "calculation_details": {
                "kwh_consumed": kwh_consumed,
                "emission_factor": effective_factor,
                "grid_factor": grid_factor,
                "renewable_percentage": renewable_percentage
            }
        }
    
    def calculate_fuel_emissions(self, fuel_type: str, quantity: float, unit: str = "liters") -> Dict[str, Any]:
        """Calculate emissions from fuel combustion"""
        if fuel_type == "natural_gas" and unit == "kwh":
            factor = self.emission_factors["natural_gas"]
        else:
            factor = self.emission_factors.get(fuel_type, 0)
        
        total_emissions = quantity * factor
        
        return {
            "co2_equivalent_kg": total_emissions,
            "scope": "scope_1",
            "calculation_details": {
                "fuel_type": fuel_type,
                "quantity": quantity,
                "unit": unit,
                "emission_factor": factor
            }
        }
    
    def calculate_business_travel_emissions(self, trips: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate emissions from business travel"""
        total_emissions = 0
        calculation_details = []
        
        for trip in trips:
            transport_mode = trip.get("transport_mode", "car_petrol")
            distance_km = trip.get("distance_km", 0)
            passengers = trip.get("passengers", 1)
            
            # Special handling for flights
            if "flight" in transport_mode or "business_travel" in transport_mode:
                if distance_km < 500:
                    factor = self.emission_factors["business_travel_short_haul"]
                elif distance_km < 1500:
                    factor = self.emission_factors["business_travel_medium_haul"]
                else:
                    factor = self.emission_factors["business_travel_long_haul"]
            else:
                factor = self.emission_factors.get(transport_mode, self.emission_factors["car_petrol"])
            
            trip_emissions = (distance_km * factor) / passengers
            total_emissions += trip_emissions
            
            calculation_details.append({
                "transport_mode": transport_mode,
                "distance_km": distance_km,
                "passengers": passengers,
                "emission_factor": factor,
                "trip_emissions": trip_emissions
            })
        
        return {
            "co2_equivalent_kg": total_emissions,
            "scope": "scope_3",
            "calculation_details": calculation_details
        }
    
    def calculate_office_emissions(self, office_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate emissions from office operations"""
        total_emissions = 0
        calculation_details = {}
        
        # Paper consumption
        if "paper_kg" in office_data:
            paper_emissions = office_data["paper_kg"] * self.emission_factors["office_paper"]
            total_emissions += paper_emissions
            calculation_details["paper"] = {
                "quantity_kg": office_data["paper_kg"],
                "emissions": paper_emissions
            }
        
        # Waste
        if "waste_kg" in office_data:
            recycling_rate = office_data.get("recycling_rate", 0.3)  # 30% default
            landfill_waste = office_data["waste_kg"] * (1 - recycling_rate)
            recycled_waste = office_data["waste_kg"] * recycling_rate
            
            waste_emissions = (landfill_waste * self.emission_factors["waste_landfill"]) + \
                             (recycled_waste * self.emission_factors["waste_recycled"])
            total_emissions += waste_emissions
            calculation_details["waste"] = {
                "total_waste_kg": office_data["waste_kg"],
                "recycling_rate": recycling_rate,
                "emissions": waste_emissions
            }
        
        # Water consumption
        if "water_m3" in office_data:
            water_emissions = office_data["water_m3"] * self.emission_factors["water_supply"]
            total_emissions += water_emissions
            calculation_details["water"] = {
                "quantity_m3": office_data["water_m3"],
                "emissions": water_emissions
            }
        
        return {
            "co2_equivalent_kg": total_emissions,
            "scope": "scope_3",
            "calculation_details": calculation_details
        }
    
    def calculate_digital_emissions(self, digital_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate emissions from digital operations (especially relevant for SaaS)"""
        total_emissions = 0
        calculation_details = {}
        
        # Cloud/server usage
        if "data_processed_gb" in digital_data:
            cloud_emissions = digital_data["data_processed_gb"] * self.emission_factors["server_cloud"]
            total_emissions += cloud_emissions
            calculation_details["cloud_processing"] = {
                "data_gb": digital_data["data_processed_gb"],
                "emissions": cloud_emissions
            }
        
        # Data center operations (for companies with own servers)
        if "server_hours" in digital_data:
            server_power_kw = digital_data.get("server_power_kw", 2.0)  # Average server power
            server_emissions_calc = self.calculate_electricity_emissions(
                server_power_kw * digital_data["server_hours"],
                digital_data.get("data_center_region", "us_average"),
                digital_data.get("renewable_energy_percentage", 0)
            )
            total_emissions += server_emissions_calc["co2_equivalent_kg"]
            calculation_details["servers"] = server_emissions_calc["calculation_details"]
        
        return {
            "co2_equivalent_kg": total_emissions,
            "scope": "scope_2",  # Usually scope 2 for purchased electricity
            "calculation_details": calculation_details
        }
    
    def get_industry_benchmark(self, industry: str, employee_count: int) -> Dict[str, Any]:
        """Get industry benchmarking data"""
        benchmark_per_employee = self.industry_benchmarks.get(industry.lower(), 6.0)  # Default 6 tonnes/employee
        total_benchmark = benchmark_per_employee * employee_count
        
        return {
            "industry": industry,
            "benchmark_tonnes_per_employee": benchmark_per_employee,
            "total_benchmark_tonnes": total_benchmark,
            "employee_count": employee_count
        }
    
    def calculate_carbon_cost(self, co2_kg: float, carbon_price_per_tonne: float = 50.0) -> Dict[str, float]:
        """Calculate the cost of carbon emissions at current carbon pricing"""
        co2_tonnes = co2_kg / 1000
        carbon_cost = co2_tonnes * carbon_price_per_tonne
        
        return {
            "co2_tonnes": co2_tonnes,
            "carbon_price_per_tonne": carbon_price_per_tonne,
            "total_carbon_cost": carbon_cost
        }
    
    def calculate_reduction_value(self, reduction_kg: float, energy_cost_savings: float = 0, carbon_price_per_tonne: float = 50.0) -> Dict[str, float]:
        """Calculate the financial value of carbon reductions"""
        carbon_value = self.calculate_carbon_cost(reduction_kg, carbon_price_per_tonne)
        total_value = carbon_value["total_carbon_cost"] + energy_cost_savings
        
        return {
            "co2_reduction_tonnes": carbon_value["co2_tonnes"],
            "carbon_value": carbon_value["total_carbon_cost"],
            "energy_cost_savings": energy_cost_savings,
            "total_financial_value": total_value
        }
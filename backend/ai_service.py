import openai
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import numpy as np
from models import CarbonForecast, CarbonReductionInitiative

class CarbonAIService:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    async def process_natural_language_query(self, company_data: Dict, query: str, user_context: Optional[Dict] = None) -> str:
        """Process natural language queries about carbon data using GPT-4"""
        
        # Safely convert data to JSON strings, handling datetime objects
        def safe_json_dumps(obj):
            def default(o):
                if isinstance(o, datetime):
                    return o.isoformat()
                return str(o)
            return json.dumps(obj, default=default, indent=2)
        
        # Prepare context for AI
        context = f"""
        You are ClimaBill's Carbon Intelligence AI. Analyze the following company data and answer the user's question.
        
        Company Data:
        - Name: {company_data.get('name', 'Unknown')}
        - Industry: {company_data.get('industry', 'Unknown')}
        - Employee Count: {company_data.get('employee_count', 0)}
        - Annual Revenue: ${company_data.get('annual_revenue', 0):,.2f}
        
        Recent Emissions Data:
        {safe_json_dumps(company_data.get('recent_emissions', {}))}
        
        Emission Sources:
        {safe_json_dumps(company_data.get('emission_sources', []))}
        
        Carbon Targets:
        {safe_json_dumps(company_data.get('targets', []))}
        
        Recent Initiatives:
        {safe_json_dumps(company_data.get('initiatives', []))}
        
        Please provide a comprehensive, data-driven answer that:
        1. Uses specific numbers from the data
        2. Provides actionable insights
        3. Includes financial implications where relevant
        4. Suggests next steps or recommendations
        5. Uses a professional but accessible tone
        
        User Question: {query}
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are ClimaBill's AI Carbon Intelligence expert. Provide data-driven, actionable insights about carbon emissions and sustainability initiatives. Always include financial implications and ROI considerations."},
                    {"role": "user", "content": context}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"I apologize, but I'm experiencing technical difficulties processing your query. Please try again later. Error: {str(e)}"
    
    async def generate_emission_forecast(self, historical_data: List[Dict], company_info: Dict, horizon_months: int = 12) -> CarbonForecast:
        """Generate predictive emissions forecasting using AI and statistical models"""
        
        # Prepare historical data for analysis
        data_summary = self._prepare_forecast_data(historical_data)
        
        # Use AI to analyze trends and make predictions
        forecast_prompt = f"""
        Analyze the following historical carbon emissions data and generate a forecast for the next {horizon_months} months.
        
        Company Information:
        - Industry: {company_info.get('industry')}
        - Employee Count: {company_info.get('employee_count')}
        - Revenue: ${company_info.get('annual_revenue', 0):,.2f}
        
        Historical Emissions Data (monthly):
        {self.safe_json_dumps(data_summary)}
        
        Please provide:
        1. Monthly emission predictions for each scope (1, 2, 3)
        2. Confidence intervals (min/max) for each prediction
        3. Key assumptions affecting the forecast
        4. Potential risks or opportunities that could impact emissions
        
        Format the response as a JSON object with the following structure:
        {{
            "monthly_predictions": {{
                "scope_1": [list of monthly values],
                "scope_2": [list of monthly values], 
                "scope_3": [list of monthly values]
            }},
            "confidence_intervals": {{
                "scope_1": [[min, max] for each month],
                "scope_2": [[min, max] for each month],
                "scope_3": [[min, max] for each month]
            }},
            "assumptions": ["list", "of", "key", "assumptions"],
            "risk_factors": ["list", "of", "potential", "risks"]
        }}
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert carbon emissions forecasting analyst. Provide detailed, data-driven predictions based on historical trends, industry benchmarks, and business factors."},
                    {"role": "user", "content": forecast_prompt}
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            # Parse AI response and create forecast object
            ai_response = json.loads(response.choices[0].message.content)
            
            # Calculate aggregated predictions
            predicted_emissions = {}
            confidence_intervals = {}
            
            for scope in ['scope_1', 'scope_2', 'scope_3']:
                if scope in ai_response['monthly_predictions']:
                    predicted_emissions[scope] = sum(ai_response['monthly_predictions'][scope])
                    min_total = sum([interval[0] for interval in ai_response['confidence_intervals'][scope]])
                    max_total = sum([interval[1] for interval in ai_response['confidence_intervals'][scope]])
                    confidence_intervals[scope] = [min_total, max_total]
            
            return CarbonForecast(
                company_id=company_info['id'],
                forecast_date=datetime.utcnow(),
                forecast_horizon_months=horizon_months,
                predicted_emissions=predicted_emissions,
                confidence_interval=confidence_intervals,
                assumptions=ai_response.get('assumptions', []) + ai_response.get('risk_factors', [])
            )
            
        except Exception as e:
            # Fallback to simple statistical forecast
            return self._simple_statistical_forecast(historical_data, company_info, horizon_months)
    
    async def generate_reduction_recommendations(self, company_data: Dict, emission_data: Dict) -> List[Dict[str, Any]]:
        """Generate AI-powered carbon reduction recommendations with ROI calculations"""
        
        recommendations_prompt = f"""
        Based on the following company and emissions data, recommend specific carbon reduction initiatives with detailed ROI analysis.
        
        Company Profile:
        - Industry: {company_data.get('industry')}
        - Size: {company_data.get('employee_count')} employees
        - Revenue: ${company_data.get('annual_revenue', 0):,.2f}
        - Location: {company_data.get('headquarters_location')}
        
        Current Emissions Breakdown:
        {json.dumps(emission_data, indent=2)}
        
        Please recommend 5-7 specific initiatives that:
        1. Target the highest impact emission sources
        2. Are realistic for this company size/industry
        3. Include estimated implementation costs
        4. Provide clear ROI calculations (cost savings + carbon price value)
        5. Consider both direct savings and risk mitigation benefits
        
        Format each recommendation as:
        {{
            "initiative_name": "Clear, actionable name",
            "description": "Detailed implementation approach",
            "implementation_cost": <number>,
            "annual_savings": <number>,
            "annual_co2_reduction": <number>,
            "roi_percentage": <number>,
            "payback_period_months": <number>,
            "difficulty": "low|medium|high",
            "priority_score": <1-10>
        }}
        
        Return as a JSON array of recommendations.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a carbon reduction strategy expert. Provide specific, actionable recommendations with detailed financial analysis. Focus on initiatives that deliver both environmental and business value."},
                    {"role": "user", "content": recommendations_prompt}
                ],
                max_tokens=2000,
                temperature=0.4
            )
            
            recommendations = json.loads(response.choices[0].message.content)
            return recommendations
            
        except Exception as e:
            # Fallback recommendations based on industry best practices
            return self._get_default_recommendations(company_data, emission_data)
    
    def _prepare_forecast_data(self, historical_data: List[Dict]) -> Dict:
        """Prepare historical data for AI analysis"""
        monthly_data = {}
        for record in historical_data:
            month_key = record['period_start'][:7]  # YYYY-MM format
            if month_key not in monthly_data:
                monthly_data[month_key] = {'scope_1': 0, 'scope_2': 0, 'scope_3': 0}
            monthly_data[month_key][record['scope']] += record['co2_equivalent_kg']
        
        return monthly_data
    
    def _simple_statistical_forecast(self, historical_data: List[Dict], company_info: Dict, horizon_months: int) -> CarbonForecast:
        """Fallback statistical forecasting method"""
        # Simple trend-based forecast
        monthly_data = self._prepare_forecast_data(historical_data)
        
        predicted_emissions = {}
        confidence_intervals = {}
        
        for scope in ['scope_1', 'scope_2', 'scope_3']:
            scope_values = [month_data.get(scope, 0) for month_data in monthly_data.values()]
            if scope_values:
                avg_emissions = np.mean(scope_values)
                std_emissions = np.std(scope_values)
                predicted_emissions[scope] = avg_emissions * horizon_months
                confidence_intervals[scope] = [
                    max(0, (avg_emissions - std_emissions) * horizon_months),
                    (avg_emissions + std_emissions) * horizon_months
                ]
            else:
                predicted_emissions[scope] = 0
                confidence_intervals[scope] = [0, 0]
        
        return CarbonForecast(
            company_id=company_info['id'],
            forecast_date=datetime.utcnow(),
            forecast_horizon_months=horizon_months,
            predicted_emissions=predicted_emissions,
            confidence_interval=confidence_intervals,
            assumptions=["Statistical forecast based on historical trends", "Assumes current business operations continue"]
        )
    
    def _get_default_recommendations(self, company_data: Dict, emission_data: Dict) -> List[Dict[str, Any]]:
        """Fallback recommendations when AI is unavailable"""
        return [
            {
                "initiative_name": "LED Lighting Upgrade",
                "description": "Replace all fluorescent and incandescent lighting with LED alternatives",
                "implementation_cost": 15000,
                "annual_savings": 3500,
                "annual_co2_reduction": 12000,
                "roi_percentage": 23.3,
                "payback_period_months": 51,
                "difficulty": "low",
                "priority_score": 8
            },
            {
                "initiative_name": "Remote Work Policy",
                "description": "Implement hybrid remote work to reduce commuting emissions",
                "implementation_cost": 5000,
                "annual_savings": 8000,
                "annual_co2_reduction": 25000,
                "roi_percentage": 160,
                "payback_period_months": 8,
                "difficulty": "medium",
                "priority_score": 9
            }
        ]
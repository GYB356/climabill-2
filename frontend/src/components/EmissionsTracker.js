import React, { useState, useEffect } from 'react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const EmissionsTracker = ({ company }) => {
  const [activeTab, setActiveTab] = useState('add');
  const [emissionSources, setEmissionSources] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);

  // Form state for adding emissions
  const [formData, setFormData] = useState({
    source_type: 'electricity',
    period_start: new Date().toISOString().split('T')[0],
    period_end: new Date().toISOString().split('T')[0],
    activity_data: {},
    data_quality: 'estimated'
  });

  useEffect(() => {
    fetchEmissionSources();
    fetchSummary();
  }, [company.id]);

  const fetchEmissionSources = async () => {
    try {
      const response = await fetch(`${API}/companies/${company.id}/emissions/sources/top?limit=10`);
      if (response.ok) {
        const sources = await response.json();
        setEmissionSources(sources);
      }
    } catch (error) {
      console.error('Error fetching emission sources:', error);
    }
  };

  const fetchSummary = async () => {
    try {
      const response = await fetch(`${API}/companies/${company.id}/emissions/summary`);
      if (response.ok) {
        const summaryData = await response.json();
        setSummary(summaryData);
      }
    } catch (error) {
      console.error('Error fetching summary:', error);
    }
  };

  const handleCalculateEmissions = async () => {
    setLoading(true);
    try {
      let calculationData = {};
      
      // Prepare calculation data based on source type
      switch (formData.source_type) {
        case 'electricity':
          calculationData = {
            kwh_consumed: parseFloat(formData.activity_data.kwh_consumed || 0),
            region: formData.activity_data.region || 'us_average',
            renewable_percentage: parseFloat(formData.activity_data.renewable_percentage || 0)
          };
          break;
        case 'fuel':
          calculationData = {
            fuel_type: formData.activity_data.fuel_type || 'gasoline',
            quantity: parseFloat(formData.activity_data.quantity || 0),
            unit: formData.activity_data.unit || 'liters'
          };
          break;
        case 'travel':
          calculationData = {
            trips: [{
              transport_mode: formData.activity_data.transport_mode || 'car_petrol',
              distance_km: parseFloat(formData.activity_data.distance_km || 0),
              passengers: parseInt(formData.activity_data.passengers || 1)
            }]
          };
          break;
        default:
          // Default calculation for other types
          calculationData = {
            kwh_consumed: parseFloat(formData.activity_data.energy_consumed || 0),
            region: 'us_average'
          };
      }

      // Calculate emissions using the appropriate endpoint
      let calculationEndpoint = '';
      let requestBody = {};

      switch (formData.source_type) {
        case 'electricity':
          calculationEndpoint = '/calculate/electricity';
          requestBody = calculationData;
          break;
        case 'fuel':
          calculationEndpoint = '/calculate/fuel';
          requestBody = calculationData;
          break;
        case 'travel':
          calculationEndpoint = '/calculate/travel';
          requestBody = calculationData.trips;
          break;
        default:
          calculationEndpoint = '/calculate/electricity';
          requestBody = calculationData;
      }

      const calculationResponse = await fetch(`${API}${calculationEndpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });

      if (!calculationResponse.ok) {
        throw new Error('Calculation failed');
      }

      const calculationResult = await calculationResponse.json();

      // Find the appropriate source ID (we'll use the first available source for now)
      const sourceId = emissionSources[0]?.id || 'default-source-id';

      // Add the emission record
      const recordData = {
        source_id: sourceId,
        period_start: new Date(formData.period_start).toISOString(),
        period_end: new Date(formData.period_end).toISOString(),
        co2_equivalent_kg: calculationResult.co2_equivalent_kg,
        activity_data: formData.activity_data,
        emission_factor: calculationResult.calculation_details?.emission_factor || 0,
        data_quality: formData.data_quality
      };

      const addResponse = await fetch(`${API}/companies/${company.id}/emissions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(recordData)
      });

      if (addResponse.ok) {
        alert(`Successfully added emission record: ${calculationResult.co2_equivalent_kg.toFixed(2)} kg CO₂eq`);
        // Reset form
        setFormData({
          source_type: 'electricity',
          period_start: new Date().toISOString().split('T')[0],
          period_end: new Date().toISOString().split('T')[0],
          activity_data: {},
          data_quality: 'estimated'
        });
        // Refresh data
        fetchSummary();
      } else {
        throw new Error('Failed to add emission record');
      }

    } catch (error) {
      console.error('Error calculating emissions:', error);
      alert('Error calculating emissions. Please try again.');
    }
    setLoading(false);
  };

  const updateActivityData = (field, value) => {
    setFormData(prev => ({
      ...prev,
      activity_data: {
        ...prev.activity_data,
        [field]: value
      }
    }));
  };

  const renderActivityDataForm = () => {
    switch (formData.source_type) {
      case 'electricity':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Electricity Consumed (kWh)
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.activity_data.kwh_consumed || ''}
                onChange={(e) => updateActivityData('kwh_consumed', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                placeholder="1000"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Grid Region
              </label>
              <select
                value={formData.activity_data.region || 'us_average'}
                onChange={(e) => updateActivityData('region', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
              >
                <option value="us_average">US Average</option>
                <option value="renewable">Renewable Energy</option>
                <option value="coal">Coal</option>
                <option value="natural_gas">Natural Gas</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Renewable Energy Percentage
              </label>
              <input
                type="number"
                min="0"
                max="100"
                value={formData.activity_data.renewable_percentage || ''}
                onChange={(e) => updateActivityData('renewable_percentage', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                placeholder="0"
              />
            </div>
          </div>
        );

      case 'fuel':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Fuel Type
              </label>
              <select
                value={formData.activity_data.fuel_type || 'gasoline'}
                onChange={(e) => updateActivityData('fuel_type', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
              >
                <option value="gasoline">Gasoline</option>
                <option value="diesel">Diesel</option>
                <option value="natural_gas">Natural Gas</option>
                <option value="jet_fuel">Jet Fuel</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Quantity
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.activity_data.quantity || ''}
                onChange={(e) => updateActivityData('quantity', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                placeholder="100"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Unit
              </label>
              <select
                value={formData.activity_data.unit || 'liters'}
                onChange={(e) => updateActivityData('unit', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
              >
                <option value="liters">Liters</option>
                <option value="gallons">Gallons</option>
                <option value="kwh">kWh (for natural gas)</option>
              </select>
            </div>
          </div>
        );

      case 'travel':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Transport Mode
              </label>
              <select
                value={formData.activity_data.transport_mode || 'car_petrol'}
                onChange={(e) => updateActivityData('transport_mode', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
              >
                <option value="car_petrol">Car (Petrol)</option>
                <option value="car_diesel">Car (Diesel)</option>
                <option value="car_electric">Car (Electric)</option>
                <option value="business_travel_short_haul">Flight (Short Haul)</option>
                <option value="business_travel_medium_haul">Flight (Medium Haul)</option>
                <option value="business_travel_long_haul">Flight (Long Haul)</option>
                <option value="train">Train</option>
                <option value="bus">Bus</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Distance (km)
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.activity_data.distance_km || ''}
                onChange={(e) => updateActivityData('distance_km', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                placeholder="100"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Number of Passengers
              </label>
              <input
                type="number"
                min="1"
                value={formData.activity_data.passengers || '1'}
                onChange={(e) => updateActivityData('passengers', e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                placeholder="1"
              />
            </div>
          </div>
        );

      default:
        return (
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Energy Consumed (kWh equivalent)
            </label>
            <input
              type="number"
              step="0.01"
              value={formData.activity_data.energy_consumed || ''}
              onChange={(e) => updateActivityData('energy_consumed', e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
              placeholder="100"
            />
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">
          🌱 Emissions Tracker
        </h1>
        <p className="text-gray-400">
          Track and calculate carbon emissions for {company.name}
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="mb-8">
        <div className="border-b border-gray-700">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('add')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'add'
                  ? 'border-green-500 text-green-400'
                  : 'border-transparent text-gray-400 hover:text-gray-300'
              }`}
            >
              Add Emissions
            </button>
            <button
              onClick={() => setActiveTab('summary')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'summary'
                  ? 'border-green-500 text-green-400'
                  : 'border-transparent text-gray-400 hover:text-gray-300'
              }`}
            >
              Summary
            </button>
          </nav>
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'add' && (
        <div className="max-w-2xl">
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-6">Add New Emission Data</h3>
            
            <div className="space-y-6">
              {/* Source Type */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Emission Source Type
                </label>
                <select
                  value={formData.source_type}
                  onChange={(e) => setFormData(prev => ({ ...prev, source_type: e.target.value, activity_data: {} }))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="electricity">Electricity Consumption</option>
                  <option value="fuel">Fuel Combustion</option>
                  <option value="travel">Business Travel</option>
                  <option value="office">Office Operations</option>
                  <option value="digital">Digital/Cloud Services</option>
                </select>
              </div>

              {/* Date Range */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Period Start
                  </label>
                  <input
                    type="date"
                    value={formData.period_start}
                    onChange={(e) => setFormData(prev => ({ ...prev, period_start: e.target.value }))}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Period End
                  </label>
                  <input
                    type="date"
                    value={formData.period_end}
                    onChange={(e) => setFormData(prev => ({ ...prev, period_end: e.target.value }))}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                </div>
              </div>

              {/* Activity Data Form */}
              {renderActivityDataForm()}

              {/* Data Quality */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Data Quality
                </label>
                <select
                  value={formData.data_quality}
                  onChange={(e) => setFormData(prev => ({ ...prev, data_quality: e.target.value }))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="estimated">Estimated</option>
                  <option value="calculated">Calculated</option>
                  <option value="measured">Measured</option>
                </select>
              </div>

              {/* Submit Button */}
              <button
                onClick={handleCalculateEmissions}
                disabled={loading}
                className="w-full bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white font-medium py-3 px-4 rounded-md transition-colors"
              >
                {loading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Calculating...
                  </div>
                ) : (
                  'Calculate & Add Emissions'
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'summary' && (
        <div>
          {summary ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Total Emissions */}
              <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                <h3 className="text-lg font-semibold text-white mb-4">Total Emissions</h3>
                <div className="text-3xl font-bold text-green-400 mb-2">
                  {(summary.total_emissions_kg / 1000).toFixed(1)} tonnes
                </div>
                <div className="text-sm text-gray-400">CO₂ equivalent</div>
              </div>

              {/* Scope Breakdown */}
              <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                <h3 className="text-lg font-semibold text-white mb-4">Scope Breakdown</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Scope 1:</span>
                    <span className="text-white">{(summary.scope_breakdown.scope_1 / 1000).toFixed(1)}t</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Scope 2:</span>
                    <span className="text-white">{(summary.scope_breakdown.scope_2 / 1000).toFixed(1)}t</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Scope 3:</span>
                    <span className="text-white">{(summary.scope_breakdown.scope_3 / 1000).toFixed(1)}t</span>
                  </div>
                </div>
              </div>

              {/* Emissions Intensity */}
              <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                <h3 className="text-lg font-semibold text-white mb-4">Emissions Intensity</h3>
                <div className="text-3xl font-bold text-orange-400 mb-2">
                  {(summary.emissions_intensity / company.employee_count).toFixed(1)}
                </div>
                <div className="text-sm text-gray-400">tonnes per employee</div>
              </div>
            </div>
          ) : (
            <div className="text-center text-gray-400">
              <div className="text-6xl mb-4">📊</div>
              <div className="text-lg">No emission data available yet</div>
              <div className="text-sm">Add some emission data to see your summary</div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default EmissionsTracker;
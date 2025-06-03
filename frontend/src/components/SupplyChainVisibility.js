import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SupplyChainVisibility = ({ company }) => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [dashboardData, setDashboardData] = useState(null);
  const [suppliers, setSuppliers] = useState([]);
  const [emissions, setEmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddSupplier, setShowAddSupplier] = useState(false);
  const [showAddEmission, setShowAddEmission] = useState(false);

  const [newSupplier, setNewSupplier] = useState({
    supplier_name: '',
    industry: '',
    location: '',
    contact_email: '',
    annual_revenue: '',
    employee_count: '',
    carbon_score: '',
    verification_status: 'pending',
    partnership_level: 'basic'
  });

  const [newEmission, setNewEmission] = useState({
    supplier_id: '',
    emission_type: 'upstream',
    scope: 'scope_3',
    co2_equivalent_kg: '',
    activity_description: '',
    data_quality: 'estimated'
  });

  useEffect(() => {
    fetchDashboardData();
    fetchSuppliers();
    fetchEmissions();
  }, [company.id]);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch(`${API}/companies/${company.id}/supply-chain/dashboard`);
      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
    setLoading(false);
  };

  const fetchSuppliers = async () => {
    try {
      const response = await fetch(`${API}/companies/${company.id}/suppliers`);
      if (response.ok) {
        const data = await response.json();
        setSuppliers(data);
      }
    } catch (error) {
      console.error('Error fetching suppliers:', error);
    }
  };

  const fetchEmissions = async () => {
    try {
      const response = await fetch(`${API}/companies/${company.id}/supply-chain-emissions`);
      if (response.ok) {
        const data = await response.json();
        setEmissions(data);
      }
    } catch (error) {
      console.error('Error fetching emissions:', error);
    }
  };

  const handleAddSupplier = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API}/companies/${company.id}/suppliers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...newSupplier,
          annual_revenue: parseFloat(newSupplier.annual_revenue),
          employee_count: parseInt(newSupplier.employee_count),
          carbon_score: parseFloat(newSupplier.carbon_score)
        })
      });

      if (response.ok) {
        setShowAddSupplier(false);
        setNewSupplier({
          supplier_name: '',
          industry: '',
          location: '',
          contact_email: '',
          annual_revenue: '',
          employee_count: '',
          carbon_score: '',
          verification_status: 'pending',
          partnership_level: 'basic'
        });
        fetchSuppliers();
        fetchDashboardData();
      } else {
        alert('Failed to add supplier');
      }
    } catch (error) {
      console.error('Error adding supplier:', error);
      alert('Error adding supplier');
    }
  };

  const handleAddEmission = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API}/companies/${company.id}/supply-chain-emissions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...newEmission,
          co2_equivalent_kg: parseFloat(newEmission.co2_equivalent_kg),
          reporting_period_start: new Date().toISOString(),
          reporting_period_end: new Date().toISOString()
        })
      });

      if (response.ok) {
        setShowAddEmission(false);
        setNewEmission({
          supplier_id: '',
          emission_type: 'upstream',
          scope: 'scope_3',
          co2_equivalent_kg: '',
          activity_description: '',
          data_quality: 'estimated'
        });
        fetchEmissions();
        fetchDashboardData();
      } else {
        alert('Failed to add emission data');
      }
    } catch (error) {
      console.error('Error adding emission:', error);
      alert('Error adding emission data');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-green-500"></div>
      </div>
    );
  }

  // Prepare chart data
  const scoreDistributionData = dashboardData?.score_distribution ? Object.entries(dashboardData.score_distribution).map(([range, count]) => ({
    range,
    count,
    color: range === '76-100' ? '#10b981' : range === '51-75' ? '#f59e0b' : range === '26-50' ? '#f97316' : '#ef4444'
  })) : [];

  return (
    <div className="min-h-screen bg-gray-900 p-8">
      {/* Header */}
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">
            🔗 Supply Chain Carbon Visibility
          </h1>
          <p className="text-gray-400">
            Track and manage carbon emissions across {company.name}'s supply chain
          </p>
        </div>
        <div className="space-x-4">
          <button
            onClick={() => setShowAddSupplier(true)}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md"
          >
            + Add Supplier
          </button>
          <button
            onClick={() => setShowAddEmission(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md"
          >
            + Add Emission Data
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="mb-8">
        <div className="border-b border-gray-700">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'dashboard'
                  ? 'border-green-500 text-green-400'
                  : 'border-transparent text-gray-400 hover:text-gray-300'
              }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => setActiveTab('suppliers')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'suppliers'
                  ? 'border-green-500 text-green-400'
                  : 'border-transparent text-gray-400 hover:text-gray-300'
              }`}
            >
              Suppliers
            </button>
            <button
              onClick={() => setActiveTab('emissions')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'emissions'
                  ? 'border-green-500 text-green-400'
                  : 'border-transparent text-gray-400 hover:text-gray-300'
              }`}
            >
              Emissions
            </button>
          </nav>
        </div>
      </div>

      {/* Dashboard Tab */}
      {activeTab === 'dashboard' && dashboardData && (
        <div>
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <MetricCard
              title="Total Suppliers"
              value={dashboardData.total_suppliers}
              subtitle="In supply chain"
              icon="🏢"
              color="blue"
            />
            <MetricCard
              title="Verified Suppliers"
              value={`${dashboardData.verification_rate.toFixed(1)}%`}
              subtitle={`${dashboardData.verified_suppliers} of ${dashboardData.total_suppliers}`}
              icon="✅"
              color="green"
            />
            <MetricCard
              title="Avg Carbon Score"
              value={dashboardData.average_carbon_score.toFixed(1)}
              subtitle="Out of 100"
              icon="📊"
              color="purple"
            />
            <MetricCard
              title="Supply Chain Emissions"
              value={`${(dashboardData.total_supply_chain_emissions / 1000).toFixed(1)}t`}
              subtitle="CO₂ equivalent"
              icon="🌍"
              color="orange"
            />
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {/* Carbon Score Distribution */}
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-4">Carbon Score Distribution</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={scoreDistributionData}
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="count"
                    label={({ range, count }) => `${range}: ${count}`}
                  >
                    {scoreDistributionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Top Performing Suppliers */}
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-4">Top Performing Suppliers</h3>
              <div className="space-y-3">
                {dashboardData.top_performing_suppliers.slice(0, 5).map((supplier, index) => (
                  <div key={supplier.id || index} className="flex justify-between items-center">
                    <div>
                      <div className="text-white font-medium">{supplier.supplier_name || 'Unknown Supplier'}</div>
                      <div className="text-gray-400 text-sm">{supplier.industry || 'Unknown Industry'}</div>
                    </div>
                    <div className="text-green-400 font-semibold">
                      {(supplier.carbon_score || 0).toFixed(1)}
                    </div>
                  </div>
                ))}
                {dashboardData.top_performing_suppliers.length === 0 && (
                  <div className="text-gray-400 text-center py-4">No suppliers added yet</div>
                )}
              </div>
            </div>
          </div>

          {/* Suppliers Needing Attention */}
          {dashboardData.suppliers_needing_attention && dashboardData.suppliers_needing_attention.length > 0 && (
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-4">🚨 Suppliers Needing Attention</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {dashboardData.suppliers_needing_attention.map((supplier) => (
                  <div key={supplier.id} className="bg-red-900 bg-opacity-30 border border-red-600 rounded-lg p-4">
                    <div className="text-white font-medium">{supplier.supplier_name}</div>
                    <div className="text-gray-400 text-sm">{supplier.industry}</div>
                    <div className="text-red-400 font-semibold mt-2">
                      Score: {supplier.carbon_score.toFixed(1)}/100
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Suppliers Tab */}
      {activeTab === 'suppliers' && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4">Supplier Directory</h3>
          {suppliers.length === 0 ? (
            <div className="text-center text-gray-400 py-8">
              <div className="text-4xl mb-4">🏢</div>
              <div>No suppliers added yet</div>
              <button
                onClick={() => setShowAddSupplier(true)}
                className="mt-4 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md"
              >
                Add Your First Supplier
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-gray-400 border-b border-gray-700">
                    <th className="text-left py-3 px-4">Supplier</th>
                    <th className="text-left py-3 px-4">Industry</th>
                    <th className="text-left py-3 px-4">Location</th>
                    <th className="text-right py-3 px-4">Carbon Score</th>
                    <th className="text-center py-3 px-4">Status</th>
                    <th className="text-center py-3 px-4">Partnership</th>
                  </tr>
                </thead>
                <tbody>
                  {suppliers.map((supplier) => (
                    <tr key={supplier.id} className="border-b border-gray-700 hover:bg-gray-700">
                      <td className="py-3 px-4">
                        <div className="text-white font-medium">{supplier.supplier_name}</div>
                        <div className="text-gray-400 text-xs">{supplier.contact_email}</div>
                      </td>
                      <td className="py-3 px-4 text-white">{supplier.industry}</td>
                      <td className="py-3 px-4 text-white">{supplier.location}</td>
                      <td className="py-3 px-4 text-right">
                        <span className={`font-semibold ${
                          supplier.carbon_score >= 75 ? 'text-green-400' :
                          supplier.carbon_score >= 50 ? 'text-yellow-400' :
                          'text-red-400'
                        }`}>
                          {supplier.carbon_score.toFixed(1)}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center">
                        <StatusBadge status={supplier.verification_status} />
                      </td>
                      <td className="py-3 px-4 text-center">
                        <PartnershipBadge level={supplier.partnership_level} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Emissions Tab */}
      {activeTab === 'emissions' && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4">Supply Chain Emissions</h3>
          {emissions.length === 0 ? (
            <div className="text-center text-gray-400 py-8">
              <div className="text-4xl mb-4">📊</div>
              <div>No emission data added yet</div>
              <button
                onClick={() => setShowAddEmission(true)}
                className="mt-4 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md"
              >
                Add Emission Data
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {emissions.map((emission) => (
                <div key={emission.id} className="bg-gray-700 rounded-lg p-4 border border-gray-600">
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="text-white font-semibold">{emission.activity_description}</h4>
                      <p className="text-gray-400 text-sm">
                        {emission.emission_type} • {emission.scope} • {emission.data_quality}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-green-400 font-semibold">
                        {(emission.co2_equivalent_kg / 1000).toFixed(2)} tonnes CO₂eq
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Add Supplier Modal */}
      {showAddSupplier && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-2xl border border-gray-700 max-h-96 overflow-y-auto">
            <h3 className="text-lg font-semibold text-white mb-4">Add New Supplier</h3>
            <form onSubmit={handleAddSupplier} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Supplier Name</label>
                  <input
                    type="text"
                    value={newSupplier.supplier_name}
                    onChange={(e) => setNewSupplier(prev => ({ ...prev, supplier_name: e.target.value }))}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Industry</label>
                  <input
                    type="text"
                    value={newSupplier.industry}
                    onChange={(e) => setNewSupplier(prev => ({ ...prev, industry: e.target.value }))}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Location</label>
                  <input
                    type="text"
                    value={newSupplier.location}
                    onChange={(e) => setNewSupplier(prev => ({ ...prev, location: e.target.value }))}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Contact Email</label>
                  <input
                    type="email"
                    value={newSupplier.contact_email}
                    onChange={(e) => setNewSupplier(prev => ({ ...prev, contact_email: e.target.value }))}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Annual Revenue ($)</label>
                  <input
                    type="number"
                    value={newSupplier.annual_revenue}
                    onChange={(e) => setNewSupplier(prev => ({ ...prev, annual_revenue: e.target.value }))}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Employee Count</label>
                  <input
                    type="number"
                    value={newSupplier.employee_count}
                    onChange={(e) => setNewSupplier(prev => ({ ...prev, employee_count: e.target.value }))}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Carbon Score (0-100)</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    step="0.1"
                    value={newSupplier.carbon_score}
                    onChange={(e) => setNewSupplier(prev => ({ ...prev, carbon_score: e.target.value }))}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Partnership Level</label>
                  <select
                    value={newSupplier.partnership_level}
                    onChange={(e) => setNewSupplier(prev => ({ ...prev, partnership_level: e.target.value }))}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                  >
                    <option value="basic">Basic</option>
                    <option value="preferred">Preferred</option>
                    <option value="strategic">Strategic</option>
                  </select>
                </div>
              </div>
              <div className="flex space-x-4 pt-4">
                <button
                  type="button"
                  onClick={() => setShowAddSupplier(false)}
                  className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-2 rounded-md"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 rounded-md"
                >
                  Add Supplier
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Emission Modal */}
      {showAddEmission && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-4">Add Emission Data</h3>
            <form onSubmit={handleAddEmission} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Supplier</label>
                <select
                  value={newEmission.supplier_id}
                  onChange={(e) => setNewEmission(prev => ({ ...prev, supplier_id: e.target.value }))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                  required
                >
                  <option value="">Select Supplier</option>
                  {suppliers.map((supplier) => (
                    <option key={supplier.id} value={supplier.id}>
                      {supplier.supplier_name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Activity Description</label>
                <input
                  type="text"
                  value={newEmission.activity_description}
                  onChange={(e) => setNewEmission(prev => ({ ...prev, activity_description: e.target.value }))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                  placeholder="e.g., Raw material transportation"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Emission Type</label>
                  <select
                    value={newEmission.emission_type}
                    onChange={(e) => setNewEmission(prev => ({ ...prev, emission_type: e.target.value }))}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                  >
                    <option value="upstream">Upstream</option>
                    <option value="downstream">Downstream</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Scope</label>
                  <select
                    value={newEmission.scope}
                    onChange={(e) => setNewEmission(prev => ({ ...prev, scope: e.target.value }))}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                  >
                    <option value="scope_1">Scope 1</option>
                    <option value="scope_2">Scope 2</option>
                    <option value="scope_3">Scope 3</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">CO₂ Equivalent (kg)</label>
                <input
                  type="number"
                  step="0.01"
                  value={newEmission.co2_equivalent_kg}
                  onChange={(e) => setNewEmission(prev => ({ ...prev, co2_equivalent_kg: e.target.value }))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Data Quality</label>
                <select
                  value={newEmission.data_quality}
                  onChange={(e) => setNewEmission(prev => ({ ...prev, data_quality: e.target.value }))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                >
                  <option value="estimated">Estimated</option>
                  <option value="calculated">Calculated</option>
                  <option value="measured">Measured</option>
                </select>
              </div>
              <div className="flex space-x-4 pt-4">
                <button
                  type="button"
                  onClick={() => setShowAddEmission(false)}
                  className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-2 rounded-md"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-md"
                >
                  Add Emission
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

const MetricCard = ({ title, value, subtitle, icon, color }) => {
  const colorClasses = {
    blue: 'border-blue-500 text-blue-400',
    green: 'border-green-500 text-green-400',
    purple: 'border-purple-500 text-purple-400',
    orange: 'border-orange-500 text-orange-400'
  };

  return (
    <div className={`bg-gray-800 rounded-lg p-6 border-l-4 ${colorClasses[color]}`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-2xl">{icon}</span>
      </div>
      <div className="text-2xl font-bold text-white mb-1">{value}</div>
      <div className="text-sm text-gray-400">{subtitle}</div>
    </div>
  );
};

const StatusBadge = ({ status }) => {
  const statusClasses = {
    pending: 'bg-yellow-600 text-yellow-100',
    verified: 'bg-green-600 text-green-100',
    flagged: 'bg-red-600 text-red-100'
  };

  return (
    <span className={`px-2 py-1 rounded-full text-xs ${statusClasses[status]}`}>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
};

const PartnershipBadge = ({ level }) => {
  const levelClasses = {
    basic: 'bg-gray-600 text-gray-100',
    preferred: 'bg-blue-600 text-blue-100',
    strategic: 'bg-purple-600 text-purple-100'
  };

  return (
    <span className={`px-2 py-1 rounded-full text-xs ${levelClasses[level]}`}>
      {level.charAt(0).toUpperCase() + level.slice(1)}
    </span>
  );
};

export default SupplyChainVisibility;
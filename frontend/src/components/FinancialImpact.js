import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const FinancialImpact = ({ company }) => {
  const [financialData, setFinancialData] = useState(null);
  const [initiatives, setInitiatives] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddInitiative, setShowAddInitiative] = useState(false);

  // Form for adding new initiative
  const [newInitiative, setNewInitiative] = useState({
    initiative_name: '',
    description: '',
    implementation_cost: '',
    annual_savings: '',
    annual_co2_reduction: '',
    implementation_date: new Date().toISOString().split('T')[0],
    status: 'planned'
  });

  useEffect(() => {
    fetchFinancialData();
    fetchInitiatives();
  }, [company.id]);

  const fetchFinancialData = async () => {
    try {
      const response = await fetch(`${API}/companies/${company.id}/financial-impact`);
      if (response.ok) {
        const data = await response.json();
        setFinancialData(data);
      }
    } catch (error) {
      console.error('Error fetching financial data:', error);
    }
    setLoading(false);
  };

  const fetchInitiatives = async () => {
    try {
      const response = await fetch(`${API}/companies/${company.id}/initiatives`);
      if (response.ok) {
        const data = await response.json();
        setInitiatives(data);
      }
    } catch (error) {
      console.error('Error fetching initiatives:', error);
    }
  };

  const handleAddInitiative = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API}/companies/${company.id}/initiatives`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company_id: company.id,
          initiative_name: newInitiative.initiative_name,
          description: newInitiative.description,
          implementation_cost: parseFloat(newInitiative.implementation_cost),
          annual_savings: parseFloat(newInitiative.annual_savings),
          annual_co2_reduction: parseFloat(newInitiative.annual_co2_reduction),
          roi_percentage: ((parseFloat(newInitiative.annual_savings) / parseFloat(newInitiative.implementation_cost)) * 100),
          implementation_date: new Date(newInitiative.implementation_date).toISOString(),
          status: newInitiative.status
        })
      });

      if (response.ok) {
        setShowAddInitiative(false);
        setNewInitiative({
          initiative_name: '',
          description: '',
          implementation_cost: '',
          annual_savings: '',
          annual_co2_reduction: '',
          implementation_date: new Date().toISOString().split('T')[0],
          status: 'planned'
        });
        fetchInitiatives();
        fetchFinancialData(); // Refresh financial data
      } else {
        alert('Failed to add initiative');
      }
    } catch (error) {
      console.error('Error adding initiative:', error);
      alert('Error adding initiative');
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
  const roiData = initiatives.map(init => ({
    name: init.initiative_name.substring(0, 20) + (init.initiative_name.length > 20 ? '...' : ''),
    roi: init.roi_percentage,
    cost: init.implementation_cost,
    savings: init.annual_savings
  }));

  const statusData = [
    { name: 'Planned', value: initiatives.filter(i => i.status === 'planned').length, color: '#f59e0b' },
    { name: 'In Progress', value: initiatives.filter(i => i.status === 'in_progress').length, color: '#3b82f6' },
    { name: 'Completed', value: initiatives.filter(i => i.status === 'completed').length, color: '#10b981' }
  ];

  const cumulativeSavings = initiatives.reduce((acc, init, index) => {
    const previousSavings = acc[index - 1]?.total || 0;
    acc.push({
      month: `Month ${index + 1}`,
      total: previousSavings + init.annual_savings
    });
    return acc;
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 p-8">
      {/* Header */}
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">
            💰 Financial Impact Analysis
          </h1>
          <p className="text-gray-400">
            Track the financial benefits of {company.name}'s carbon reduction initiatives
          </p>
        </div>
        <button
          onClick={() => setShowAddInitiative(true)}
          className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md font-medium"
        >
          + Add Initiative
        </button>
      </div>

      {/* Key Financial Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title="Total Investment"
          value={`$${(financialData?.total_carbon_investment || 0).toLocaleString()}`}
          subtitle="In carbon initiatives"
          icon="💼"
          color="blue"
        />
        <MetricCard
          title="Annual Savings"
          value={`$${(financialData?.annual_cost_savings || 0).toLocaleString()}`}
          subtitle="Cost reductions"
          icon="💰"
          color="green"
        />
        <MetricCard
          title="Annual ROI"
          value={`${(financialData?.annual_roi_percentage || 0).toFixed(1)}%`}
          subtitle="Return on investment"
          icon="📈"
          color="purple"
        />
        <MetricCard
          title="Payback Period"
          value={`${(financialData?.payback_period_years || 0).toFixed(1)} years`}
          subtitle="Investment recovery"
          icon="⏰"
          color="orange"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* ROI by Initiative */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4">ROI by Initiative</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={roiData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
                formatter={(value, name) => [
                  name === 'roi' ? `${value.toFixed(1)}%` : `$${value.toLocaleString()}`,
                  name === 'roi' ? 'ROI' : name === 'cost' ? 'Cost' : 'Savings'
                ]}
              />
              <Bar dataKey="roi" fill="#22c55e" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Initiative Status Distribution */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4">Initiative Status</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={statusData}
                cx="50%"
                cy="50%"
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}
              >
                {statusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Initiative List */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4">Carbon Reduction Initiatives</h3>
        {initiatives.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-gray-400 border-b border-gray-700">
                  <th className="text-left py-3 px-4">Initiative</th>
                  <th className="text-left py-3 px-4">Status</th>
                  <th className="text-right py-3 px-4">Investment</th>
                  <th className="text-right py-3 px-4">Annual Savings</th>
                  <th className="text-right py-3 px-4">CO₂ Reduction</th>
                  <th className="text-right py-3 px-4">ROI</th>
                </tr>
              </thead>
              <tbody>
                {initiatives.map((initiative) => (
                  <tr key={initiative.id} className="border-b border-gray-700 hover:bg-gray-700">
                    <td className="py-3 px-4">
                      <div className="text-white font-medium">{initiative.initiative_name}</div>
                      <div className="text-gray-400 text-xs">{initiative.description}</div>
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={initiative.status} />
                    </td>
                    <td className="py-3 px-4 text-right text-white">
                      ${initiative.implementation_cost.toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-right text-green-400">
                      ${initiative.annual_savings.toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-right text-white">
                      {(initiative.annual_co2_reduction / 1000).toFixed(1)}t CO₂
                    </td>
                    <td className="py-3 px-4 text-right text-white">
                      {initiative.roi_percentage.toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center text-gray-400 py-8">
            <div className="text-4xl mb-4">📊</div>
            <div>No initiatives added yet</div>
            <button
              onClick={() => setShowAddInitiative(true)}
              className="mt-4 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md"
            >
              Add Your First Initiative
            </button>
          </div>
        )}
      </div>

      {/* Add Initiative Modal */}
      {showAddInitiative && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-4">Add Carbon Reduction Initiative</h3>
            <form onSubmit={handleAddInitiative} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Initiative Name</label>
                <input
                  type="text"
                  value={newInitiative.initiative_name}
                  onChange={(e) => setNewInitiative(prev => ({ ...prev, initiative_name: e.target.value }))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Description</label>
                <textarea
                  value={newInitiative.description}
                  onChange={(e) => setNewInitiative(prev => ({ ...prev, description: e.target.value }))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                  rows="3"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Implementation Cost ($)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={newInitiative.implementation_cost}
                    onChange={(e) => setNewInitiative(prev => ({ ...prev, implementation_cost: e.target.value }))}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Annual Savings ($)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={newInitiative.annual_savings}
                    onChange={(e) => setNewInitiative(prev => ({ ...prev, annual_savings: e.target.value }))}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                    required
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Annual CO₂ Reduction (kg)</label>
                <input
                  type="number"
                  step="0.01"
                  value={newInitiative.annual_co2_reduction}
                  onChange={(e) => setNewInitiative(prev => ({ ...prev, annual_co2_reduction: e.target.value }))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Implementation Date</label>
                  <input
                    type="date"
                    value={newInitiative.implementation_date}
                    onChange={(e) => setNewInitiative(prev => ({ ...prev, implementation_date: e.target.value }))}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Status</label>
                  <select
                    value={newInitiative.status}
                    onChange={(e) => setNewInitiative(prev => ({ ...prev, status: e.target.value }))}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                  >
                    <option value="planned">Planned</option>
                    <option value="in_progress">In Progress</option>
                    <option value="completed">Completed</option>
                  </select>
                </div>
              </div>
              <div className="flex space-x-4 pt-4">
                <button
                  type="button"
                  onClick={() => setShowAddInitiative(false)}
                  className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-2 rounded-md"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 rounded-md"
                >
                  Add Initiative
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
    planned: 'bg-yellow-600 text-yellow-100',
    in_progress: 'bg-blue-600 text-blue-100',
    completed: 'bg-green-600 text-green-100'
  };

  const statusLabels = {
    planned: 'Planned',
    in_progress: 'In Progress',
    completed: 'Completed'
  };

  return (
    <span className={`px-2 py-1 rounded-full text-xs ${statusClasses[status]}`}>
      {statusLabels[status]}
    </span>
  );
};

export default FinancialImpact;
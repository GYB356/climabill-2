import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar } from 'recharts';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = ({ company }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, [company.id]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API}/companies/${company.id}/dashboard`);
      
      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
      } else {
        setError('Failed to load dashboard data');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    }
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-green-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 p-8">
        <div className="text-center">
          <div className="text-red-400 text-lg mb-4">{error}</div>
          <button
            onClick={fetchDashboardData}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Prepare chart data
  const emissionsScopeData = dashboardData?.total_emissions ? [
    { name: 'Scope 1', value: dashboardData.total_emissions.scope_1 / 1000, color: '#ef4444' },
    { name: 'Scope 2', value: dashboardData.total_emissions.scope_2 / 1000, color: '#f97316' },
    { name: 'Scope 3', value: dashboardData.total_emissions.scope_3 / 1000, color: '#22c55e' }
  ] : [];

  const trendData = dashboardData?.emissions_trend?.map(item => ({
    month: `${item.month}/${item.year}`,
    emissions: item.emissions_tonnes
  })) || [];

  const topSourcesData = dashboardData?.top_emission_sources?.map(source => ({
    name: source.source_name,
    emissions: source.total_emissions / 1000
  })) || [];

  const financialImpact = dashboardData?.financial_impact || {};

  return (
    <div className="min-h-screen bg-gray-900 p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">
          Carbon Intelligence Dashboard
        </h1>
        <p className="text-gray-400">
          Real-time insights into {company.name}'s carbon footprint and financial impact
        </p>
      </div>

      {/* Key Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title="Total Emissions"
          value={`${((dashboardData?.total_emissions?.scope_1 + dashboardData?.total_emissions?.scope_2 + dashboardData?.total_emissions?.scope_3) / 1000 || 0).toFixed(1)} tonnes`}
          subtitle="CO₂ equivalent"
          icon="🌍"
          trend="+5.2%"
          trendUp={false}
        />
        <MetricCard
          title="Carbon Cost"
          value={`$${(financialImpact.current_annual_carbon_cost || 0).toLocaleString()}`}
          subtitle="Annual impact"
          icon="💰"
          trend="+$2.5K"
          trendUp={false}
        />
        <MetricCard
          title="Savings Potential"
          value={`$${(financialImpact.annual_cost_savings || 0).toLocaleString()}`}
          subtitle="From initiatives"
          icon="💡"
          trend="+12.3%"
          trendUp={true}
        />
        <MetricCard
          title="ROI"
          value={`${(financialImpact.annual_roi_percentage || 0).toFixed(1)}%`}
          subtitle="On green investments"
          icon="📈"
          trend="+8.1%"
          trendUp={true}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Emissions by Scope */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4">Emissions by Scope</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={emissionsScopeData}
                cx="50%"
                cy="50%"
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
                label={({ name, value }) => `${name}: ${value.toFixed(1)}t`}
              >
                {emissionsScopeData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => `${value.toFixed(1)} tonnes`} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Emissions Trend */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4">Emissions Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="month" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
                formatter={(value) => [`${value.toFixed(1)} tonnes`, 'Emissions']}
              />
              <Line type="monotone" dataKey="emissions" stroke="#22c55e" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Emission Sources */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4">Top Emission Sources</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={topSourcesData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
                formatter={(value) => [`${value.toFixed(1)} tonnes`, 'Emissions']}
              />
              <Bar dataKey="emissions" fill="#22c55e" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Quick Actions */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4">Quick Actions</h3>
          <div className="space-y-4">
            <ActionCard
              title="Ask AI Assistant"
              description="Get insights about your carbon data"
              icon="🤖"
              action="Chat with AI"
              href="/ai-chat"
            />
            <ActionCard
              title="Add Emissions Data"
              description="Track new emission sources"
              icon="📊"
              action="Add Data"
              href="/emissions"
            />
            <ActionCard
              title="View Financial Impact"
              description="See ROI of green initiatives"
              icon="💰"
              action="View Report"
              href="/financial-impact"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

const MetricCard = ({ title, value, subtitle, icon, trend, trendUp }) => (
  <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
    <div className="flex items-center justify-between mb-2">
      <span className="text-2xl">{icon}</span>
      <span className={`text-sm ${trendUp ? 'text-green-400' : 'text-red-400'}`}>
        {trend}
      </span>
    </div>
    <div className="text-2xl font-bold text-white mb-1">{value}</div>
    <div className="text-sm text-gray-400">{subtitle}</div>
  </div>
);

const ActionCard = ({ title, description, icon, action, href }) => (
  <div className="flex items-center p-4 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors cursor-pointer">
    <span className="text-2xl mr-4">{icon}</span>
    <div className="flex-1">
      <div className="font-medium text-white">{title}</div>
      <div className="text-sm text-gray-400">{description}</div>
    </div>
    <a 
      href={href} 
      className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm"
    >
      {action}
    </a>
  </div>
);

export default Dashboard;
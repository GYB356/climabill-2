import React, { useState } from 'react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CompanySetup = ({ onCompanyCreated }) => {
  const [formData, setFormData] = useState({
    name: '',
    industry: 'saas',
    employee_count: '',
    annual_revenue: '',
    headquarters_location: '',
    compliance_standards: []
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const industries = [
    { value: 'saas', label: 'SaaS / Technology' },
    { value: 'fintech', label: 'Fintech' },
    { value: 'ecommerce', label: 'E-commerce' },
    { value: 'manufacturing', label: 'Manufacturing' },
    { value: 'healthcare', label: 'Healthcare' },
    { value: 'consulting', label: 'Consulting' }
  ];

  const complianceStandards = [
    { value: 'eu_csrd', label: 'EU CSRD (Corporate Sustainability Reporting Directive)' },
    { value: 'sec_climate', label: 'SEC Climate Disclosure Rules' },
    { value: 'ghg_protocol', label: 'GHG Protocol' },
    { value: 'tcfd', label: 'TCFD (Task Force on Climate-related Financial Disclosures)' }
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleComplianceChange = (standard) => {
    setFormData(prev => ({
      ...prev,
      compliance_standards: prev.compliance_standards.includes(standard)
        ? prev.compliance_standards.filter(s => s !== standard)
        : [...prev.compliance_standards, standard]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API}/companies`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          employee_count: parseInt(formData.employee_count),
          annual_revenue: parseFloat(formData.annual_revenue)
        })
      });

      if (response.ok) {
        const company = await response.json();
        onCompanyCreated(company);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to create company');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <span className="text-4xl">🌍</span>
            <span className="text-3xl font-bold text-green-400">ClimaBill</span>
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">Welcome to ClimaBill</h2>
          <p className="text-gray-400">Set up your company profile to start tracking carbon emissions and financial impact</p>
        </div>

        {/* Setup Form */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Company Name */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Company Name
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="Enter your company name"
              />
            </div>

            {/* Industry */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Industry
              </label>
              <select
                name="industry"
                value={formData.industry}
                onChange={handleInputChange}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                {industries.map(industry => (
                  <option key={industry.value} value={industry.value}>
                    {industry.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Employee Count */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Number of Employees
              </label>
              <input
                type="number"
                name="employee_count"
                value={formData.employee_count}
                onChange={handleInputChange}
                required
                min="1"
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="50"
              />
            </div>

            {/* Annual Revenue */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Annual Revenue (USD)
              </label>
              <input
                type="number"
                name="annual_revenue"
                value={formData.annual_revenue}
                onChange={handleInputChange}
                required
                min="0"
                step="0.01"
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="1000000"
              />
            </div>

            {/* Location */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Headquarters Location
              </label>
              <input
                type="text"
                name="headquarters_location"
                value={formData.headquarters_location}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="San Francisco, CA"
              />
            </div>

            {/* Compliance Standards */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Compliance Standards (Optional)
              </label>
              <div className="space-y-2">
                {complianceStandards.map(standard => (
                  <label key={standard.value} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.compliance_standards.includes(standard.value)}
                      onChange={() => handleComplianceChange(standard.value)}
                      className="mr-2 rounded border-gray-600 bg-gray-700 text-green-500 focus:ring-green-500"
                    />
                    <span className="text-sm text-gray-300">{standard.label}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="text-red-400 text-sm mt-2">
                {error}
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white font-medium py-2 px-4 rounded-md transition-colors"
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Creating Company...
                </div>
              ) : (
                'Create Company Profile'
              )}
            </button>
          </form>
        </div>

        {/* Features Preview */}
        <div className="mt-8 text-center text-gray-400 text-sm">
          <p className="mb-2">🚀 Get started with ClimaBill's features:</p>
          <div className="flex justify-center space-x-4 text-xs">
            <span>🤖 AI Carbon Intelligence</span>
            <span>📊 Real-time Analytics</span>
            <span>💰 Financial Impact</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompanySetup;
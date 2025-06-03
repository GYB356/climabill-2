import React, { useState } from 'react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Auth = ({ onAuthSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [loginData, setLoginData] = useState({
    email: '',
    password: ''
  });

  const [signupData, setSignupData] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    company_name: '',
    industry: 'saas',
    employee_count: '',
    annual_revenue: '',
    headquarters_location: '',
    compliance_standards: []
  });

  const industries = [
    { value: 'saas', label: 'SaaS / Technology' },
    { value: 'fintech', label: 'Fintech' },
    { value: 'ecommerce', label: 'E-commerce' },
    { value: 'manufacturing', label: 'Manufacturing' },
    { value: 'healthcare', label: 'Healthcare' },
    { value: 'consulting', label: 'Consulting' }
  ];

  const complianceStandards = [
    { value: 'eu_csrd', label: 'EU CSRD' },
    { value: 'sec_climate', label: 'SEC Climate Disclosure' },
    { value: 'ghg_protocol', label: 'GHG Protocol' },
    { value: 'tcfd', label: 'TCFD' }
  ];

  const handleLoginChange = (e) => {
    setLoginData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const handleSignupChange = (e) => {
    setSignupData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const handleComplianceChange = (standard) => {
    setSignupData(prev => ({
      ...prev,
      compliance_standards: prev.compliance_standards.includes(standard)
        ? prev.compliance_standards.filter(s => s !== standard)
        : [...prev.compliance_standards, standard]
    }));
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API}/auth/login?email=${encodeURIComponent(loginData.email)}&password=${encodeURIComponent(loginData.password)}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (response.ok) {
        const result = await response.json();
        // Store auth data
        localStorage.setItem('climabill_token', result.access_token);
        localStorage.setItem('climabill_user', JSON.stringify(result.user));
        localStorage.setItem('climabill_tenant', JSON.stringify(result.tenant));
        onAuthSuccess(result);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Login failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    }

    setLoading(false);
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...signupData,
          employee_count: parseInt(signupData.employee_count),
          annual_revenue: parseFloat(signupData.annual_revenue)
        })
      });

      if (response.ok) {
        const result = await response.json();
        // Store auth data
        localStorage.setItem('climabill_token', result.access_token);
        localStorage.setItem('climabill_user', JSON.stringify(result.user));
        localStorage.setItem('climabill_tenant', JSON.stringify(result.tenant));
        localStorage.setItem('climabill_company_id', result.company.id);
        onAuthSuccess(result);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Registration failed');
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
          <h2 className="text-2xl font-bold text-white mb-2">
            {isLogin ? 'Welcome Back' : 'Get Started'}
          </h2>
          <p className="text-gray-400">
            {isLogin 
              ? 'Sign in to your ClimaBill account' 
              : 'Create your account and start tracking carbon emissions'
            }
          </p>
        </div>

        {/* Auth Form */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          {/* Tab Switcher */}
          <div className="flex mb-6 border-b border-gray-600">
            <button
              className={`flex-1 py-2 text-center ${
                isLogin ? 'text-green-400 border-b-2 border-green-400' : 'text-gray-400'
              }`}
              onClick={() => {
                setIsLogin(true);
                setError('');
              }}
            >
              Sign In
            </button>
            <button
              className={`flex-1 py-2 text-center ${
                !isLogin ? 'text-green-400 border-b-2 border-green-400' : 'text-gray-400'
              }`}
              onClick={() => {
                setIsLogin(false);
                setError('');
              }}
            >
              Sign Up
            </button>
          </div>

          {/* Login Form */}
          {isLogin ? (
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  name="email"
                  value={loginData.email}
                  onChange={handleLoginChange}
                  required
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="Enter your email"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Password
                </label>
                <input
                  type="password"
                  name="password"
                  value={loginData.password}
                  onChange={handleLoginChange}
                  required
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="Enter your password"
                />
              </div>

              {error && (
                <div className="text-red-400 text-sm mt-2">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white font-medium py-2 px-4 rounded-md transition-colors"
              >
                {loading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Signing In...
                  </div>
                ) : (
                  'Sign In'
                )}
              </button>
            </form>
          ) : (
            /* Signup Form */
            <form onSubmit={handleSignup} className="space-y-4 max-h-96 overflow-y-auto">
              {/* Personal Info */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    First Name
                  </label>
                  <input
                    type="text"
                    name="first_name"
                    value={signupData.first_name}
                    onChange={handleSignupChange}
                    required
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="John"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Last Name
                  </label>
                  <input
                    type="text"
                    name="last_name"
                    value={signupData.last_name}
                    onChange={handleSignupChange}
                    required
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="Doe"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  name="email"
                  value={signupData.email}
                  onChange={handleSignupChange}
                  required
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="john@company.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Password
                </label>
                <input
                  type="password"
                  name="password"
                  value={signupData.password}
                  onChange={handleSignupChange}
                  required
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="Enter a strong password"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Company Name
                </label>
                <input
                  type="text"
                  name="company_name"
                  value={signupData.company_name}
                  onChange={handleSignupChange}
                  required
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="Your Company Inc."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Industry
                </label>
                <select
                  name="industry"
                  value={signupData.industry}
                  onChange={handleSignupChange}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  {industries.map(industry => (
                    <option key={industry.value} value={industry.value}>
                      {industry.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Employees
                  </label>
                  <input
                    type="number"
                    name="employee_count"
                    value={signupData.employee_count}
                    onChange={handleSignupChange}
                    required
                    min="1"
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="50"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Annual Revenue
                  </label>
                  <input
                    type="number"
                    name="annual_revenue"
                    value={signupData.annual_revenue}
                    onChange={handleSignupChange}
                    required
                    min="0"
                    step="0.01"
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="1000000"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Location
                </label>
                <input
                  type="text"
                  name="headquarters_location"
                  value={signupData.headquarters_location}
                  onChange={handleSignupChange}
                  required
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="San Francisco, CA"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Compliance Standards (Optional)
                </label>
                <div className="space-y-2">
                  {complianceStandards.map(standard => (
                    <label key={standard.value} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={signupData.compliance_standards.includes(standard.value)}
                        onChange={() => handleComplianceChange(standard.value)}
                        className="mr-2 rounded border-gray-600 bg-gray-700 text-green-500 focus:ring-green-500"
                      />
                      <span className="text-sm text-gray-300">{standard.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              {error && (
                <div className="text-red-400 text-sm mt-2">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white font-medium py-2 px-4 rounded-md transition-colors"
              >
                {loading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Creating Account...
                  </div>
                ) : (
                  'Create Account'
                )}
              </button>
            </form>
          )}
        </div>

        {/* Sample Credentials for Testing */}
        <div className="mt-6 p-4 bg-gray-800 rounded-lg border border-gray-700">
          <h3 className="text-sm font-medium text-gray-300 mb-2">Test Accounts</h3>
          <div className="text-xs text-gray-400 space-y-1">
            <div>Alpha Tech: admin@alpha-tech.com / admin123</div>
            <div>Beta Manufacturing: admin@beta-manufacturing.com / admin123</div>
          </div>
        </div>

        {/* Features Preview */}
        <div className="mt-6 text-center text-gray-400 text-sm">
          <p className="mb-2">🚀 Enterprise-Ready Carbon Intelligence Platform</p>
          <div className="flex justify-center space-x-4 text-xs">
            <span>🔒 Multi-Tenant</span>
            <span>🤖 AI Analytics</span>
            <span>📊 Real-time Data</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Auth;
import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navbar = ({ company, onCompanyChange }) => {
  const location = useLocation();

  const handleNewCompany = () => {
    localStorage.removeItem('climabill_company_id');
    onCompanyChange(null);
  };

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/ai-chat', label: 'AI Assistant', icon: '🤖' },
    { path: '/emissions', label: 'Emissions', icon: '🌱' },
    { path: '/financial-impact', label: 'Financial Impact', icon: '💰' },
    { path: '/marketplace', label: 'Carbon Marketplace', icon: '⛓️' },
    { path: '/supply-chain', label: 'Supply Chain', icon: '🔗' },
  ];

  return (
    <nav className="fixed top-0 left-0 right-0 bg-gray-800 border-b border-gray-700 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Company */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <span className="text-2xl">🌍</span>
              <span className="text-xl font-bold text-green-400">ClimaBill</span>
            </div>
            {company && (
              <div className="hidden md:block text-sm text-gray-300">
                {company.name} • {company.industry}
              </div>
            )}
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-4">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  location.pathname === item.path
                    ? 'bg-green-600 text-white'
                    : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                }`}
              >
                <span className="mr-2">{item.icon}</span>
                {item.label}
              </Link>
            ))}
          </div>

          {/* Company Actions */}
          <div className="flex items-center space-x-4">
            <button
              onClick={handleNewCompany}
              className="px-3 py-2 rounded-md text-sm font-medium text-gray-300 hover:bg-gray-700 hover:text-white transition-colors"
            >
              Switch Company
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      <div className="md:hidden bg-gray-800 border-t border-gray-700">
        <div className="px-2 pt-2 pb-3 space-y-1">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`block px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                location.pathname === item.path
                  ? 'bg-green-600 text-white'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'
              }`}
            >
              <span className="mr-2">{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Navbar = ({ company, onCompanyChange }) => {
  const location = useLocation();
  const { user, tenant, logout } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);

  const handleLogout = () => {
    logout();
    setShowUserMenu(false);
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

          {/* User Menu */}
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium text-gray-300 hover:bg-gray-700 hover:text-white transition-colors"
            >
              <div className="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                {user?.first_name?.[0]}{user?.last_name?.[0]}
              </div>
              <div className="hidden md:block text-left">
                <div className="text-sm">{user?.first_name} {user?.last_name}</div>
                <div className="text-xs text-gray-400">{tenant?.name}</div>
              </div>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {/* Dropdown Menu */}
            {showUserMenu && (
              <div className="absolute right-0 mt-2 w-56 bg-gray-800 border border-gray-700 rounded-md shadow-lg z-50">
                <div className="py-2">
                  {/* User Info */}
                  <div className="px-4 py-2 border-b border-gray-700">
                    <div className="text-sm font-medium text-white">
                      {user?.first_name} {user?.last_name}
                    </div>
                    <div className="text-xs text-gray-400">{user?.email}</div>
                    <div className="text-xs text-green-400 mt-1">
                      {tenant?.name} • {tenant?.plan}
                    </div>
                  </div>

                  {/* Menu Items */}
                  <button
                    onClick={() => setShowUserMenu(false)}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 hover:text-white"
                  >
                    👤 Profile Settings
                  </button>
                  
                  <button
                    onClick={() => setShowUserMenu(false)}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 hover:text-white"
                  >
                    🔐 Security
                  </button>
                  
                  <button
                    onClick={() => setShowUserMenu(false)}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 hover:text-white"
                  >
                    🏢 Tenant Settings
                  </button>

                  <div className="border-t border-gray-700 mt-2"></div>
                  
                  <button
                    onClick={handleLogout}
                    className="block w-full text-left px-4 py-2 text-sm text-red-400 hover:bg-gray-700 hover:text-red-300"
                  >
                    🚪 Sign Out
                  </button>
                </div>
              </div>
            )}
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
          
          {/* Mobile User Actions */}
          <div className="border-t border-gray-700 pt-2 mt-2">
            <div className="px-3 py-2 text-sm text-gray-400">
              {user?.first_name} {user?.last_name} • {tenant?.name}
            </div>
            <button
              onClick={handleLogout}
              className="block w-full text-left px-3 py-2 text-sm text-red-400 hover:bg-gray-700 hover:text-red-300"
            >
              🚪 Sign Out
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
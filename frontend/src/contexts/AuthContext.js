import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [tenant, setTenant] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  const API = `${BACKEND_URL}/api`;

  // Check for existing auth on mount
  useEffect(() => {
    const savedToken = localStorage.getItem('climabill_token');
    const savedUser = localStorage.getItem('climabill_user');
    const savedTenant = localStorage.getItem('climabill_tenant');

    if (savedToken && savedUser && savedTenant) {
      try {
        setToken(savedToken);
        setUser(JSON.parse(savedUser));
        setTenant(JSON.parse(savedTenant));
      } catch (error) {
        console.error('Error parsing saved auth data:', error);
        logout();
      }
    }
    setLoading(false);
  }, []);

  const login = (authData) => {
    setToken(authData.access_token);
    setUser(authData.user);
    setTenant(authData.tenant);
    
    localStorage.setItem('climabill_token', authData.access_token);
    localStorage.setItem('climabill_user', JSON.stringify(authData.user));
    localStorage.setItem('climabill_tenant', JSON.stringify(authData.tenant));
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    setTenant(null);
    
    localStorage.removeItem('climabill_token');
    localStorage.removeItem('climabill_user');
    localStorage.removeItem('climabill_tenant');
    localStorage.removeItem('climabill_company_id');
  };

  // API helper with automatic token inclusion
  const authenticatedFetch = async (url, options = {}) => {
    if (!token) {
      throw new Error('No authentication token available');
    }

    const defaultHeaders = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    };

    const config = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    };

    const response = await fetch(url, config);

    // If unauthorized, logout user
    if (response.status === 401) {
      logout();
      throw new Error('Authentication expired');
    }

    return response;
  };

  const value = {
    user,
    tenant,
    token,
    loading,
    login,
    logout,
    authenticatedFetch,
    isAuthenticated: !!token,
    API
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
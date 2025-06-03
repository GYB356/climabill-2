import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import Auth from "./components/Auth";
import Dashboard from "./components/Dashboard";
import AIChat from "./components/AIChat";
import EmissionsTracker from "./components/EmissionsTracker";
import FinancialImpact from "./components/FinancialImpact";
import CarbonMarketplace from "./components/CarbonMarketplace";
import SupplyChainVisibility from "./components/SupplyChainVisibility";
import Navbar from "./components/Navbar";

const AppContent = () => {
  const { isAuthenticated, loading, login, authenticatedFetch, API } = useAuth();
  const [currentCompany, setCurrentCompany] = useState(null);
  const [companiesLoading, setCompaniesLoading] = useState(false);

  useEffect(() => {
    if (isAuthenticated && !currentCompany) {
      fetchUserCompanies();
    }
  }, [isAuthenticated]);

  const fetchUserCompanies = async () => {
    try {
      setCompaniesLoading(true);
      const response = await authenticatedFetch(`${API}/companies`);
      
      if (response.ok) {
        const companies = await response.json();
        if (companies.length > 0) {
          // Set the first company as current
          setCurrentCompany(companies[0]);
          localStorage.setItem('climabill_company_id', companies[0].id);
        }
      } else {
        console.error('Failed to fetch companies');
      }
    } catch (error) {
      console.error('Error fetching companies:', error);
    } finally {
      setCompaniesLoading(false);
    }
  };

  const handleAuthSuccess = (authData) => {
    login(authData);
    
    // If registration provides company data, use it
    if (authData.company) {
      setCurrentCompany(authData.company);
      localStorage.setItem('climabill_company_id', authData.company.id);
    }
  };

  if (loading || companiesLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-green-500 mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading ClimaBill...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Auth onAuthSuccess={handleAuthSuccess} />;
  }

  if (!currentCompany) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl mb-4">🏢</div>
          <h2 className="text-2xl font-bold text-white mb-2">No Companies Found</h2>
          <p className="text-gray-400 mb-4">
            It looks like you don't have any companies set up yet.
          </p>
          <button
            onClick={fetchUserCompanies}
            className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-md transition-colors"
          >
            Refresh
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="App bg-gray-900 min-h-screen text-white">
      <BrowserRouter>
        <Navbar company={currentCompany} onCompanyChange={setCurrentCompany} />
        <div className="pt-16">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route 
              path="/dashboard" 
              element={<Dashboard company={currentCompany} />} 
            />
            <Route 
              path="/ai-chat" 
              element={<AIChat company={currentCompany} />} 
            />
            <Route 
              path="/emissions" 
              element={<EmissionsTracker company={currentCompany} />} 
            />
            <Route 
              path="/financial-impact" 
              element={<FinancialImpact company={currentCompany} />} 
            />
            <Route 
              path="/marketplace" 
              element={<CarbonMarketplace company={currentCompany} />} 
            />
            <Route 
              path="/supply-chain" 
              element={<SupplyChainVisibility company={currentCompany} />} 
            />
          </Routes>
        </div>
      </BrowserRouter>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
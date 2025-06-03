import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Dashboard from "./components/Dashboard";
import AIChat from "./components/AIChat";
import EmissionsTracker from "./components/EmissionsTracker";
import FinancialImpact from "./components/FinancialImpact";
import Navbar from "./components/Navbar";
import CompanySetup from "./components/CompanySetup";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [currentCompany, setCurrentCompany] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if we have a company stored or need to create one
    const savedCompanyId = localStorage.getItem('climabill_company_id');
    if (savedCompanyId) {
      fetchCompany(savedCompanyId);
    } else {
      setLoading(false);
    }
  }, []);

  const fetchCompany = async (companyId) => {
    try {
      const response = await fetch(`${API}/companies/${companyId}`);
      if (response.ok) {
        const company = await response.json();
        setCurrentCompany(company);
      } else {
        localStorage.removeItem('climabill_company_id');
      }
    } catch (error) {
      console.error('Error fetching company:', error);
      localStorage.removeItem('climabill_company_id');
    }
    setLoading(false);
  };

  const handleCompanyCreated = (company) => {
    setCurrentCompany(company);
    localStorage.setItem('climabill_company_id', company.id);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-green-500"></div>
      </div>
    );
  }

  if (!currentCompany) {
    return <CompanySetup onCompanyCreated={handleCompanyCreated} />;
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
          </Routes>
        </div>
      </BrowserRouter>
    </div>
  );
}

export default App;
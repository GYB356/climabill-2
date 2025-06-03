import React, { useState, useEffect } from 'react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CarbonMarketplace = ({ company }) => {
  const [projects, setProjects] = useState([]);
  const [certificates, setCertificates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('marketplace');
  const [selectedProject, setSelectedProject] = useState(null);
  const [purchaseAmount, setPurchaseAmount] = useState(1);
  const [filters, setFilters] = useState({
    project_type: '',
    max_price: '',
    min_rating: ''
  });

  useEffect(() => {
    fetchMarketplaceData();
    fetchCertificates();
  }, [company.id]);

  const fetchMarketplaceData = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.project_type) params.append('project_type', filters.project_type);
      if (filters.max_price) params.append('max_price', filters.max_price);
      if (filters.min_rating) params.append('min_rating', filters.min_rating);

      const response = await fetch(`${API}/marketplace/projects?${params}`);
      if (response.ok) {
        const data = await response.json();
        setProjects(data.projects);
      }
    } catch (error) {
      console.error('Error fetching marketplace data:', error);
    }
    setLoading(false);
  };

  const fetchCertificates = async () => {
    try {
      const response = await fetch(`${API}/companies/${company.id}/certificates`);
      if (response.ok) {
        const data = await response.json();
        setCertificates(data);
      }
    } catch (error) {
      console.error('Error fetching certificates:', error);
    }
  };

  const handlePurchase = async (project) => {
    try {
      const response = await fetch(`${API}/marketplace/purchase`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          listing_id: project.listing_id,
          credits_amount: purchaseAmount,
          company_id: company.id
        })
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Successfully purchased ${purchaseAmount} carbon credits for $${result.total_cost.toFixed(2)}`);
        setSelectedProject(null);
        setPurchaseAmount(1);
        fetchCertificates();
      } else {
        const error = await response.json();
        alert(`Purchase failed: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error purchasing credits:', error);
      alert('Purchase failed. Please try again.');
    }
  };

  const handleRetire = async (certificate, retireAmount, reason) => {
    try {
      const response = await fetch(`${API}/marketplace/retire`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          certificate_id: certificate.certificate_id,
          credits_amount: retireAmount,
          retirement_reason: reason,
          company_id: company.id
        })
      });

      if (response.ok) {
        alert(`Successfully retired ${retireAmount} carbon credits`);
        fetchCertificates();
      } else {
        const error = await response.json();
        alert(`Retirement failed: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error retiring credits:', error);
      alert('Retirement failed. Please try again.');
    }
  };

  const applyFilters = () => {
    fetchMarketplaceData();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-green-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">
          ⛓️ Carbon Offset Marketplace
        </h1>
        <p className="text-gray-400">
          Purchase verified carbon offsets with blockchain transparency for {company.name}
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="mb-8">
        <div className="border-b border-gray-700">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('marketplace')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'marketplace'
                  ? 'border-green-500 text-green-400'
                  : 'border-transparent text-gray-400 hover:text-gray-300'
              }`}
            >
              Marketplace
            </button>
            <button
              onClick={() => setActiveTab('portfolio')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'portfolio'
                  ? 'border-green-500 text-green-400'
                  : 'border-transparent text-gray-400 hover:text-gray-300'
              }`}
            >
              My Portfolio
            </button>
          </nav>
        </div>
      </div>

      {/* Marketplace Tab */}
      {activeTab === 'marketplace' && (
        <div>
          {/* Filters */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-6">
            <h3 className="text-lg font-semibold text-white mb-4">Filter Projects</h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Project Type</label>
                <select
                  value={filters.project_type}
                  onChange={(e) => setFilters(prev => ({ ...prev, project_type: e.target.value }))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                >
                  <option value="">All Types</option>
                  <option value="Forest Conservation">Forest Conservation</option>
                  <option value="Renewable Energy">Renewable Energy</option>
                  <option value="Waste Management">Waste Management</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Max Price ($)</label>
                <input
                  type="number"
                  value={filters.max_price}
                  onChange={(e) => setFilters(prev => ({ ...prev, max_price: e.target.value }))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                  placeholder="50"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Min Rating</label>
                <input
                  type="number"
                  step="0.1"
                  value={filters.min_rating}
                  onChange={(e) => setFilters(prev => ({ ...prev, min_rating: e.target.value }))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                  placeholder="4.0"
                />
              </div>
              <div className="flex items-end">
                <button
                  onClick={applyFilters}
                  className="w-full bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-md"
                >
                  Apply Filters
                </button>
              </div>
            </div>
          </div>

          {/* Projects Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <div key={project.listing_id} className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
                <div className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-white">{project.project_name}</h3>
                    <div className="flex items-center">
                      <span className="text-yellow-400 mr-1">⭐</span>
                      <span className="text-white text-sm">{project.rating}</span>
                    </div>
                  </div>
                  
                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Type:</span>
                      <span className="text-white">{project.project_type}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Location:</span>
                      <span className="text-white">{project.location}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Standard:</span>
                      <span className="text-white">{project.verification_standard}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Available:</span>
                      <span className="text-white">{project.credits_available} credits</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Price:</span>
                      <span className="text-green-400 font-semibold">${project.price_per_credit}/credit</span>
                    </div>
                  </div>

                  <div className="mb-4">
                    <div className="text-xs text-gray-400 mb-2">Additional Benefits:</div>
                    <div className="flex flex-wrap gap-1">
                      {project.additional_benefits.map((benefit, index) => (
                        <span key={index} className="bg-green-600 text-white text-xs px-2 py-1 rounded">
                          {benefit}
                        </span>
                      ))}
                    </div>
                  </div>

                  <button
                    onClick={() => setSelectedProject(project)}
                    className="w-full bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-md transition-colors"
                  >
                    Purchase Credits
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Portfolio Tab */}
      {activeTab === 'portfolio' && (
        <div>
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-4">My Carbon Certificates</h3>
            {certificates.length === 0 ? (
              <div className="text-center text-gray-400 py-8">
                <div className="text-4xl mb-4">📜</div>
                <div>No certificates owned yet</div>
                <div className="text-sm">Purchase carbon offsets to build your portfolio</div>
              </div>
            ) : (
              <div className="space-y-4">
                {certificates.map((cert) => (
                  <div key={cert.id} className="bg-gray-700 rounded-lg p-4 border border-gray-600">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h4 className="text-white font-semibold">{cert.certificate_id}</h4>
                        <p className="text-gray-400 text-sm">Project: {cert.project_id}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-green-400 font-semibold">{cert.credits_amount} credits</div>
                        <div className="text-gray-400 text-sm">${cert.purchase_price.toFixed(2)}</div>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 text-sm mb-3">
                      <div>
                        <span className="text-gray-400">Purchase Date:</span>
                        <div className="text-white">{new Date(cert.purchase_date).toLocaleDateString()}</div>
                      </div>
                      <div>
                        <span className="text-gray-400">Status:</span>
                        <div className={`${cert.retirement_status === 'retired' ? 'text-red-400' : 'text-green-400'}`}>
                          {cert.retirement_status === 'retired' ? 'Retired' : 'Active'}
                        </div>
                      </div>
                    </div>

                    <div className="text-xs text-gray-400 mb-3">
                      <div>Blockchain: {cert.blockchain_address}</div>
                      <div>Transaction: {cert.transaction_hash}</div>
                    </div>

                    {cert.retirement_status === 'active' && (
                      <button
                        onClick={() => {
                          const retireAmount = prompt('How many credits to retire?', cert.credits_amount);
                          const reason = prompt('Retirement reason:', 'Annual carbon neutrality commitment');
                          if (retireAmount && reason) {
                            handleRetire(cert, parseFloat(retireAmount), reason);
                          }
                        }}
                        className="bg-red-600 hover:bg-red-700 text-white py-1 px-3 rounded text-sm"
                      >
                        Retire Credits
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Purchase Modal */}
      {selectedProject && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-4">Purchase Carbon Credits</h3>
            <div className="mb-4">
              <h4 className="text-white font-medium">{selectedProject.project_name}</h4>
              <p className="text-gray-400 text-sm">{selectedProject.project_type} • {selectedProject.location}</p>
            </div>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Number of Credits
              </label>
              <input
                type="number"
                min="1"
                max={selectedProject.credits_available}
                value={purchaseAmount}
                onChange={(e) => setPurchaseAmount(parseInt(e.target.value))}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
              />
            </div>

            <div className="mb-6">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-400">Price per credit:</span>
                <span className="text-white">${selectedProject.price_per_credit}</span>
              </div>
              <div className="flex justify-between text-lg font-semibold">
                <span className="text-white">Total Cost:</span>
                <span className="text-green-400">${(purchaseAmount * selectedProject.price_per_credit).toFixed(2)}</span>
              </div>
            </div>

            <div className="flex space-x-4">
              <button
                onClick={() => setSelectedProject(null)}
                className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-2 rounded-md"
              >
                Cancel
              </button>
              <button
                onClick={() => handlePurchase(selectedProject)}
                className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 rounded-md"
              >
                Purchase
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CarbonMarketplace;
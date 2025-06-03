from web3 import Web3
from eth_account import Account
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel

class BlockchainService:
    """Blockchain service for carbon offset marketplace on Polygon"""
    
    def __init__(self):
        # Polygon Mumbai testnet configuration
        self.polygon_rpc = "https://rpc-mumbai.maticvigil.com/"
        self.w3 = Web3(Web3.HTTPProvider(self.polygon_rpc))
        
        # Smart contract addresses (deployed contracts)
        self.carbon_token_address = "0x742d35Cc6269C7c1e5AEcFd7c7C4c1d5C5E6F7A8"  # Mock address
        self.marketplace_address = "0x841e45Dc7d5AEcFd7c7C4c1d5C5E6F7A8742d35"  # Mock address
        
        # ABI for carbon credit smart contract
        self.carbon_credit_abi = [
            {
                "inputs": [
                    {"internalType": "address", "name": "to", "type": "address"},
                    {"internalType": "uint256", "name": "amount", "type": "uint256"},
                    {"internalType": "string", "name": "projectId", "type": "string"},
                    {"internalType": "string", "name": "metadata", "type": "string"}
                ],
                "name": "mintCarbonCredit",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "uint256", "name": "tokenId", "type": "uint256"},
                    {"internalType": "uint256", "name": "amount", "type": "uint256"}
                ],
                "name": "retireCarbonCredit",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}],
                "name": "getCreditDetails",
                "outputs": [
                    {"internalType": "string", "name": "projectId", "type": "string"},
                    {"internalType": "uint256", "name": "totalAmount", "type": "uint256"},
                    {"internalType": "uint256", "name": "retiredAmount", "type": "uint256"},
                    {"internalType": "string", "name": "metadata", "type": "string"}
                ],
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
        # Marketplace ABI
        self.marketplace_abi = [
            {
                "inputs": [
                    {"internalType": "uint256", "name": "tokenId", "type": "uint256"},
                    {"internalType": "uint256", "name": "amount", "type": "uint256"},
                    {"internalType": "uint256", "name": "pricePerCredit", "type": "uint256"}
                ],
                "name": "listCarbonCredits",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "uint256", "name": "listingId", "type": "uint256"},
                    {"internalType": "uint256", "name": "amount", "type": "uint256"}
                ],
                "name": "purchaseCredits",
                "outputs": [],
                "stateMutability": "payable",
                "type": "function"
            }
        ]

    def get_account_from_private_key(self, private_key: str):
        """Get account from private key"""
        try:
            account = Account.from_key(private_key)
            return account
        except Exception as e:
            raise Exception(f"Invalid private key: {str(e)}")

    def create_carbon_credit_certificate(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a blockchain-verified carbon credit certificate"""
        try:
            # Generate certificate data
            certificate = {
                "id": f"CC-{datetime.utcnow().strftime('%Y%m%d')}-{project_data['project_id']}",
                "project_id": project_data["project_id"],
                "project_name": project_data["project_name"],
                "project_type": project_data["project_type"],
                "location": project_data["location"],
                "credits_amount": project_data["credits_amount"],
                "verification_standard": project_data.get("verification_standard", "VCS"),
                "vintage_year": project_data.get("vintage_year", datetime.utcnow().year),
                "issued_date": datetime.utcnow().isoformat(),
                "blockchain_network": "Polygon",
                "smart_contract_address": self.carbon_token_address,
                "verification_status": "verified",
                "metadata": {
                    "co2_reduction_tonnes": project_data["credits_amount"],
                    "project_developer": project_data.get("developer", "Unknown"),
                    "methodology": project_data.get("methodology", "ACM0001"),
                    "monitoring_period": project_data.get("monitoring_period", "2023-2024"),
                    "additional_benefits": project_data.get("additional_benefits", [])
                }
            }
            
            # In a real implementation, this would mint an NFT on Polygon
            # For demo purposes, we'll simulate the blockchain transaction
            certificate["transaction_hash"] = f"0x{os.urandom(32).hex()}"
            certificate["block_number"] = 12345678
            certificate["gas_used"] = 150000
            
            return certificate
            
        except Exception as e:
            raise Exception(f"Failed to create certificate: {str(e)}")

    def retire_carbon_credits(self, certificate_id: str, amount: float, retirement_reason: str) -> Dict[str, Any]:
        """Retire carbon credits (permanently remove from circulation)"""
        try:
            retirement_record = {
                "retirement_id": f"RET-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "certificate_id": certificate_id,
                "retired_amount": amount,
                "retirement_reason": retirement_reason,
                "retired_by": "ClimaBill User",
                "retirement_date": datetime.utcnow().isoformat(),
                "blockchain_proof": f"0x{os.urandom(32).hex()}",
                "permanent": True,
                "status": "completed"
            }
            
            return retirement_record
            
        except Exception as e:
            raise Exception(f"Failed to retire credits: {str(e)}")

    def verify_offset_authenticity(self, certificate_id: str) -> Dict[str, Any]:
        """Verify the authenticity of carbon offset certificate"""
        try:
            # In real implementation, this would query the blockchain
            verification_result = {
                "certificate_id": certificate_id,
                "is_authentic": True,
                "verification_date": datetime.utcnow().isoformat(),
                "blockchain_verified": True,
                "smart_contract_verified": True,
                "registry_verified": True,
                "double_counting_check": "passed",
                "verification_details": {
                    "registry": "Verra Registry",
                    "verification_body": "SCS Global Services",
                    "last_updated": datetime.utcnow().isoformat(),
                    "verification_score": 95.5
                }
            }
            
            return verification_result
            
        except Exception as e:
            raise Exception(f"Failed to verify authenticity: {str(e)}")

    def get_marketplace_listings(self, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Get available carbon credit listings from marketplace"""
        # Mock marketplace data - in real implementation, query blockchain
        sample_listings = [
            {
                "listing_id": "LIST-001",
                "project_name": "Amazon Rainforest Preservation",
                "project_type": "Forest Conservation",
                "location": "Brazil",
                "credits_available": 1000,
                "price_per_credit": 25.50,
                "verification_standard": "VCS",
                "vintage_year": 2023,
                "seller": "GreenEarth Foundation",
                "rating": 4.8,
                "additional_benefits": ["Biodiversity", "Community Development"],
                "image_url": "https://example.com/amazon-project.jpg"
            },
            {
                "listing_id": "LIST-002", 
                "project_name": "Solar Farm Development",
                "project_type": "Renewable Energy",
                "location": "India",
                "credits_available": 2500,
                "price_per_credit": 18.75,
                "verification_standard": "Gold Standard",
                "vintage_year": 2023,
                "seller": "CleanEnergy Partners",
                "rating": 4.6,
                "additional_benefits": ["Job Creation", "Energy Access"],
                "image_url": "https://example.com/solar-project.jpg"
            },
            {
                "listing_id": "LIST-003",
                "project_name": "Methane Capture Facility",
                "project_type": "Waste Management",
                "location": "California, USA",
                "credits_available": 750,
                "price_per_credit": 32.00,
                "verification_standard": "ACR",
                "vintage_year": 2024,
                "seller": "WasteToEnergy Corp",
                "rating": 4.9,
                "additional_benefits": ["Air Quality", "Waste Reduction"],
                "image_url": "https://example.com/methane-project.jpg"
            }
        ]
        
        # Apply filters if provided
        if filters:
            if "max_price" in filters:
                sample_listings = [l for l in sample_listings if l["price_per_credit"] <= filters["max_price"]]
            if "project_type" in filters:
                sample_listings = [l for l in sample_listings if l["project_type"] == filters["project_type"]]
            if "min_rating" in filters:
                sample_listings = [l for l in sample_listings if l["rating"] >= filters["min_rating"]]
        
        return sample_listings

    def purchase_carbon_credits(self, listing_id: str, amount: int, buyer_address: str) -> Dict[str, Any]:
        """Purchase carbon credits from marketplace"""
        try:
            # Find the listing
            listings = self.get_marketplace_listings()
            listing = next((l for l in listings if l["listing_id"] == listing_id), None)
            
            if not listing:
                raise Exception("Listing not found")
            
            if amount > listing["credits_available"]:
                raise Exception("Insufficient credits available")
            
            total_cost = amount * listing["price_per_credit"]
            
            purchase_record = {
                "purchase_id": f"PUR-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "listing_id": listing_id,
                "project_name": listing["project_name"],
                "buyer_address": buyer_address,
                "credits_purchased": amount,
                "price_per_credit": listing["price_per_credit"],
                "total_cost": total_cost,
                "purchase_date": datetime.utcnow().isoformat(),
                "transaction_hash": f"0x{os.urandom(32).hex()}",
                "status": "completed",
                "certificate_issued": True,
                "blockchain_verified": True
            }
            
            return purchase_record
            
        except Exception as e:
            raise Exception(f"Failed to purchase credits: {str(e)}")

    def get_user_carbon_portfolio(self, user_address: str) -> Dict[str, Any]:
        """Get user's carbon credit portfolio"""
        # Mock user portfolio data
        portfolio = {
            "user_address": user_address,
            "total_credits_owned": 2250,
            "total_credits_retired": 500,
            "total_investment": 47500.00,
            "portfolio_value": 51750.00,
            "credits_by_project": [
                {
                    "project_name": "Amazon Rainforest Preservation",
                    "credits_owned": 1000,
                    "credits_retired": 200,
                    "purchase_price": 25.50,
                    "current_value": 27.25,
                    "certificate_id": "CC-20241203-AMZN-001"
                },
                {
                    "project_name": "Solar Farm Development", 
                    "credits_owned": 1250,
                    "credits_retired": 300,
                    "purchase_price": 18.75,
                    "current_value": 19.50,
                    "certificate_id": "CC-20241203-SOLAR-002"
                }
            ],
            "retirement_history": [
                {
                    "retirement_date": "2024-11-15",
                    "project_name": "Amazon Rainforest Preservation",
                    "credits_retired": 200,
                    "reason": "Annual carbon neutrality commitment"
                },
                {
                    "retirement_date": "2024-10-01",
                    "project_name": "Solar Farm Development",
                    "credits_retired": 300,
                    "reason": "Q3 offset requirements"
                }
            ]
        }
        
        return portfolio
"""
Performance optimization utilities for ClimaBill MVP
"""
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from datetime import datetime
import logging

class PerformanceOptimizer:
    """Database and API performance optimization"""
    
    def __init__(self, db):
        self.db = db
        
    async def create_database_indexes(self):
        """Create indexes for optimal query performance"""
        print("🚀 Creating database indexes for performance...")
        
        try:
            # Companies collection indexes
            await self.db.companies.create_index("id")
            await self.db.companies.create_index("industry")
            print("✅ Companies indexes created")
            
            # Emission records indexes
            await self.db.emission_records.create_index("company_id")
            await self.db.emission_records.create_index([("company_id", 1), ("period_start", -1)])
            await self.db.emission_records.create_index("source_id")
            print("✅ Emission records indexes created")
            
            # Emission sources indexes
            await self.db.emission_sources.create_index("company_id")
            await self.db.emission_sources.create_index("id")
            print("✅ Emission sources indexes created")
            
            # Carbon targets indexes
            await self.db.carbon_targets.create_index("company_id")
            await self.db.carbon_targets.create_index([("company_id", 1), ("target_year", 1)])
            print("✅ Carbon targets indexes created")
            
            # Reduction initiatives indexes
            await self.db.reduction_initiatives.create_index("company_id")
            await self.db.reduction_initiatives.create_index([("company_id", 1), ("status", 1)])
            print("✅ Reduction initiatives indexes created")
            
            # AI queries indexes
            await self.db.ai_queries.create_index("company_id")
            await self.db.ai_queries.create_index([("company_id", 1), ("timestamp", -1)])
            print("✅ AI queries indexes created")
            
            # Suppliers indexes
            await self.db.suppliers.create_index("company_id")
            await self.db.suppliers.create_index([("company_id", 1), ("carbon_score", -1)])
            print("✅ Suppliers indexes created")
            
            # Supply chain emissions indexes
            await self.db.supply_chain_emissions.create_index("company_id")
            await self.db.supply_chain_emissions.create_index("supplier_id")
            print("✅ Supply chain emissions indexes created")
            
            # Carbon certificates indexes
            await self.db.carbon_certificates.create_index("company_id")
            await self.db.carbon_certificates.create_index("certificate_id")
            print("✅ Carbon certificates indexes created")
            
            print("🎉 All performance indexes created successfully!")
            
        except Exception as e:
            print(f"❌ Error creating indexes: {e}")
    
    async def optimize_database_queries(self):
        """Optimize common database queries"""
        print("🔧 Running database optimization...")
        
        # Get collection stats
        collections = [
            "companies", "emission_records", "emission_sources", 
            "carbon_targets", "reduction_initiatives", "ai_queries",
            "suppliers", "supply_chain_emissions", "carbon_certificates"
        ]
        
        for collection_name in collections:
            try:
                collection = getattr(self.db, collection_name)
                stats = await self.db.command("collStats", collection_name)
                count = stats.get("count", 0)
                size = stats.get("size", 0) / 1024 / 1024  # MB
                print(f"  📊 {collection_name}: {count} documents, {size:.2f} MB")
            except Exception as e:
                print(f"  ⚠️ {collection_name}: Collection not found or error: {e}")
        
        print("✅ Database optimization analysis complete")

async def run_performance_optimization():
    """Run all performance optimizations"""
    # Connect to MongoDB
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'climabill_database')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    optimizer = PerformanceOptimizer(db)
    
    await optimizer.create_database_indexes()
    await optimizer.optimize_database_queries()
    
    client.close()
    print("🎯 Performance optimization complete!")

if __name__ == "__main__":
    import os
    os.chdir('/app/backend')
    asyncio.run(run_performance_optimization())
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import asyncio
from typing import Dict, Any, Optional

from config.settings import settings


class MongoDBClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBClient, cls).__new__(cls)
            cls._instance.client = None
            cls._instance.db = None
        return cls._instance
    
    async def connect(self):
        """Initialize connection to MongoDB"""
        if self.client is None:
            try:
                self.client = AsyncIOMotorClient(settings.MONGODB_URL)
                self.db = self.client[settings.DATABASE_NAME]
                
                # Test connection
                await self.client.admin.command('ping')
                print(f"Connected to MongoDB at {settings.MONGODB_URL}")
                
                # Create indexes
                await self._create_indexes()
                
            except ConnectionFailure:
                print(f"Failed to connect to MongoDB at {settings.MONGODB_URL}")
                raise
                
    async def _create_indexes(self):
        """Create database indexes for better performance"""
        # Analyses collection
        await self.db.analyses.create_index("address")
        await self.db.analyses.create_index("analysis_timestamp")
        await self.db.analyses.create_index([("address", 1), ("analysis_timestamp", -1)])
        
        # Contracts collection
        await self.db.contracts.create_index("address", unique=True)
        await self.db.contracts.create_index([("address", 1), ("chain_id", 1)], unique=True)
        
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            
    @property
    def database(self):
        """Get database instance"""
        if self.db is None:
            raise ConnectionError("Database not connected")
        return self.db
        
    def get_collection(self, collection_name: str):
        """Get a specific collection"""
        return self.database[collection_name]

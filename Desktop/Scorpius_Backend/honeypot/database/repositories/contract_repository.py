"""
Contract repository for managing contract data in MongoDB
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pymongo import UpdateOne, ASCENDING, DESCENDING

from database.mongodb_client import MongoDBClient

# Configure logger
logger = logging.getLogger("database.contract_repository")


class ContractRepository:
    """Repository for managing contract data"""
    
    def __init__(self, mongo_client: MongoDBClient):
        """Initialize contract repository with MongoDB client"""
        self.mongo_client = mongo_client
        self.collection_name = "contracts"
        
    @property
    def collection(self):
        """Get MongoDB collection"""
        return self.mongo_client.db[self.collection_name]
    
    async def save_contract(self, contract_data: Dict[str, Any]) -> str:
        """
        Save or update contract data in database
        
        Args:
            contract_data: Contract data to save
            
        Returns:
            ID of saved document
        """
        try:
            # Ensure required fields
            if "address" not in contract_data or "chain_id" not in contract_data:
                raise ValueError("Contract data must include address and chain_id")
            
            # Create filter for upsert
            filter_doc = {
                "address": contract_data["address"].lower(),
                "chain_id": contract_data["chain_id"]
            }
            
            # Add timestamps
            now = datetime.utcnow()
            contract_data["updated_at"] = now
            
            # Perform upsert operation
            result = await self.collection.update_one(
                filter=filter_doc,
                update={
                    "$set": contract_data,
                    "$setOnInsert": {"created_at": now}
                },
                upsert=True
            )
            
            if result.upserted_id:
                logger.info(f"Created new contract: {contract_data['address']} on chain {contract_data['chain_id']}")
                return str(result.upserted_id)
            else:
                logger.info(f"Updated contract: {contract_data['address']} on chain {contract_data['chain_id']}")
                
                # Get document ID
                doc = await self.collection.find_one(filter_doc)
                return str(doc["_id"])
                
        except Exception as e:
            logger.error(f"Error saving contract: {e}", exc_info=True)
            raise
    
    async def get_contract(self, address: str, chain_id: int) -> Optional[Dict[str, Any]]:
        """
        Get contract data from database
        
        Args:
            address: Contract address
            chain_id: Blockchain network ID
            
        Returns:
            Contract data or None if not found
        """
        try:
            result = await self.collection.find_one({
                "address": address.lower(),
                "chain_id": chain_id
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting contract: {e}", exc_info=True)
            return None
    
    async def get_contracts(self, 
                           limit: int = 100, 
                           skip: int = 0, 
                           chain_id: Optional[int] = None,
                           is_token: Optional[bool] = None,
                           sort_by: str = "created_at") -> List[Dict[str, Any]]:
        """
        Get multiple contracts with filtering
        
        Args:
            limit: Maximum number of results
            skip: Number of results to skip
            chain_id: Optional filter by chain ID
            is_token: Optional filter for token contracts
            sort_by: Field to sort by
            
        Returns:
            List of contracts
        """
        try:
            # Build query
            query = {}
            
            if chain_id is not None:
                query["chain_id"] = chain_id
                
            if is_token is not None:
                query["is_token"] = is_token
            
            # Sort direction
            sort_direction = DESCENDING if sort_by in ["created_at", "updated_at"] else ASCENDING
            
            # Execute query
            cursor = self.collection.find(query)
            cursor = cursor.sort(sort_by, sort_direction)
            cursor = cursor.skip(skip).limit(limit)
            
            return await cursor.to_list(length=limit)
            
        except Exception as e:
            logger.error(f"Error getting contracts: {e}", exc_info=True)
            return []
    
    async def count_contracts(self, chain_id: Optional[int] = None) -> int:
        """
        Count contracts in database
        
        Args:
            chain_id: Optional filter by chain ID
            
        Returns:
            Contract count
        """
        try:
            query = {}
            if chain_id is not None:
                query["chain_id"] = chain_id
                
            return await self.collection.count_documents(query)
            
        except Exception as e:
            logger.error(f"Error counting contracts: {e}", exc_info=True)
            return 0
    
    async def update_contract_metadata(self, address: str, chain_id: int, metadata: Dict[str, Any]) -> bool:
        """
        Update contract metadata
        
        Args:
            address: Contract address
            chain_id: Blockchain network ID
            metadata: Metadata fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = await self.collection.update_one(
                {"address": address.lower(), "chain_id": chain_id},
                {"$set": {**metadata, "updated_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating contract metadata: {e}", exc_info=True)
            return False
    
    async def bulk_save_contracts(self, contracts: List[Dict[str, Any]]) -> int:
        """
        Bulk save multiple contracts
        
        Args:
            contracts: List of contract data
            
        Returns:
            Number of contracts saved/updated
        """
        try:
            if not contracts:
                return 0
                
            operations = []
            now = datetime.utcnow()
            
            for contract in contracts:
                if "address" not in contract or "chain_id" not in contract:
                    logger.warning(f"Skipping contract without address or chain_id")
                    continue
                    
                filter_doc = {
                    "address": contract["address"].lower(),
                    "chain_id": contract["chain_id"]
                }
                
                contract["updated_at"] = now
                
                operations.append(
                    UpdateOne(
                        filter=filter_doc,
                        update={
                            "$set": contract,
                            "$setOnInsert": {"created_at": now}
                        },
                        upsert=True
                    )
                )
            
            if not operations:
                return 0
                
            result = await self.collection.bulk_write(operations)
            return result.upserted_count + result.modified_count
            
        except Exception as e:
            logger.error(f"Error in bulk save contracts: {e}", exc_info=True)
            return 0
    
    async def delete_contract(self, address: str, chain_id: int) -> bool:
        """
        Delete a contract from database
        
        Args:
            address: Contract address
            chain_id: Blockchain network ID
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            result = await self.collection.delete_one({
                "address": address.lower(),
                "chain_id": chain_id
            })
            
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting contract: {e}", exc_info=True)
            return False

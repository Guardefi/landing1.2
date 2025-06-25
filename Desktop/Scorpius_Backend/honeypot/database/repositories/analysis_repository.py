import asyncio
from typing import Dict, Any, List, Optional
from bson import ObjectId
from datetime import datetime
import uuid

from database.mongodb_client import MongoDBClient
from models.data_models import AnalysisResponse, AnalysisHistoryItem


class AnalysisRepository:
    def __init__(self):
        self.db_client = MongoDBClient()
        self._ensure_connection()
    
    async def _ensure_connection(self):
        """Ensure database connection is established"""
        if self.db_client.db is None:
            await self.db_client.connect()
    
    async def save_analysis(self, address: str, analysis_result: AnalysisResponse) -> str:
        """Save analysis result to database"""
        await self._ensure_connection()
        
        # Create analysis document
        analysis_id = str(uuid.uuid4())
        analysis_doc = {
            "analysis_id": analysis_id,
            "address": address.lower(),
            "is_honeypot": analysis_result.is_honeypot,
            "confidence": analysis_result.confidence,
            "risk_level": analysis_result.risk_level,
            "detected_techniques": analysis_result.detected_techniques,
            "analysis_timestamp": analysis_result.analysis_timestamp,
            "engine_results": analysis_result.engine_results,
            "transaction_history": analysis_result.transaction_history
        }
        
        # Insert into analyses collection
        await self.db_client.get_collection("analyses").insert_one(analysis_doc)
        
        # Update contract metadata
        await self._update_contract_metadata(address, analysis_result)
        
        return analysis_id
    
    async def _update_contract_metadata(self, address: str, analysis_result: AnalysisResponse):
        """Update contract metadata with latest analysis result"""
        contracts_coll = self.db_client.get_collection("contracts")
        
        update_doc = {
            "$set": {
                "last_analysis": {
                    "is_honeypot": analysis_result.is_honeypot,
                    "confidence": analysis_result.confidence,
                    "risk_level": analysis_result.risk_level,
                    "analysis_timestamp": analysis_result.analysis_timestamp
                }
            },
            "$inc": {"analysis_count": 1}
        }
        
        await contracts_coll.update_one(
            {"address": address.lower()},
            update_doc,
            upsert=True
        )
    
    async def get_analysis_history(self, address: str, limit: int = 10) -> List[AnalysisHistoryItem]:
        """Get analysis history for a contract address"""
        await self._ensure_connection()
        
        cursor = self.db_client.get_collection("analyses").find(
            {"address": address.lower()}
        ).sort("analysis_timestamp", -1).limit(limit)
        
        results = []
        async for doc in cursor:
            results.append(AnalysisHistoryItem(
                analysis_id=doc["analysis_id"],
                address=doc["address"],
                is_honeypot=doc["is_honeypot"],
                confidence=doc["confidence"],
                risk_level=doc["risk_level"],
                detected_techniques=doc["detected_techniques"],
                analysis_timestamp=doc["analysis_timestamp"],
                requested_by=doc.get("requested_by")
            ))
        
        return results
    
    async def get_analysis_by_id(self, analysis_id: str) -> Optional[Dict]:
        """Retrieve a specific analysis by ID"""
        await self._ensure_connection()
        
        result = await self.db_client.get_collection("analyses").find_one(
            {"analysis_id": analysis_id}
        )
        
        return result
    
    async def get_honeypot_statistics(self) -> Dict[str, Any]:
        """Get statistics about analyzed honeypots"""
        await self._ensure_connection()
        
        pipeline = [
            {"$group": {
                "_id": "$is_honeypot",
                "count": {"$sum": 1},
                "avg_confidence": {"$avg": "$confidence"}
            }}
        ]
        
        results = await self.db_client.get_collection("analyses").aggregate(pipeline).to_list(length=None)
        
        # Restructure statistics
        stats = {
            "total_analyzed": 0,
            "honeypot_count": 0,
            "clean_count": 0,
            "avg_confidence": 0
        }
        
        for result in results:
            is_honeypot = result["_id"]
            count = result["count"]
            stats["total_analyzed"] += count
            
            if is_honeypot:
                stats["honeypot_count"] = count
            else:
                stats["clean_count"] = count
        
        if stats["total_analyzed"] > 0:
            honeypot_ratio = stats["honeypot_count"] / stats["total_analyzed"]
            stats["honeypot_ratio"] = round(honeypot_ratio, 4)
        
        return stats

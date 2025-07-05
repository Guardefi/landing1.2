"""
Scorpius Reporting Service - Audit Service
Comprehensive audit trail for all reporting operations
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from uuid import uuid4
import aiofiles
import asyncio
import os

# Database libraries
try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False

try:
    import aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class AuditError(Exception):
    """Audit service error"""
    pass


class AuditService:
    """Audit trail service for enterprise compliance"""
    
    def __init__(self):
        self.settings = settings
        self.db_pool = None
        self.redis_client = None
        self.audit_queue = asyncio.Queue()
        self.initialized = False
        self.background_task = None
    
    async def initialize(self):
        """Initialize audit service"""
        try:
            # Initialize database connection
            if ASYNCPG_AVAILABLE and self.settings.DATABASE_URL.startswith('postgresql'):
                self.db_pool = await asyncpg.create_pool(
                    self.settings.DATABASE_URL,
                    min_size=2,
                    max_size=10
                )
                await self._create_audit_table()
                logger.info("PostgreSQL audit database initialized")
            
            # Initialize Redis for caching
            if REDIS_AVAILABLE:
                self.redis_client = await aioredis.from_url(
                    self.settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True
                )
                logger.info("Redis audit cache initialized")
            
            # Start background audit processor
            self.background_task = asyncio.create_task(self._process_audit_queue())
            
            self.initialized = True
            logger.info("Audit service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize audit service: {e}")
            # Fall back to file-based auditing
            self.initialized = True
    
    async def _create_audit_table(self):
        """Create audit table if it doesn't exist"""
        if not self.db_pool:
            return
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS audit_events (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            event_id VARCHAR(255) UNIQUE NOT NULL,
            event_type VARCHAR(100) NOT NULL,
            timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
            user_id VARCHAR(255) NOT NULL,
            session_id VARCHAR(255),
            ip_address INET,
            user_agent TEXT,
            service VARCHAR(100) NOT NULL DEFAULT 'reporting',
            details JSONB NOT NULL,
            risk_score INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            INDEX (event_type, timestamp),
            INDEX (user_id, timestamp),
            INDEX (timestamp)
        );
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(create_table_sql)
    
    async def log_event(
        self,
        event_type: str,
        user_id: str,
        details: Dict[str, Any],
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        risk_score: int = 0
    ) -> str:
        """
        Log audit event
        
        Args:
            event_type: Type of event
            user_id: User identifier
            details: Event details
            session_id: Session identifier
            ip_address: Client IP address
            user_agent: Client user agent
            risk_score: Risk score (0-100)
            
        Returns:
            Event ID
        """
        event_id = str(uuid4())
        
        audit_entry = {
            "event_id": event_id,
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "session_id": session_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "service": "reporting",
            "details": details,
            "risk_score": risk_score
        }
        
        # Add to queue for background processing
        await self.audit_queue.put(audit_entry)
        
        logger.info(f"Audit event queued: {event_type} for user {user_id}")
        return event_id
    
    async def _process_audit_queue(self):
        """Background task to process audit queue"""
        while True:
            try:
                # Get audit entry from queue
                audit_entry = await self.audit_queue.get()
                
                # Store in database
                await self._store_audit_entry(audit_entry)
                
                # Cache in Redis
                await self._cache_audit_entry(audit_entry)
                
                # Write to file as backup
                await self._write_audit_file(audit_entry)
                
                # Check for security alerts
                await self._check_security_alerts(audit_entry)
                
                self.audit_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error processing audit entry: {e}")
                await asyncio.sleep(1)
    
    async def _store_audit_entry(self, audit_entry: Dict[str, Any]):
        """Store audit entry in database"""
        if not self.db_pool:
            return
        
        try:
            insert_sql = """
            INSERT INTO audit_events (
                event_id, event_type, timestamp, user_id, session_id,
                ip_address, user_agent, service, details, risk_score
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """
            
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    insert_sql,
                    audit_entry["event_id"],
                    audit_entry["event_type"],
                    datetime.fromisoformat(audit_entry["timestamp"].replace('Z', '+00:00')),
                    audit_entry["user_id"],
                    audit_entry.get("session_id"),
                    audit_entry.get("ip_address"),
                    audit_entry.get("user_agent"),
                    audit_entry["service"],
                    json.dumps(audit_entry["details"]),
                    audit_entry["risk_score"]
                )
            
        except Exception as e:
            logger.error(f"Failed to store audit entry in database: {e}")
    
    async def _cache_audit_entry(self, audit_entry: Dict[str, Any]):
        """Cache audit entry in Redis"""
        if not self.redis_client:
            return
        
        try:
            # Cache recent events by user
            user_key = f"audit:user:{audit_entry['user_id']}"
            await self.redis_client.lpush(user_key, json.dumps(audit_entry))
            await self.redis_client.ltrim(user_key, 0, 99)  # Keep last 100 events
            await self.redis_client.expire(user_key, 3600)  # 1 hour TTL
            
            # Cache recent events by type
            type_key = f"audit:type:{audit_entry['event_type']}"
            await self.redis_client.lpush(type_key, json.dumps(audit_entry))
            await self.redis_client.ltrim(type_key, 0, 99)
            await self.redis_client.expire(type_key, 3600)
            
        except Exception as e:
            logger.error(f"Failed to cache audit entry: {e}")
    
    async def _write_audit_file(self, audit_entry: Dict[str, Any]):
        """Write audit entry to file as backup"""
        try:
            # Create audit directory
            audit_dir = "./audit_logs"
            os.makedirs(audit_dir, exist_ok=True)
            
            # Create daily log file
            date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            log_file = os.path.join(audit_dir, f"audit_{date_str}.jsonl")
            
            # Write audit entry
            async with aiofiles.open(log_file, 'a') as f:
                await f.write(json.dumps(audit_entry) + '\n')
            
        except Exception as e:
            logger.error(f"Failed to write audit file: {e}")
    
    async def _check_security_alerts(self, audit_entry: Dict[str, Any]):
        """Check for security alerts based on audit entry"""
        try:
            # Check for high-risk events
            if audit_entry["risk_score"] >= 80:
                logger.warning(f"High-risk audit event: {audit_entry['event_type']} by {audit_entry['user_id']}")
            
            # Check for suspicious patterns
            if audit_entry["event_type"] in ["report_download", "signature_verification"]:
                await self._check_download_patterns(audit_entry)
            
        except Exception as e:
            logger.error(f"Failed to check security alerts: {e}")
    
    async def _check_download_patterns(self, audit_entry: Dict[str, Any]):
        """Check for suspicious download patterns"""
        if not self.redis_client:
            return
        
        try:
            user_id = audit_entry["user_id"]
            
            # Get recent downloads by user
            user_key = f"audit:user:{user_id}"
            recent_events = await self.redis_client.lrange(user_key, 0, 20)
            
            download_count = 0
            for event_json in recent_events:
                event = json.loads(event_json)
                if event["event_type"] == "report_download":
                    download_count += 1
            
            # Alert if too many downloads
            if download_count > 10:
                logger.warning(f"Suspicious download pattern: {download_count} downloads by user {user_id}")
                
                # Increase risk score for future events
                await self.redis_client.set(f"risk:user:{user_id}", "high", ex=3600)
                
        except Exception as e:
            logger.error(f"Failed to check download patterns: {e}")
    
    async def get_audit_events(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get audit events with filtering
        
        Args:
            user_id: Filter by user ID
            event_type: Filter by event type
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum number of events
            
        Returns:
            List of audit events
        """
        if not self.db_pool:
            return await self._get_audit_events_from_file(user_id, event_type, start_time, end_time, limit)
        
        try:
            # Build query
            conditions = []
            params = []
            param_count = 0
            
            if user_id:
                param_count += 1
                conditions.append(f"user_id = ${param_count}")
                params.append(user_id)
            
            if event_type:
                param_count += 1
                conditions.append(f"event_type = ${param_count}")
                params.append(event_type)
            
            if start_time:
                param_count += 1
                conditions.append(f"timestamp >= ${param_count}")
                params.append(start_time)
            
            if end_time:
                param_count += 1
                conditions.append(f"timestamp <= ${param_count}")
                params.append(end_time)
            
            where_clause = " AND ".join(conditions) if conditions else "TRUE"
            
            query = f"""
            SELECT event_id, event_type, timestamp, user_id, session_id,
                   ip_address, user_agent, service, details, risk_score
            FROM audit_events
            WHERE {where_clause}
            ORDER BY timestamp DESC
            LIMIT {limit}
            """
            
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch(query, *params)
                
                events = []
                for row in rows:
                    event = {
                        "event_id": str(row["event_id"]),
                        "event_type": row["event_type"],
                        "timestamp": row["timestamp"].isoformat(),
                        "user_id": row["user_id"],
                        "session_id": row["session_id"],
                        "ip_address": str(row["ip_address"]) if row["ip_address"] else None,
                        "user_agent": row["user_agent"],
                        "service": row["service"],
                        "details": json.loads(row["details"]) if row["details"] else {},
                        "risk_score": row["risk_score"]
                    }
                    events.append(event)
                
                return events
                
        except Exception as e:
            logger.error(f"Failed to get audit events: {e}")
            return []
    
    async def _get_audit_events_from_file(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get audit events from file backup"""
        events = []
        
        try:
            audit_dir = "./audit_logs"
            if not os.path.exists(audit_dir):
                return events
            
            # Read recent log files
            log_files = sorted([f for f in os.listdir(audit_dir) if f.startswith("audit_")])
            
            for log_file in reversed(log_files[-7:]):  # Last 7 days
                file_path = os.path.join(audit_dir, log_file)
                
                async with aiofiles.open(file_path, 'r') as f:
                    async for line in f:
                        if len(events) >= limit:
                            break
                        
                        try:
                            event = json.loads(line.strip())
                            
                            # Apply filters
                            if user_id and event.get("user_id") != user_id:
                                continue
                            
                            if event_type and event.get("event_type") != event_type:
                                continue
                            
                            event_time = datetime.fromisoformat(event["timestamp"].replace('Z', '+00:00'))
                            
                            if start_time and event_time < start_time:
                                continue
                            
                            if end_time and event_time > end_time:
                                continue
                            
                            events.append(event)
                            
                        except json.JSONDecodeError:
                            continue
                
                if len(events) >= limit:
                    break
            
        except Exception as e:
            logger.error(f"Failed to read audit events from file: {e}")
        
        return events[:limit]
    
    async def get_audit_summary(
        self,
        user_id: Optional[str] = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get audit summary statistics
        
        Args:
            user_id: Filter by user ID
            days: Number of days to include
            
        Returns:
            Audit summary statistics
        """
        try:
            end_time = datetime.now(timezone.utc)
            start_time = end_time.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days)
            
            events = await self.get_audit_events(
                user_id=user_id,
                start_time=start_time,
                end_time=end_time,
                limit=10000
            )
            
            # Calculate statistics
            event_types = {}
            risk_scores = []
            daily_counts = {}
            
            for event in events:
                # Count by event type
                event_type = event["event_type"]
                event_types[event_type] = event_types.get(event_type, 0) + 1
                
                # Collect risk scores
                risk_scores.append(event["risk_score"])
                
                # Count by day
                event_date = datetime.fromisoformat(event["timestamp"].replace('Z', '+00:00')).date()
                daily_counts[str(event_date)] = daily_counts.get(str(event_date), 0) + 1
            
            summary = {
                "total_events": len(events),
                "event_types": event_types,
                "average_risk_score": sum(risk_scores) / len(risk_scores) if risk_scores else 0,
                "max_risk_score": max(risk_scores) if risk_scores else 0,
                "daily_counts": daily_counts,
                "period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "days": days
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get audit summary: {e}")
            return {}
    
    async def cleanup(self):
        """Cleanup audit service"""
        try:
            if self.background_task:
                self.background_task.cancel()
            
            if self.redis_client:
                await self.redis_client.close()
            
            if self.db_pool:
                await self.db_pool.close()
            
            logger.info("Audit service cleanup completed")
            
        except Exception as e:
            logger.error(f"Audit service cleanup error: {e}")



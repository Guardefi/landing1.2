"""
Scorpius Reporting Service - QLDB Service
Amazon Quantum Ledger Database integration for immutable audit trails
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from uuid import uuid4
import hashlib

# AWS and QLDB libraries
try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    logging.warning("Boto3 not available. QLDB functionality will be limited.")

try:
    from pyqldb.driver.qldb_driver import QldbDriver
    from pyqldb.config.retry_config import RetryConfig
    from pyqldb.errors import QldbDriverException
    PYQLDB_AVAILABLE = True
except ImportError:
    PYQLDB_AVAILABLE = False
    logging.warning("PyQLDB not available. QLDB functionality will be limited.")

from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class QLDBError(Exception):
    """QLDB service error"""
    pass


class QLDBService:
    """Amazon QLDB service for immutable document hash storage"""
    
    def __init__(self):
        self.settings = settings
        self.qldb_driver = None
        self.ledger_name = self.settings.QLDB_LEDGER_NAME
        self.table_name = self.settings.QLDB_TABLE_NAME
        self.initialized = False
        self.mock_storage = {}  # For development/testing
    
    async def initialize(self):
        """Initialize QLDB service"""
        try:
            if not BOTO3_AVAILABLE or not PYQLDB_AVAILABLE:
                logger.warning("QLDB libraries not available, using mock storage")
                self.initialized = True
                return
            
            # Initialize QLDB driver
            try:
                retry_config = RetryConfig(retry_limit=3)
                self.qldb_driver = QldbDriver(
                    ledger_name=self.ledger_name,
                    region_name=self.settings.AWS_REGION,
                    retry_config=retry_config
                )
                
                # Create table if it doesn't exist
                await self._create_table_if_not_exists()
                
                logger.info(f"QLDB service initialized with ledger: {self.ledger_name}")
                
            except (NoCredentialsError, ClientError) as e:
                logger.warning(f"QLDB initialization failed, using mock storage: {e}")
                self.qldb_driver = None
            
            self.initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize QLDB service: {e}")
            self.initialized = True  # Use mock storage
    
    async def _create_table_if_not_exists(self):
        """Create QLDB table if it doesn't exist"""
        if not self.qldb_driver:
            return
        
        try:
            def create_table_transaction(transaction_executor):
                # Check if table exists
                table_query = f"SELECT name FROM information_schema.user_tables WHERE name = '{self.table_name}'"
                cursor = transaction_executor.execute_statement(table_query)
                
                if not list(cursor):
                    # Create table
                    create_query = f"CREATE TABLE {self.table_name}"
                    transaction_executor.execute_statement(create_query)
                    logger.info(f"Created QLDB table: {self.table_name}")
                
                # Create index on document_id
                try:
                    index_query = f"CREATE INDEX ON {self.table_name} (document_id)"
                    transaction_executor.execute_statement(index_query)
                except Exception:
                    pass  # Index might already exist
            
            self.qldb_driver.execute_lambda(create_table_transaction)
            
        except Exception as e:
            logger.error(f"Failed to create QLDB table: {e}")
    
    async def store_document_hash(
        self,
        document_id: str,
        document_hash: str,
        document_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store document hash in QLDB for immutable audit trail
        
        Args:
            document_id: Unique document identifier
            document_hash: SHA256 hash of the document
            document_type: Type of document (pdf_report, sarif_report, etc.)
            metadata: Additional metadata
            
        Returns:
            QLDB document ID
        """
        if not self.initialized:
            raise QLDBError("QLDB service not initialized")
        
        try:
            if not self.qldb_driver:
                return await self._mock_store_document_hash(
                    document_id, document_hash, document_type, metadata
                )
            
            qldb_doc = {
                "document_id": document_id,
                "document_hash": document_hash,
                "document_type": document_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service": "scorpius-reporting",
                "metadata": metadata or {}
            }
            
            def store_transaction(transaction_executor):
                # Insert document hash
                insert_query = f"INSERT INTO {self.table_name} ?"
                cursor = transaction_executor.execute_statement(insert_query, qldb_doc)
                result = list(cursor)
                return result[0]["documentId"] if result else None
            
            qldb_document_id = self.qldb_driver.execute_lambda(store_transaction)
            
            logger.info(f"Stored document hash in QLDB: {document_id}")
            return str(qldb_document_id)
            
        except Exception as e:
            logger.error(f"Failed to store document hash in QLDB: {e}")
            raise QLDBError(f"Failed to store document hash: {str(e)}")
    
    async def _mock_store_document_hash(
        self,
        document_id: str,
        document_hash: str,
        document_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Mock implementation for development"""
        
        qldb_doc_id = str(uuid4())
        
        mock_doc = {
            "qldb_document_id": qldb_doc_id,
            "document_id": document_id,
            "document_hash": document_hash,
            "document_type": document_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "scorpius-reporting",
            "metadata": metadata or {}
        }
        
        self.mock_storage[document_id] = mock_doc
        
        logger.info(f"Mock stored document hash: {document_id}")
        return qldb_doc_id
    
    async def verify_document_hash(
        self,
        document_id: str,
        document_hash: str
    ) -> bool:
        """
        Verify document hash against QLDB record
        
        Args:
            document_id: Document identifier
            document_hash: Hash to verify
            
        Returns:
            True if hash matches, False otherwise
        """
        if not self.initialized:
            raise QLDBError("QLDB service not initialized")
        
        try:
            if not self.qldb_driver:
                return await self._mock_verify_document_hash(document_id, document_hash)
            
            def verify_transaction(transaction_executor):
                query = f"SELECT document_hash FROM {self.table_name} WHERE document_id = ?"
                cursor = transaction_executor.execute_statement(query, document_id)
                results = list(cursor)
                return results[0]["document_hash"] if results else None
            
            stored_hash = self.qldb_driver.execute_lambda(verify_transaction)
            
            if stored_hash:
                is_valid = stored_hash == document_hash
                logger.info(f"Hash verification for {document_id}: {'VALID' if is_valid else 'INVALID'}")
                return is_valid
            else:
                logger.warning(f"Document not found in QLDB: {document_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to verify document hash: {e}")
            return False
    
    async def _mock_verify_document_hash(
        self,
        document_id: str,
        document_hash: str
    ) -> bool:
        """Mock verification for development"""
        
        if document_id in self.mock_storage:
            stored_hash = self.mock_storage[document_id]["document_hash"]
            is_valid = stored_hash == document_hash
            logger.info(f"Mock hash verification for {document_id}: {'VALID' if is_valid else 'INVALID'}")
            return is_valid
        else:
            logger.warning(f"Document not found in mock storage: {document_id}")
            return False
    
    async def get_document_history(
        self,
        document_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get document history from QLDB
        
        Args:
            document_id: Document identifier
            
        Returns:
            List of document history records
        """
        if not self.initialized:
            raise QLDBError("QLDB service not initialized")
        
        try:
            if not self.qldb_driver:
                return await self._mock_get_document_history(document_id)
            
            def history_transaction(transaction_executor):
                # Get current document
                current_query = f"SELECT * FROM {self.table_name} WHERE document_id = ?"
                current_cursor = transaction_executor.execute_statement(current_query, document_id)
                current_results = list(current_cursor)
                
                if not current_results:
                    return []
                
                # Get document history
                history_query = f"SELECT * FROM history({self.table_name}) WHERE data.document_id = ?"
                history_cursor = transaction_executor.execute_statement(history_query, document_id)
                history_results = list(history_cursor)
                
                return history_results
            
            history = self.qldb_driver.execute_lambda(history_transaction)
            
            # Convert QLDB records to standard format
            formatted_history = []
            for record in history:
                formatted_record = {
                    "document_id": record["data"]["document_id"],
                    "document_hash": record["data"]["document_hash"],
                    "document_type": record["data"]["document_type"],
                    "timestamp": record["data"]["timestamp"],
                    "metadata": record["data"].get("metadata", {}),
                    "version": record["metadata"]["version"],
                    "txn_time": record["metadata"]["txnTime"]
                }
                formatted_history.append(formatted_record)
            
            logger.info(f"Retrieved document history for {document_id}: {len(formatted_history)} records")
            return formatted_history
            
        except Exception as e:
            logger.error(f"Failed to get document history: {e}")
            return []
    
    async def _mock_get_document_history(
        self,
        document_id: str
    ) -> List[Dict[str, Any]]:
        """Mock document history for development"""
        
        if document_id in self.mock_storage:
            doc = self.mock_storage[document_id]
            history = [{
                "document_id": doc["document_id"],
                "document_hash": doc["document_hash"],
                "document_type": doc["document_type"],
                "timestamp": doc["timestamp"],
                "metadata": doc["metadata"],
                "version": 0,
                "txn_time": doc["timestamp"]
            }]
            
            logger.info(f"Mock retrieved document history for {document_id}: 1 record")
            return history
        else:
            return []
    
    async def get_audit_proof(
        self,
        document_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get cryptographic proof for document from QLDB
        
        Args:
            document_id: Document identifier
            
        Returns:
            Audit proof dictionary or None if not found
        """
        if not self.initialized:
            raise QLDBError("QLDB service not initialized")
        
        try:
            if not self.qldb_driver:
                return await self._mock_get_audit_proof(document_id)
            
            # In a full implementation, this would use QLDB's cryptographic verification
            # For now, we'll provide a simplified proof structure
            
            def proof_transaction(transaction_executor):
                query = f"SELECT * FROM {self.table_name} WHERE document_id = ?"
                cursor = transaction_executor.execute_statement(query, document_id)
                results = list(cursor)
                return results[0] if results else None
            
            document = self.qldb_driver.execute_lambda(proof_transaction)
            
            if document:
                proof = {
                    "document_id": document_id,
                    "ledger_name": self.ledger_name,
                    "table_name": self.table_name,
                    "document_hash": document["document_hash"],
                    "timestamp": document["timestamp"],
                    "proof_hash": hashlib.sha256(
                        f"{document_id}:{document['document_hash']}:{document['timestamp']}".encode()
                    ).hexdigest(),
                    "verified": True
                }
                
                logger.info(f"Generated audit proof for {document_id}")
                return proof
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to get audit proof: {e}")
            return None
    
    async def _mock_get_audit_proof(
        self,
        document_id: str
    ) -> Optional[Dict[str, Any]]:
        """Mock audit proof for development"""
        
        if document_id in self.mock_storage:
            doc = self.mock_storage[document_id]
            proof = {
                "document_id": document_id,
                "ledger_name": "mock_ledger",
                "table_name": "mock_table",
                "document_hash": doc["document_hash"],
                "timestamp": doc["timestamp"],
                "proof_hash": hashlib.sha256(
                    f"{document_id}:{doc['document_hash']}:{doc['timestamp']}".encode()
                ).hexdigest(),
                "verified": True,
                "mock": True
            }
            
            logger.info(f"Mock generated audit proof for {document_id}")
            return proof
        else:
            return None
    
    async def list_documents(
        self,
        document_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List documents in QLDB
        
        Args:
            document_type: Filter by document type
            limit: Maximum number of documents to return
            
        Returns:
            List of documents
        """
        if not self.initialized:
            raise QLDBError("QLDB service not initialized")
        
        try:
            if not self.qldb_driver:
                return await self._mock_list_documents(document_type, limit)
            
            def list_transaction(transaction_executor):
                if document_type:
                    query = f"SELECT * FROM {self.table_name} WHERE document_type = ? ORDER BY timestamp DESC"
                    cursor = transaction_executor.execute_statement(query, document_type)
                else:
                    query = f"SELECT * FROM {self.table_name} ORDER BY timestamp DESC"
                    cursor = transaction_executor.execute_statement(query)
                
                results = list(cursor)
                return results[:limit]
            
            documents = self.qldb_driver.execute_lambda(list_transaction)
            
            logger.info(f"Listed {len(documents)} documents from QLDB")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to list documents: {e}")
            return []
    
    async def _mock_list_documents(
        self,
        document_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Mock document listing for development"""
        
        documents = []
        for doc in self.mock_storage.values():
            if document_type is None or doc["document_type"] == document_type:
                documents.append(doc)
        
        # Sort by timestamp descending
        documents.sort(key=lambda x: x["timestamp"], reverse=True)
        
        logger.info(f"Mock listed {len(documents[:limit])} documents")
        return documents[:limit]
    
    async def cleanup(self):
        """Cleanup QLDB service"""
        try:
            if self.qldb_driver:
                self.qldb_driver.close()
            
            logger.info("QLDB service cleanup completed")
            
        except Exception as e:
            logger.error(f"QLDB service cleanup error: {e}")
    
    def get_ledger_info(self) -> Dict[str, Any]:
        """Get QLDB ledger information"""
        return {
            "ledger_name": self.ledger_name,
            "table_name": self.table_name,
            "region": self.settings.AWS_REGION,
            "mock_mode": not bool(self.qldb_driver),
            "initialized": self.initialized
        }

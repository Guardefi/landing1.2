"""
Enterprise Reporting Database Layer
==================================

Database operations and connection management for the reporting system.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, List, Optional

try:
    from sqlalchemy import select, update, delete
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

# Handle both relative and absolute imports
try:
    from ..config import Settings
    from ..models import (
        Base,
        ScanResult,
        VulnerabilityFinding,
        Report,
        AuditLog,
        User,
    )
except ImportError:
    # Fall back to absolute imports
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from config import Settings
    from models import (
        Base,
        ScanResult,
        VulnerabilityFinding,
        Report,
        AuditLog,
        User,
    )

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database connection and session management"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.engine = create_async_engine(
            settings.database.url,
            pool_size=settings.database.pool_size,
            max_overflow=settings.database.max_overflow,
            echo=settings.api.debug
        )
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def init_db(self):
        """Initialize database tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def close(self):
        """Close database connections"""
        await self.engine.dispose()
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session"""
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


class ScanResultRepository:
    """Repository for scan result operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def create_scan_result(self, scan_result: ScanResult) -> ScanResult:
        """Create a new scan result"""
        async with self.db_manager.get_session() as session:
            session.add(scan_result)
            await session.flush()
            await session.refresh(scan_result)
            return scan_result
    
    async def get_scan_result(self, scan_id: str) -> Optional[ScanResult]:
        """Get scan result by ID"""
        async with self.db_manager.get_session() as session:
            query = select(ScanResult).where(ScanResult.scan_id == scan_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()
    
    async def get_scan_results(
        self,
        limit: int = 100,
        offset: int = 0,
        target_address: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[ScanResult]:
        """Get scan results with filtering"""
        async with self.db_manager.get_session() as session:
            query = select(ScanResult)
            
            # Apply filters
            if target_address:
                query = query.where(ScanResult.target_info["address"] == target_address)
            if status:
                query = query.where(ScanResult.status == status)
            
            # Apply pagination
            query = query.limit(limit).offset(offset).order_by(ScanResult.timestamp.desc())
            
            result = await session.execute(query)
            return list(result.scalars().all())
    
    async def update_scan_result(self, scan_id: str, updates: Dict) -> Optional[ScanResult]:
        """Update scan result"""
        async with self.db_manager.get_session() as session:
            query = update(ScanResult).where(ScanResult.scan_id == scan_id).values(**updates)
            await session.execute(query)
            
            # Return updated result
            return await self.get_scan_result(scan_id)
    
    async def delete_scan_result(self, scan_id: str) -> bool:
        """Delete scan result"""
        async with self.db_manager.get_session() as session:
            query = delete(ScanResult).where(ScanResult.scan_id == scan_id)
            result = await session.execute(query)
            return result.rowcount > 0


class VulnerabilityRepository:
    """Repository for vulnerability operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def create_vulnerability(self, vulnerability: VulnerabilityFinding) -> VulnerabilityFinding:
        """Create a new vulnerability"""
        async with self.db_manager.get_session() as session:
            session.add(vulnerability)
            await session.flush()
            await session.refresh(vulnerability)
            return vulnerability
    
    async def get_vulnerabilities_for_scan(self, scan_id: str) -> List[VulnerabilityFinding]:
        """Get all vulnerabilities for a scan"""
        async with self.db_manager.get_session() as session:
            query = select(VulnerabilityFinding).where(VulnerabilityFinding.scan_id == scan_id)
            result = await session.execute(query)
            return list(result.scalars().all())
    
    async def get_vulnerabilities_by_severity(
        self,
        severity: str,
        limit: int = 100
    ) -> List[VulnerabilityFinding]:
        """Get vulnerabilities by severity level"""
        async with self.db_manager.get_session() as session:
            query = (
                select(VulnerabilityFinding)
                .where(VulnerabilityFinding.severity == severity)
                .limit(limit)
                .order_by(VulnerabilityFinding.created_at.desc())
            )
            result = await session.execute(query)
            return list(result.scalars().all())
    
    async def update_vulnerability(
        self,
        vulnerability_id: str,
        updates: Dict
    ) -> Optional[VulnerabilityFinding]:
        """Update vulnerability"""
        async with self.db_manager.get_session() as session:
            query = (
                update(VulnerabilityFinding)
                .where(VulnerabilityFinding.id == vulnerability_id)
                .values(**updates)
            )
            await session.execute(query)
            
            # Return updated vulnerability
            get_query = select(VulnerabilityFinding).where(
                VulnerabilityFinding.id == vulnerability_id
            )
            result = await session.execute(get_query)
            return result.scalar_one_or_none()


class ReportRepository:
    """Repository for report operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def create_report(self, report: Report) -> Report:
        """Create a new report"""
        async with self.db_manager.get_session() as session:
            session.add(report)
            await session.flush()
            await session.refresh(report)
            return report
    
    async def get_report(self, report_id: str) -> Optional[Report]:
        """Get report by ID"""
        async with self.db_manager.get_session() as session:
            query = select(Report).where(Report.id == report_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()
    
    async def get_reports_for_scan(self, scan_id: str) -> List[Report]:
        """Get all reports for a scan"""
        async with self.db_manager.get_session() as session:
            query = select(Report).where(Report.scan_id == scan_id)
            result = await session.execute(query)
            return list(result.scalars().all())
    
    async def get_reports(
        self,
        limit: int = 100,
        offset: int = 0,
        status: Optional[str] = None,
        format_type: Optional[str] = None
    ) -> List[Report]:
        """Get reports with filtering"""
        async with self.db_manager.get_session() as session:
            query = select(Report)
            
            # Apply filters
            if status:
                query = query.where(Report.status == status)
            if format_type:
                query = query.where(Report.format == format_type)
            
            # Apply pagination
            query = query.limit(limit).offset(offset).order_by(Report.created_at.desc())
            
            result = await session.execute(query)
            return list(result.scalars().all())
    
    async def update_report(self, report_id: str, updates: Dict) -> Optional[Report]:
        """Update report"""
        async with self.db_manager.get_session() as session:
            query = update(Report).where(Report.id == report_id).values(**updates)
            await session.execute(query)
            
            # Return updated report
            return await self.get_report(report_id)
    
    async def delete_report(self, report_id: str) -> bool:
        """Delete report"""
        async with self.db_manager.get_session() as session:
            query = delete(Report).where(Report.id == report_id)
            result = await session.execute(query)
            return result.rowcount > 0


class AuditLogRepository:
    """Repository for audit log operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def create_audit_log(self, audit_log: AuditLog) -> AuditLog:
        """Create audit log entry"""
        async with self.db_manager.get_session() as session:
            session.add(audit_log)
            await session.flush()
            await session.refresh(audit_log)
            return audit_log
    
    async def get_audit_logs(
        self,
        limit: int = 100,
        offset: int = 0,
        user_id: Optional[str] = None,
        action: Optional[str] = None
    ) -> List[AuditLog]:
        """Get audit logs with filtering"""
        async with self.db_manager.get_session() as session:
            query = select(AuditLog)
            
            # Apply filters
            if user_id:
                query = query.where(AuditLog.user_id == user_id)
            if action:
                query = query.where(AuditLog.action == action)
            
            # Apply pagination
            query = query.limit(limit).offset(offset).order_by(AuditLog.timestamp.desc())
            
            result = await session.execute(query)
            return list(result.scalars().all())


class UserRepository:
    """Repository for user operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def create_user(self, user: User) -> User:
        """Create a new user"""
        async with self.db_manager.get_session() as session:
            session.add(user)
            await session.flush()
            await session.refresh(user)
            return user
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        async with self.db_manager.get_session() as session:
            query = select(User).where(User.id == user_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        async with self.db_manager.get_session() as session:
            query = select(User).where(User.username == username)
            result = await session.execute(query)
            return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        async with self.db_manager.get_session() as session:
            query = select(User).where(User.email == email)
            result = await session.execute(query)
            return result.scalar_one_or_none()
    
    async def update_user(self, user_id: str, updates: Dict) -> Optional[User]:
        """Update user"""
        async with self.db_manager.get_session() as session:
            query = update(User).where(User.id == user_id).values(**updates)
            await session.execute(query)
            
            # Return updated user
            return await self.get_user(user_id)
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        async with self.db_manager.get_session() as session:
            query = delete(User).where(User.id == user_id)
            result = await session.execute(query)
            return result.rowcount > 0


# Global database manager and repositories
db_manager: Optional[DatabaseManager] = None
scan_result_repo: Optional[ScanResultRepository] = None
vulnerability_repo: Optional[VulnerabilityRepository] = None
report_repo: Optional[ReportRepository] = None
audit_log_repo: Optional[AuditLogRepository] = None
user_repo: Optional[UserRepository] = None


async def init_database(settings: Settings):
    """Initialize database and repositories"""
    global db_manager, scan_result_repo, vulnerability_repo, report_repo, audit_log_repo, user_repo
    
    db_manager = DatabaseManager(settings)
    await db_manager.init_db()
    
    scan_result_repo = ScanResultRepository(db_manager)
    vulnerability_repo = VulnerabilityRepository(db_manager)
    report_repo = ReportRepository(db_manager)
    audit_log_repo = AuditLogRepository(db_manager)
    user_repo = UserRepository(db_manager)
    
    logger.info("Database initialized successfully")


async def close_database():
    """Close database connections"""
    global db_manager
    if db_manager:
        await db_manager.close()
        logger.info("Database connections closed")


async def get_db() -> AsyncSession:
    """Dependency for getting database session"""
    if not db_manager:
        raise RuntimeError("Database not initialized")
    
    async with db_manager.get_session() as session:
        yield session


def get_scan_result_repository() -> ScanResultRepository:
    """Get scan result repository"""
    if not scan_result_repo:
        raise RuntimeError("Database not initialized")
    return scan_result_repo


def get_vulnerability_repository() -> VulnerabilityRepository:
    """Get vulnerability repository"""
    if not vulnerability_repo:
        raise RuntimeError("Database not initialized")
    return vulnerability_repo


def get_report_repository() -> ReportRepository:
    """Get report repository"""
    if not report_repo:
        raise RuntimeError("Database not initialized")
    return report_repo


def get_audit_log_repository() -> AuditLogRepository:
    """Get audit log repository"""
    if not audit_log_repo:
        raise RuntimeError("Database not initialized")
    return audit_log_repo


def get_user_repository() -> UserRepository:
    """Get user repository"""
    if not user_repo:
        raise RuntimeError("Database not initialized")
    return user_repo

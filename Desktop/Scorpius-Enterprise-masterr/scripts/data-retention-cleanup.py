#!/usr/bin/env python3
"""
Scorpius Data Retention and Privacy Compliance Script
Implements GDPR/CCPA data retention policies and PII cleanup
Runs as a scheduled job to maintain compliance
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List

import asyncpg
import boto3
import redis

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class RetentionPolicy:
    """Data retention policy configuration"""

    name: str
    table_name: str
    date_column: str
    retention_days: int
    has_pii: bool = False
    anonymize_columns: List[str] = None
    cascade_delete: List[str] = None


@dataclass
class CleanupResult:
    """Result of cleanup operation"""

    policy_name: str
    records_deleted: int
    records_anonymized: int
    bytes_freed: int
    execution_time: float
    errors: List[str]


class DataRetentionManager:
    """Manages data retention and privacy compliance"""

    def __init__(self, config: Dict):
        self.config = config
        self.db_pool = None
        self.redis_client = None
        self.s3_client = None
        self.results: List[CleanupResult] = []

        # Default retention policies
        self.policies = [
            RetentionPolicy(
                name="user_activity_logs",
                table_name="user_activity_logs",
                date_column="created_at",
                retention_days=30,
                has_pii=True,
                anonymize_columns=["ip_address", "user_agent", "session_id"],
            ),
            RetentionPolicy(
                name="audit_logs",
                table_name="audit_logs",
                date_column="timestamp",
                retention_days=90,
                has_pii=True,
                anonymize_columns=["user_id", "ip_address"],
            ),
            RetentionPolicy(
                name="scan_results_detailed",
                table_name="scan_results",
                date_column="scan_date",
                retention_days=365,
                has_pii=False,
            ),
            RetentionPolicy(
                name="transaction_logs",
                table_name="mempool_transactions",
                date_column="processed_at",
                retention_days=90,
                has_pii=False,
            ),
            RetentionPolicy(
                name="user_sessions",
                table_name="user_sessions",
                date_column="last_activity",
                retention_days=30,
                has_pii=True,
                anonymize_columns=["session_data", "ip_address"],
            ),
            RetentionPolicy(
                name="error_logs",
                table_name="application_logs",
                date_column="timestamp",
                retention_days=60,
                has_pii=True,
                anonymize_columns=["user_context", "request_data"],
            ),
            RetentionPolicy(
                name="api_access_logs",
                table_name="api_access_logs",
                date_column="request_time",
                retention_days=90,
                has_pii=True,
                anonymize_columns=["client_ip", "user_id", "request_headers"],
            ),
        ]

    async def initialize(self):
        """Initialize database and cache connections"""
        try:
            # Database connection
            self.db_pool = await asyncpg.create_pool(
                host=self.config.get("db_host"),
                port=self.config.get("db_port", 5432),
                user=self.config.get("db_user"),
                password=self.config.get("db_password"),
                database=self.config.get("db_name"),
                min_size=2,
                max_size=10,
            )

            # Redis connection
            if self.config.get("redis_host"):
                self.redis_client = redis.Redis(
                    host=self.config.get("redis_host"),
                    port=self.config.get("redis_port", 6379),
                    password=self.config.get("redis_password"),
                    decode_responses=True,
                )

            # S3 connection for log archival
            if self.config.get("aws_region"):
                self.s3_client = boto3.client(
                    "s3", region_name=self.config.get("aws_region")
                )

            logger.info("Initialized connections successfully")

        except Exception as e:
            logger.error(f"Failed to initialize connections: {e}")
            raise

    async def cleanup(self):
        """Cleanup connections"""
        if self.db_pool:
            await self.db_pool.close()
        if self.redis_client:
            self.redis_client.close()

    async def execute_retention_policy(
        self, policy: RetentionPolicy, dry_run: bool = False
    ) -> CleanupResult:
        """Execute a specific retention policy"""
        start_time = datetime.now()
        result = CleanupResult(
            policy_name=policy.name,
            records_deleted=0,
            records_anonymized=0,
            bytes_freed=0,
            execution_time=0.0,
            errors=[],
        )

        try:
            cutoff_date = datetime.now() - timedelta(days=policy.retention_days)

            logger.info(
                f"Executing policy '{
                    policy.name}' with cutoff date: {cutoff_date}"
            )

            async with self.db_pool.acquire() as conn:
                # Check if table exists
                table_exists = await conn.fetchval(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = $1)",
                    policy.table_name,
                )

                if not table_exists:
                    logger.warning(
                        f"Table {
                            policy.table_name} does not exist, skipping"
                    )
                    return result

                # Get count of records to be affected
                count_query = f"""
                    SELECT COUNT(*) FROM {policy.table_name}
                    WHERE {policy.date_column} < $1
                """
                records_count = await conn.fetchval(count_query, cutoff_date)

                if records_count == 0:
                    logger.info(
                        f"No records to clean up for policy '{
                            policy.name}'"
                    )
                    return result

                logger.info(
                    f"Found {records_count} records to process for policy '{
                        policy.name}'"
                )

                # Handle PII anonymization before deletion
                if policy.has_pii and policy.anonymize_columns:
                    anonymized_count = await self._anonymize_pii(
                        conn, policy, cutoff_date, dry_run
                    )
                    result.records_anonymized = anonymized_count

                # Calculate storage space before deletion
                size_query = f"""
                    SELECT pg_total_relation_size('{policy.table_name}')
                """
                table_size_before = await conn.fetchval(size_query)

                # Delete old records
                if not dry_run:
                    delete_query = f"""
                        DELETE FROM {policy.table_name}
                        WHERE {policy.date_column} < $1
                    """
                    delete_result = await conn.execute(delete_query, cutoff_date)
                    result.records_deleted = int(delete_result.split()[-1])

                    # Calculate space freed
                    await conn.execute("VACUUM ANALYZE")
                    table_size_after = await conn.fetchval(size_query)
                    result.bytes_freed = max(0, table_size_before - table_size_after)
                else:
                    result.records_deleted = records_count
                    result.bytes_freed = 0

                # Handle cascade deletions
                if policy.cascade_delete and not dry_run:
                    for cascade_table in policy.cascade_delete:
                        cascade_query = f"""
                            DELETE FROM {cascade_table}
                            WHERE {policy.table_name}_id NOT IN (
                                SELECT id FROM {policy.table_name}
                            )
                        """
                        await conn.execute(cascade_query)

        except Exception as e:
            error_msg = f"Error executing policy '{policy.name}': {e}"
            logger.error(error_msg)
            result.errors.append(error_msg)

        result.execution_time = (datetime.now() - start_time).total_seconds()
        return result

    async def _anonymize_pii(
        self, conn, policy: RetentionPolicy, cutoff_date: datetime, dry_run: bool
    ) -> int:
        """Anonymize PII data before deletion"""
        try:
            if dry_run:
                # Just count records that would be anonymized
                count_query = f"""
                    SELECT COUNT(*) FROM {policy.table_name}
                    WHERE {policy.date_column} < $1
                """
                return await conn.fetchval(count_query, cutoff_date)

            # Build anonymization query
            anonymization_updates = []
            for column in policy.anonymize_columns:
                # Different anonymization strategies based on column name
                if "email" in column.lower():
                    anonymization_updates.append(f"{column} = 'anonymized@example.com'")
                elif "ip" in column.lower():
                    anonymization_updates.append(f"{column} = '0.0.0.0'")
                elif "id" in column.lower():
                    anonymization_updates.append(f"{column} = NULL")
                elif "phone" in column.lower():
                    anonymization_updates.append(f"{column} = '000-000-0000'")
                else:
                    anonymization_updates.append(f"{column} = '[REDACTED]'")

            if anonymization_updates:
                update_query = f"""
                    UPDATE {policy.table_name}
                    SET {', '.join(anonymization_updates)},
                        updated_at = NOW(),
                        anonymized = TRUE
                    WHERE {policy.date_column} < $1
                    AND (anonymized IS NULL OR anonymized = FALSE)
                """

                result = await conn.execute(update_query, cutoff_date)
                anonymized_count = int(result.split()[-1])

                logger.info(
                    f"Anonymized {anonymized_count} records in {
                        policy.table_name}"
                )
                return anonymized_count

        except Exception as e:
            logger.error(f"Error anonymizing PII for {policy.table_name}: {e}")

        return 0

    async def cleanup_redis_sessions(
        self, retention_days: int = 30, dry_run: bool = False
    ) -> int:
        """Clean up expired Redis sessions"""
        if not self.redis_client:
            return 0

        try:
            cutoff_time = datetime.now() - timedelta(days=retention_days)
            cutoff_timestamp = int(cutoff_time.timestamp())

            # Find session keys
            session_keys = self.redis_client.keys("session:*")
            expired_sessions = []

            for key in session_keys:
                # Check last activity timestamp
                last_activity = self.redis_client.hget(key, "last_activity")
                if last_activity and int(last_activity) < cutoff_timestamp:
                    expired_sessions.append(key)

            if not dry_run and expired_sessions:
                self.redis_client.delete(*expired_sessions)

            logger.info(
                f"{
                    'Would delete' if dry_run else 'Deleted'} {
                    len(expired_sessions)} expired Redis sessions"
            )
            return len(expired_sessions)

        except Exception as e:
            logger.error(f"Error cleaning up Redis sessions: {e}")
            return 0

    async def archive_logs_to_s3(
        self, retention_days: int = 90, dry_run: bool = False
    ) -> int:
        """Archive old logs to S3 for long-term storage"""
        if not self.s3_client:
            return 0

        try:
            bucket_name = self.config.get("archive_bucket", "scorpius-log-archive")
            cutoff_date = datetime.now() - timedelta(days=retention_days)

            # Query logs to archive
            async with self.db_pool.acquire() as conn:
                logs_query = """
                    SELECT id, timestamp, level, message, metadata
                    FROM application_logs
                    WHERE timestamp < $1
                    AND archived = FALSE
                    ORDER BY timestamp
                    LIMIT 10000
                """

                logs = await conn.fetch(logs_query, cutoff_date)

                if not logs:
                    return 0

                # Group logs by date for efficient S3 storage
                logs_by_date = {}
                for log in logs:
                    date_key = log["timestamp"].strftime("%Y-%m-%d")
                    if date_key not in logs_by_date:
                        logs_by_date[date_key] = []
                    logs_by_date[date_key].append(
                        {
                            "id": log["id"],
                            "timestamp": log["timestamp"].isoformat(),
                            "level": log["level"],
                            "message": log["message"],
                            "metadata": log["metadata"],
                        }
                    )

                archived_count = 0

                for date_key, date_logs in logs_by_date.items():
                    if not dry_run:
                        # Upload to S3
                        s3_key = f"logs/{date_key}/application-logs.json"
                        self.s3_client.put_object(
                            Bucket=bucket_name,
                            Key=s3_key,
                            Body=json.dumps(date_logs, indent=2),
                            ContentType="application/json",
                            StorageClass="STANDARD_IA",  # Cheaper storage for archives
                        )

                        # Mark as archived in database
                        log_ids = [log["id"] for log in date_logs]
                        await conn.execute(
                            "UPDATE application_logs SET archived = TRUE WHERE id = ANY($1)",
                            log_ids,
                        )

                    archived_count += len(date_logs)

                logger.info(
                    f"{'Would archive' if dry_run else 'Archived'} {archived_count} log records to S3"
                )
                return archived_count

        except Exception as e:
            logger.error(f"Error archiving logs to S3: {e}")
            return 0

    async def generate_compliance_report(self) -> Dict:
        """Generate compliance report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "retention_policies": len(self.policies),
            "total_records_deleted": sum(r.records_deleted for r in self.results),
            "total_records_anonymized": sum(r.records_anonymized for r in self.results),
            "total_bytes_freed": sum(r.bytes_freed for r in self.results),
            "total_execution_time": sum(r.execution_time for r in self.results),
            "policies_executed": len(self.results),
            "errors": sum(len(r.errors) for r in self.results),
            "policy_results": [],
        }

        for result in self.results:
            report["policy_results"].append(
                {
                    "policy_name": result.policy_name,
                    "records_deleted": result.records_deleted,
                    "records_anonymized": result.records_anonymized,
                    "bytes_freed": result.bytes_freed,
                    "execution_time": result.execution_time,
                    "success": len(result.errors) == 0,
                    "errors": result.errors,
                }
            )

        # Add compliance status
        report["compliance_status"] = {
            "gdpr_compliant": all(
                r.records_deleted > 0 or len(r.errors) == 0 for r in self.results
            ),
            "ccpa_compliant": all(
                r.records_anonymized > 0 or len(r.errors) == 0
                for r in self.results
                if any(p.has_pii for p in self.policies if p.name == r.policy_name)
            ),
            "data_minimization": report["total_records_deleted"] > 0,
            "right_to_be_forgotten": report["total_records_anonymized"] > 0,
        }

        return report

    async def run_cleanup(
        self, dry_run: bool = False, specific_policies: List[str] = None
    ) -> Dict:
        """Run data retention cleanup"""
        logger.info(f"Starting data retention cleanup (dry_run={dry_run})")

        try:
            await self.initialize()

            # Filter policies if specific ones requested
            policies_to_run = self.policies
            if specific_policies:
                policies_to_run = [
                    p for p in self.policies if p.name in specific_policies
                ]

            # Execute retention policies
            for policy in policies_to_run:
                result = await self.execute_retention_policy(policy, dry_run)
                self.results.append(result)

            # Clean up Redis sessions
            redis_cleaned = await self.cleanup_redis_sessions(30, dry_run)

            # Archive logs to S3
            logs_archived = await self.archive_logs_to_s3(90, dry_run)

            # Generate compliance report
            report = await self.generate_compliance_report()
            report["redis_sessions_cleaned"] = redis_cleaned
            report["logs_archived"] = logs_archived

            logger.info(f"Data retention cleanup completed")
            logger.info(f"Records deleted: {report['total_records_deleted']}")
            logger.info(
                f"Records anonymized: {
                    report['total_records_anonymized']}"
            )
            logger.info(f"Bytes freed: {report['total_bytes_freed']:,}")

            return report

        finally:
            await self.cleanup()


def load_config() -> Dict:
    """Load configuration from environment variables"""
    return {
        "db_host": os.getenv("DB_HOST", "localhost"),
        "db_port": int(os.getenv("DB_PORT", "5432")),
        "db_user": os.getenv("DB_USER", "scorpius"),
        "db_password": os.getenv("DB_PASSWORD"),
        "db_name": os.getenv("DB_NAME", "scorpius"),
        "redis_host": os.getenv("REDIS_HOST"),
        "redis_port": int(os.getenv("REDIS_PORT", "6379")),
        "redis_password": os.getenv("REDIS_PASSWORD"),
        "aws_region": os.getenv("AWS_REGION", "us-east-1"),
        "archive_bucket": os.getenv("ARCHIVE_BUCKET", "scorpius-log-archive"),
    }


async def main():
    parser = argparse.ArgumentParser(
        description="Scorpius Data Retention and Privacy Cleanup"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Perform dry run without making changes"
    )
    parser.add_argument("--policies", nargs="+", help="Specific policies to run")
    parser.add_argument("--output", help="Output file for compliance report")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load configuration
    config = load_config()

    # Validate required configuration
    if not config["db_password"]:
        logger.error("Database password not provided")
        sys.exit(1)

    # Run cleanup
    manager = DataRetentionManager(config)

    try:
        report = await manager.run_cleanup(
            dry_run=args.dry_run, specific_policies=args.policies
        )

        # Save report
        output_file = (
            args.output
            or f"compliance-report-{
                datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Compliance report saved to: {output_file}")

        # Exit with error if there were failures
        if report["errors"] > 0:
            logger.error(f"Cleanup completed with {report['errors']} errors")
            sys.exit(1)
        else:
            logger.info("Cleanup completed successfully")
            sys.exit(0)

    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

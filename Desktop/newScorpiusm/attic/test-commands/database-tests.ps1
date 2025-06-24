# Database and Migration Test Commands
# These commands test database connections, migrations, and data integrity

Write-Host "=== DATABASE AND MIGRATION COMMANDS ===" -ForegroundColor Green

# Database Connection Tests
Write-Host "`n1. Database Connection Tests..." -ForegroundColor Yellow

# Test PostgreSQL connection
Write-Host "   - PostgreSQL connection..." -ForegroundColor Cyan
python -c "import psycopg2; conn = psycopg2.connect('postgresql://user:pass@localhost/dbname'); print('Connected:', conn.status)"

# Test SQLAlchemy connection
Write-Host "   - SQLAlchemy connection..." -ForegroundColor Cyan
python -c "from backend.database import engine; conn = engine.connect(); print('Connected:', bool(conn)); conn.close()"

# Test Redis connection (if used)
Write-Host "   - Redis connection..." -ForegroundColor Cyan
python -c "import redis; r = redis.Redis(host='localhost', port=6379, db=0); print('Redis ping:', r.ping())"

# Database Schema Tests
Write-Host "`n2. Database Schema Tests..." -ForegroundColor Yellow

# Create all tables
Write-Host "   - Create tables..." -ForegroundColor Cyan
python -c "from backend.database import Base, engine; Base.metadata.create_all(engine); print('Tables created')"

# Inspect table structure
Write-Host "   - Inspect tables..." -ForegroundColor Cyan
python -c "from backend.database import engine; print(engine.table_names())"

# Check table columns
Write-Host "   - Check columns..." -ForegroundColor Cyan
python -c "from sqlalchemy import inspect; from backend.database import engine; inspector = inspect(engine); print(inspector.get_columns('users'))"

# Alembic Migration Tests
Write-Host "`n3. Alembic Migration Tests..." -ForegroundColor Yellow

# Initialize Alembic (if not done)
Write-Host "   - Initialize Alembic..." -ForegroundColor Cyan
alembic init alembic

# Generate new migration
Write-Host "   - Generate migration..." -ForegroundColor Cyan
alembic revision --autogenerate -m "Test migration"

# Apply migrations
Write-Host "   - Apply migrations..." -ForegroundColor Cyan
alembic upgrade head

# Downgrade migration
Write-Host "   - Downgrade migration..." -ForegroundColor Cyan
alembic downgrade -1

# Check migration history
Write-Host "   - Migration history..." -ForegroundColor Cyan
alembic history

# Check current revision
Write-Host "   - Current revision..." -ForegroundColor Cyan
alembic current

# Data Integrity Tests
Write-Host "`n4. Data Integrity Tests..." -ForegroundColor Yellow

# Test foreign key constraints
Write-Host "   - Foreign key constraints..." -ForegroundColor Cyan
python backend/tests/test_database_constraints.py

# Test unique constraints
Write-Host "   - Unique constraints..." -ForegroundColor Cyan
python -c "from backend.models import User; from backend.database import Session; session = Session(); user = User(username='test'); session.add(user); session.commit()"

# Test null constraints
Write-Host "   - Null constraints..." -ForegroundColor Cyan
python backend/tests/test_null_constraints.py

# Model Relationship Tests
Write-Host "`n5. Model Relationship Tests..." -ForegroundColor Yellow

# Test one-to-many relationships
Write-Host "   - One-to-many relationships..." -ForegroundColor Cyan
python -c "from backend.models import User, MEVStrategy; from backend.database import Session; session = Session(); user = session.query(User).first(); print('Strategies:', len(user.strategies))"

# Test many-to-many relationships
Write-Host "   - Many-to-many relationships..." -ForegroundColor Cyan
python backend/tests/test_model_relationships.py

# Test cascade operations
Write-Host "   - Cascade operations..." -ForegroundColor Cyan
python backend/tests/test_cascade_operations.py

# Database Performance Tests
Write-Host "`n6. Database Performance Tests..." -ForegroundColor Yellow

# Test query performance
Write-Host "   - Query performance..." -ForegroundColor Cyan
python backend/tests/test_query_performance.py

# Test bulk operations
Write-Host "   - Bulk operations..." -ForegroundColor Cyan
python backend/tests/test_bulk_operations.py

# Test connection pooling
Write-Host "   - Connection pooling..." -ForegroundColor Cyan
python backend/tests/test_connection_pool.py

# Test Database Transactions
Write-Host "`n7. Transaction Tests..." -ForegroundColor Yellow

# Test transaction rollback
Write-Host "   - Transaction rollback..." -ForegroundColor Cyan
python backend/tests/test_transaction_rollback.py

# Test transaction isolation
Write-Host "   - Transaction isolation..." -ForegroundColor Cyan
python backend/tests/test_transaction_isolation.py

# Test deadlock handling
Write-Host "   - Deadlock handling..." -ForegroundColor Cyan
python backend/tests/test_deadlock_handling.py

# Data Seeding and Fixtures
Write-Host "`n8. Data Seeding Tests..." -ForegroundColor Yellow

# Load test fixtures
Write-Host "   - Load test fixtures..." -ForegroundColor Cyan
python backend/fixtures/load_test_data.py

# Create sample data
Write-Host "   - Create sample data..." -ForegroundColor Cyan
python backend/scripts/create_sample_data.py

# Seed production data
Write-Host "   - Seed production data..." -ForegroundColor Cyan
python backend/scripts/seed_production_data.py

# Backup and Restore Tests
Write-Host "`n9. Backup and Restore Tests..." -ForegroundColor Yellow

# Create database backup
Write-Host "   - Create backup..." -ForegroundColor Cyan
pg_dump -h localhost -U username dbname > backup.sql

# Restore database backup
Write-Host "   - Restore backup..." -ForegroundColor Cyan
psql -h localhost -U username dbname < backup.sql

# Test backup integrity
Write-Host "   - Test backup integrity..." -ForegroundColor Cyan
python backend/tests/test_backup_integrity.py

# Database Security Tests
Write-Host "`n10. Database Security Tests..." -ForegroundColor Yellow

# Test SQL injection protection
Write-Host "   - SQL injection protection..." -ForegroundColor Cyan
python backend/tests/test_sql_injection.py

# Test user permissions
Write-Host "   - User permissions..." -ForegroundColor Cyan
python backend/tests/test_db_permissions.py

# Test connection encryption
Write-Host "   - Connection encryption..." -ForegroundColor Cyan
python -c "from backend.database import engine; print('SSL Mode:', engine.url.query.get('sslmode', 'none'))"

# Database Monitoring Tests
Write-Host "`n11. Database Monitoring..." -ForegroundColor Yellow

# Check database size
Write-Host "   - Database size..." -ForegroundColor Cyan
psql -c "SELECT pg_size_pretty(pg_database_size('dbname'));"

# Check table sizes
Write-Host "   - Table sizes..." -ForegroundColor Cyan
psql -c "SELECT schemaname,tablename,pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size FROM pg_tables ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"

# Check active connections
Write-Host "   - Active connections..." -ForegroundColor Cyan
psql -c "SELECT count(*) FROM pg_stat_activity;"

# Database Cleanup Tests
Write-Host "`n12. Database Cleanup..." -ForegroundColor Yellow

# Drop test database
Write-Host "   - Drop test database..." -ForegroundColor Cyan
python -c "from backend.database import Base, engine; Base.metadata.drop_all(engine); print('Tables dropped')"

# Clean test data
Write-Host "   - Clean test data..." -ForegroundColor Cyan
python backend/scripts/clean_test_data.py

# Vacuum database
Write-Host "   - Vacuum database..." -ForegroundColor Cyan
psql -c "VACUUM ANALYZE;"

# Environment-Specific Database Tests
Write-Host "`n13. Environment-Specific Tests..." -ForegroundColor Yellow

# Test development database
Write-Host "   - Development database..." -ForegroundColor Cyan
Write-Host "     DATABASE_URL=postgresql://dev:dev@localhost/scorpius_dev python backend/tests/test_db_connection.py" -ForegroundColor Gray

# Test staging database
Write-Host "   - Staging database..." -ForegroundColor Cyan
Write-Host "     DATABASE_URL=postgresql://staging:staging@staging-db/scorpius_staging python backend/tests/test_db_connection.py" -ForegroundColor Gray

# Test production database (read-only)
Write-Host "   - Production database (read-only)..." -ForegroundColor Cyan
Write-Host "     DATABASE_URL=postgresql://readonly:readonly@prod-db/scorpius python backend/tests/test_readonly_connection.py" -ForegroundColor Gray

# Database Migration Testing
Write-Host "`n14. Migration Testing..." -ForegroundColor Yellow

# Test migration up and down
Write-Host "   - Test migration cycle..." -ForegroundColor Cyan
python backend/tests/test_migration_cycle.py

# Test migration with data
Write-Host "   - Migration with data..." -ForegroundColor Cyan
python backend/tests/test_migration_with_data.py

# Test migration rollback safety
Write-Host "   - Migration rollback safety..." -ForegroundColor Cyan
python backend/tests/test_migration_safety.py

# Expected successful output
Write-Host "`n=== EXPECTED SUCCESSFUL OUTPUT ===" -ForegroundColor Green
Write-Host "Connection: Connected: True
Schema: Tables created successfully
Migration: INFO  [alembic.runtime.migration] Context impl PostgreSQLImpl.
Data: All constraints and relationships working
Performance: Query execution time < 100ms
Backup: Database backup created successfully" -ForegroundColor Gray

Write-Host "`n=== TROUBLESHOOTING ===" -ForegroundColor Red
Write-Host "Common database issues:"
Write-Host "1. Connection refused: Check if PostgreSQL/database service is running"
Write-Host "2. Authentication failed: Verify username, password, and database name"
Write-Host "3. Permission denied: Check user permissions and database ownership"
Write-Host "4. Migration errors: Check for conflicting schema changes"
Write-Host "5. Performance issues: Analyze query plans and add indexes"

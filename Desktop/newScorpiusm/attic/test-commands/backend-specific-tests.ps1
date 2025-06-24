# Backend-Specific Test Commands
# These commands test backend functionality, APIs, and services

Write-Host "=== BACKEND-SPECIFIC TEST COMMANDS ===" -ForegroundColor Green

# FastAPI Server Tests
Write-Host "`n1. FastAPI Server Tests..." -ForegroundColor Yellow

# Start development server
Write-Host "   - Start development server..." -ForegroundColor Cyan
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Start production server
Write-Host "   - Start production server..." -ForegroundColor Cyan
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4

# Test server with simple script
Write-Host "   - Test with simple server..." -ForegroundColor Cyan
python backend/simple_server.py

# API Endpoint Tests
Write-Host "`n2. API Endpoint Tests..." -ForegroundColor Yellow

# Health check endpoint
Write-Host "   - Health check..." -ForegroundColor Cyan
curl http://localhost:8000/healthz

# Readiness check endpoint
Write-Host "   - Readiness check..." -ForegroundColor Cyan
curl http://localhost:8000/readyz

# Metrics endpoint
Write-Host "   - Prometheus metrics..." -ForegroundColor Cyan
curl http://localhost:8000/metrics

# Authentication endpoints
Write-Host "   - Authentication test..." -ForegroundColor Cyan
Write-Host "     curl -X POST http://localhost:8000/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"test\",\"password\":\"test\"}'" -ForegroundColor Gray

# MEV endpoints
Write-Host "   - MEV endpoints..." -ForegroundColor Cyan
Write-Host "     curl http://localhost:8000/api/mev/strategies" -ForegroundColor Gray

# Database Tests
Write-Host "`n3. Database Tests..." -ForegroundColor Yellow

# Test database connection
Write-Host "   - Database connection..." -ForegroundColor Cyan
python -c "from backend.database import engine; print('DB Connected:', engine.connect())"

# Run database migrations
Write-Host "   - Database migrations..." -ForegroundColor Cyan
alembic upgrade head

# Test database models
Write-Host "   - Test models..." -ForegroundColor Cyan
python -c "from backend.models import User, MEVStrategy; print('Models imported successfully')"

# Create test data
Write-Host "   - Create test data..." -ForegroundColor Cyan
python backend/create_test_data.py

# Authentication System Tests
Write-Host "`n4. Authentication System Tests..." -ForegroundColor Yellow

# Test JWT token generation
Write-Host "   - JWT token test..." -ForegroundColor Cyan
python -c "from backend.auth import create_access_token; print(create_access_token({'sub': 'test'}))"

# Test password hashing
Write-Host "   - Password hashing..." -ForegroundColor Cyan
python -c "from backend.auth import hash_password, verify_password; h=hash_password('test'); print(verify_password('test', h))"

# Test user registration
Write-Host "   - User registration..." -ForegroundColor Cyan
Write-Host "     curl -X POST http://localhost:8000/api/auth/register -H 'Content-Type: application/json' -d '{\"username\":\"testuser\",\"email\":\"test@example.com\",\"password\":\"testpass123\"}'" -ForegroundColor Gray

# MEV Bot Tests
Write-Host "`n5. MEV Bot Tests..." -ForegroundColor Yellow

# Test MEV strategy loading
Write-Host "   - MEV strategy loading..." -ForegroundColor Cyan
python -c "from backend.mev_bot.strategies import load_strategies; print(load_strategies())"

# Test mempool monitoring
Write-Host "   - Mempool monitoring..." -ForegroundColor Cyan
python backend/mev_bot/mempool_monitor.py --test

# Test arbitrage detection
Write-Host "   - Arbitrage detection..." -ForegroundColor Cyan
python backend/mev_bot/arbitrage_detector.py --test

# Blockchain Integration Tests
Write-Host "`n6. Blockchain Integration Tests..." -ForegroundColor Yellow

# Test Web3 connection
Write-Host "   - Web3 connection..." -ForegroundColor Cyan
python -c "from backend.blockchain import get_web3; w3=get_web3(); print('Connected:', w3.isConnected())"

# Test contract interaction
Write-Host "   - Contract interaction..." -ForegroundColor Cyan
python backend/blockchain/contract_tester.py

# Test transaction simulation
Write-Host "   - Transaction simulation..." -ForegroundColor Cyan
python backend/simulation/transaction_simulator.py --test

# Security Tests
Write-Host "`n7. Security Tests..." -ForegroundColor Yellow

# Test rate limiting
Write-Host "   - Rate limiting test..." -ForegroundColor Cyan
Write-Host "     for i in {1..15}; do curl -w '%{http_code}\n' http://localhost:8000/; done" -ForegroundColor Gray

# Test CORS configuration
Write-Host "   - CORS test..." -ForegroundColor Cyan
Write-Host "     curl -H 'Origin: http://evil.com' http://localhost:8000/api/health" -ForegroundColor Gray

# Test SQL injection protection
Write-Host "   - SQL injection test..." -ForegroundColor Cyan
Write-Host "     curl 'http://localhost:8000/api/users?id=1; DROP TABLE users;--'" -ForegroundColor Gray

# Performance Tests
Write-Host "`n8. Performance Tests..." -ForegroundColor Yellow

# Load testing with simple script
Write-Host "   - Load test..." -ForegroundColor Cyan
python backend/tests/load_test.py

# Memory usage test
Write-Host "   - Memory usage..." -ForegroundColor Cyan
python -c "import psutil; print('Memory:', psutil.virtual_memory().percent, '%')"

# Response time test
Write-Host "   - Response time..." -ForegroundColor Cyan
Write-Host "     curl -w '@curl-format.txt' -o /dev/null -s http://localhost:8000/healthz" -ForegroundColor Gray

# Logging and Monitoring Tests
Write-Host "`n9. Logging and Monitoring Tests..." -ForegroundColor Yellow

# Test structured logging
Write-Host "   - Structured logging..." -ForegroundColor Cyan
python -c "from backend.logging_config import logger; logger.info('Test log message', extra={'test': True})"

# Test log rotation
Write-Host "   - Log rotation..." -ForegroundColor Cyan
ls -la logs/

# Test metrics collection
Write-Host "   - Metrics collection..." -ForegroundColor Cyan
curl http://localhost:8000/metrics | grep scorpius

# Configuration Tests
Write-Host "`n10. Configuration Tests..." -ForegroundColor Yellow

# Test environment loading
Write-Host "   - Environment config..." -ForegroundColor Cyan
python -c "from backend.config import settings; print('Environment:', settings.ENVIRONMENT)"

# Test database URL
Write-Host "   - Database URL..." -ForegroundColor Cyan
python -c "from backend.config import settings; print('DB URL set:', bool(settings.DATABASE_URL))"

# Test secret key
Write-Host "   - Secret key..." -ForegroundColor Cyan
python -c "from backend.config import settings; print('Secret key set:', bool(settings.SECRET_KEY))"

# Background Tasks Tests
Write-Host "`n11. Background Tasks Tests..." -ForegroundColor Yellow

# Test Celery workers (if using Celery)
Write-Host "   - Celery workers..." -ForegroundColor Cyan
Write-Host "     celery -A backend.tasks worker --loglevel=info" -ForegroundColor Gray

# Test scheduled tasks
Write-Host "   - Scheduled tasks..." -ForegroundColor Cyan
python backend/scheduler/test_scheduler.py

# Test async tasks
Write-Host "   - Async tasks..." -ForegroundColor Cyan
python backend/tasks/test_async_tasks.py

# Integration with External Services
Write-Host "`n12. External Service Integration..." -ForegroundColor Yellow

# Test Redis connection
Write-Host "   - Redis connection..." -ForegroundColor Cyan
python -c "import redis; r=redis.Redis(); print('Redis ping:', r.ping())"

# Test email service
Write-Host "   - Email service..." -ForegroundColor Cyan
python backend/email/test_email.py

# Test external APIs
Write-Host "   - External APIs..." -ForegroundColor Cyan
python backend/external/test_api_clients.py

# Expected successful output
Write-Host "`n=== EXPECTED SUCCESSFUL OUTPUT ===" -ForegroundColor Green
Write-Host "Server: INFO:     Uvicorn running on http://0.0.0.0:8000
Health: {'status': 'healthy', 'timestamp': '2025-06-23T...'}
Database: DB Connected: <sqlalchemy.engine.base.Connection object>
Auth: JWT token generated successfully
MEV: Strategies loaded: 5 active strategies
Performance: Response time < 100ms, Memory < 50%" -ForegroundColor Gray

Write-Host "`n=== TROUBLESHOOTING ===" -ForegroundColor Red
Write-Host "Common backend issues:"
Write-Host "1. Import errors: Check PYTHONPATH and virtual environment"
Write-Host "2. Database connection: Verify database is running and credentials"
Write-Host "3. Port in use: Kill existing processes or use different port"
Write-Host "4. Missing environment variables: Check .env file"
Write-Host "5. Authentication errors: Verify JWT secret and token format"

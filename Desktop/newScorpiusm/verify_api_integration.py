#!/usr/bin/env python3
"""
Comprehensive Backend-Frontend API Integration Verification
Checks database models, API routes, and frontend service alignment
"""

import os
import re
import json
import sys
from pathlib import Path

def check_environment_vars():
    """Check frontend environment variables for API endpoints"""
    print("🔧 Environment Variables:")
    env_files = ['.env', '.env.local', 'frontend/.env', 'frontend/.env.local']
    found_vars = {}
    
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"  ✅ Found {env_file}")
            with open(env_file, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            if 'API' in key or 'WS' in key:
                                found_vars[key] = value
    
    # Check frontend test setup
    setup_file = 'frontend/src/test/setup.ts'
    if os.path.exists(setup_file):
        print(f"  ✅ Found {setup_file}")
        with open(setup_file, 'r') as f:
            content = f.read()
            api_vars = re.findall(r"vi\.stubEnv\('([^']*)', '([^']*)'\)", content)
            for var, value in api_vars:
                found_vars[var] = value
    
    print("  📍 API Endpoint Configuration:")
    for key, value in found_vars.items():
        print(f"    {key}: {value}")
    
    return found_vars

def analyze_backend_routes():
    """Analyze backend API routes"""
    print("\n🔙 Backend API Routes:")
    routes_dir = 'backend/routes'
    fastapi_routes = []
    flask_routes = []
    
    if os.path.exists(routes_dir):
        for file in os.listdir(routes_dir):
            if file.endswith('.py'):
                file_path = os.path.join(routes_dir, file)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Check for FastAPI routes
                    fastapi_patterns = [
                        r'@router\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',
                        r'@app\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']'
                    ]
                    
                    for pattern in fastapi_patterns:
                        matches = re.findall(pattern, content)
                        for method, route in matches:
                            fastapi_routes.append((file, method.upper(), route))
                    
                    # Check for Flask routes
                    flask_patterns = [
                        r'@[^.]+\.route\s*\(\s*["\']([^"\']+)["\'].*methods\s*=\s*\[([^\]]+)\]',
                        r'@[^.]+\.route\s*\(\s*["\']([^"\']+)["\']'
                    ]
                    
                    for pattern in flask_patterns:
                        matches = re.findall(pattern, content)
                        for match in matches:
                            if len(match) == 2:
                                route, methods = match
                                methods = methods.replace('"', '').replace("'", '').split(',')
                                for method in methods:
                                    flask_routes.append((file, method.strip().upper(), route))
                            else:
                                flask_routes.append((file, 'GET', match))
    
    print(f"  🚀 FastAPI Routes ({len(fastapi_routes)}):")
    for file, method, route in fastapi_routes[:10]:  # Show first 10
        print(f"    {method:6} {route:30} ({file})")
    
    print(f"  🌶️  Flask Routes ({len(flask_routes)}):")
    for file, method, route in flask_routes[:10]:  # Show first 10
        print(f"    {method:6} {route:30} ({file})")
    
    return fastapi_routes + flask_routes

def analyze_database_models():
    """Analyze database models"""
    print("\n🗄️  Database Models:")
    models_files = ['backend/models.py', 'backend/models_clean.py', 'backend/database.py']
    
    models = []
    for file_path in models_files:
        if os.path.exists(file_path):
            print(f"  ✅ Found {file_path}")
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Look for SQLAlchemy models
                class_matches = re.findall(r'class\s+(\w+)\s*\([^)]*Model[^)]*\):', content)
                table_matches = re.findall(r'__tablename__\s*=\s*["\']([^"\']+)["\']', content)
                
                models.extend(class_matches)
                print(f"    📋 Models: {', '.join(class_matches)}")
                print(f"    📊 Tables: {', '.join(table_matches)}")
    
    return models

def analyze_frontend_services():
    """Analyze frontend API service files"""
    print("\n🎨 Frontend API Services:")
    services_dir = 'frontend/src/services'
    
    if not os.path.exists(services_dir):
        print("  ❌ Services directory not found")
        return []
    
    api_calls = []
    for file in os.listdir(services_dir):
        if file.endswith('.ts'):
            file_path = os.path.join(services_dir, file)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Look for API calls
                api_patterns = [
                    r'fetch\s*\(\s*[`"\']([^`"\']+)[`"\']',
                    r'axios\.(get|post|put|delete|patch)\s*\(\s*[`"\']([^`"\']+)[`"\']',
                    r'api\.(get|post|put|delete|patch)\s*\(\s*[`"\']([^`"\']+)[`"\']'
                ]
                
                for pattern in api_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        if isinstance(match, tuple):
                            if len(match) == 2:
                                method, endpoint = match
                                api_calls.append((file, method.upper(), endpoint))
                            else:
                                api_calls.append((file, 'GET', match[0]))
                        else:
                            api_calls.append((file, 'GET', match))
    
    print(f"  🔄 API Calls Found ({len(api_calls)}):")
    for file, method, endpoint in api_calls[:15]:  # Show first 15
        print(f"    {method:6} {endpoint:40} ({file})")
    
    return api_calls

def check_database_connection():
    """Check database configuration"""
    print("\n💾 Database Configuration:")
    
    # Check database config files
    db_files = [
        'backend/database.py',
        'backend/config.py', 
        'backend/settings.py',
        '.env'
    ]
    
    db_config = {}
    for file_path in db_files:
        if os.path.exists(file_path):
            print(f"  ✅ Found {file_path}")
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Look for database URLs and configs
                db_patterns = [
                    r'DATABASE_URL\s*=\s*["\']([^"\']+)["\']',
                    r'SQLALCHEMY_DATABASE_URI\s*=\s*["\']([^"\']+)["\']',
                    r'DB_HOST\s*=\s*["\']([^"\']+)["\']',
                    r'DB_NAME\s*=\s*["\']([^"\']+)["\']'
                ]
                
                for pattern in db_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        key = pattern.split('\\')[0]
                        db_config[key] = match
    
    print("  🔗 Database Settings:")
    for key, value in db_config.items():
        # Mask sensitive info
        if 'password' in value.lower() or 'pass' in value.lower():
            value = value[:10] + "***"
        print(f"    {key}: {value}")
    
    return db_config

def verify_cors_configuration():
    """Check CORS configuration for frontend-backend communication"""
    print("\n🌐 CORS Configuration:")
    
    cors_files = [
        'backend/main.py',
        'backend/app.py',
        'backend/main_minimal.py'
    ]
    
    cors_found = False
    for file_path in cors_files:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                if 'CORS' in content or 'cors' in content:
                    cors_found = True
                    print(f"  ✅ CORS configuration found in {file_path}")
                    
                    # Extract CORS origins
                    origins_pattern = r'origins\s*=\s*\[([^\]]+)\]'
                    origins = re.findall(origins_pattern, content)
                    if origins:
                        print(f"    🎯 Allowed origins: {origins[0]}")
    
    if not cors_found:
        print("  ⚠️  No CORS configuration found - may cause frontend connection issues")
    
    return cors_found

def generate_integration_report():
    """Generate comprehensive integration report"""
    print("=" * 60)
    print("🔍 BACKEND-FRONTEND API INTEGRATION ANALYSIS")
    print("=" * 60)
    
    # Run all checks
    env_vars = check_environment_vars()
    backend_routes = analyze_backend_routes()
    models = analyze_database_models()
    frontend_calls = analyze_frontend_services()
    db_config = check_database_connection()
    cors_enabled = verify_cors_configuration()
    
    # Generate summary
    print("\n📊 INTEGRATION SUMMARY:")
    print("=" * 30)
    print(f"✅ Environment Variables: {len(env_vars)} found")
    print(f"🔙 Backend Routes: {len(backend_routes)} endpoints")
    print(f"🗄️  Database Models: {len(models)} models")
    print(f"🎨 Frontend API Calls: {len(frontend_calls)} calls")
    print(f"🌐 CORS Enabled: {'Yes' if cors_enabled else 'No'}")
    
    # Check for potential issues
    print("\n⚠️  POTENTIAL ISSUES:")
    issues = []
    
    if len(backend_routes) == 0:
        issues.append("No backend routes found")
    
    if len(models) == 0:
        issues.append("No database models found")
    
    if len(frontend_calls) == 0:
        issues.append("No frontend API calls found")
    
    if not cors_enabled:
        issues.append("CORS not configured - frontend may not connect")
    
    if not env_vars:
        issues.append("No API environment variables found")
    
    if issues:
        for issue in issues:
            print(f"  ❌ {issue}")
    else:
        print("  🎉 No major issues detected!")
    
    print("\n🚀 NEXT STEPS:")
    if backend_routes and frontend_calls:
        print("  1. Start backend server")
        print("  2. Start frontend dev server") 
        print("  3. Test API connections in browser")
        print("  4. Verify database operations")
    else:
        print("  1. Fix missing API routes or frontend services")
        print("  2. Ensure CORS is properly configured")
        print("  3. Verify environment variables")

if __name__ == "__main__":
    try:
        generate_integration_report()
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        sys.exit(1)

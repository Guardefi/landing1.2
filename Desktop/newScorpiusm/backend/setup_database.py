#!/usr/bin/env python3
"""
Database Setup Script
Initializes the database and creates a default admin user
"""

import hashlib
import os
import sys
from datetime import datetime

from models import MEVStrategy, User, get_db, init_database
from services.blockchain import Web3Service

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import from the root models.py file

# Try to import blockchain service
try:
    except ImportError as e:
    Web3Service = None
    logger.error(f"Error: {e}")}")
        db.rollback()
        return

    print("\n🎉 Database setup completed successfully!")
    print("\n📝 You can now:")
    print("   1. Start the backend server: python app.py")
    print("   2. Login with admin/admin123 or demo/demo")
    print("   3. Access the API at http://localhost:5000")
    # Test Web3 connection
    print("\n🔗 Testing Web3 connection...")
    try:
        if Web3Service:
            web3_service = Web3Service()
            if web3_service.is_connected:
                print("✅ Web3 connection successful!")
            else:
                print("⚠️  Web3 connection failed - check your RPC URL")
        else:
            print("⚠️  Web3Service not available")
    except Exception as e:
        print(f"⚠️  Web3 connection error: {str(e)}")

    print("\n🔧 Environment Variables:")
    print(f"   WEB3_RPC_URL: {os.getenv('WEB3_RPC_URL', 'Not set (using default)')}")
    print(f"   DATABASE_URL: {os.getenv('DATABASE_URL', 'Not set (using SQLite)')}")


if __name__ == "__main__":
    setup_database()

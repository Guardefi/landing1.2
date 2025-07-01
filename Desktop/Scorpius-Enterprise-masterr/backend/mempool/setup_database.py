#!/usr/bin/env python3
"""
Database setup script for Elite Mempool System
Creates database, user, and applies schema
"""

import sys
from pathlib import Path

import psycopg2


def setup_database():
    """Set up the database and apply schema"""

    # Database configuration
    db_configs = [
        {
            "host": "localhost",
            "port": 5432,
            "user": "postgres",
            "password": "password",
            "database": "postgres",
        },
        {
            "host": "localhost",
            "port": 5432,
            "user": "postgres",
            "password": "",
            "database": "postgres",
        },
        {
            "host": "localhost",
            "port": 5432,
            "user": "postgres",
            "password": "postgres",
            "database": "postgres",
        },
    ]

    print("🔍 Setting up Elite Mempool Database...")

    conn = None
    for config in db_configs:
        try:
            print(f"Trying to connect with user: {config['user']}")
            conn = psycopg2.connect(**config)
            print("✅ Connected to PostgreSQL")
            break
        except Exception as e:
            print(f"❌ Failed with {config['user']}: {e}")
            continue

    if not conn:
        print("❌ Could not connect to PostgreSQL with any credentials")
        return False

    try:
        conn.autocommit = True
        cursor = conn.cursor()

        # Create database
        try:
            cursor.execute("CREATE DATABASE elite_mempool_db;")
            print("✅ Database 'elite_mempool_db' created")
        except psycopg2.errors.DuplicateDatabase:
            print("ℹ️  Database 'elite_mempool_db' already exists")

        # Create user
        try:
            cursor.execute("CREATE USER elite_user WITH PASSWORD 'elite_password';")
            print("✅ User 'elite_user' created")
        except psycopg2.errors.DuplicateObject:
            print("ℹ️  User 'elite_user' already exists")

        # Grant privileges
        cursor.execute(
            "GRANT ALL PRIVILEGES ON DATABASE elite_mempool_db TO elite_user;"
        )
        print("✅ Privileges granted")

        cursor.close()
        conn.close()

        # Now connect to the new database and apply schema
        print("\n📊 Applying database schema...")

        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="elite_user",
            password="elite_password",
            database="elite_mempool_db",
        )

        cursor = conn.cursor()

        # Read and apply schema
        schema_path = Path("database/schema.sql")
        if schema_path.exists():
            with open(schema_path, "r") as f:
                schema_sql = f.read()

            # Split into individual statements and execute
            statements = [
                stmt.strip() for stmt in schema_sql.split(";") if stmt.strip()
            ]

            for i, statement in enumerate(statements):
                try:
                    cursor.execute(statement)
                    print(f"✅ Executed statement {i + 1}/{len(statements)}")
                except Exception as e:
                    print(f"⚠️  Statement {i + 1} warning: {e}")

            conn.commit()
            print("✅ Schema applied successfully")
        else:
            print("⚠️  Schema file not found at database/schema.sql")

        cursor.close()
        conn.close()

        print("🎉 Database setup completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        if conn:
            conn.close()
        return False


if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)

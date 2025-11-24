"""
Script to create PostgreSQL database
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Connect to PostgreSQL server (not to a specific database)
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    user="postgres",
    password="123"
)

# Set autocommit mode
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

# Create database
cursor = conn.cursor()

# Check if database exists
cursor.execute("SELECT 1 FROM pg_database WHERE datname='Evena'")
exists = cursor.fetchone()

if not exists:
    cursor.execute('CREATE DATABASE "Evena"')
    print("✅ Database 'Evena' created successfully")
else:
    print("ℹ️  Database 'Evena' already exists")

cursor.close()
conn.close()

print("\nNow creating tables...")

# Now create tables
from database import create_tables
create_tables()
print("✅ All database tables created successfully!")

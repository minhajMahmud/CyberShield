"""
setup_database.py
-----------------
Sets up the CyberShield database using SQLAlchemy ORM models.
Run this after configuring .env file.
"""

import os
from dotenv import load_dotenv
import pymysql
from app import create_app
from models import db, User
from flask_bcrypt import Bcrypt

# Load environment variables
load_dotenv()

def create_database_if_not_exists():
    """Create the database if it doesn't exist."""
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", 3306))
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "")
    db_name = os.getenv("DB_NAME", "cybershield_db")
    
    print(f"Connecting to MySQL server at {db_host}:{db_port}...")
    
    # Connect without specifying a database
    connection = pymysql.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password
    )
    
    try:
        with connection.cursor() as cursor:
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"Database '{db_name}' created or already exists.")
        connection.commit()
    finally:
        connection.close()

# Create database first
create_database_if_not_exists()

# Create Flask app
app = create_app()
bcrypt = Bcrypt(app)

def setup_database():
    """Create all tables and seed admin user."""
    with app.app_context():
        print("Creating database tables...")
        
        # Drop all tables and recreate (be careful in production!)
        db.drop_all()
        db.create_all()
        
        print("Tables created successfully!")
        
        # Create admin user
        # Password: Admin@12345 (CHANGE THIS IMMEDIATELY!)
        admin_password_hash = bcrypt.generate_password_hash('Admin@12345').decode('utf-8')
        
        admin_user = User(
            username='admin',
            email='admin@cybershield.local',
            password_hash=admin_password_hash,
            full_name='System Administrator',
            role='admin',
            is_active_flag=True
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        print(f"Admin user created successfully!")
        print(f"  Username: admin")
        print(f"  Password: Admin@12345")
        print(f"  Email: admin@cybershield.local")
        print(f"\n⚠️  IMPORTANT: Change the admin password immediately after first login!")
        print(f"\nDatabase setup complete! ✅")

if __name__ == "__main__":
    setup_database()

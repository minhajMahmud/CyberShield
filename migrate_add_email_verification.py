"""
Migration script to add email verification support
--------------------------------------------------
Adds:
1. email_verified column to Users table
2. email_verification purpose to OTP enum
"""

import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

db_host = os.getenv("DB_HOST", "localhost")
db_port = int(os.getenv("DB_PORT", 3306))
db_user = os.getenv("DB_USER", "root")
db_password = os.getenv("DB_PASSWORD", "")
db_name = os.getenv("DB_NAME", "cybershield_db")

print("=" * 70)
print("CyberShield Database Migration: Add Email Verification")
print("=" * 70)

connection = pymysql.connect(
    host=db_host,
    port=db_port,
    user=db_user,
    password=db_password,
    database=db_name
)

try:
    with connection.cursor() as cursor:
        print("\n1️⃣  Adding email_verified column to Users table...")
        try:
            cursor.execute("""
                ALTER TABLE Users 
                ADD COLUMN email_verified BOOLEAN NOT NULL DEFAULT FALSE
                AFTER is_active
            """)
            print("   ✅ email_verified column added successfully")
        except pymysql.err.OperationalError as e:
            if "Duplicate column name" in str(e):
                print("   ⚠️  email_verified column already exists, skipping...")
            else:
                raise

        print("\n2️⃣  Updating OTP purpose enum...")
        try:
            # Drop the constraint first
            cursor.execute("""
                ALTER TABLE OTP 
                MODIFY COLUMN purpose 
                ENUM('login', 'enable_2fa', 'reset_password', 'email_verification') 
                NOT NULL DEFAULT 'login'
            """)
            print("   ✅ OTP purpose enum updated successfully")
        except pymysql.err.OperationalError as e:
            print(f"   ⚠️  Enum update warning: {e}")

        print("\n3️⃣  Setting existing users as email verified...")
        cursor.execute("""
            UPDATE Users 
            SET email_verified = TRUE 
            WHERE email_verified = FALSE
        """)
        affected = cursor.rowcount
        print(f"   ✅ {affected} existing users marked as email verified")

        connection.commit()
        print("\n" + "=" * 70)
        print("✅ Migration completed successfully!")
        print("=" * 70)
        print("\nChanges applied:")
        print("  • Added email_verified column to Users table")
        print("  • Updated OTP purpose enum to include 'email_verification'")
        print("  • Marked all existing users as email verified")
        print("\nEmail verification is now active for new registrations!")

except Exception as e:
    connection.rollback()
    print(f"\n❌ Migration failed: {e}")
    raise
finally:
    connection.close()

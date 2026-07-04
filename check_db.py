"""
Check if database exists and show all databases
"""
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

db_host = os.getenv("DB_HOST", "localhost")
db_port = int(os.getenv("DB_PORT", 3306))
db_user = os.getenv("DB_USER", "root")
db_password = os.getenv("DB_PASSWORD", "")

print(f"Connecting to MySQL at {db_host}:{db_port} as {db_user}...")

try:
    connection = pymysql.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password
    )
    
    with connection.cursor() as cursor:
        # Show all databases
        print("\n" + "="*60)
        print("ALL DATABASES:")
        print("="*60)
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        for db in databases:
            print(f"  • {db[0]}")
        
        # Check if cybershield_db exists
        print("\n" + "="*60)
        cursor.execute("SHOW DATABASES LIKE 'cybershield_db'")
        result = cursor.fetchone()
        if result:
            print("✅ cybershield_db EXISTS")
            
            # Show tables in cybershield_db
            cursor.execute("USE cybershield_db")
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"\nTables in cybershield_db ({len(tables)} tables):")
            for table in tables:
                print(f"  • {table[0]}")
        else:
            print("❌ cybershield_db DOES NOT EXIST")
        print("="*60)
        
    connection.close()
    print("\n✅ Connection successful!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")

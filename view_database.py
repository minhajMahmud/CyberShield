"""
view_database.py
----------------
Script to view the CyberShield database structure and content.
"""

import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

# Database connection details
db_host = os.getenv("DB_HOST", "localhost")
db_port = int(os.getenv("DB_PORT", 3306))
db_user = os.getenv("DB_USER", "root")
db_password = os.getenv("DB_PASSWORD", "")
db_name = os.getenv("DB_NAME", "cybershield_db")

print("=" * 80)
print(f"CYBERSHIELD DATABASE: {db_name}")
print("=" * 80)

# Connect to MySQL
connection = pymysql.connect(
    host=db_host,
    port=db_port,
    user=db_user,
    password=db_password,
    database=db_name
)

try:
    with connection.cursor() as cursor:
        # Show all tables
        print("\n📋 TABLES IN DATABASE:")
        print("-" * 80)
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        for table in tables:
            print(f"  • {table[0]}")
        
        print("\n" + "=" * 80)
        
        # For each table, show structure and data
        for table in tables:
            table_name = table[0]
            
            print(f"\n📊 TABLE: {table_name}")
            print("-" * 80)
            
            # Show table structure
            print("\n🏗️  STRUCTURE:")
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            for col in columns:
                field, type_, null, key, default, extra = col
                key_info = f" [{key}]" if key else ""
                null_info = "NULL" if null == "YES" else "NOT NULL"
                default_info = f" DEFAULT {default}" if default else ""
                extra_info = f" {extra}" if extra else ""
                print(f"  {field}: {type_} {null_info}{key_info}{default_info}{extra_info}")
            
            # Show row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"\n📈 ROWS: {count}")
            
            # Show data if there are rows
            if count > 0:
                print(f"\n📄 DATA:")
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                # Get column names
                cursor.execute(f"DESCRIBE {table_name}")
                col_names = [col[0] for col in cursor.fetchall()]
                
                for i, row in enumerate(rows, 1):
                    print(f"\n  Row {i}:")
                    for col_name, value in zip(col_names, row):
                        # Truncate long values
                        if isinstance(value, str) and len(value) > 60:
                            value = value[:60] + "..."
                        print(f"    {col_name}: {value}")
            
            print("\n" + "=" * 80)
        
        # Database statistics
        print("\n📊 DATABASE STATISTICS:")
        print("-" * 80)
        cursor.execute("""
            SELECT 
                table_name,
                table_rows,
                ROUND((data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
            FROM information_schema.tables 
            WHERE table_schema = %s
            ORDER BY table_name
        """, (db_name,))
        stats = cursor.fetchall()
        for stat in stats:
            table, rows, size = stat
            print(f"  {table}: {rows} rows, {size} MB")
        
finally:
    connection.close()

print("\n" + "=" * 80)
print("DATABASE VIEW COMPLETE")
print("=" * 80)

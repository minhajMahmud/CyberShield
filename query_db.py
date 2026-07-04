"""
Query CyberShield database and display results
"""
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

db_host = os.getenv("DB_HOST", "localhost")
db_port = int(os.getenv("DB_PORT", 3306))
db_user = os.getenv("DB_USER", "root")
db_password = os.getenv("DB_PASSWORD", "")

connection = pymysql.connect(
    host=db_host,
    port=db_port,
    user=db_user,
    password=db_password,
    database="cybershield_db"
)

print("=" * 80)
print("CYBERSHIELD DATABASE - QUERY RESULTS")
print("=" * 80)

with connection.cursor() as cursor:
    # Show all tables
    print("\n1️⃣  SHOW TABLES;")
    print("-" * 80)
    cursor.execute("SHOW TABLES")
    for row in cursor.fetchall():
        print(f"   {row[0]}")
    
    # Show users
    print("\n2️⃣  SELECT * FROM users;")
    print("-" * 80)
    cursor.execute("SELECT id, username, email, full_name, role, is_2fa_enabled, last_login FROM users")
    print(f"{'ID':<5} {'Username':<15} {'Email':<30} {'Full Name':<25} {'Role':<10} {'2FA':<5} {'Last Login':<20}")
    print("-" * 80)
    for row in cursor.fetchall():
        last_login = str(row[6])[:19] if row[6] else "Never"
        print(f"{row[0]:<5} {row[1]:<15} {row[2]:<30} {row[3] or 'N/A':<25} {row[4]:<10} {row[5]:<5} {last_login:<20}")
    
    # Show files
    print("\n3️⃣  SELECT * FROM files WHERE is_deleted = 0;")
    print("-" * 80)
    cursor.execute("SELECT id, user_id, original_filename, file_size, file_type, uploaded_at FROM files WHERE is_deleted = 0")
    files = cursor.fetchall()
    if files:
        print(f"{'ID':<5} {'User ID':<10} {'Filename':<40} {'Size (KB)':<12} {'Type':<8} {'Uploaded':<20}")
        print("-" * 80)
        for row in files:
            size_kb = round(row[3] / 1024, 2)
            uploaded = str(row[5])[:19] if row[5] else "N/A"
            print(f"{row[0]:<5} {row[1]:<10} {row[2][:38]:<40} {size_kb:<12} {row[4]:<8} {uploaded:<20}")
    else:
        print("   No files found")
    
    # Show activity log
    print("\n4️⃣  SELECT * FROM activity_log ORDER BY created_at DESC LIMIT 10;")
    print("-" * 80)
    cursor.execute("""
        SELECT a.id, u.username, a.action, a.description, a.ip_address, a.created_at
        FROM activity_log a
        LEFT JOIN users u ON a.user_id = u.id
        ORDER BY a.created_at DESC
        LIMIT 10
    """)
    print(f"{'ID':<5} {'User':<15} {'Action':<20} {'Description':<35} {'IP':<15} {'Time':<20}")
    print("-" * 80)
    for row in cursor.fetchall():
        desc = (row[3] or "")[:33]
        created = str(row[5])[:19] if row[5] else "N/A"
        print(f"{row[0]:<5} {row[1] or 'Anonymous':<15} {row[2]:<20} {desc:<35} {row[4] or 'N/A':<15} {created:<20}")
    
    # Show password check history summary
    print("\n5️⃣  SELECT COUNT(*), strength_label FROM password_check_history GROUP BY strength_label;")
    print("-" * 80)
    cursor.execute("SELECT strength_label, COUNT(*) FROM password_check_history GROUP BY strength_label ORDER BY strength_label")
    print(f"{'Strength Level':<20} {'Count':<10}")
    print("-" * 80)
    for row in cursor.fetchall():
        print(f"{row[0]:<20} {row[1]:<10}")
    
    # Show table row counts
    print("\n6️⃣  TABLE ROW COUNTS:")
    print("-" * 80)
    tables = ['users', 'files', 'activity_log', 'digital_signatures', 'otp', 'password_check_history']
    print(f"{'Table Name':<30} {'Row Count':<10}")
    print("-" * 80)
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table:<30} {count:<10}")

connection.close()

print("\n" + "=" * 80)
print("QUERY COMPLETE ✅")
print("=" * 80)

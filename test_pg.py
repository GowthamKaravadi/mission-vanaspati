import psycopg2

print("Testing PostgreSQL connection...")
print("Username: missionvanaspati")
print("Database: vanaspati_db")

try:
    conn = psycopg2.connect(
        host="localhost",
        database="vanaspati_db",
        user="missionvanaspati",
        password="mI$$ion_van@spati",
        port=5432
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("✓ Connection successful!")
    
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"PostgreSQL version: {version[0]}")
    
    cursor.close()
    conn.close()
    
except psycopg2.OperationalError as e:
    print(f"\n✗ Connection failed!")
    print(f"Error: {e}")
    print("\nPossible issues:")
    print("1. User 'missionvanaspati' doesn't exist or password is incorrect")
    print("2. Database 'vanaspati_db' doesn't exist")
    print("3. User doesn't have access permissions to the database")
    print("\nTo fix in pgAdmin:")
    print("1. Check if user 'missionvanaspati' exists")
    print("2. Check if database 'vanaspati_db' exists")
    print("3. Grant permissions: GRANT ALL PRIVILEGES ON DATABASE vanaspati_db TO missionvanaspati;")
except Exception as e:
    print(f"Unexpected error: {e}")

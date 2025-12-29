import psycopg2

print("Checking database tables...\n")

try:
    conn = psycopg2.connect(
        host="localhost",
        database="vanaspati_db",
        user="missionvanaspati",
        password="mI$$ion_van@spati",
        port=5432
    )
    cursor = conn.cursor()
    
    # Get list of tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    
    tables = cursor.fetchall()
    
    if tables:
        print("✓ Tables found in vanaspati_db:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Get structure of users table
        print("\n✓ Users table structure:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'users'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[0]}: {col[1]} (Nullable: {col[2]})")
        
        # Count users
        cursor.execute("SELECT COUNT(*) FROM users;")
        count = cursor.fetchone()[0]
        print(f"\n✓ Current users in database: {count}")
        
    else:
        print("✗ No tables found in the database")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")

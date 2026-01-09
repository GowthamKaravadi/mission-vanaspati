"""
Add products column to remedies table
"""
import psycopg2

DB_CONFIG = {
    'dbname': 'vanaspati_db',
    'user': 'missionvanaspati',
    'password': 'mI$$ion_van@spati',
    'host': 'localhost',
    'port': 5432
}

def add_products_column():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Adding products column to remedies table...")
        
        cursor.execute("""
            ALTER TABLE remedies 
            ADD COLUMN IF NOT EXISTS products JSONB;
        """)
        
        conn.commit()
        print("✓ Successfully added products column")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if conn:
            conn.rollback()

if __name__ == "__main__":
    add_products_column()

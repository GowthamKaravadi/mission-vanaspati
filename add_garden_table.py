"""
Database migration to add saved_plants table for Plant Garden feature
"""
import psycopg2
from urllib.parse import quote_plus

# Database configuration
password = quote_plus("mI$$ion_van@spati")
DB_CONFIG = {
    'dbname': 'vanaspati_db',
    'user': 'missionvanaspati',
    'password': 'mI$$ion_van@spati',
    'host': 'localhost',
    'port': 5432
}

def add_garden_table():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Creating saved_plants table...")
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS saved_plants (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            plant_name VARCHAR NOT NULL,
            disease_name VARCHAR NOT NULL,
            confidence FLOAT NOT NULL,
            image_path VARCHAR,
            notes TEXT,
            status VARCHAR DEFAULT 'monitoring',
            diagnosed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        cursor.execute(create_table_query)
        conn.commit()
        print("✓ Successfully created saved_plants table")
        
        # Create index for faster queries
        print("Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_saved_plants_user_id ON saved_plants(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_saved_plants_diagnosed_at ON saved_plants(diagnosed_at DESC);")
        conn.commit()
        print("✓ Successfully created indexes")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Garden table migration completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if conn:
            conn.rollback()

if __name__ == "__main__":
    add_garden_table()

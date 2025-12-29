"""
Migration script to add username column to users table
Run this script to update existing database
"""

from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
import sys

# PostgreSQL configuration
password = quote_plus("mI$$ion_van@spati")
DATABASE_URL = f"postgresql://missionvanaspati:{password}@localhost:5432/vanaspati_db"

def add_username_column():
    """Add username column to users table"""
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Check if username column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='username'
            """))
            
            if result.fetchone():
                print("✓ Username column already exists")
                return
            
            print("Adding username column to users table...")
            
            # Add username column (allow NULL temporarily)
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN username VARCHAR
            """))
            
            # Set default usernames from email (part before @)
            conn.execute(text("""
                UPDATE users 
                SET username = SPLIT_PART(email, '@', 1)
            """))
            
            # Make username NOT NULL and UNIQUE
            conn.execute(text("""
                ALTER TABLE users 
                ALTER COLUMN username SET NOT NULL
            """))
            
            conn.execute(text("""
                CREATE UNIQUE INDEX users_username_key 
                ON users(username)
            """))
            
            conn.commit()
            
            print("✓ Successfully added username column")
            print("✓ Set default usernames from email addresses")
            print("✓ Made username column NOT NULL and UNIQUE")
            print("\nMigration completed successfully!")
            
    except Exception as e:
        print(f"✗ Error during migration: {e}")
        sys.exit(1)
    finally:
        engine.dispose()

if __name__ == "__main__":
    print("=" * 60)
    print("Database Migration: Adding Username Column")
    print("=" * 60)
    add_username_column()

"""
Migration: Add diagnosis_history table
"""
from src.database import Base, engine, SessionLocal, DiagnosisHistory
from sqlalchemy import inspect

try:
    # Create diagnosis_history table
    Base.metadata.create_all(bind=engine, tables=[DiagnosisHistory.__table__])
    print("✓ Successfully created diagnosis_history table")
    
    # Verify table structure
    inspector = inspect(engine)
    columns = inspector.get_columns('diagnosis_history')
    indexes = inspector.get_indexes('diagnosis_history')
    
    print("\nTable structure:")
    for col in columns:
        print(f"  - {col['name']}: {col['type']} (nullable: {col['nullable']})")
    
    print("\nIndexes:")
    for idx in indexes:
        print(f"  - {idx['name']}: {idx['column_names']}")
    
    # Test connection
    db = SessionLocal()
    count = db.query(DiagnosisHistory).count()
    db.close()
    print(f"\n✓ Table is accessible. Current records: {count}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    raise

print("\n✓ Migration completed successfully!")

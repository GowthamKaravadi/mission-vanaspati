import json
from src.database import SessionLocal, Remedy, init_db

# Initialize database and create tables
init_db()

# Load remedies from JSON
with open('remedies.json', 'r') as f:
    remedies_data = json.load(f)

db = SessionLocal()

try:
    # Clear existing remedies
    db.query(Remedy).delete()
    
    # Insert new remedies
    for class_name, info in remedies_data.items():
        remedy = Remedy(
            class_name=class_name,
            description=info.get('description', ''),
            remedies=info.get('remedies', [])
        )
        db.add(remedy)
    
    db.commit()
    print(f"✓ Successfully loaded {len(remedies_data)} remedies into database!")
    
    # Verify
    count = db.query(Remedy).count()
    print(f"✓ Total remedies in database: {count}")
    
except Exception as e:
    db.rollback()
    print(f"✗ Error loading remedies: {e}")
finally:
    db.close()

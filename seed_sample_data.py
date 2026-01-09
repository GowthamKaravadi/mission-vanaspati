"""
Seed script to add sample data to the database.
Run: python seed_sample_data.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime, timedelta
import random
from src.database import SessionLocal, User, Feedback, SavedPlant, DiagnosisHistory, init_db

# Sample disease classes (from your 44 classes)
DISEASE_CLASSES = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Tomato___Late_blight",
    "Tomato___Early_blight",
    "Tomato___Bacterial_spot",
    "Tomato___healthy",
    "Potato___Late_blight",
    "Potato___Early_blight",
    "Potato___healthy",
    "Corn___Common_rust",
    "Corn___Northern_Leaf_Blight",
    "Corn___healthy",
    "Grape___Black_rot",
    "Grape___healthy",
    "Pepper_bell___Bacterial_spot",
    "Pepper_bell___healthy",
    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",
]

# Common password for all test users
TEST_PASSWORD = "Test@1234"


def seed_users(db):
    """Create 15 sample users with 2 admins."""
    users_data = [
        # Admins
        {"username": "admin", "email": "admin@vanaspati.com", "is_admin": True},
        {"username": "superadmin", "email": "superadmin@vanaspati.com", "is_admin": True},
        # Regular users
        {"username": "rahul_sharma", "email": "rahul.sharma@gmail.com", "is_admin": False},
        {"username": "priya_patel", "email": "priya.patel@yahoo.com", "is_admin": False},
        {"username": "amit_kumar", "email": "amit.kumar@outlook.com", "is_admin": False},
        {"username": "sneha_gupta", "email": "sneha.gupta@gmail.com", "is_admin": False},
        {"username": "vikram_singh", "email": "vikram.singh@hotmail.com", "is_admin": False},
        {"username": "anita_reddy", "email": "anita.reddy@gmail.com", "is_admin": False},
        {"username": "rajesh_nair", "email": "rajesh.nair@yahoo.com", "is_admin": False},
        {"username": "meera_joshi", "email": "meera.joshi@gmail.com", "is_admin": False},
        {"username": "suresh_yadav", "email": "suresh.yadav@outlook.com", "is_admin": False},
        {"username": "kavita_mishra", "email": "kavita.mishra@gmail.com", "is_admin": False},
        {"username": "farmer_john", "email": "john.farmer@agri.org", "is_admin": False},
        {"username": "garden_guru", "email": "guru@gardens.com", "is_admin": False},
        {"username": "plant_lover", "email": "plantlover@nature.com", "is_admin": False},
    ]
    
    created_users = []
    for user_data in users_data:
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if existing:
            print(f"  User '{user_data['username']}' already exists, skipping...")
            created_users.append(existing)
            continue
        
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=User.hash_password(TEST_PASSWORD),
            is_active=True,
            is_admin=user_data["is_admin"],
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 90))
        )
        db.add(user)
        created_users.append(user)
        print(f"  Created user: {user_data['username']} ({'Admin' if user_data['is_admin'] else 'User'})")
    
    db.commit()
    return created_users


def seed_feedback(db, users):
    """Create 15 sample feedback entries."""
    feedback_data = [
        {"subject": "Great app for farmers!", "message": "This app has helped me identify diseases in my tomato crop. Very accurate!", "type": "general", "status": "reviewed"},
        {"subject": "Bug in batch upload", "message": "When I upload more than 10 images, the app freezes for a few seconds.", "type": "bug", "status": "pending"},
        {"subject": "Add mango diseases", "message": "Please add support for mango leaf diseases. Very common in my region.", "type": "feature", "status": "pending"},
        {"subject": "Excellent accuracy", "message": "Detected late blight in my potato field with 95% confidence. Saved my crop!", "type": "general", "status": "reviewed"},
        {"subject": "Dark mode needed", "message": "Would love to have a dark mode option for night usage.", "type": "feature", "status": "resolved"},
        {"subject": "Login issue on mobile", "message": "Sometimes the login button doesn't respond on my Android phone.", "type": "bug", "status": "pending"},
        {"subject": "Offline mode request", "message": "Can you add offline prediction? Network is weak in rural areas.", "type": "feature", "status": "pending"},
        {"subject": "Thank you!", "message": "Your app helped me save my apple orchard from black rot. Eternally grateful!", "type": "general", "status": "reviewed"},
        {"subject": "Slow loading", "message": "The disease library takes too long to load on slow connections.", "type": "bug", "status": "pending"},
        {"subject": "Add regional languages", "message": "Please add Hindi and Marathi language support for farmers.", "type": "feature", "status": "pending"},
        {"subject": "Image quality warning", "message": "App should warn users if uploaded image is too blurry.", "type": "feature", "status": "resolved"},
        {"subject": "History not syncing", "message": "My diagnosis history doesn't show up on my other device.", "type": "bug", "status": "pending"},
        {"subject": "Love the remedies section", "message": "The treatment recommendations are very helpful and practical.", "type": "general", "status": "reviewed"},
        {"subject": "Export to PDF", "message": "Would be great to export diagnosis reports as PDF for record keeping.", "type": "feature", "status": "pending"},
        {"subject": "App crashed", "message": "App crashed when I tried to analyze a very large image (10MB).", "type": "bug", "status": "pending"},
    ]
    
    regular_users = [u for u in users if not u.is_admin]
    
    for i, fb_data in enumerate(feedback_data):
        user = random.choice(regular_users)
        feedback = Feedback(
            email=user.email,
            subject=fb_data["subject"],
            message=fb_data["message"],
            type=fb_data["type"],
            status=fb_data["status"],
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60))
        )
        db.add(feedback)
        print(f"  Created feedback: '{fb_data['subject'][:40]}...' ({fb_data['type']})")
    
    db.commit()


def seed_saved_plants(db, users):
    """Create 15 sample saved plants."""
    plant_names = [
        "My Tomato Plant", "Kitchen Garden Potato", "Backyard Apple Tree",
        "Balcony Pepper", "Farm Corn Batch 1", "Grape Vine Section A",
        "Strawberry Pot 1", "Main Field Tomatoes", "Organic Potatoes",
        "Heritage Apple", "Bell Pepper Row 2", "Sweet Corn Plot",
        "Wine Grapes", "Berry Garden", "Terrace Tomatoes"
    ]
    
    statuses = ["monitoring", "treating", "recovered", "monitoring", "treating"]
    regular_users = [u for u in users if not u.is_admin]
    
    for i, plant_name in enumerate(plant_names):
        user = regular_users[i % len(regular_users)]
        disease = random.choice(DISEASE_CLASSES)
        
        notes_options = [
            "Noticed spots last week, keeping an eye on it.",
            "Applied organic fungicide yesterday.",
            "Seems to be recovering after treatment.",
            "Need to check again in 3 days.",
            "Healthy so far, regular monitoring.",
            None, None  # Some plants without notes
        ]
        
        plant = SavedPlant(
            user_id=user.id,
            plant_name=plant_name,
            disease_name=disease,
            confidence=round(random.uniform(0.75, 0.99), 2),
            notes=random.choice(notes_options),
            status=random.choice(statuses),
            diagnosed_at=datetime.utcnow() - timedelta(days=random.randint(1, 45)),
            updated_at=datetime.utcnow() - timedelta(days=random.randint(0, 10))
        )
        db.add(plant)
        print(f"  Created plant: '{plant_name}' - {disease.split('___')[1]} ({plant.status})")
    
    db.commit()


def seed_diagnosis_history(db, users):
    """Create 15 sample diagnosis history entries."""
    regular_users = [u for u in users if not u.is_admin]
    
    for i in range(15):
        user = regular_users[i % len(regular_users)]
        disease = random.choice(DISEASE_CLASSES)
        confidence = round(random.uniform(0.70, 0.98), 2)
        
        # Generate alternative predictions
        other_diseases = [d for d in DISEASE_CLASSES if d != disease]
        alternatives = [
            {"class_name": random.choice(other_diseases), "confidence": round(random.uniform(0.05, 0.15), 2)},
            {"class_name": random.choice(other_diseases), "confidence": round(random.uniform(0.01, 0.08), 2)},
        ]
        
        diagnosis_type = random.choice(["single", "single", "single", "batch"])
        image_name = f"plant_image_{i+1:03d}.jpg" if diagnosis_type == "single" else f"batch_{i+1}_image.jpg"
        
        history = DiagnosisHistory(
            user_id=user.id,
            diagnosis_type=diagnosis_type,
            image_name=image_name,
            disease_name=disease,
            confidence=confidence,
            alternatives=alternatives,
            remedy_info={"description": f"Treatment info for {disease.split('___')[1]}"},
            diagnosed_at=datetime.utcnow() - timedelta(days=random.randint(1, 30), hours=random.randint(0, 23)),
            status="active"
        )
        db.add(history)
        print(f"  Created history: {disease.split('___')[1]} ({confidence:.0%}) - {diagnosis_type}")
    
    db.commit()


def main():
    print("=" * 60)
    print("MISSION VANASPATI - SAMPLE DATA SEEDER")
    print("=" * 60)
    
    # Initialize database tables
    init_db()
    
    db = SessionLocal()
    
    try:
        print("\n[1/4] Creating Users...")
        users = seed_users(db)
        
        print("\n[2/4] Creating Feedback...")
        seed_feedback(db, users)
        
        print("\n[3/4] Creating Saved Plants (My Garden)...")
        seed_saved_plants(db, users)
        
        print("\n[4/4] Creating Diagnosis History...")
        seed_diagnosis_history(db, users)
        
        print("\n" + "=" * 60)
        print("SAMPLE DATA SEEDED SUCCESSFULLY!")
        print("=" * 60)
        print(f"\nTest Login Credentials:")
        print(f"  Admin: admin@vanaspati.com / {TEST_PASSWORD}")
        print(f"  User:  rahul.sharma@gmail.com / {TEST_PASSWORD}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

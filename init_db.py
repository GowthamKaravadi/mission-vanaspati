from src.database import init_db

if __name__ == "__main__":
    init_db()
    print("✅ Database tables created/updated successfully!")
    print("   - users")
    print("   - remedies")
    print("   - feedback (NEW)")

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, ARRAY, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from passlib.context import CryptContext
from urllib.parse import quote_plus
import os

# PostgreSQL configuration - Use environment variables with fallbacks
DB_USER = os.getenv("DB_USER", "missionvanaspati")
DB_PASSWORD = os.getenv("DB_PASSWORD", "mI$$ion_van@spati")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "vanaspati_db")

password = quote_plus(DB_PASSWORD)
DATABASE_URL = os.getenv("DATABASE_URL", f"postgresql://{DB_USER}:{password}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)
    
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)


class Remedy(Base):
    __tablename__ = "remedies"
    
    id = Column(Integer, primary_key=True, index=True)
    class_name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    remedies = Column(ARRAY(Text), nullable=False)
    products = Column(JSON, nullable=True)  # Store product recommendations as JSON
    created_at = Column(DateTime, default=datetime.utcnow)


class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)
    subject = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String, default="bug")  # bug, feature, general
    status = Column(String, default="pending")  # pending, reviewed, resolved
    created_at = Column(DateTime, default=datetime.utcnow)


class SavedPlant(Base):
    __tablename__ = "saved_plants"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plant_name = Column(String, nullable=False)
    disease_name = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    image_path = Column(String, nullable=True)  # Optional: store image reference
    notes = Column(Text, nullable=True)  # User's personal notes
    status = Column(String, default="monitoring")  # monitoring, treating, recovered
    diagnosed_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DiagnosisHistory(Base):
    __tablename__ = "diagnosis_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    diagnosis_type = Column(String, nullable=False)  # 'single' or 'batch'
    image_name = Column(String)
    disease_name = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    alternatives = Column(JSON)  # Store alternative predictions
    remedy_info = Column(JSON)  # Store remedy details
    diagnosed_at = Column(DateTime, default=datetime.utcnow, index=True)
    notes = Column(Text)
    status = Column(String, default='active')  # active, archived


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)

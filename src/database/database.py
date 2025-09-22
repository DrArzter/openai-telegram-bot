# database/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base
from utils.logger import get_logger
import os

logger = get_logger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chatgpt_bot.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all tables in the database."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_sync():
    """Get database session for synchronous operations."""
    return SessionLocal()
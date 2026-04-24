from pydantic_settings import BaseSettings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

class Settings(BaseSettings):
    DATABASE_URL: str
    ENVIRONMENT: str = "development"
    ALLOWED_ORIGINS: str = "http://localhost:8000"
    ADMIN_API_KEY: str = ""  # Should be set in .env for admin authentication

    class Config:
        env_file = ".env"

settings = Settings()

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=20,  # Increased from 5 for better concurrency
    max_overflow=30, # Increased from 10 for burst traffic handling
    pool_recycle=3600,  # Recycle connections after 1 hour to prevent stale connections
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

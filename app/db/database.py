# app/db/database.py

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# Load environment variables from .env file
# load_dotenv()
# Load environment variables from a known path
load_dotenv(dotenv_path="/home/ss/Source/fast_api/.env")

# Build the database URL from environment variables
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB")

required = [POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_DB]
if not all(required):
    raise RuntimeError("❌ Missing one or more required database environment variables.")


SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# Create the engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base class
Base = declarative_base()

# Dependency for FastAPI or general use
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Optional: Connection test at startup
if __name__ == "__main__":
    with engine.connect() as conn:
        print(f"📡 Using DB: {SQLALCHEMY_DATABASE_URL}")

        result = conn.execute(text("SELECT 1"))
        print(f"Test query result: {result.scalar()}")

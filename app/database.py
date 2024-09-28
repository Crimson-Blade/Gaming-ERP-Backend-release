from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import sqlite3
DATABASE_URL = "postgresql://arcade_owner:ZeA4pKB9jfQS@ep-misty-tooth-a1g6z2bc.ap-southeast-1.aws.neon.tech/arcade?sslmode=require"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get the DB session for each request
def get_db():
    db: Session = SessionLocal()
    try:
        yield db  # Provides the DB session to the calling function
    finally:
        db.close()  # Ensures the session is closed after the request is completed
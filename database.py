import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SAVE_TO_DB = os.getenv("SAVE_TO_DB", "false").lower() == "true"

engine = None
SessionLocal = None
Base = declarative_base()

if SAVE_TO_DB:
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        # Create table if it doesn’t exist
        models.Base.metadata.create_all(bind=engine)

    except Exception as e:
        print(f"Error setting up database: {e}")


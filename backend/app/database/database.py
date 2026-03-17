import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def session_generator():
    try:
        db = Session()
        yield db

    finally:
        db.close()


def create_tables():
    from app.database import models

    try:
        models.Base.metadata.create_all(bind=engine)
        print(f"OK: All Tables created")

    except Exception as e:
        print(f"ERROR: {e}")

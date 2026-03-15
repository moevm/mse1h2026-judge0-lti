import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


def session_generator():
    try:
        db = Session()
        yield db

    finally:
        db.close()

def create_tables():
    try:
        Base.metadata.create_all(bind=engine)

    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        print(f"OK: All Tables created")
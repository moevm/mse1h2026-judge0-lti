from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

settings = get_settings()
DATABASE_URL = settings.database_url

engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def session_generator():
    db = Session()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()


def create_tables():
    from app.database import models

    try:
        models.Base.metadata.create_all(bind=engine)
        print(f"OK: All Tables created")

    except Exception as e:
        print(f"ERROR: {e}")


def seed_database():
    from app.database.inserts import run_seed

    db = Session()
    try:
        run_seed(db)
    except Exception as e:
        db.rollback()
        print(f"ERROR: Seed failed: {e}")
        raise
    finally:
        db.close()

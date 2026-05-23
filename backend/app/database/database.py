from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from app.core.config import get_settings

settings = get_settings()
DATABASE_URL = settings.async_database_url

engine = create_async_engine(DATABASE_URL, echo=True)
Session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)


async def session_generator():
    async with Session() as db:
        try:
            yield db
            await db.commit()
        except:
            await db.rollback()
            raise


async def create_tables():
    from app.database import models
    try:
        async with engine.begin() as conn:
            await conn.run_sync(models.Base.metadata.create_all)
        print("OK: All Tables created")
    except Exception as e:
        print(f"ERROR: {e}")


async def seed_database():
    from app.database.inserts import run_seed
    async with Session() as db:
        try:
            await run_seed(db)
            await db.commit()
        except Exception as e:
            await db.rollback()
            print(f"ERROR: Seed failed or data exists: {e}")

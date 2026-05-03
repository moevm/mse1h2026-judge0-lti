from contextlib import asynccontextmanager

import httpx
import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
from app.routers import lti, tasks, modules, check, languages, users, run, auth, analytics
from app.database.database import create_tables, seed_database

# создает таблицы в postgres
create_tables()
seed_database()

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient(
        timeout=30.0
    )
    yield
    await app.state.http_client.aclose()

app = FastAPI(lifespan=lifespan)
api_router = APIRouter(prefix="/api")

api_router.include_router(auth.router)
api_router.include_router(lti.router)
api_router.include_router(tasks.router)
api_router.include_router(check.router)
api_router.include_router(modules.router)
api_router.include_router(languages.router)
api_router.include_router(users.router)
api_router.include_router(run.router)
api_router.include_router(analytics.router)


app.include_router(api_router)


@app.get("/", tags=["root"], summary="Главная страница")
async def root():
    return {"message": "каркас"}


@app.get("/health", summary="Health Check", tags=["health"])
async def health_check():
    return JSONResponse(content={"status": "healthy"}, status_code=200)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, host="127.0.0.1", port=8000)

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.routers import lti, tasks, modules, check
from app.database.database import create_tables, seed_database

# создает таблицы в postgres
create_tables()
seed_database()

app = FastAPI()
app.include_router(lti.router)
app.include_router(tasks.router)
app.include_router(check.router)
app.include_router(modules.router)


@app.get("/", tags=["root"], summary="Главная страница")
async def root():
    return {"message": "каркас"}


@app.get("/health", summary="Health Check", tags=["health"])
async def health_check():
    return JSONResponse(content={"status": "healthy"}, status_code=200)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, host="127.0.0.1", port=8000)

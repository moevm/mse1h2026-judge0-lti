import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.routers import lti


app = FastAPI()
app.include_router(lti.router)

@app.get("/", tags=["root"], summary="Главная страница")
async def root():
    return  {"message": "каркас"}

@app.get("/health", summary="Health Check", tags=["health"])
async def health_check():
    return JSONResponse(
        content={"status": "healthy"},
        status_code=200
    )
    
if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, host="127.0.0.1", port=8000)
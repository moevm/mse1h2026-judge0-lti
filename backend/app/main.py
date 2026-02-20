import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/", tags=["root"], summary="Главная страница")
async def root():
    return  {"message": "каркас"}

@app.get("/health", summary="Health Check", tags=["health"])
async def health_check():
    return {"status": "healthy"}
    
if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, host="127.0.0.1", port=8000)
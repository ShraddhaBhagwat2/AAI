from fastapi import FastAPI
from services.user_service.src.api.user_routes import router

app = FastAPI(title="GFG Backend", version="1.0.0")

app.include_router(router, prefix="/users", tags=["users"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

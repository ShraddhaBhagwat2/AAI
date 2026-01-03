import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import asyncio

from services.user_service.src.api.user_routes import router as user_router
from services.AIFormFilling.src.apis.routes import router as grievance_router
from services.AIFormFilling.src.db.connection import connect_to_mongo, close_mongo_connection
# from services.AIAnalysis.apis.routes import router as analysis_router, monitor_grievance_submissions

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    # Start background worker to monitor grievance submissions
    # asyncio.create_task(monitor_grievance_submissions())
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title="GFG Backend",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(grievance_router, prefix="/grievance")
# app.include_router(analysis_router, prefix="/analysis", tags=["analysis"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

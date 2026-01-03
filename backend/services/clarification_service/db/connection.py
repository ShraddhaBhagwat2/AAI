from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

client = AsyncIOMotorClient(MONGO_URI)

def get_grievance_db():
    return client.grievance_db

def get_grievance_forms_collection():
    return get_grievance_db().grievance_forms

def get_officer_resolution_db():
    return client.officer_resolution_db

def get_clarifications_collection():
    return get_officer_resolution_db().clarifications

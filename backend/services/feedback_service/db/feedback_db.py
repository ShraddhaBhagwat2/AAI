from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import List, Optional
import os
from bson import ObjectId
import uuid
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

class FeedbackDatabase:
    def __init__(self):
        self.mongo_url = os.getenv("MONGO_URI")
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client.feedback_db
        self.feedback_collection = self.db.feedback
        
        # References to other databases
        self.grievance_db = self.client.grievance_db
        self.users_db = self.client.user_db
        self.superuser_db = self.client.superuserdb

    async def create_feedback(self, feedback_data: dict) -> str:
        feedback_data["feedback_id"] = f"FB_{uuid.uuid4().hex[:8].upper()}"
        feedback_data["created_at"] = datetime.utcnow()
        
        result = await self.feedback_collection.insert_one(feedback_data)
        return feedback_data["feedback_id"]

    async def get_feedback_by_id(self, feedback_id: str) -> Optional[dict]:
        return await self.feedback_collection.find_one({"feedback_id": feedback_id})

    async def get_pending_feedbacks(self, citizen_id: str) -> List[dict]:
        # Get form_ids already rated by this citizen
        rated_form_ids = await self._get_rated_form_ids(citizen_id)
        
        # Query grievance_db for completed grievances by this citizen
        cursor = self.grievance_db.grievance_forms.find({
            "user_id": citizen_id,
            "status": "completed"
        })
        grievances = await cursor.to_list(length=None)
        
        # Filter out already rated grievances
        pending_grievances = [g for g in grievances if g["form_id"] not in rated_form_ids]
        
        # Format for response
        return [{
            "form_id": g["form_id"],
            "grievance_title": g.get("title", "Unknown Title"),
            "officer_name": g.get("officer_name", "Unknown Officer"),
            "resolved_date": g.get("resolved_date", datetime.utcnow()).isoformat(),
            "officer_evidence_path": g.get("officer_evidence_path")
        } for g in pending_grievances]

    async def _get_rated_form_ids(self, citizen_id: str) -> List[str]:
        cursor = self.feedback_collection.find(
            {"citizen_id": citizen_id}, 
            {"form_id": 1, "_id": 0}
        )
        feedbacks = await cursor.to_list(length=None)
        return [f["form_id"] for f in feedbacks]

    async def get_officer_stats(self, officer_id: str) -> dict:
        pipeline = [
            {"$match": {"officer_id": officer_id}},
            {
                "$group": {
                    "_id": "$officer_id",
                    "total_feedbacks": {"$sum": 1},
                    "avg_overall": {"$avg": "$ratings.overall"},
                    "avg_speed": {"$avg": "$ratings.speed"},
                    "avg_quality": {"$avg": "$ratings.quality"},
                    "conflicts": {"$sum": {"$cond": ["$conflict_detected", 1, 0]}},
                    "escalations": {"$sum": {"$cond": ["$escalated", 1, 0]}}
                }
            }
        ]
        
        cursor = self.feedback_collection.aggregate(pipeline)
        stats = await cursor.to_list(length=1)
        
        if not stats:
            return {
                "officer_id": officer_id,
                "total_feedbacks": 0,
                "average_rating": 0.0,
                "conflict_rate": 0.0,
                "escalation_rate": 0.0,
                "performance_score": 0.0
            }
        
        stat = stats[0]
        conflict_rate = stat["conflicts"] / stat["total_feedbacks"] if stat["total_feedbacks"] > 0 else 0
        escalation_rate = stat["escalations"] / stat["total_feedbacks"] if stat["total_feedbacks"] > 0 else 0
        avg_rating = (stat["avg_overall"] + stat["avg_speed"] + stat["avg_quality"]) / 3
        performance_score = avg_rating * (1 - conflict_rate * 0.3 - escalation_rate * 0.2)
        
        return {
            "officer_id": officer_id,
            "total_feedbacks": stat["total_feedbacks"],
            "average_rating": round(avg_rating, 2),
            "conflict_rate": round(conflict_rate * 100, 2),
            "escalation_rate": round(escalation_rate * 100, 2),
            "performance_score": round(performance_score, 2)
        }

    async def get_grievance_details(self, form_id: str) -> Optional[dict]:
        return await self.grievance_db.grievances.find_one({"form_id": form_id})

    async def update_grievance_status(self, form_id: str, status: str, escalated: bool = False):
        update_data = {"status": status}
        if escalated:
            update_data["escalated"] = True
            update_data["escalation_date"] = datetime.utcnow()
        
        await self.grievance_db.grievances.update_one(
            {"form_id": form_id},
            {"$set": update_data}
        )

feedback_db = FeedbackDatabase()

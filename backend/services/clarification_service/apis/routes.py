from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from typing import List
from bson import ObjectId
from ..db.connection import get_grievance_forms_collection, get_clarifications_collection
from ..models.clarification import Clarification
from ..schema.clarification import ClarificationResponse, RespondToClarificationRequest
from shared.utils.auth_middleware import get_current_user

router = APIRouter()

# expose both "/clarifications" (current) and root "/" so GET /clarifications works
@router.get("/", response_model=ClarificationResponse)
@router.get("/clarifications", response_model=ClarificationResponse)
async def get_clarifications(current_user: str = Depends(get_current_user)):
    grievance_col = get_grievance_forms_collection()
    clarification_col = get_clarifications_collection()
    
    # Get grievances for the current user (assuming 'user_id' field matches current_user)
    grievances = await grievance_col.find({"user_id": current_user}).to_list(None)
    if not grievances:
        return ClarificationResponse(clarifications=[])
    
    # Extract form_ids (assuming grievances have a 'form_id' field matching grievance_id in clarifications)
    grievance_ids = [g["form_id"] for g in grievances if "form_id" in g]
    
    # Get clarifications matching grievance_ids
    clarifications_cursor = clarification_col.find({"grievance_id": {"$in": grievance_ids}})
    clarifications = []
    async for doc in clarifications_cursor:
        clarifications.append(Clarification(
            id=str(doc["_id"]),
            resolution_id=doc["resolution_id"],
            grievance_id=doc["grievance_id"],
            officer_id=doc["officer_id"],
            message=doc["message"],
            requested_at=doc["requested_at"],
            citizen_response=doc.get("citizen_response"),
            responded_at=doc.get("responded_at")
        ))
    
    return ClarificationResponse(clarifications=clarifications)

# expose both "/{id}/respond" (root) and "/clarifications/{id}/respond" for compatibility
@router.post("/{clarification_id}/respond")
@router.post("/clarifications/{clarification_id}/respond")
async def respond_to_clarification(
    clarification_id: str,
    request: RespondToClarificationRequest,
    current_user: str = Depends(get_current_user)
):
    grievance_col = get_grievance_forms_collection()
    clarification_col = get_clarifications_collection()
    
    # Verify the clarification belongs to the user's grievances
    clarification = await clarification_col.find_one({"_id": ObjectId(clarification_id)})
    if not clarification:
        raise HTTPException(status_code=404, detail="Clarification not found")
    
    # Check if grievance_id belongs to user's grievances (match form_id with grievance_id)
    grievance = await grievance_col.find_one({"form_id": clarification["grievance_id"], "user_id": current_user})
    if not grievance:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update the clarification
    await clarification_col.update_one(
        {"_id": ObjectId(clarification_id)},
        {"$set": {"citizen_response": request.citizen_response, "responded_at": datetime.utcnow()}}
    )
    
    return {"message": "Response submitted successfully"}

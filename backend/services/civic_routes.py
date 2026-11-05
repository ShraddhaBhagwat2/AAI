from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from services.civic_operations import (
    get_citizen_reputation,
    get_heatmap,
    get_transparency_report,
    predict_risk,
    verify_resolution,
)

router = APIRouter(prefix="/civic", tags=["civic operations"])


class VerificationRequest(BaseModel):
    citizen_confirmed: bool
    comment: str = ""


class RiskPredictionRequest(BaseModel):
    rainfall_mm: float = 0
    days: int = 7


@router.get("/reports/transparency")
async def transparency_report(days: int = Query(30, ge=1, le=365)):
    return await get_transparency_report(days)


@router.get("/reports/heatmap")
async def issue_heatmap(days: int = Query(30, ge=1, le=365)):
    return {"days": days, "points": await get_heatmap(days)}


@router.post("/predictions/risk")
async def civic_risk_prediction(request: RiskPredictionRequest):
    return await predict_risk(request.rainfall_mm, request.days)


@router.get("/citizens/{citizen_id}/reputation")
async def citizen_reputation(citizen_id: str):
    return await get_citizen_reputation(citizen_id)


@router.post("/grievances/{form_id}/verification")
async def resolution_verification(form_id: str, request: VerificationRequest):
    try:
        return await verify_resolution(form_id, request.citizen_confirmed, request.comment)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unable to update resolution verification") from exc

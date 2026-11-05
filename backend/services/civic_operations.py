"""Shared civic operations layer.

This module owns the cross-service lifecycle data that was previously spread
across grievance, analysis, resolution, and feedback collections.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional
import asyncio
import logging

from services.AIFormFilling.src.db.connection import get_database as get_grievance_db

logger = logging.getLogger(__name__)

SLA_HOURS = {
    "critical": 2,
    "high": 12,
    "medium": 24,
    "low": 48,
}

STATUS_ORDER = ("submitted", "analyzed", "assigned", "in_progress", "inspection", "resolved", "closed")


def _now() -> datetime:
    return datetime.utcnow()


def _hours_for(urgency: str) -> int:
    return SLA_HOURS.get(str(urgency or "medium").lower(), SLA_HOURS["medium"])


async def register_complaint(form_id: str, grievance: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Create or update the canonical lifecycle record and SLA deadline."""
    db = get_grievance_db()
    now = _now()
    urgency = str(analysis.get("urgency_level", "medium")).lower()
    deadline = now + timedelta(hours=_hours_for(urgency))
    record = {
        "form_id": form_id,
        "user_id": grievance.get("user_id"),
        "title": grievance.get("title"),
        "category": grievance.get("category", "Other"),
        "area_ward_name": grievance.get("area_ward_name"),
        "geo_coordinates": grievance.get("geo_coordinates"),
        "assigned_department": analysis.get("assigned_department"),
        "assigned_officer_id": analysis.get("assigned_officer_id"),
        "assigned_officer_name": analysis.get("assigned_officer_name"),
        "priority_score": analysis.get("priority_score", 0),
        "urgency_level": urgency,
        "sla_hours": _hours_for(urgency),
        "sla_deadline": deadline,
        "sla_breach_risk": False,
        "status": analysis.get("status", "assigned").lower(),
        "escalated": False,
        "created_at": now,
        "updated_at": now,
        "last_event_at": now,
    }
    await db.civic_lifecycles.update_one(
        {"form_id": form_id},
        {"$set": record, "$setOnInsert": {"events": []}},
        upsert=True,
    )
    await append_event(form_id, record["status"], "AI analysis completed", record)
    return record


async def append_event(form_id: str, status: str, note: str = "", metadata: Optional[Dict[str, Any]] = None):
    db = get_grievance_db()
    event = {
        "status": status,
        "note": note,
        "metadata": metadata or {},
        "timestamp": _now(),
    }
    await db.civic_lifecycles.update_one(
        {"form_id": form_id},
        {"$push": {"events": event}, "$set": {"status": status, "updated_at": event["timestamp"], "last_event_at": event["timestamp"]}},
        upsert=True,
    )


async def update_lifecycle(form_id: str, status: str, note: str = "", **fields: Any):
    db = get_grievance_db()
    status = str(status).lower()
    fields.update({"status": status, "updated_at": _now()})
    if status == "resolved":
        fields["resolved_at"] = fields.get("resolved_at", _now())
        fields["verification_status"] = "awaiting_citizen_confirmation"
    await db.civic_lifecycles.update_one({"form_id": form_id}, {"$set": fields}, upsert=True)
    await append_event(form_id, status, note, fields)


async def verify_resolution(form_id: str, citizen_confirmed: bool, comment: str = "") -> Dict[str, Any]:
    status = "closed" if citizen_confirmed else "escalated"
    verification = "verified" if citizen_confirmed else "rejected"
    await update_lifecycle(
        form_id,
        status,
        comment or ("Citizen confirmed resolution" if citizen_confirmed else "Citizen rejected resolution"),
        verification_status=verification,
        citizen_feedback_comment=comment,
    )
    db = get_grievance_db()
    await db.grievance_forms.update_one(
        {"form_id": form_id},
        {"$set": {"status": status, "verification_status": verification, "verification_comment": comment, "updated_at": _now()}},
    )
    return {"form_id": form_id, "status": status, "verification_status": verification}


async def monitor_slas(interval_seconds: int = 60):
    """Mark breach risk and escalate overdue unresolved complaints."""
    while True:
        try:
            db = get_grievance_db()
            now = _now()
            risk_cutoff = now + timedelta(hours=6)
            await db.civic_lifecycles.update_many(
                {"status": {"$nin": ["resolved", "closed", "escalated"]}, "sla_deadline": {"$lte": risk_cutoff, "$gt": now}},
                {"$set": {"sla_breach_risk": True, "updated_at": now}},
            )
            overdue = db.civic_lifecycles.find(
                {"status": {"$nin": ["resolved", "closed", "escalated"]}, "sla_deadline": {"$lte": now}, "escalated": {"$ne": True}}
            )
            async for record in overdue:
                form_id = record["form_id"]
                await update_lifecycle(form_id, "escalated", "Automatically escalated after SLA breach", escalated=True, escalation_reason="sla_breach", escalated_at=now)
                await db.grievance_forms.update_one({"form_id": form_id}, {"$set": {"status": "escalated", "escalated": True, "escalation_reason": "sla_breach", "escalation_date": now}})
        except Exception:
            logger.exception("SLA monitor iteration failed")
        await asyncio.sleep(interval_seconds)


async def get_transparency_report(days: int = 30) -> Dict[str, Any]:
    db = get_grievance_db()
    since = _now() - timedelta(days=max(1, min(days, 365)))
    records = await db.civic_lifecycles.find({"created_at": {"$gte": since}}).to_list(length=None)
    total = len(records)
    resolved = [r for r in records if r.get("status") in ("resolved", "closed")]
    escalated = [r for r in records if r.get("escalated") or r.get("status") == "escalated"]
    by_category: Dict[str, int] = {}
    by_department: Dict[str, Dict[str, int]] = {}
    for record in records:
        category = record.get("category") or "Other"
        department = record.get("assigned_department") or "Unassigned"
        by_category[category] = by_category.get(category, 0) + 1
        stats = by_department.setdefault(department, {"total": 0, "resolved": 0, "escalated": 0})
        stats["total"] += 1
        stats["resolved"] += int(record in resolved)
        stats["escalated"] += int(record in escalated)
    durations = [
        (r["resolved_at"] - r["created_at"]).total_seconds() / 3600
        for r in resolved if r.get("resolved_at") and r.get("created_at")
    ]
    return {
        "period_days": days,
        "total_complaints": total,
        "resolved_complaints": len(resolved),
        "open_complaints": total - len(resolved),
        "escalated_complaints": len(escalated),
        "resolution_rate": round(len(resolved) / total * 100, 2) if total else 0,
        "average_resolution_hours": round(sum(durations) / len(durations), 2) if durations else None,
        "top_issues": sorted(({"category": k, "count": v} for k, v in by_category.items()), key=lambda x: x["count"], reverse=True)[:10],
        "department_performance": [
            {"department": name, **stats, "efficiency_score": round(stats["resolved"] / stats["total"] * 100, 2) if stats["total"] else 0}
            for name, stats in sorted(by_department.items())
        ],
    }


async def get_heatmap(days: int = 30) -> list:
    db = get_grievance_db()
    since = _now() - timedelta(days=max(1, min(days, 365)))
    pipeline = [
        {"$match": {"created_at": {"$gte": since}, "geo_coordinates": {"$ne": None}}},
        {"$group": {"_id": {"lat": "$geo_coordinates.lat", "lng": "$geo_coordinates.lng", "category": "$category"}, "count": {"$sum": 1}}},
        {"$project": {"_id": 0, "lat": "$_id.lat", "lng": "$_id.lng", "category": "$_id.category", "count": 1}},
    ]
    return await db.grievance_forms.aggregate(pipeline).to_list(length=None)


async def predict_risk(rainfall_mm: float = 0, days: int = 7) -> Dict[str, Any]:
    """Return explainable risk signals from recent complaints and rainfall input.

    This is deliberately deterministic until a city weather provider is configured;
    callers can pass an observed or forecast rainfall value.
    """
    db = get_grievance_db()
    since = _now() - timedelta(days=max(1, min(days, 30)))
    recent = await db.grievance_forms.find({"created_at": {"$gte": since}}).to_list(length=None)
    waterlogging = sum(1 for item in recent if str(item.get("category", "")).lower() in {"drainage", "water supply", "roads"})
    rainfall_factor = min(max(rainfall_mm / 50, 0), 2)
    risk_score = min(100, round(waterlogging * 5 + rainfall_factor * 35))
    return {
        "risk_score": risk_score,
        "risk_level": "high" if risk_score >= 70 else "medium" if risk_score >= 35 else "low",
        "signal": "waterlogging",
        "rainfall_mm": rainfall_mm,
        "recent_related_complaints": waterlogging,
        "recommendation": "Pre-position drainage teams and inspect known hotspots." if risk_score >= 35 else "Continue routine monitoring.",
    }


async def get_citizen_reputation(citizen_id: str) -> Dict[str, Any]:
    db = get_grievance_db()
    feedback_db = db.client.feedback_db
    records = await feedback_db.feedback.find({"citizen_id": citizen_id}).to_list(length=None)
    helpful = sum(1 for item in records if not item.get("conflict_detected") and item.get("is_resolved_by_user"))
    conflicts = sum(1 for item in records if item.get("conflict_detected"))
    score = max(0, min(100, 50 + helpful * 5 - conflicts * 10))
    return {"citizen_id": citizen_id, "score": score, "helpful_confirmations": helpful, "conflicts": conflicts}

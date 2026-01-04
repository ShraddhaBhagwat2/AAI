from typing import Dict, Optional
from ..db.feedback_db import feedback_db
import logging

logger = logging.getLogger(__name__)

class ConflictResolver:
    
    async def process_feedback(self, feedback_data: dict, evidence_path: Optional[str] = None) -> Dict[str, any]:
        """
        Main conflict resolution logic (simplified without AI)
        """
        conflict_detected = False
        escalated = False
        
        # Get grievance details
        grievance = await feedback_db.get_grievance_details(feedback_data["form_id"])
        if not grievance:
            return {"error": "Grievance not found"}
        
        # Check for positive feedback (happy path)
        if (feedback_data["is_resolved_by_user"] and 
            feedback_data["ratings"]["overall"] > 3):
            # Final close - citizen is satisfied
            await feedback_db.update_grievance_status(
                feedback_data["form_id"], 
                "closed"
            )
            return {
                "conflict_detected": False,
                "escalated": False,
                "action": "closed",
                "message": "Ticket closed - citizen satisfied"
            }
        
        # Check for conflict (citizen says not resolved)
        if not feedback_data["is_resolved_by_user"]:
            conflict_detected = True
            
            # Escalate if rating is low (no AI verification)
            if feedback_data["ratings"]["overall"] <= 2:
                escalated = True
                await self._escalate_ticket(feedback_data["form_id"], grievance["officer_id"])
        
        # Update feedback data with conflict resolution results
        feedback_data.update({
            "conflict_detected": conflict_detected,
            "escalated": escalated
        })
        
        return {
            "conflict_detected": conflict_detected,
            "escalated": escalated,
            "action": "escalated" if escalated else "reopened"
        }
    
    async def _escalate_ticket(self, form_id: str, officer_id: str):
        """Escalate ticket to department admin"""
        try:
            await feedback_db.update_grievance_status(
                form_id, 
                "escalated", 
                escalated=True
            )
            
            # TODO: Send notification to department admin
            # await notification_service.notify_admin(officer_id, form_id)
            
            logger.info(f"Escalated ticket {form_id} for officer {officer_id}")
            
        except Exception as e:
            logger.error(f"Failed to escalate ticket {form_id}: {str(e)}")

conflict_resolver = ConflictResolver()

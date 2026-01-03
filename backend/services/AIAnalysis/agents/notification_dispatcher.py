import httpx
from typing import Dict
from services.AIAnalysis.shared.schemas import AnalysisResult
from services.AIAnalysis.utils.config import settings

class NotificationDispatcherAgent:
    def __init__(self):
        self.notification_service_url = settings.NOTIFICATION_SERVICE_URL
    
    async def dispatch_notifications(self, analysis: AnalysisResult):
        """
        Send notifications to both citizen and assigned officer
        """
        # Notification for citizen
        citizen_notification = self._create_citizen_notification(analysis)
        await self._send_notification(citizen_notification)
        
        # Notification for officer
        officer_notification = self._create_officer_notification(analysis)
        await self._send_notification(officer_notification)
    
    def _create_citizen_notification(self, analysis: AnalysisResult) -> Dict:
        """Create notification payload for citizen"""
        if analysis.vector_check.is_duplicate:
            message = (
                f"Your grievance #{analysis.form_id} has been linked to an existing case "
                f"#{analysis.vector_check.parent_form_id}. You'll receive updates on the resolution."
            )
        else:
            message = (
                f"Your grievance #{analysis.form_id} has been assigned to "
                f"{analysis.routing.officer_name} ({analysis.routing.department}). "
                f"Expected response time: {analysis.routing.estimated_response_time}."
            )
        
        return {
            "recipient_type": "citizen",
            "recipient_id": analysis.form_id,  # Will be mapped to user_id in notification service
            "notification_type": "grievance_update",
            "priority": analysis.priority_score.urgency_level,
            "title": "Grievance Status Update",
            "message": message,
            "metadata": {
                "form_id": analysis.form_id,
                "status": analysis.status
            }
        }
    
    def _create_officer_notification(self, analysis: AnalysisResult) -> Dict:
        """Create notification payload for officer"""
        # Don't notify officer if it's a duplicate
        if analysis.vector_check.is_duplicate:
            return None
        
        urgency_prefix = {
            "critical": "🚨 CRITICAL ALERT",
            "high": "⚠️ High Priority",
            "medium": "📋 New Assignment",
            "low": "📝 New Case"
        }.get(analysis.priority_score.urgency_level, "📋 New Assignment")
        
        message = (
            f"{urgency_prefix}: New grievance #{analysis.form_id} assigned to you. "
            f"Priority Score: {analysis.priority_score.score}/100. "
            f"Area: {analysis.vector_check.similarity_score or 'N/A'}. "
            f"Expected resolution: {analysis.routing.estimated_response_time}."
        )
        
        return {
            "recipient_type": "officer",
            "recipient_id": analysis.routing.officer_id,
            "notification_type": "new_assignment",
            "priority": analysis.priority_score.urgency_level,
            "title": f"New Grievance Assignment - {analysis.routing.department}",
            "message": message,
            "metadata": {
                "form_id": analysis.form_id,
                "priority_score": analysis.priority_score.score,
                "department": analysis.routing.department
            }
        }
    
    async def _send_notification(self, notification: Dict):
        """Send notification to notification service"""
        if notification is None:
            return
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.notification_service_url}/api/notifications/send",
                    json=notification,
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    print(f"Failed to send notification: {response.text}")
                    
        except Exception as e:
            print(f"Error sending notification: {e}")

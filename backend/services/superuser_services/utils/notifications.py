import logging
from typing import Dict, Any
import asyncio

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for sending notifications (Email/SMS)"""
    
    async def send_credentials_email(self, email: str, temp_password: str, full_name: str) -> bool:
        """Send temporary password via email"""
        try:
            # In a real implementation, integrate with email service (SendGrid, SES, etc.)
            message = f"""
            Dear {full_name},
            
            Your government portal account has been created successfully.
            
            Login Details:
            Email: {email}
            Temporary Password: {temp_password}
            
            Please log in and change your password immediately for security.
            
            Best regards,
            Government Portal Team
            """
            
            # Simulate email sending
            logger.info(f"Email sent to {email} with temporary password")
            await asyncio.sleep(0.1)  # Simulate network delay
            
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {email}: {e}")
            return False
    
    async def send_credentials_sms(self, phone_number: str, temp_password: str) -> bool:
        """Send temporary password via SMS"""
        try:
            # In a real implementation, integrate with SMS service (Twilio, AWS SNS, etc.)
            message = f"Your govt portal password: {temp_password}. Login & change it immediately."
            
            # Simulate SMS sending
            logger.info(f"SMS sent to {phone_number} with temporary password")
            await asyncio.sleep(0.1)  # Simulate network delay
            
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS to {phone_number}: {e}")
            return False
    
    async def send_credentials(self, user_data: Dict[str, Any], temp_password: str) -> Dict[str, bool]:
        """Send credentials via both email and SMS"""
        results = {
            "email_sent": False,
            "sms_sent": False
        }
        
        # Send email
        email_task = self.send_credentials_email(
            user_data["email"], 
            temp_password, 
            user_data["full_name"]
        )
        
        # Send SMS
        sms_task = self.send_credentials_sms(
            user_data["phone_number"], 
            temp_password
        )
        
        print("Password", temp_password)
        # Execute both tasks concurrently
        email_result, sms_result = await asyncio.gather(
            email_task, sms_task, return_exceptions=True
        )
        
        results["email_sent"] = email_result if isinstance(email_result, bool) else False
        results["sms_sent"] = sms_result if isinstance(sms_result, bool) else False
        
        return results

notification_service = NotificationService()

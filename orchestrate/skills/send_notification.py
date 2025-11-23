"""
Send Notification Skill - Sends notifications to recipients
"""
import sys
import os
from typing import Dict, Any

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.skill_base import BaseSkill, SkillInput, SkillOutput, SkillStatus
from backend.security.audit_logger import get_audit_logger, AuditEventType


class SendNotificationSkill(BaseSkill):
    """
    Sends notifications to recipients via email or other channels.
    
    Input: recipient (str), message (str), notification_type (str, optional)
    Output: status (str), notification_id (str)
    """
    
    def __init__(self):
        super().__init__("send_notification")
        self.audit_logger = get_audit_logger()
        self.notification_counter = 0
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate required fields: recipient, message"""
        if not input_data:
            raise ValueError("Input data is required")
        
        required_fields = ["recipient", "message"]
        for field in required_fields:
            if field not in input_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate types
        if not isinstance(input_data["recipient"], str):
            raise ValueError("recipient must be a string")
        if not isinstance(input_data["message"], str):
            raise ValueError("message must be a string")
        
        # Basic email validation
        recipient = input_data["recipient"].strip()
        if '@' not in recipient or '.' not in recipient:
            raise ValueError("recipient must be a valid email address")
        
        if len(input_data["message"].strip()) == 0:
            raise ValueError("message cannot be empty")
        
        return True
    
    def _execute_logic(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute notification sending logic"""
        recipient = input_data["recipient"].strip()
        message = input_data["message"].strip()
        notification_type = input_data.get("notification_type", "email").lower()
        priority = input_data.get("priority", "normal")
        
        # Generate notification ID
        self.notification_counter += 1
        notification_id = f"NOTIF-{notification_counter:05d}"
        
        # Simulate sending notification
        try:
            if notification_type == "email":
                send_status = self._send_email(recipient, message, priority)
            elif notification_type == "sms":
                send_status = self._send_sms(recipient, message, priority)
            else:
                send_status = self._send_generic(recipient, message, priority)
            
            # Log to audit
            try:
                self.audit_logger.log_event(
                    event_type=AuditEventType.NOTIFICATION_SENT,
                    user_id="system",
                    resource_type="notification",
                    resource_id=notification_id,
                    action="send",
                    details={
                        "recipient": recipient,
                        "type": notification_type,
                        "priority": priority,
                        "status": send_status["status"]
                    }
                )
            except Exception as e:
                self.logger.warning(f"Failed to log notification: {str(e)}")
            
            return {
                "status": "sent",
                "notification_id": notification_id,
                "recipient": recipient,
                "type": notification_type,
                "priority": priority,
                "timestamp": "2025-11-23T12:00:00Z"
            }
        except Exception as e:
            return {
                "status": "failed",
                "notification_id": notification_id,
                "recipient": recipient,
                "error": str(e)
            }
    
    def _send_email(self, recipient: str, message: str, priority: str) -> Dict[str, Any]:
        """Send email notification"""
        # In production, this would connect to email service
        return {
            "status": "sent",
            "method": "email",
            "recipient": recipient
        }
    
    def _send_sms(self, recipient: str, message: str, priority: str) -> Dict[str, Any]:
        """Send SMS notification"""
        # In production, this would connect to SMS service
        return {
            "status": "sent",
            "method": "sms",
            "recipient": recipient
        }
    
    def _send_generic(self, recipient: str, message: str, priority: str) -> Dict[str, Any]:
        """Send generic notification"""
        return {
            "status": "sent",
            "method": "generic",
            "recipient": recipient
        }


# Backward compatibility wrapper
def send_notification(recipient: str, message: str, 
                      notification_type: str = "email",
                      priority: str = "normal") -> Dict[str, Any]:
    """
    Legacy function-based interface for backward compatibility.
    
    Args:
        recipient: Email address or contact identifier
        message: Notification message content
        notification_type: Type of notification (email, sms, etc.)
        priority: Priority level (low, normal, high, urgent)
        
    Returns:
        Dictionary with status and notification_id
    """
    skill = SendNotificationSkill()
    try:
        output = skill.execute({
            "recipient": recipient,
            "message": message,
            "notification_type": notification_type,
            "priority": priority
        })
        return output.dict() if hasattr(output, 'dict') else output
    except Exception as e:
        return {
            "status": "failed",
            "recipient": recipient,
            "error": str(e)
        }


if __name__ == "__main__":
    # Test the skill
    skill = SendNotificationSkill()
    result = skill.execute({
        "recipient": "manager@example.com",
        "message": "Approval needed for REQ-123",
        "notification_type": "email",
        "priority": "high"
    })
    print(f"Notification result: {result}")
    print(f"Status: {result.status if hasattr(result, 'status') else 'success'}")


class NotificationService:
    def __init__(self):
        self.templates = {
            "welcome": "Welcome {name}! Your vendor registration is complete.",
            "approval_needed": "Action Required: Requisition #{req_id} needs your approval.",
            "status_update": "Update: Your request #{req_id} is now {status}."
        }

    def send_notification(self, user_id, template_key, **kwargs):
        template = self.templates.get(template_key)
        if not template:
            return {"status": "failed", "error": "Template not found"}
        
        message = template.format(**kwargs)
        print(f"\n[NOTIFICATION] User: {user_id} | Message: {message}\n")
        return {"status": "sent", "message": message}

notification_service = NotificationService()

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.sender_email = os.getenv('SENDER_EMAIL', 'mock_sender@example.com')
        self.sender_password = os.getenv('SENDER_PASSWORD', 'mock_password')
        self.mock_mode = True  # Default to mock mode for hackathon

    def send_email(self, recipient, subject, body):
        if self.mock_mode:
            print(f"\n[MOCK EMAIL] To: {recipient}\nSubject: {subject}\nBody: {body}\n")
            return {"status": "sent", "mode": "mock"}
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            return {"status": "sent", "mode": "live"}
        except Exception as e:
            print(f"Failed to send email: {e}")
            return {"status": "failed", "error": str(e)}

email_service = EmailService()

def send_notification(recipient, message):
    """
    Sends a notification (mock).
    """
    print(f"Sending email to {recipient}: {message}")
    return {"status": "sent", "recipient": recipient}

if __name__ == "__main__":
    send_notification("manager@example.com", "Approval needed for REQ-123")

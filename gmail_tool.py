import base64
from email.message import EmailMessage
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from auth import get_credentials

def create_email_draft(to: str, subject: str, body: str) -> dict:
    """
    Creates a draft email in the authenticated user's Gmail account.
    
    Args:
        to (str): Recipient email address.
        subject (str): Email subject.
        body (str): Email body text.
        
    Returns:
        dict: The response from the Gmail API including draft metadata and ID.
    """
    try:
        # Retrieve authenticated Google OAuth credentials
        creds = get_credentials()
        
        # Build the Gmail API service client
        service = build('gmail', 'v1', credentials=creds)
        
        # Construct the email message
        message = EmailMessage()
        message.set_content(body)
        message["To"] = to
        message["Subject"] = subject
        
        # Encode the MIME message into base64url format as required by the Gmail API
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {
            "message": {
                "raw": encoded_message
            }
        }
        
        # Request draft creation from Gmail
        draft = (
            service.users()
            .drafts()
            .create(userId="me", body=create_message)
            .execute()
        )
        
        return draft
        
    except HttpError as err:
        print(f"Gmail API HTTP error: {err.resp.status} - {err.content}")
        raise err
    except Exception as err:
        print(f"Error creating Gmail draft: {err}")
        raise err

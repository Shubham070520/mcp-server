from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from auth import get_credentials

def append_to_doc(doc_id: str, content: str) -> dict:
    """
    Appends text content to the end of the specified Google Document.
    
    Args:
        doc_id (str): The Google Document ID.
        content (str): The text content to append.
        
    Returns:
        dict: The response from the Google Docs API.
    """
    try:
        # Retrieve authenticated Google OAuth credentials
        creds = get_credentials()
        
        # Build the Google Docs API service client
        service = build('docs', 'v1', credentials=creds)
        
        # Define the batch update request payload to append text to the end of segment (body)
        requests = [
            {
                'insertText': {
                    'text': content,
                    'endOfSegmentLocation': {}  # Targets the end of the document body
                }
            }
        ]
        
        # Execute the update request
        response = service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()
        
        return response
        
    except HttpError as err:
        print(f"Google Docs API HTTP error: {err.resp.status} - {err.content}")
        raise err
    except Exception as err:
        print(f"Error appending to Google Doc: {err}")
        raise err

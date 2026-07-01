import sys
import os
from fastapi import FastAPI, HTTPException, status, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field
from docs_tool import append_to_doc
from gmail_tool import create_email_draft

app = FastAPI(
    title="Google MCP Server",
    description="A FastAPI server providing Google Docs and Gmail tools with manual console approval.",
    version="1.0.0"
)

# API Key Security Setup
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def verify_api_key(api_key: str = Depends(api_key_header)):
    """
    Checks if X-API-Key header matches MCP_API_KEY environment variable.
    If MCP_API_KEY is not configured in the environment, API key authentication is bypassed.
    """
    expected_key = os.environ.get("MCP_API_KEY")
    if not expected_key:
        return
    if api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key"
        )

# Pydantic request models
class AppendToDocRequest(BaseModel):
    doc_id: str = Field(..., description="The ID of the Google Document to append text to.")
    content: str = Field(..., description="The text content to append to the document.")

class CreateEmailDraftRequest(BaseModel):
    to: str = Field(..., description="The recipient email address.")
    subject: str = Field(..., description="The email subject line.")
    body: str = Field(..., description="The main text body of the email.")

def ask_approval(action_name: str, payload: dict) -> bool:
    """
    Prints action details to the console and waits for the user's manual y/n approval.
    Runs inside a synchronous endpoint thread, safely blocking only the current request thread.
    """
    print("\n" + "="*50)
    print(f"PENDING OPERATOR APPROVAL")
    print(f"Action: {action_name}")
    print("Payload:")
    for key, val in payload.items():
        print(f"  {key}: {val}")
    print("="*50)
    
    try:
        user_input = input("Approve? (y/n): ").strip().lower()
        return user_input == 'y'
    except EOFError:
        print("Error: Standard input is closed/not available. Rejecting action.")
        return False
    except Exception as e:
        print(f"Error reading approval: {e}. Rejecting action.")
        return False

@app.post("/append_to_doc", status_code=status.HTTP_200_OK)
def append_to_doc_endpoint(payload: AppendToDocRequest, _ = Depends(verify_api_key)):
    """
    Endpoint to append text to a Google Document. Requires console-based manual approval if no API key is set.
    """
    data = payload.model_dump()
    if not os.environ.get("MCP_API_KEY"):
        if not ask_approval("append_to_doc", data):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Action rejected by user."
            )
    
    try:
        result = append_to_doc(payload.doc_id, payload.content)
        return {
            "status": "success",
            "message": "Text successfully appended to Google Doc",
            "documentId": payload.doc_id,
            "response": result
        }
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to append to Google Doc: {str(err)}"
        )

@app.post("/create_email_draft", status_code=status.HTTP_200_OK)
def create_email_draft_endpoint(payload: CreateEmailDraftRequest, _ = Depends(verify_api_key)):
    """
    Endpoint to create a Gmail email draft. Requires console-based manual approval if no API key is set.
    """
    data = payload.model_dump()
    if not os.environ.get("MCP_API_KEY"):
        if not ask_approval("create_email_draft", data):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Action rejected by user."
            )
        
    try:
        result = create_email_draft(payload.to, payload.subject, payload.body)
        return {
            "status": "success",
            "message": "Email draft created successfully",
            "draft": result
        }
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create Gmail draft: {str(err)}"
        )

if __name__ == '__main__':
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0") if os.environ.get("PORT") else "127.0.0.1"
    print(f"Starting Google MCP-style Server on http://{host}:{port}")
    print("Press Ctrl+C to stop the server.")
    uvicorn.run("server:app", host=host, port=port, reload=False)

import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Define the scopes required for the application
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/gmail.compose'
]

# Set path relative to this script directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(BASE_DIR, 'credentials.json')
TOKEN_PATH = os.path.join(BASE_DIR, 'token.json')

def get_credentials():
    """
    Load existing OAuth credentials from token.json if they exist.
    If not, or if credentials are invalid/expired, run the local OAuth flow.
    """
    # Write credentials from environment variables if present (useful for cloud deployments like Railway)
    credentials_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    if credentials_json and not os.path.exists(CREDENTIALS_PATH):
        with open(CREDENTIALS_PATH, 'w') as f:
            f.write(credentials_json)

    token_json = os.environ.get("GOOGLE_TOKEN_JSON")
    if token_json and not os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'w') as f:
            f.write(token_json)

    creds = None
    
    # Load credentials if token.json already exists
    if os.path.exists(TOKEN_PATH):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        except Exception as e:
            print(f"Error loading token.json: {e}. Re-authenticating...")
            creds = None

    # Authenticate if valid credentials are not found
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Failed to refresh token: {e}. Running full authentication flow...")
                creds = None
        
        # If refreshing failed or wasn't possible, run local auth flow
        if not creds:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(
                    f"credentials.json not found at '{CREDENTIALS_PATH}'.\n"
                    "Please download OAuth 2.0 client credentials from Google Cloud Console, "
                    "save it as credentials.json, and place it in the same directory."
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save token for subsequent runs
        with open(TOKEN_PATH, 'w') as token_file:
            token_file.write(creds.to_json())
            
    return creds

if __name__ == '__main__':
    # Simple CLI test run to perform authentication flow standalone
    print("Testing Google OAuth...")
    try:
        credentials = get_credentials()
        print("Authentication successful! Token saved to token.json.")
    except Exception as err:
        print(f"Authentication failed: {err}")

# Google MCP Server

A Python-based MCP-style server built with FastAPI that integrates with **Google Docs** and **Gmail**. Before running any action, the server requires manual approval in the terminal (`Approve? (y/n)`).

---

## 📁 Project Structure

```text
google-mcp-server/
├── server.py             # FastAPI app with tool endpoints & approval prompt
├── auth.py               # Google OAuth authentication & token manager
├── docs_tool.py          # Google Docs tool (appends content)
├── gmail_tool.py         # Gmail tool (creates draft)
├── requirements.txt      # Python dependencies
├── README.md             # Setup and usage instructions
├── credentials.json      # (NOT committed) OAuth 2.0 client secret credentials from Google Cloud Console
└── token.json            # (NOT committed) Auto-generated user access/refresh token
```

---

## ⚙️ Features

1. **FastAPI Endpoints**:
   - `POST /append_to_doc`: Appends text to the end of a Google Doc body.
   - `POST /create_email_draft`: Creates a draft email in your Gmail drafts folder.
2. **Operator-in-the-loop Verification**:
   - Whenever an endpoint is hit, the server pauses, prints the payload, and prompts `Approve? (y/n)` in the command line interface.
   - The API client waits and will receive a `200 OK` on approval (`y`), or a `403 Forbidden` on rejection (`n`).
3. **Seamless Google OAuth2 Flow**:
   - Skips web authentication on subsequent runs if a valid `token.json` already exists.

---

## 🚀 Setup Instructions

### 1. Prerequisites & Virtual Environment

Ensure you have Python 3.10+ installed.

```bash
# Clone or navigate to the project directory
cd google-mcp-server

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install the dependencies
pip install -r requirements.txt
```

### 2. Configure Google Cloud Console

To interact with the APIs, you must download a client secrets credentials file:

1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new Google Cloud Project (or select an existing one).
3. Enable the **Google Docs API** and **Gmail API**:
   - Go to **APIs & Services > Library**.
   - Search for **Google Docs API** and click **Enable**.
   - Search for **Gmail API** and click **Enable**.
4. Configure the **OAuth Consent Screen**:
   - Go to **APIs & Services > OAuth consent screen**.
   - Select **External** (or Internal if you are within a Google Workspace organization) and click **Create**.
   - Fill in the required fields (App Name, User support email, Developer contact information).
   - Under **Scopes**, you can add or skip (the app requests scopes dynamically).
   - Under **Test Users**, add the Google email address you plan to authenticate with.
5. Create **OAuth 2.0 Client Credentials**:
   - Go to **APIs & Services > Credentials**.
   - Click **Create Credentials** and select **OAuth client ID**.
   - Select **Desktop App** as the Application Type.
   - Set a name (e.g., `Google MCP Server Desktop Client`) and click **Create**.
6. Download the Client Secret:
   - In the Credentials list, find your new Client ID under **OAuth 2.0 Client IDs**.
   - Click the **Download JSON** icon on the right.
   - Rename the downloaded file to `credentials.json` and save it directly in the `google-mcp-server/` directory.

---

## 🔑 Initial Authentication

Before running the server, you can optionally test and run the OAuth authentication flow standalone to create `token.json`:

```bash
python auth.py
```

This will automatically open your default web browser. Log in with your test Google account, accept the security warnings (as this is your own developer app), and authorize the requested permissions for Docs and Gmail.

Once completed, a file named `token.json` will be saved in the directory, allowing future executions to run headlessly.

---

## 🟢 Running the Server

Start the server using `uvicorn` or by running the script directly:

```bash
python server.py
```

The server will launch at `http://127.0.0.1:8000`.

---

## 🧪 Testing the Endpoints

Keep the server running and open a new terminal window to execute test requests using `curl`.

### Test 1: Append text to a Google Doc

Replace `YOUR_DOCUMENT_ID` with the ID of a Google Document you own and have edit access to (from the document URL: `https://docs.google.com/document/d/YOUR_DOCUMENT_ID/edit`).

```bash
curl -X POST "http://127.0.0.1:8000/append_to_doc" \
     -H "Content-Type: application/json" \
     -d "{\"doc_id\": \"YOUR_DOCUMENT_ID\", \"content\": \"\nHello from the Google MCP-style Server!\"}"
```

#### Terminal prompt response:
1. In the server terminal, you will see:
   ```text
   ==================================================
   PENDING OPERATOR APPROVAL
   Action: append_to_doc
   Payload:
     doc_id: YOUR_DOCUMENT_ID
     content: \nHello from the Google MCP-style Server!
   ==================================================
   Approve? (y/n): 
   ```
2. Type `y` and press **Enter**.
3. The API client will receive:
   ```json
   {
     "status": "success",
     "message": "Text successfully appended to Google Doc",
     "documentId": "YOUR_DOCUMENT_ID",
     "response": { ... }
   }
   ```
4. Verify the new line in your Google Doc!

---

### Test 2: Create a Gmail Email Draft

```bash
curl -X POST "http://127.0.0.1:8000/create_email_draft" \
     -H "Content-Type: application/json" \
     -d "{\"to\": \"recipient@example.com\", \"subject\": \"FastAPI MCP Server Test\", \"body\": \"This email draft was generated using the Python Google API server integration with console-based approval validation.\"}"
```

#### Terminal prompt response:
1. In the server terminal, approve the request by typing `y` and pressing **Enter**.
2. Go to [Gmail Drafts](https://mail.google.com/mail/#drafts) in your browser and verify the new draft is created.
3. Try sending another request and typing `n` to reject it. Verify that the server returns a `403 Forbidden` response:
   ```json
   {
     "detail": "Action rejected by user."
   }
   ```

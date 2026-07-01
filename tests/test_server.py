import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import sys
import os

# Add the parent directory (google-mcp-server) to the path so we can import the server modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import app

client = TestClient(app)

class TestMCPServer(unittest.TestCase):
    
    @patch('server.input', return_value='y')
    @patch('server.append_to_doc')
    def test_append_to_doc_approved(self, mock_append_to_doc, mock_input):
        # Setup mock behavior
        mock_append_to_doc.return_value = {"updated_document_id": "test-doc-id-123"}
        
        # Act
        response = client.post("/append_to_doc", json={
            "doc_id": "test-doc-id-123",
            "content": "Line of text to append."
        })
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        self.assertEqual(response.json()["documentId"], "test-doc-id-123")
        mock_append_to_doc.assert_called_once_with("test-doc-id-123", "Line of text to append.")
        mock_input.assert_called_once()

    @patch('server.input', return_value='n')
    @patch('server.append_to_doc')
    def test_append_to_doc_rejected(self, mock_append_to_doc, mock_input):
        # Act
        response = client.post("/append_to_doc", json={
            "doc_id": "test-doc-id-123",
            "content": "Line of text to append."
        })
        
        # Assert
        self.assertEqual(response.status_code, 403)
        self.assertIn("Action rejected by user", response.json()["detail"])
        mock_append_to_doc.assert_not_called()
        mock_input.assert_called_once()

    @patch('server.input', return_value='y')
    @patch('server.create_email_draft')
    def test_create_email_draft_approved(self, mock_create_draft, mock_input):
        # Setup mock behavior
        mock_create_draft.return_value = {"id": "draft-abc-123"}
        
        # Act
        response = client.post("/create_email_draft", json={
            "to": "user@example.com",
            "subject": "Test Draft Subject",
            "body": "This is the draft body."
        })
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        self.assertEqual(response.json()["draft"]["id"], "draft-abc-123")
        mock_create_draft.assert_called_once_with("user@example.com", "Test Draft Subject", "This is the draft body.")
        mock_input.assert_called_once()

    @patch('server.input', return_value='n')
    @patch('server.create_email_draft')
    def test_create_email_draft_rejected(self, mock_create_draft, mock_input):
        # Act
        response = client.post("/create_email_draft", json={
            "to": "user@example.com",
            "subject": "Test Draft Subject",
            "body": "This is the draft body."
        })
        
        # Assert
        self.assertEqual(response.status_code, 403)
        self.assertIn("Action rejected by user", response.json()["detail"])
        mock_create_draft.assert_not_called()
        mock_input.assert_called_once()

    @patch('server.input', return_value='y')
    @patch('server.append_to_doc', side_effect=Exception("Google Docs API simulated failure"))
    def test_append_to_doc_failure_propagation(self, mock_append_to_doc, mock_input):
        # Act
        response = client.post("/append_to_doc", json={
            "doc_id": "test-doc-id-123",
            "content": "Line of text to append."
        })
        
        # Assert
        self.assertEqual(response.status_code, 500)
        self.assertIn("Failed to append to Google Doc", response.json()["detail"])
        mock_append_to_doc.assert_called_once()

    def test_health_check(self):
        # Act
        response = client.get("/health")
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})

if __name__ == '__main__':
    unittest.main()

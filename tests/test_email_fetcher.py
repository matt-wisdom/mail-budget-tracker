import base64
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from google.oauth2.credentials import Credentials
from src.email_fetcher import authenticate_gmail, fetch_emails
from src.models import EmailData


@pytest.fixture
def mock_credentials():
    creds = MagicMock(spec=Credentials)
    creds.valid = True
    creds.expired = False
    creds.refresh_token = "mock_reftok"
    return creds


@patch("src.email_fetcher.pickle.load")
@patch("src.email_fetcher.open", create=True)
@patch("src.email_fetcher.os.path.exists", return_value=True)
def test_authenticate_gmail_existing_token(
    mock_exists, mock_open, mock_pickle_load, mock_credentials
):
    mock_pickle_load.return_value = mock_credentials
    creds = authenticate_gmail()
    assert creds.valid
    assert creds.refresh_token == "mock_reftok"


@patch("src.email_fetcher.InstalledAppFlow.from_client_secrets_file")
@patch("src.email_fetcher.pickle.dump")
@patch("src.email_fetcher.open", create=True)
def test_auth_gmail_new_token(mock_open, mock_pickle_dump, mock_flow):
    mock_flow.return_value.run_local_server.return_value = MagicMock(
        spec=Credentials, valid=True
    )
    creds = authenticate_gmail()
    assert creds.valid
    mock_pickle_dump.assert_called()


@patch("src.email_fetcher.authenticate_gmail")
@patch("src.email_fetcher.build")
def test_fetch_emails(mock_build, mock_authenticate_gmail, mock_credentials):
    mock_authenticate_gmail.return_value = mock_credentials
    mock_service = MagicMock()
    mock_build.return_value = mock_service

    mock_service.users().messages().list().execute.return_value = {
        "messages": [{"id": "12345"}]
    }

    mock_service.users().messages().get().execute.return_value = {
        "payload": {
            "headers": [
                {"name": "Subject", "value": "Test"},
                {"name": "From", "value": "test@example.com"},
                {"name": "Date", "value": "Fri, 26 Jan 2025 14:00:00"},
            ],
            "parts": [
                {
                    "mimeType": "text/plain",
                    "body": {"data": base64.urlsafe_b64encode(b"Yo Yo YO").decode()},
                }
            ],  # Base64 encoded "Test body"
        }
    }
    emails = fetch_emails(datetime(2025, 1, 25))
    assert len(emails) == 1
    assert emails[0].subject == "Test"
    assert emails[0].sender == "test@example.com"
    assert emails[0].body == "Yo Yo YO"
    assert isinstance(emails[0], EmailData)

import base64
from datetime import datetime
import os
import pickle
from typing import List
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import oauthlib
import oauthlib.oauth2
import oauthlib.oauth2.rfc6749

from src.transaction_filters import FILTERS

from .logger import LOGGER

from .models import EmailData

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def authenticate_gmail() -> Credentials:
    creds: Credentials = None
    token_path = "token.pickle"

    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "wb") as token:
            pickle.dump(creds, token)
    return creds


def is_alert_tx(header_text: str) -> bool:
    """
    Determines if the header_text corresponds to a bank alert (transaction, payment, withdrawal,
    deposit, or funding) by checking if any of the filter keyword combinations are present.

    Args:
        header_text (str): The email header text (typically the Subject field).

    Returns:
        bool: True if the header_text matches any of the alert keyword combinations, else False.
    """
    # Convert the header text to lowercase for case-insensitive matching.
    text = header_text.lower()

    # Iterate over each keyword pair (or combination) in the filters list.
    for combo in FILTERS:
        # Check if every keyword in the combination is found in the text.
        if all(keyword in text for keyword in combo):
            return True
    return False


def fetch_emails(date: datetime, mark_unread: bool = True) -> List[EmailData]:
    """
    Fetches emails from the Gmail inbox after a specified date.
    Args:
        date (datetime): The date after which emails should be fetched.
        mark_unread (bool, optional): Whether to mark the fetched emails as unread. Defaults to True.
    Returns:
        list: A list of dictionaries containing email data such as subject, sender, date received, and body.
    Raises:
        googleapiclient.errors.HttpError: If there is an error with the Gmail API request.
    Example:
        >>> from datetime import datetime
        >>> date = datetime(2023, 10, 1)
        >>> emails = fetch_emails(date)
        >>> for email in emails:
        >>>     print(email["subject"])
    """
    try:
        creds = authenticate_gmail()
    except oauthlib.oauth2.rfc6749.errors.AccessDeniedError as e:
        LOGGER.error(e)
        return []
    service = build("gmail", "v1", credentials=creds)
    date_str = date.strftime("%Y/%m/%d")
    query = f"after:{date_str}"
    results = (
        service.users()
        .messages()
        .list(userId="me", q=query, labelIds=["INBOX"])
        .execute()
    )
    messages = results.get("messages", [])

    if not messages:
        return []

    res: List[EmailData] = []
    for msg in messages:
        msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
        email_payload = msg_data["payload"]
        headers = email_payload["headers"]

        # Extract subject, sender, and date
        subject = next(
            (h["value"] for h in headers if h["name"] == "Subject"), "No Subject"
        )
        if is_alert_tx(subject) is False:
            continue

        sender = next(
            (h["value"] for h in headers if h["name"] == "From"), "Unknown Sender"
        )
        date_received = next(
            (h["value"] for h in headers if h["name"] == "Date"), "Unknown Date"
        )

        # Extract email body (plain text or HTML)
        body = "No Content"
        if "parts" in email_payload:
            for part in email_payload["parts"]:
                if part["mimeType"] == "text/plain":
                    body = base64.urlsafe_b64decode(part["body"]["data"]).decode(
                        "utf-8"
                    )
                    break  # Get first plain text part
        # Parse the date to a datetime object
        # Clean and parse the date received
        date_received = date_received.split(" (")[
            0
        ]  # Remove timezone in parentheses if present
        date_received = date_received.split(" +")[
            0
        ]  # Remove timezone offset if present
        date_received = date_received.split(" -")[
            0
        ]  # Remove timezone offset if present
        date_received = date_received.replace("GMT", "").replace("UTC", "").strip()

        try:
            date_received_dt = datetime.strptime(date_received, "%a, %d %b %Y %H:%M:%S")
        except ValueError as e:
            LOGGER.error(f"Error parsing date: {date_received} - {e}")
            date_received_dt = None

        if mark_unread:
            service.users().messages().modify(
                userId="me",
                id=msg["id"],
                body={
                    "removeLabelIds": ["UNREAD"],
                    "addLabelIds": ["UNREAD"],
                },  # Re-add UNREAD label
            ).execute()
        email_data = EmailData(
            id=msg["id"],
            subject=subject,
            sender=sender,
            date_received=date_received_dt,
            body=body,
        )
        res.append(email_data)
    return res

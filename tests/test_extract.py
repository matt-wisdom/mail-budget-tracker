import pytest
from unittest.mock import patch
from src.extract import (
    extract_from_mail,
    extract_json_from_markdown,
    write_transaction_to_db,
)
from src.models import Transaction

# Sample email with structured transaction details
EMAIL_TEXT = """Card Deposit Successful
Inbox

Grey <hello@grey.co>
Mon, Jan 20, 7:20 AM (13 days ago)
to me

Grey
Hello Wisdom,

Your card deposit was successful 🤑
The details are shown below:

Transaction Type:	NGN-USD
Amount tendered:	165000.00
Amount received:	96.40
Bank name: Grey
Payment Method:	card_deposit
Account number: 1234567890
Reference:	EPCMBKYWGMF
Date & Time:	01/20/2025 - 6:19 AM UTC
If you didn't initiate this transaction, please contact our support team immediately via in-app or email support@grey.co"""

# Mocked Gemini response based on the updated prompt
MOCK_GEMINI_RESPONSE = """```json
{
    "amount": 165000.00,
    "currency": "NGN",
    "date": "2025-01-20 06:19:00",
    "bank_name": "Grey",
    "sender": "Your Account",
    "receiver": "Grey",
    "transaction_type": "deposit",
    "classification": "personal",
    "account_number": "1234567890",
    "transaction_id": "EPCMBKYWGMF",
    "description": "Card deposit successful"
}
```"""

EXPECTED_TRANSACTION = Transaction(
    amount=165000.00,
    currency="NGN",
    date="2025-01-20 06:19:00",
    bank_name="Grey",
    sender="Your Account",
    receiver="Grey",
    transaction_type="deposit",
    classification="personal",
    account_number="1234567890",
    transaction_id="EPCMBKYWGMF",
    description="Card deposit successful",
)


@pytest.mark.parametrize(
    "markdown_text, expected",
    [
        (
            MOCK_GEMINI_RESPONSE,
            {
                "amount": 165000.00,
                "currency": "NGN",
                "date": "2025-01-20 06:19:00",
                "bank_name": "Grey",
                "sender": "Your Account",
                "receiver": "Grey",
                "transaction_type": "deposit",
                "classification": "personal",
                "account_number": "1234567890",
                "transaction_id": "EPCMBKYWGMF",
                "description": "Card deposit successful",
            },
        ),
        ("```json\n{invalid json}\n```", {"error": "Invalid JSON format"}),
        ("No JSON here", {"error": "No JSON found"}),
    ],
)
def test_extract_json_from_markdown(markdown_text, expected):
    """Test JSON extraction from markdown-formatted text."""
    assert extract_json_from_markdown(markdown_text) == expected


@patch("src.extract.prompt_gemini", return_value=MOCK_GEMINI_RESPONSE)
def test_extract_from_mail(mock_prompt_gemini):
    """Test extracting transaction details from email."""
    transaction = extract_from_mail(EMAIL_TEXT)

    assert transaction == EXPECTED_TRANSACTION
    mock_prompt_gemini.assert_called_once()


@patch("src.extract.insert_transaction", return_value=1)
@patch("src.extract.insert_transaction_details", return_value=1)
@patch("src.extract.insert_bank", return_value=1)
@patch("src.extract.insert_date", return_value=1)
@patch("src.extract.insert_customer", return_value=1)
def test_write_transaction_to_db(
    mock_cust, mock_date, mock_bank, mock_tdet, mock_trans
):
    assert write_transaction_to_db(EXPECTED_TRANSACTION, 0) == 1
    mock_cust.assert_called_once()
    mock_date.assert_called_once()
    mock_bank.assert_called_once()
    mock_tdet.assert_called_once()
    mock_trans.assert_called_once()

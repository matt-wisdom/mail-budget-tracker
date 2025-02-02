import json
import os
import re
import google.generativeai as genai

from src.db import (
    insert_bank,
    insert_customer,
    insert_date,
    insert_transaction,
    insert_transaction_details,
)
from src.models import Transaction

from .prompts import EXTRACT_EMAIL_PROMPT

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel(os.getenv("GEMINI_MODEL_TYPE") or "gemini-1.5-flash")


def prompt_gemini(prompt: str) -> str:
    response = model.generate_content(prompt)
    resp_text = response.text
    return resp_text


def extract_json_from_markdown(markdown_text):
    # Regular expression to match JSON block inside triple backticks
    json_match = re.search(r"```json\n(.*?)\n```", markdown_text, re.DOTALL)

    if json_match:
        json_str = json_match.group(1)
        try:
            return json.loads(json_str)  # Convert to Python dictionary
        except json.JSONDecodeError:
            return {"error": "Invalid JSON format"}

    return {"error": "No JSON found"}


def extract_from_mail(email: str) -> Transaction:
    json_string = prompt_gemini(EXTRACT_EMAIL_PROMPT.format(email=email))
    data = extract_json_from_markdown(json_string)
    return Transaction(**data)


def write_transaction_to_db(transaction: Transaction) -> int:
    cust_id = insert_customer(
        transaction.sender, transaction.receiver, transaction.account_number
    )
    bank_id = insert_bank(transaction.bank_name)
    date_id = insert_date(transaction.date)
    transaction_details_id = insert_transaction_details(
        transaction.transaction_id,
        transaction.transaction_type,
        transaction.classification,
        transaction.description,
    )
    id = insert_transaction(
        transaction.amount,
        transaction.currency,
        date_id,
        cust_id,
        bank_id,
        transaction_details_id,
    )
    return id


if __name__ == "__main__":
    txt = """Card Deposit Successful
Inbox

Grey <hello@grey.co>
Mon, Jan 20, 7:20 AM (13 days ago)
to me

Grey
Hello Wisdom,

Your card deposit was successful 🤑
The details are shown below:

Transaction Type:	NGN-USD
Amount tendered:	165000.00
Amount received:	96.40
Payment Method:	card_deposit
Reference:	EPCMBKYWGMF
Date & Time:	01/20/2025 - 6:19 AM UTC
If you didn't initiate this transaction, please contact our support team immediately via in-app or email support@grey.co"""
    print(write_transaction_to_db(extract_from_mail(txt)))

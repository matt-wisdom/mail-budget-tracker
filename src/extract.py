import json
import os
import re
import google.generativeai as genai
from pydantic import ValidationError
import pydantic_core

from src.db import (
    insert_bank,
    insert_customer,
    insert_date,
    insert_time,
    insert_transaction,
    insert_transaction_details,
)
from src.logger import LOGGER
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
            LOGGER.error("Invalid JSON")
            return {"error": "Invalid JSON format"}
    LOGGER.error("No JSON data could be extracted")
    return {"error": "No JSON found"}


def extract_from_mail(email: str) -> Transaction:
    json_string = prompt_gemini(EXTRACT_EMAIL_PROMPT.format(email=email))
    data = extract_json_from_markdown(json_string)
    try:
        print(data)
        return Transaction(**data)
    except (
        ValueError,
        ValidationError,
        pydantic_core._pydantic_core.ValidationError,
    ) as e:
        LOGGER.error(f"Error parsing transaction data: {e}")
        raise e


def write_transaction_to_db(transaction: Transaction, email_id: int) -> int:
    sender_id = insert_customer(transaction.sender)
    receiver_id = insert_customer(transaction.receiver)
    bank_id = insert_bank(transaction.bank_name)
    date_id = insert_date(transaction.date)
    time_id = insert_time(transaction.date)
    transaction_details_id = insert_transaction_details(
        transaction.transaction_id,
        transaction.transaction_type,
        transaction.classification,
        transaction.description,
        transaction.account_number,
    )
    id = insert_transaction(
        transaction.amount,
        transaction.currency,
        date_id,
        time_id,
        sender_id,
        receiver_id,
        bank_id,
        email_id,
        transaction_details_id,
    )
    return id

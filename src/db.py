import os
import psycopg
from datetime import datetime
from contextlib import contextmanager

import holidays

from src.logger import LOGGER


# Reusable context manager for DB connections
@contextmanager
def get_db_connection():
    conn = psycopg.connect(os.getenv("DATABASE_URL"))
    try:
        yield conn
    finally:
        conn.commit()  # Commit changes once at the end
        conn.close()  # Ensure connection is closed


def check_existence(table: str, field: str, value: str) -> int:
    query = f"SELECT id FROM {table} WHERE {field} = %s"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (value,))
                result = cur.fetchone()
                if result:
                    return result[0]
    except Exception as e:
        LOGGER.error(f"Error checking {field} existence in {table}: {e}")
    return 0


def email_exists(email_id: str) -> bool:
    query = "SELECT 1 FROM dim_email WHERE email_id = %s"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (email_id,))
                return cur.fetchone() is not None
    except Exception as e:
        LOGGER.error(f"Error checking email existence: {e}")
        return False


def insert_data(query: str, values: tuple) -> int:
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, values)
                return cur.fetchone()[0]  # Return the inserted ID
    except Exception as e:
        LOGGER.error(f"Error inserting data: {e}")
        return 0


def insert_transaction_details(
    transaction_id: str,
    transaction_type: str,
    classification: str,
    description: str,
    account_number: str,
) -> int:
    transaction_id = check_existence(
        "dim_transaction_details", "transaction_id", transaction_id
    )
    if transaction_id:
        return transaction_id
    query = """
        INSERT INTO dim_transaction_details (transaction_id, transaction_type, classification, description, account_number)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """
    return insert_data(
        query,
        (transaction_id, transaction_type, classification, description, account_number),
    )


def insert_time(time: datetime) -> int:
    time_id = check_existence("dim_time", "time", time.time())
    if time_id:
        return time_id

    hour = time.hour
    minute = time.minute
    is_day = 6 <= hour < 18
    is_morning = 6 <= hour < 12
    is_afternoon = 12 <= hour < 18
    is_evening = 18 <= hour < 24

    query = """
        INSERT INTO dim_time (time, hour, minute, is_day, is_morning, is_afternoon, is_evening)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """
    values = (time.time(), hour, minute, is_day, is_morning, is_afternoon, is_evening)
    return insert_data(query, values)


def insert_date(date: datetime) -> int:
    date_id = check_existence("dim_date", "date", date.date())
    if date_id:
        return date_id

    def is_holiday(date: datetime) -> bool:
        all_holidays = getattr(holidays, os.getenv("HOLIDAY_LOCALE", "NG"))
        return date.date() in all_holidays

    is_weekday = date.weekday() < 5
    query = """
        INSERT INTO dim_date (date, year, day_of_week, month, day_of_month, is_holiday, is_weekday)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """
    values = (
        date.date(),
        date.year,
        date.weekday(),
        date.month,
        date.day,
        is_holiday(date),
        is_weekday,
    )
    return insert_data(query, values)


def insert_bank(bank_name: str) -> int:
    # Use the new function to check for bank existence
    bank_id = check_existence("dim_bank", "bank_name", bank_name)
    if bank_id:
        return bank_id

    query = """
        INSERT INTO dim_bank (bank_name)
        VALUES (%s)
        RETURNING id
    """
    return insert_data(query, (bank_name,))


def insert_email(
    email_id: str, subject: str, sender: str, date_received: datetime, body: str
) -> int:
    query = """
        INSERT INTO dim_email (email_id, subject, sender, date_received, body)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """
    return insert_data(query, (email_id, subject, sender, date_received, body))


def insert_customer(name: str) -> int:
    customer_id = check_existence("dim_customer", "name", name)
    if customer_id:
        return customer_id
    query = """
        INSERT INTO dim_customer (name)
        VALUES (%s)
        RETURNING id
    """
    return insert_data(query, (name,))


def insert_transaction(
    amount: float,
    currency: str,
    date_id: int,
    time_id: int,
    sender_id: int,
    receiver_id: int,
    bank_id: int,
    transaction_id: int,
    email_id: int,
) -> int:
    query = """
        INSERT INTO transactions (amount, currency, date_id, time_id, sender_id, receiver_id, bank_id, transaction_id, email_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING transaction_id
    """
    return insert_data(
        query,
        (
            amount,
            currency,
            date_id,
            time_id,
            sender_id,
            receiver_id,
            bank_id,
            transaction_id,
            email_id,
        ),
    )

import os
import psycopg
from datetime import datetime
from contextlib import contextmanager

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


def insert_data(query: str, values: tuple) -> int:
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, values)
                return cur.fetchone()[0]  # Return the inserted ID
    except Exception as e:
        LOGGER.error(f"Error inserting data: {e}")
        return 0


# Function to insert transaction details
def insert_transaction_details(
    transaction_id: str, transaction_type: str, classification: str, description: str
) -> int:
    query = """
        INSERT INTO dim_transaction_details (transaction_id, transaction_type, classification, description)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """
    return insert_data(
        query, (transaction_id, transaction_type, classification, description)
    )


# Function to insert date details
def insert_date(date: datetime) -> int:
    query = """
        INSERT INTO dim_date (date, year, day_of_week, month, day_of_month, hour, minute, second)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """
    values = (
        date,
        date.year,
        date.weekday(),
        date.month,
        date.day,
        date.hour,
        date.minute,
        date.second,
    )
    return insert_data(query, values)


# Function to insert bank details
def insert_bank(bank_name: str) -> int:
    query = """
        INSERT INTO dim_bank (bank_name)
        VALUES (%s)
        RETURNING id
    """
    return insert_data(query, (bank_name,))


# Function to insert customer details
def insert_customer(sender: str, receiver: str, account_number: str) -> int:
    query = """
        INSERT INTO dim_customer (sender, receiver, account_number)
        VALUES (%s, %s, %s)
        RETURNING id
    """
    return insert_data(query, (sender, receiver, account_number))


# Function to insert transaction
def insert_transaction(
    amount: float,
    currency: str,
    date_id: int,
    cust_id: int,
    bank_id: int,
    transaction_id: int,
) -> int:
    query = """
        INSERT INTO transactions (amount, currency, date_id, customer_id, bank_id, transaction_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING transaction_id
    """
    return insert_data(
        query, (amount, currency, date_id, cust_id, bank_id, transaction_id)
    )

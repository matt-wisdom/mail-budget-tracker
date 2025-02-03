from typing import List, Tuple
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
import pendulum

from src.db import email_exists, insert_email
from src.email_fetcher import fetch_emails
from src.extract import extract_from_mail, write_transaction_to_db
from src.models import EmailData, Transaction


@dag(
    schedule="@daily",
    catchup=True,
    start_date=pendulum.datetime(2020, 1, 1, tz="UTC"),
    tags=["ETL"],
)
def mail_etl():
    @task()
    def extract() -> List[EmailData]:
        """
        Extract emails that are bank transaction alerts
        during current execution date.
        """

        context = get_current_context()
        emails = fetch_emails(context["execution_date"], False)
        return emails

    @task()
    def transform(email: EmailData) -> Tuple[EmailData, Transaction]:
        date = get_current_context()["execution_date"].isoformat()
        tx = extract_from_mail(f"{email.subject}\nDate received: {date} \n{email.body}")
        return email, tx

    @task()
    def load(email_tx: Tuple[EmailData, Transaction]):
        email, tx = email_tx
        if email_exists(email.id):
            return
        email_id = insert_email(
            email.id, email.subject, email.sender, email.date_received, email.body
        )
        write_transaction_to_db(tx, email_id)

    tf = transform.expand(email=extract())
    load.expand(email_tx=tf)


mail_etl()

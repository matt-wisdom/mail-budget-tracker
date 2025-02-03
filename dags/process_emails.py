import sys
from pathlib import Path
from typing import List, Tuple
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
import pendulum
import pydantic_core

src_path = Path(__file__).resolve().parent.parent
sys.path.append(src_path.absolute().as_posix())
from src.db import email_exists, insert_email  # noqa: E402
from src.email_fetcher import fetch_emails  # noqa: E402
from src.extract import extract_from_mail, write_transaction_to_db  # noqa: E402
from src.models import EmailData, Transaction  # noqa: E402


@dag(
    schedule="@daily",
    catchup=True,
    start_date=pendulum.datetime(2024, 1, 28, tz="UTC"),
    tags=["ETL"],
)
def mail_etl():
    @task()
    def extract() -> List[dict]:
        """
        Extract emails that are bank transaction alerts
        during current execution date.
        """

        context = get_current_context()
        emails = fetch_emails(context["execution_date"], False)
        return [email.model_dump() for email in emails]

    @task()
    def transform(emails: List[dict]) -> List[Tuple[dict, dict]]:
        out = []
        for email in emails:
            email_md = EmailData(**email)
            date = get_current_context()["execution_date"].isoformat()
            try:
                tx = extract_from_mail(
                    f"{email_md.subject}\nDate received: {date} \n{email_md.body}"
                )
            except pydantic_core._pydantic_core.ValidationError:
                continue
            out.append((email, tx.model_dump()))
        return out

    @task()
    def load(email_tx: Tuple[dict, dict]):
        email, tx = email_tx
        email = EmailData(**email)
        tx = Transaction(**tx)
        if email_exists(email.id):
            return
        email_id = insert_email(
            email.id, email.subject, email.sender, email.date_received, email.body
        )
        write_transaction_to_db(tx, email_id)

    tf = transform(emails=extract())
    load.expand(email_tx=tf)


mail_etl()

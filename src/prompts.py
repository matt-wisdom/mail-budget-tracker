EXTRACT_EMAIL_PROMPT = """
Task: Extract structured data from bank transaction alert emails.
Output Format: JSON

Required Fields:

amount: Extract the transaction amount as a numerical value.
currency: Identify the currency used in the transaction (e.g., USD, NGN, EUR).
date: Extract and format the transaction date as YYYY-MM-DD HH:MM:SS.
bank_name: Identify the bank/organization sending the alert (usually in the footer or header, bank names in the body tend to be recievers bank).
sender: Extract the sender's name or account details (if available).
receiver: Extract the recipient's name or account number (if available).
account_number: Account the money is going to
transaction_type: Classify the transaction type (deposit, withdrawal, transfer, payment, refund).
classification: Determine if the transaction is personal, business, salary, loan, investment, utility, etc.
transaction_id: Transaction ID
description: Description text
Example Input Email: Your withdrawal was successful 😀
Inbox
Grey <hello@grey.co>
Jan 30, 2025, 1:14 PM (3 days ago)
to me
Grey Inc
Hello Wisdom,
Your withdrawal was successful 😀
The details are shown below:
Transaction Type:	NGN to NGN
Amount tendered:	₦8,100.00
Amount received:	₦8,065.00
Bank name:	Opay
Account name:	WISDOM OCHEJE MATTHEW
Account number:	9064442596
Fee:	₦35.00
Reference:	ZJDGUOGLCVY
Date & Time:	01/30/2025 - 12:11 PM UTC
If you didn't initiate this transaction, please contact our support team immediately via in-app or email support@grey.com
Get foreign banking at your fingertips
Get our mobile app on any device you use on the App Store or Google Playstore
Grey
Grey
For any feedback or inquiries, get in touch with us at
support@grey.co
Grey's services are provided by Grey Inc.
A company duly incorporated under the laws of Delaware,
United States of America.
651 N Broad St, Suite 206, Middletown DE 19700 US
Copyright © Grey. 2023 All rights reserved.


Expected JSON Output:
{{
  "amount": 8100.00,
  "currency": "NGN",
  "date": "2025-01-30 12:11:00",
  "bank_name": "Grey",
  "sender": "Your Account",
  "receiver": "WISDOM OCHEJE MATTHEW",
  "transaction_type": "withdrawal",
  "classification": "personal",
  "account_number": "9064442596",
  "transaction_id": "ZJDGUOGLCVY",
  "description": null
}}

Instructions:

If the transaction is a debit, infer the sender as "Customer’s Account" and extract the receiver.
If the transaction is a credit, infer the receiver as "Customer’s Account" and extract the sender.
Identify the transaction type using keywords:
"POS", "ATM", "debit" → withdrawal
"credit", "deposit" → deposit
"transfer", "wire" → transfer
"salary", "wages" → salary
"loan disbursed", "repayment" → loan
"utility", "electricity", "water", "bill" → utility
Also use hints like account name in cases where you can find keywords.
Ensure date formatting is consistent (YYYY-MM-DD HH:MM:SS).
Ignore irrelevant information like available balance.

Email: {email}
JSON fields are:
"""

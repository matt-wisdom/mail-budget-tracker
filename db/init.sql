CREATE TABLE "dim_date" (
  "id" SERIAL PRIMARY KEY,
  "date" timestamp,
  "year" integer,
  "day_of_week" integer,
  "month" integer,
  "day_of_month" integer,
  "hour" integer,
  "minute" integer,
  "second" integer
);

CREATE TABLE "dim_email" (
  "id" SERIAL PRIMARY KEY,
  "email_id" varchar(255),
  "subject" varchar(988),
  "sender" varchar(320),
  "date_received" timestamp,
  "body" text
);

CREATE TABLE "dim_customer" (
  "id" SERIAL PRIMARY KEY,
  "sender" varchar(64),
  "receiver" varchar(64),
  "account_number" varchar(10)
);

CREATE TABLE "transactions" (
  "amount" float,
  "currency" varchar(3),
  "date_id" integer,
  "customer_id" integer,
  "bank_id" integer,
  "transaction_id" integer,
  "email_id" integer
);

CREATE TABLE "dim_bank" (
  "id" SERIAL PRIMARY KEY,
  "bank_name" varchar(64)
);

CREATE TABLE "dim_transaction_details" (
  "id" SERIAL PRIMARY KEY,
  "transaction_id" varchar(32),
  "transaction_type" varchar(12),
  "classification" varchar(12),
  "description" varchar(128)
);

ALTER TABLE "transactions" ADD FOREIGN KEY ("bank_id") REFERENCES "dim_bank" ("id");

ALTER TABLE "transactions" ADD FOREIGN KEY ("transaction_id") REFERENCES "dim_transaction_details" ("id");

ALTER TABLE "transactions" ADD FOREIGN KEY ("date_id") REFERENCES "dim_date" ("id");

ALTER TABLE "transactions" ADD FOREIGN KEY ("customer_id") REFERENCES "dim_customer" ("id");

ALTER TABLE "transactions" ADD FOREIGN KEY ("email_id") REFERENCES "dim_email" ("id");

CREATE INDEX "email_id_index" ON "dim_email" ("email_id");

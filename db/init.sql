-- Create additional users
CREATE USER airflow WITH ENCRYPTED PASSWORD 'airflow';
-- CREATE USER postgres WITH ENCRYPTED PASSWORD 'postgres';

-- Create databases
-- CREATE DATABASE mailbudget OWNER postgres;
CREATE DATABASE airflow OWNER airflow;

-- Grant privileges
-- GRANT ALL PRIVILEGES ON DATABASE mailbudget TO postgres;
GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;

CREATE TABLE "dim_date" (
  "id" SERIAL PRIMARY KEY,
  "date" DATE UNIQUE,
  "year" integer,
  "day_of_week" integer,
  "month" integer,
  "day_of_month" integer,
  "is_holiday" bool,
  "is_weekday" bool
);

CREATE TABLE "dim_time" (
  "id" SERIAL PRIMARY KEY,
  "time" TIME UNIQUE,
  "hour" integer,
  "minute" integer,
  "is_day" bool,
  "is_morning" bool,
  "is_afternoon" bool,
  "is_evening" bool
);

CREATE TABLE "dim_email" (
  "id" SERIAL PRIMARY KEY,
  "email_id" varchar(255) UNIQUE,
  "subject" varchar(988),
  "sender" varchar(320),
  "date_received" timestamp,
  "body" text
);

CREATE TABLE "dim_customer" (
  "id" SERIAL PRIMARY KEY,
  "name" varchar(64) UNIQUE
);

CREATE TABLE "transactions" (
  "amount" float,
  "currency" varchar(3),
  "date_id" integer,
  "time_id" integer,
  "sender_id" integer,
  "receiver_id" integer,
  "bank_id" integer,
  "transaction_id" integer,
  "email_id" integer
);

CREATE TABLE "dim_bank" (
  "id" SERIAL PRIMARY KEY,
  "bank_name" varchar(64) UNIQUE
);

CREATE TABLE "dim_transaction_details" (
  "id" SERIAL PRIMARY KEY,
  "transaction_id" varchar(32),
  "transaction_type" varchar(12),
  "account_number" varchar(10),
  "classification" varchar(12),
  "description" varchar(128)
);

CREATE INDEX "email_id_index" ON "dim_email" ("email_id");

ALTER TABLE "transactions" ADD FOREIGN KEY ("bank_id") REFERENCES "dim_bank" ("id");

ALTER TABLE "transactions" ADD FOREIGN KEY ("transaction_id") REFERENCES "dim_transaction_details" ("id");

ALTER TABLE "transactions" ADD FOREIGN KEY ("date_id") REFERENCES "dim_date" ("id");

ALTER TABLE "transactions" ADD FOREIGN KEY ("time_id") REFERENCES "dim_time" ("id");

ALTER TABLE "transactions" ADD FOREIGN KEY ("sender_id") REFERENCES "dim_customer" ("id");

ALTER TABLE "transactions" ADD FOREIGN KEY ("receiver_id") REFERENCES "dim_customer" ("id");

ALTER TABLE "transactions" ADD FOREIGN KEY ("email_id") REFERENCES "dim_email" ("id");

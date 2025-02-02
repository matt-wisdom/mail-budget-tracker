CREATE TABLE "dim_date" (
  "id" serial PRIMARY KEY,
  "date" timestamp,
  "year" integer,
  "day_of_week" integer,
  "month" integer,
  "day_of_month" integer,
  "hour" integer,
  "minute" integer,
  "second" integer
);

CREATE TABLE "dim_customer" (
  "id" serial PRIMARY KEY,
  "sender" varchar(64),
  "receiver" varchar(64),
  "account_number" varchar(10)
);

CREATE TABLE "transactions" (
  "amount" float,
  "currency" varchar(3),
  "date_id" integer,
  "user_id" integer,
  "bank_id" integer,
  "transaction_id" integer
);

CREATE TABLE "dim_bank" (
  "id" serial PRIMARY KEY,
  "bank_name" varchar(64)
);

CREATE TABLE "dim_transaction_details" (
  "id" serial PRIMARY KEY,
  "transaction_id" varchar(32),
  "transaction_type" varchar(12),
  "classification" varchar(12),
  "description" varchar(128)
);

ALTER TABLE "transactions" ADD FOREIGN KEY ("bank_id") REFERENCES "dim_bank" ("id");

ALTER TABLE "transactions" ADD FOREIGN KEY ("transaction_id") REFERENCES "dim_transaction_details" ("id");

ALTER TABLE "transactions" ADD FOREIGN KEY ("date_id") REFERENCES "dim_date" ("id");

ALTER TABLE "transactions" ADD FOREIGN KEY ("user_id") REFERENCES "dim_customer" ("id");

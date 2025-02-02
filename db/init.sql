CREATE TABLE "dimdate" (
  "id" serial PRIMARY KEY,
  "date" timestamp,
  "year" integer,
  "dow" integer,
  "month" integer,
  "dom" integer
);

CREATE TABLE "transactions" (
  "amount" float,
  "currency" varchar(3),
  "date_id" integer,
  "user_id" integer,
  "bank_id" integer,
  "transaction_type_id" integer
);

CREATE TABLE "dimuser" (
  "id" serial PRIMARY KEY,
  "username" varchar(32),
  "location" varchar(64),
  "created_at" timestamp
);

CREATE TABLE "dimbank" (
  "id" serial PRIMARY KEY,
  "name" varchar(64),
  "bank_class" varchar(10)
);

CREATE TABLE "dim_transaction_type" (
  "id" serial PRIMARY KEY,
  "transaction_type" varchar(10)
);

ALTER TABLE "transactions" ADD FOREIGN KEY ("bank_id") REFERENCES "dimbank" ("id");

ALTER TABLE "transactions" ADD FOREIGN KEY ("transaction_type_id") REFERENCES "dim_transaction_type" ("id");

ALTER TABLE "transactions" ADD FOREIGN KEY ("date_id") REFERENCES "dimdate" ("id");

ALTER TABLE "transactions" ADD FOREIGN KEY ("user_id") REFERENCES "dimuser" ("id");

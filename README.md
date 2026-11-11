# Invoice Data Pipeline

I built this project to learn how data engineers turn messy raw data into clean tables and useful reports. It takes a small file of invoices, tidies it up, and answers simple business questions like "what is the total amount in rupees for each city, biggest first"?

## The problem

The raw invoice file (`invoices.csv`) is messy:
- Names have extra spaces and inconsistent capitalisation
- One invoice appears twice
- One amount is missing
- Amounts are in three currencies (USD, EUR and INR), so they can't be added together

## What my pipeline does

1. Reads the raw invoices from `invoices.csv`
2. Cleans the data: trims spaces, fixes names, removes the duplicate, fills the missing amount with 0, and converts dates
3. Fetches today's USD and EUR exchange rates from the Frankfurter API and converts every amount to INR
4. Splits the data into a star schema: a customer table, a date table and a fact table
5. Saves everything into a SQLite database
6. Runs SQL queries for two reports and saves them as CSV files
7. Writes short log messages while it runs, so I can see what happened

## Tools I used

Python, pandas, requests, SQLite and SQL



## How to run it

```
pip install pandas requests
python pipeline.py
```

## What you get

- `invoice_star.db`: the database with all three tables
- `report_by_customer.csv`: total amount in INR for each customer
- `report_by_city.csv`: total amount in INR for each city

## How the tables are organised

| Table | What it holds |
|---|---|
| `dim_customer` | each customer once, with a `customer_id` |
| `dim_date` | each invoice date once, with a `date_id` |
| `fact` | one row per invoice: the ids, the amount, the rate and the amount in INR |

I split the data this way so each customer's name and city is stored once and not repeated on every invoice.

## What I learned

How to clean data with pandas, call an API, design a star schema, write SQL joins and group-by queries, and log a pipeline's steps.
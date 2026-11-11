import pandas as pd
import requests
import sqlite3
import logging

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s")

#  Read and clean
df = pd.read_csv("invoices.csv")
logging.info("Read %s rows from invoices.csv",len(df))
df["customer"] = df["customer"].str.strip()
df["customer"] = df["customer"].str.capitalize()
df = df.drop_duplicates()
logging.info("%s rows left after removing duplicates",len(df))
df["amount"] = df["amount"].fillna(0)
df["invoice_date"] = pd.to_datetime(df["invoice_date"])

# Convert currency to INR
usd = requests.get("https://api.frankfurter.dev/v1/latest?base=USD&symbols=INR").json()["rates"]["INR"]
eur = requests.get("https://api.frankfurter.dev/v1/latest?base=EUR&symbols=INR").json()["rates"]["INR"]
rates = {"USD": usd, "EUR": eur, "INR": 1}
df["rate"] = df["currency"].map(rates)
df["amount_inr"] = df["amount"] * df["rate"]

# Build dimension tables
dim_customer = df[["customer", "city"]]
dim_customer = dim_customer.drop_duplicates()
dim_customer = dim_customer.reset_index(drop=True)
dim_customer["customer_id"] = dim_customer.index + 1

dim_date = df[["invoice_date"]]
dim_date = dim_date.drop_duplicates()
dim_date = dim_date.reset_index(drop=True)
dim_date["date_id"] = dim_date.index + 1

# Build fact table 
fact = df.merge(dim_customer, how="left", on=["customer", "city"])
fact = fact.merge(dim_date, how="left", on=["invoice_date"])
fact = fact[["invoice_id", "customer_id", "date_id", "amount", "rate", "amount_inr"]]

# Save to database
conn = sqlite3.connect("invoice_star.db")
dim_customer.to_sql("dim_customer", conn, index=False, if_exists="replace")
dim_date.to_sql("dim_date", conn, index=False, if_exists="replace")
fact.to_sql("fact", conn, index=False, if_exists="replace")

# Query Reports
q = """SELECT c.customer, SUM(f.amount_inr) AS total_inr
FROM fact AS f
INNER JOIN dim_customer AS c ON f.customer_id = c.customer_id
GROUP BY c.customer
ORDER BY total_inr DESC"""

q2 = """SELECT c.city, SUM(f.amount_inr) AS total_inr
FROM fact AS f
INNER JOIN dim_customer AS c ON f.customer_id = c.customer_id
GROUP BY c.city
ORDER BY total_inr DESC"""

pd.read_sql(q, conn).to_csv("report_by_customer.csv", index=False)
pd.read_sql(q2, conn).to_csv("report_by_city.csv", index=False)

conn.close()
print("Pipeline finished")
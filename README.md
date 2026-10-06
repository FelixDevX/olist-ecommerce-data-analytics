# E-Commerce Sales, Customer & Delivery Analytics

Portfolio-grade analytics project built from the Olist Brazilian E-Commerce Public Dataset.

## Stack

- Python
- Pandas / NumPy
- Matplotlib / Seaborn
- MySQL
- Power BI
- VS Code

## Project flow

Raw Olist CSVs → Python cleaning & EDA → MySQL business analysis → Power BI dashboard

## Quick start in VS Code

### 1. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell blocks activation, run:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. Run the analysis

```powershell
python src\analysis.py
```

The script creates curated CSVs inside `output/` for Power BI.

### 3. SQL

Open `sql/01_schema.sql` in MySQL Workbench, create the database/tables, import the raw CSVs, then run `sql/02_business_queries.sql`.

### 4. Power BI

Follow `powerbi/POWER_BI_GUIDE.md`.

## Main business questions

- How much revenue/payment value is generated over time?
- Which product categories perform best?
- Which states generate the most revenue?
- Which payment methods are most used?
- How long do customers wait for delivery?
- What percentage of orders are late?
- How are review scores distributed?
- Which sellers generate the most item revenue?
- What share of customers are repeat customers?

## Data model

`customers` → `orders` → `order_items` → `products`

`orders` → `order_payments`

`orders` → `order_reviews`

`order_items` → `sellers`

`products` → `category_translation`

## Metric caution

The dataset does not provide seller cost/COGS. Therefore the project deliberately avoids presenting a calculated number as true profit.

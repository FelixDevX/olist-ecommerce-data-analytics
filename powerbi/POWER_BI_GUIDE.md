# Power BI Dashboard Guide

## Recommended dashboard pages

### Page 1 — Executive Overview
Cards:
- Total Payment Value
- Total Orders
- Total Customers
- Average Order Value
- Average Review Score
- Late Delivery Rate

Charts:
- Monthly revenue trend
- Revenue by state
- Top 10 categories
- Payment method mix

### Page 2 — Product & Seller Performance
- Top categories by revenue
- Units sold by category
- Top sellers
- Seller revenue by state
- Category slicer

### Page 3 — Customer & Delivery Analytics
- One-time vs repeat customers
- Orders by customer state
- Average delivery days by month
- Late vs on-time orders
- Review score distribution

## Import

1. Run `python src/analysis.py`.
2. In Power BI Desktop choose **Get Data → Text/CSV**.
3. Import the CSVs generated in `output/`.
4. Set `purchase_month` as a text/month label or create a proper Date table for time intelligence.
5. Format `revenue`, `payment_value`, `avg_order_value`, and freight as currency.
6. Format `Late Delivery Rate` as a percentage.

## Important metric note

The Olist public dataset does not contain seller cost/COGS, so this project should use **revenue/payment value/GMV-style metrics**, not claim a true profit figure.

For a polished portfolio dashboard, use consistent slicers for year, month, state, category, payment type, and order status.

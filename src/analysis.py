import os
import pandas as pd
import matplotlib.pyplot as plt

from sqlalchemy import create_engine
from sqlalchemy.engine import URL


# ============================================================
# OLIST E-COMMERCE ANALYTICS
# ============================================================

print("\n==============================================")
print("       OLIST E-COMMERCE DATA ANALYSIS")
print("==============================================\n")


# ============================================================
# 1. MYSQL CONFIGURATION
# ============================================================

MYSQL_USER = "olist_user"
MYSQL_PASSWORD = "Olist@12345"
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_DATABASE = "olist_ecommerce"


# ============================================================
# 2. PROJECT DIRECTORIES
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CHART_DIR = os.path.join(OUTPUT_DIR, "charts")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CHART_DIR, exist_ok=True)


# ============================================================
# 3. DATABASE CONNECTION
# ============================================================

connection_url = URL.create(
    drivername="mysql+pymysql",
    username=MYSQL_USER,
    password=MYSQL_PASSWORD,
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    database=MYSQL_DATABASE
)

engine = create_engine(connection_url)

print("Connecting to MySQL...")

try:
    with engine.connect() as connection:
        print("✅ MySQL connection successful!")
        print(f"Database: {MYSQL_DATABASE}\n")

except Exception as e:
    print("❌ MySQL connection failed!")
    print(e)
    exit()


# ============================================================
# 4. LOAD DATA
# ============================================================

print("Loading data...\n")


orders = pd.read_sql(
    "SELECT * FROM orders",
    engine
)

customers = pd.read_sql(
    "SELECT * FROM customers",
    engine
)

order_items = pd.read_sql(
    "SELECT * FROM order_items",
    engine
)

payments = pd.read_sql(
    "SELECT * FROM order_payments",
    engine
)

reviews = pd.read_sql(
    "SELECT * FROM order_reviews",
    engine
)

products = pd.read_sql(
    "SELECT * FROM products",
    engine
)

sellers = pd.read_sql(
    "SELECT * FROM sellers",
    engine
)

category_translation = pd.read_sql(
    "SELECT * FROM category_translation",
    engine
)


print("Data loaded successfully!")

print(f"Orders:              {len(orders):,}")
print(f"Customers:           {len(customers):,}")
print(f"Order Items:         {len(order_items):,}")
print(f"Payments:            {len(payments):,}")
print(f"Reviews:             {len(reviews):,}")
print(f"Products:            {len(products):,}")
print(f"Sellers:             {len(sellers):,}")
print(f"Categories:          {len(category_translation):,}")


# ============================================================
# 5. DATA CLEANING
# ============================================================

print("\nCleaning data...")


date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

for column in date_columns:

    if column in orders.columns:

        orders[column] = pd.to_datetime(
            orders[column],
            errors="coerce"
        )


reviews["review_creation_date"] = pd.to_datetime(
    reviews["review_creation_date"],
    errors="coerce"
)

reviews["review_answer_timestamp"] = pd.to_datetime(
    reviews["review_answer_timestamp"],
    errors="coerce"
)


print("✅ Data cleaning completed.")


# ============================================================
# 6. EXECUTIVE KPIs
# ============================================================

print("\n==============================================")
print("                 EXECUTIVE KPIs")
print("==============================================")


total_revenue = payments["payment_value"].sum()

total_orders = orders["order_id"].nunique()

total_customers = customers["customer_unique_id"].nunique()

total_products = products["product_id"].nunique()

total_sellers = sellers["seller_id"].nunique()

average_order_value = (
    total_revenue / total_orders
)

average_review_score = reviews["review_score"].mean()


kpis = pd.DataFrame({
    "metric": [
        "Total Revenue",
        "Total Orders",
        "Total Customers",
        "Total Products",
        "Total Sellers",
        "Average Order Value",
        "Average Review Score"
    ],

    "value": [
        total_revenue,
        total_orders,
        total_customers,
        total_products,
        total_sellers,
        average_order_value,
        average_review_score
    ]
})


print(kpis.to_string(index=False))


kpis.to_csv(
    os.path.join(OUTPUT_DIR, "kpis.csv"),
    index=False
)


# ============================================================
# 7. MONTHLY SALES ANALYSIS
# ============================================================

print("\nAnalyzing monthly sales...")


# Aggregate payment at order level first.
# This prevents duplicate revenue when joining tables.

order_payment_totals = (
    payments.groupby("order_id", as_index=False)
    .agg(order_revenue=("payment_value", "sum"))
)


monthly_sales = orders[
    [
        "order_id",
        "order_purchase_timestamp"
    ]
].merge(
    order_payment_totals,
    on="order_id",
    how="left"
)


monthly_sales["month"] = (
    monthly_sales[
        "order_purchase_timestamp"
    ]
    .dt.to_period("M")
    .astype(str)
)


monthly_sales = (
    monthly_sales
    .groupby("month", as_index=False)
    .agg(
        total_orders=("order_id", "nunique"),
        revenue=("order_revenue", "sum")
    )
)


monthly_sales["average_order_value"] = (
    monthly_sales["revenue"] /
    monthly_sales["total_orders"]
)


monthly_sales["revenue"] = monthly_sales[
    "revenue"
].round(2)

monthly_sales["average_order_value"] = monthly_sales[
    "average_order_value"
].round(2)


monthly_sales.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "monthly_sales.csv"
    ),
    index=False
)


print("✅ Monthly sales completed.")


# ============================================================
# 8. CATEGORY PERFORMANCE
# ============================================================

print("\nAnalyzing product categories...")


category_data = order_items.merge(
    products[
        [
            "product_id",
            "product_category_name"
        ]
    ],
    on="product_id",
    how="left"
)


category_data = category_data.merge(
    category_translation,
    on="product_category_name",
    how="left"
)


category_data["category"] = (
    category_data[
        "product_category_name_english"
    ]
    .fillna(
        category_data["product_category_name"]
    )
    .fillna("Unknown")
)


category_performance = (
    category_data
    .groupby("category", as_index=False)
    .agg(
        revenue=("price", "sum"),
        orders=("order_id", "nunique"),
        products_sold=("product_id", "count")
    )
)


category_performance["revenue"] = (
    category_performance["revenue"]
    .round(2)
)


category_performance = (
    category_performance
    .sort_values(
        "revenue",
        ascending=False
    )
)


category_performance.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "category_performance.csv"
    ),
    index=False
)


print("✅ Category analysis completed.")


# ============================================================
# 9. CUSTOMER STATE PERFORMANCE
# ============================================================

print("\nAnalyzing customer states...")


state_data = orders[
    [
        "order_id",
        "customer_id"
    ]
].merge(
    customers[
        [
            "customer_id",
            "customer_state"
        ]
    ],
    on="customer_id",
    how="left"
)


state_data = state_data.merge(
    order_payment_totals,
    on="order_id",
    how="left"
)


state_performance = (
    state_data
    .groupby("customer_state", as_index=False)
    .agg(
        revenue=("order_revenue", "sum"),
        total_orders=("order_id", "nunique")
    )
)


state_performance["average_order_value"] = (
    state_performance["revenue"] /
    state_performance["total_orders"]
)


state_performance["revenue"] = (
    state_performance["revenue"].round(2)
)

state_performance["average_order_value"] = (
    state_performance["average_order_value"]
    .round(2)
)


state_performance = state_performance.sort_values(
    "revenue",
    ascending=False
)


state_performance.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "state_performance.csv"
    ),
    index=False
)


print("✅ State analysis completed.")


# ============================================================
# 10. PAYMENT METHOD ANALYSIS
# ============================================================

print("\nAnalyzing payment methods...")


payment_method_performance = (
    payments
    .groupby("payment_type", as_index=False)
    .agg(
        payment_count=("payment_type", "count"),
        total_payment_value=(
            "payment_value",
            "sum"
        ),
        average_payment=(
            "payment_value",
            "mean"
        )
    )
)


payment_method_performance[
    "total_payment_value"
] = payment_method_performance[
    "total_payment_value"
].round(2)


payment_method_performance[
    "average_payment"
] = payment_method_performance[
    "average_payment"
].round(2)


payment_method_performance = (
    payment_method_performance
    .sort_values(
        "total_payment_value",
        ascending=False
    )
)


payment_method_performance.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "payment_method_performance.csv"
    ),
    index=False
)


print("✅ Payment analysis completed.")


# ============================================================
# 11. REVIEW ANALYSIS
# ============================================================

print("\nAnalyzing reviews...")


review_performance = (
    reviews
    .groupby("review_score", as_index=False)
    .agg(
        total_reviews=("review_id", "count")
    )
)


review_performance["percentage"] = (
    review_performance["total_reviews"] /
    review_performance["total_reviews"].sum()
) * 100


review_performance["percentage"] = (
    review_performance["percentage"]
    .round(2)
)


review_performance.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "review_performance.csv"
    ),
    index=False
)


print("✅ Review analysis completed.")


# ============================================================
# 12. DELIVERY PERFORMANCE
# ============================================================

print("\nAnalyzing delivery performance...")


delivery_data = orders[
    [
        "order_id",
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]
].copy()


delivery_data = delivery_data.dropna(
    subset=[
        "order_delivered_customer_date"
    ]
)


delivery_data["delivery_days"] = (
    delivery_data[
        "order_delivered_customer_date"
    ]
    -
    delivery_data[
        "order_purchase_timestamp"
    ]
).dt.days


delivery_data["days_vs_estimate"] = (
    delivery_data[
        "order_delivered_customer_date"
    ]
    -
    delivery_data[
        "order_estimated_delivery_date"
    ]
).dt.days


delivery_data["late_delivery"] = (
    delivery_data["days_vs_estimate"] > 0
)


average_delivery_days = (
    delivery_data["delivery_days"].mean()
)


late_delivery_rate = (
    delivery_data["late_delivery"].mean()
    * 100
)


delivery_summary = pd.DataFrame({
    "metric": [
        "Average Delivery Days",
        "Late Delivery Rate"
    ],

    "value": [
        round(average_delivery_days, 2),
        round(late_delivery_rate, 2)
    ]
})


delivery_summary.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "delivery_summary.csv"
    ),
    index=False
)


delivery_data.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "delivery_performance.csv"
    ),
    index=False
)


print(
    f"Average delivery time: "
    f"{average_delivery_days:.2f} days"
)

print(
    f"Late delivery rate: "
    f"{late_delivery_rate:.2f}%"
)


# ============================================================
# 13. SELLER PERFORMANCE
# ============================================================

print("\nAnalyzing sellers...")


seller_performance = (
    order_items
    .groupby("seller_id", as_index=False)
    .agg(
        revenue=("price", "sum"),
        total_orders=("order_id", "nunique"),
        items_sold=("product_id", "count"),
        average_item_price=("price", "mean")
    )
)


seller_performance["revenue"] = (
    seller_performance["revenue"]
    .round(2)
)


seller_performance["average_item_price"] = (
    seller_performance["average_item_price"]
    .round(2)
)


seller_performance = (
    seller_performance
    .sort_values(
        "revenue",
        ascending=False
    )
)


seller_performance.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "seller_performance.csv"
    ),
    index=False
)


print("✅ Seller analysis completed.")


# ============================================================
# 14. FREIGHT ANALYSIS
# ============================================================

print("\nAnalyzing freight...")


freight_summary = pd.DataFrame({
    "metric": [
        "Total Freight Cost",
        "Average Freight Cost"
    ],

    "value": [
        order_items["freight_value"].sum(),
        order_items["freight_value"].mean()
    ]
})


freight_summary["value"] = (
    freight_summary["value"]
    .round(2)
)


freight_summary.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "freight_summary.csv"
    ),
    index=False
)


# ============================================================
# 15. CHART 1 — MONTHLY REVENUE
# ============================================================

print("\nCreating charts...")


plt.figure(figsize=(12, 6))

plt.plot(
    monthly_sales["month"],
    monthly_sales["revenue"],
    marker="o"
)

plt.title(
    "Olist Monthly Revenue"
)

plt.xlabel("Month")

plt.ylabel(
    "Revenue (BRL)"
)

plt.xticks(
    rotation=45
)

plt.tight_layout()

plt.savefig(
    os.path.join(
        CHART_DIR,
        "monthly_revenue.png"
    ),
    dpi=150
)

plt.close()


# ============================================================
# 16. CHART 2 — TOP CATEGORIES
# ============================================================

top_categories = (
    category_performance
    .head(10)
    .sort_values("revenue")
)


plt.figure(figsize=(10, 6))

plt.barh(
    top_categories["category"],
    top_categories["revenue"]
)

plt.title(
    "Top 10 Product Categories by Revenue"
)

plt.xlabel(
    "Revenue (BRL)"
)

plt.ylabel(
    "Category"
)

plt.tight_layout()

plt.savefig(
    os.path.join(
        CHART_DIR,
        "top_categories.png"
    ),
    dpi=150
)

plt.close()


# ============================================================
# 17. CHART 3 — PAYMENT METHODS
# ============================================================

plt.figure(figsize=(8, 6))

plt.bar(
    payment_method_performance[
        "payment_type"
    ],
    payment_method_performance[
        "total_payment_value"
    ]
)

plt.title(
    "Revenue by Payment Method"
)

plt.xlabel(
    "Payment Method"
)

plt.ylabel(
    "Payment Value (BRL)"
)

plt.xticks(
    rotation=30
)

plt.tight_layout()

plt.savefig(
    os.path.join(
        CHART_DIR,
        "payment_methods.png"
    ),
    dpi=150
)

plt.close()


# ============================================================
# 18. CHART 4 — REVIEW SCORES
# ============================================================

plt.figure(figsize=(8, 6))

plt.bar(
    review_performance["review_score"],
    review_performance["total_reviews"]
)

plt.title(
    "Review Score Distribution"
)

plt.xlabel(
    "Review Score"
)

plt.ylabel(
    "Number of Reviews"
)

plt.tight_layout()

plt.savefig(
    os.path.join(
        CHART_DIR,
        "review_scores.png"
    ),
    dpi=150
)

plt.close()


# ============================================================
# 19. CHART 5 — TOP STATES
# ============================================================

top_states = (
    state_performance
    .head(10)
    .sort_values("revenue")
)


plt.figure(figsize=(10, 6))

plt.barh(
    top_states["customer_state"],
    top_states["revenue"]
)

plt.title(
    "Top 10 States by Revenue"
)

plt.xlabel(
    "Revenue (BRL)"
)

plt.ylabel(
    "State"
)

plt.tight_layout()

plt.savefig(
    os.path.join(
        CHART_DIR,
        "top_states.png"
    ),
    dpi=150
)

plt.close()


# ============================================================
# 20. CHART 6 — DELIVERY PERFORMANCE
# ============================================================

plt.figure(figsize=(8, 6))

plt.hist(
    delivery_data["delivery_days"],
    bins=30
)

plt.title(
    "Delivery Time Distribution"
)

plt.xlabel(
    "Delivery Days"
)

plt.ylabel(
    "Number of Orders"
)

plt.tight_layout()

plt.savefig(
    os.path.join(
        CHART_DIR,
        "delivery_distribution.png"
    ),
    dpi=150
)

plt.close()


# ============================================================
# 21. FINAL OUTPUT SUMMARY
# ============================================================

print("\n==============================================")
print("           ANALYSIS COMPLETED")
print("==============================================")

print("\nGenerated CSV files:")

for file in sorted(os.listdir(OUTPUT_DIR)):

    if file.endswith(".csv"):
        print(f"  ✅ {file}")


print("\nGenerated charts:")

for file in sorted(os.listdir(CHART_DIR)):

    if file.endswith(".png"):
        print(f"  📊 {file}")


print("\n==============================================")
print("All analysis outputs are ready for Power BI.")
print("==============================================\n")
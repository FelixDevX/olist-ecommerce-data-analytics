import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

# MySQL configuration
MYSQL_USER = "olist_user"
MYSQL_PASSWORD = "Olist@12345"
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_DATABASE = "olist_ecommerce"

# Database connection
connection_url = URL.create(
    drivername="mysql+pymysql",
    username=MYSQL_USER,
    password=MYSQL_PASSWORD,
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    database=MYSQL_DATABASE
)

engine = create_engine(connection_url)

# Find data folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Product CSV
file_path = os.path.join(
    DATA_DIR,
    "olist_products_dataset.csv"
)

print("\n================================")
print("      PRODUCTS TABLE LOADER")
print("================================")

print(f"\nLooking for:")
print(file_path)

# Check file
if not os.path.exists(file_path):
    print("\n❌ Product CSV not found!")
    exit()

print("\n✅ Product CSV found!")

# Read CSV
df = pd.read_csv(file_path)

print(f"Rows in CSV: {len(df):,}")
print(f"Columns: {len(df.columns)}")

# Load into MySQL
try:

    df.to_sql(
        name="products",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=5000,
        method="multi"
    )

    print("\n✅ Products loaded successfully!")

except Exception as e:

    print("\n❌ Error while loading products:")
    print(e)

# Verify
try:

    with engine.connect() as connection:

        result = connection.exec_driver_sql(
            "SELECT COUNT(*) FROM products"
        )

        count = result.scalar()

        print(f"\nProducts in MySQL: {count:,}")

except Exception as e:

    print("\n❌ Verification error:")
    print(e)

print("\n================================")
print("        DONE")
print("================================")
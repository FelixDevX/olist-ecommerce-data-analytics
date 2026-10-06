-- MySQL 8+ schema for the Olist e-commerce analytics project.
-- Import the raw CSV files into these tables using MySQL Workbench's Table Data Import Wizard.

CREATE DATABASE IF NOT EXISTS olist_ecommerce;
USE olist_ecommerce;

CREATE TABLE IF NOT EXISTS customers (
  customer_id VARCHAR(50) PRIMARY KEY,
  customer_unique_id VARCHAR(50),
  customer_zip_code_prefix INT,
  customer_city VARCHAR(100),
  customer_state CHAR(2)
);

CREATE TABLE IF NOT EXISTS sellers (
  seller_id VARCHAR(50) PRIMARY KEY,
  seller_zip_code_prefix INT,
  seller_city VARCHAR(100),
  seller_state CHAR(2)
);

CREATE TABLE IF NOT EXISTS products (
  product_id VARCHAR(50) PRIMARY KEY,
  product_category_name VARCHAR(150),
  product_name_lenght INT,
  product_description_lenght INT,
  product_photos_qty INT,
  product_weight_g DOUBLE,
  product_length_cm DOUBLE,
  product_height_cm DOUBLE,
  product_width_cm DOUBLE
);

CREATE TABLE IF NOT EXISTS orders (
  order_id VARCHAR(50) PRIMARY KEY,
  customer_id VARCHAR(50),
  order_status VARCHAR(30),
  order_purchase_timestamp DATETIME,
  order_approved_at DATETIME,
  order_delivered_carrier_date DATETIME,
  order_delivered_customer_date DATETIME,
  order_estimated_delivery_date DATETIME,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS order_items (
  order_id VARCHAR(50),
  order_item_id INT,
  product_id VARCHAR(50),
  seller_id VARCHAR(50),
  shipping_limit_date DATETIME,
  price DECIMAL(12,2),
  freight_value DECIMAL(12,2),
  PRIMARY KEY (order_id, order_item_id),
  FOREIGN KEY (order_id) REFERENCES orders(order_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id),
  FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
);

CREATE TABLE IF NOT EXISTS order_payments (
  order_id VARCHAR(50),
  payment_sequential INT,
  payment_type VARCHAR(30),
  payment_installments INT,
  payment_value DECIMAL(12,2),
  PRIMARY KEY (order_id, payment_sequential),
  FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE TABLE IF NOT EXISTS order_reviews (
  review_id VARCHAR(50) PRIMARY KEY,
  order_id VARCHAR(50),
  review_score INT,
  review_comment_title TEXT,
  review_comment_message TEXT,
  review_creation_date DATETIME,
  review_answer_timestamp DATETIME,
  FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE TABLE IF NOT EXISTS category_translation (
  product_category_name VARCHAR(150) PRIMARY KEY,
  product_category_name_english VARCHAR(150)
);

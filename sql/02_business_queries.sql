USE olist_ecommerce;

-- 1. Total orders and total payment value
SELECT COUNT(DISTINCT o.order_id) AS total_orders,
       ROUND(SUM(p.payment_value), 2) AS total_payment_value
FROM orders o
JOIN order_payments p ON o.order_id = p.order_id;

-- 2. Monthly revenue
SELECT DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m') AS month,
       ROUND(SUM(p.payment_value), 2) AS revenue,
       COUNT(DISTINCT o.order_id) AS orders
FROM orders o
JOIN order_payments p ON o.order_id = p.order_id
GROUP BY month
ORDER BY month;

-- 3. Top product categories by item revenue
SELECT COALESCE(ct.product_category_name_english, oi.product_id) AS category,
       ROUND(SUM(oi.price), 2) AS item_revenue,
       COUNT(*) AS units_sold,
       COUNT(DISTINCT oi.order_id) AS orders
FROM order_items oi
LEFT JOIN products pr ON oi.product_id = pr.product_id
LEFT JOIN category_translation ct ON pr.product_category_name = ct.product_category_name
GROUP BY category
ORDER BY item_revenue DESC
LIMIT 10;

-- 4. Revenue by customer state
SELECT c.customer_state,
       COUNT(DISTINCT o.order_id) AS orders,
       ROUND(SUM(p.payment_value), 2) AS revenue
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_payments p ON o.order_id = p.order_id
GROUP BY c.customer_state
ORDER BY revenue DESC;

-- 5. Payment method performance
SELECT payment_type,
       COUNT(DISTINCT order_id) AS orders,
       ROUND(SUM(payment_value), 2) AS payment_value,
       ROUND(AVG(payment_value), 2) AS avg_payment
FROM order_payments
GROUP BY payment_type
ORDER BY payment_value DESC;

-- 6. Average delivery time by month
SELECT DATE_FORMAT(order_purchase_timestamp, '%Y-%m') AS month,
       ROUND(AVG(DATEDIFF(order_delivered_customer_date, order_purchase_timestamp)), 2) AS avg_delivery_days
FROM orders
WHERE order_delivered_customer_date IS NOT NULL
GROUP BY month
ORDER BY month;

-- 7. Late delivery rate
SELECT ROUND(
  100 * AVG(order_delivered_customer_date > order_estimated_delivery_date), 2
) AS late_delivery_rate_pct
FROM orders
WHERE order_delivered_customer_date IS NOT NULL;

-- 8. Review score distribution
SELECT review_score, COUNT(*) AS reviews
FROM order_reviews
GROUP BY review_score
ORDER BY review_score;

-- 9. Top sellers by item revenue
SELECT oi.seller_id,
       s.seller_state,
       ROUND(SUM(oi.price), 2) AS revenue,
       COUNT(DISTINCT oi.order_id) AS orders
FROM order_items oi
JOIN sellers s ON oi.seller_id = s.seller_id
GROUP BY oi.seller_id, s.seller_state
ORDER BY revenue DESC
LIMIT 20;

-- 10. Repeat vs one-time customers
SELECT customer_type, COUNT(*) AS customers
FROM (
  SELECT c.customer_unique_id,
         CASE WHEN COUNT(DISTINCT o.order_id) > 1 THEN 'Repeat' ELSE 'One-time' END AS customer_type
  FROM customers c
  JOIN orders o ON c.customer_id = o.customer_id
  GROUP BY c.customer_unique_id
) x
GROUP BY customer_type;

-- Customer Repeat Purchase Analysis


WITH customer_orders AS (

SELECT

c.customer_unique_id,


COUNT(
DISTINCT o.order_id
)
AS order_count


FROM orders o


JOIN customers c

ON o.customer_id = c.customer_id


WHERE o.order_status='delivered'


GROUP BY c.customer_unique_id

)


SELECT


COUNT(*) 
AS total_customers,


SUM(
CASE 
WHEN order_count >=2 
THEN 1 
ELSE 0 
END
)
AS repeat_customers,


ROUND(

100.0 *
SUM(
CASE 
WHEN order_count >=2 
THEN 1 
ELSE 0 
END
)
/COUNT(*),

2

)
AS repeat_rate


FROM customer_orders;
-- RFM Customer Analysis


SELECT


c.customer_unique_id,


MAX(
o.order_purchase_timestamp
)
AS last_purchase_date,


COUNT(
DISTINCT o.order_id
)
AS frequency,


ROUND(
SUM(p.payment_value),
2
)
AS monetary



FROM orders o


JOIN customers c

ON o.customer_id=c.customer_id


JOIN payments p

ON o.order_id=p.order_id



WHERE o.order_status='delivered'


GROUP BY
c.customer_unique_id;
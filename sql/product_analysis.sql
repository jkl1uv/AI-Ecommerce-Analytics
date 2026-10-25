-- Product Category Revenue Analysis


SELECT


p.product_category_name,


COUNT(
DISTINCT oi.order_id
)
AS order_count,


ROUND(
SUM(oi.price),
2
)
AS revenue



FROM order_items oi


JOIN products p

ON oi.product_id=p.product_id



GROUP BY 
p.product_category_name


ORDER BY revenue DESC;
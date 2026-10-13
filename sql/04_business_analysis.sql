-- 月销售趋势

SELECT

strftime('%Y-%m',
CAST(o.order_purchase_timestamp AS TIMESTAMP)
) AS month,

COUNT(DISTINCT o.order_id) AS orders,

ROUND(SUM(p.payment_value),2) AS revenue,

ROUND(
SUM(p.payment_value)
/
COUNT(DISTINCT o.order_id),
2
) AS avg_order_value


FROM orders o

JOIN payments p

ON o.order_id=p.order_id


WHERE o.order_status='delivered'


GROUP BY month

ORDER BY month;
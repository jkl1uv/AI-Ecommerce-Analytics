from pathlib import Path
import duckdb


project_dir = Path(__file__).resolve().parent.parent

con = duckdb.connect(
str(project_dir/"ecommerce.duckdb")
)


result = con.execute("""

SELECT

p.product_category_name,

COUNT(DISTINCT oi.order_id)
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


ORDER BY revenue DESC


LIMIT 20;


""").fetchdf()


print(result)


result.to_csv(
project_dir/"product_analysis.csv",
index=False
)


con.close()

from pathlib import Path
import duckdb

project_dir = Path(__file__).resolve().parent.parent
db_path = project_dir / "ecommerce.duckdb"

con = duckdb.connect(str(db_path), read_only=True)

try:
    result = con.execute("""
        WITH customer_orders AS (
            SELECT
                c.customer_unique_id,
                COUNT(DISTINCT o.order_id) AS order_count
            FROM orders o
            JOIN customers c
                ON o.customer_id = c.customer_id
            WHERE o.order_status = 'delivered'
            GROUP BY c.customer_unique_id
        )
        SELECT
            COUNT(*) AS unique_customers,
            SUM(
                CASE WHEN order_count >= 2 THEN 1 ELSE 0 END
            ) AS repeat_customers,
            ROUND(
                100.0 * SUM(
                    CASE WHEN order_count >= 2 THEN 1 ELSE 0 END
                ) / COUNT(*),
                2
            ) AS repeat_rate_pct
        FROM customer_orders
    """).fetchdf()

    print("=== 客户复购分析 ===")
    print(result.to_string(index=False))

    result.to_csv(
        project_dir / "customer_repeat_rate.csv",
        index=False
    )
    print("\n结果已保存：customer_repeat_rate.csv")

finally:
    con.close()

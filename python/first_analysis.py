
from pathlib import Path
import duckdb

project_dir = Path(__file__).resolve().parent.parent
db_path = project_dir / "ecommerce.duckdb"

con = duckdb.connect(str(db_path), read_only=True)

try:
    # 分析一：订单状态分布
    print("=== 订单状态分布 ===")

    status = con.execute("""
        SELECT
            order_status,
            COUNT(*) AS order_count
        FROM orders
        GROUP BY order_status
        ORDER BY order_count DESC
    """).fetchdf()

    print(status.to_string(index=False))

    # 分析二：每月已交付订单的支付金额
    print("\n=== 每月支付金额 ===")

    monthly = con.execute("""
    SELECT

    strftime(
    CAST(o.order_purchase_timestamp AS TIMESTAMP),
    '%Y-%m'
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

    ORDER BY month

    """).fetchdf()

    monthly.to_csv(
        project_dir / "monthly_revenue.csv",
        index=False
    )

    print(monthly.to_string(index=False))

    # 保存结果，后续用于 Power BI
    output_path = project_dir / "monthly_revenue.csv"
    monthly.to_csv(output_path, index=False)

    print(f"\n分析结果已保存到：{output_path}")

finally:
    con.close()

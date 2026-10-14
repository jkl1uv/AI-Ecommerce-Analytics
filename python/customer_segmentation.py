from pathlib import Path
import duckdb
import pandas as pd

# 项目路径
project_dir = Path(__file__).resolve().parent.parent
db_path = project_dir / "ecommerce.duckdb"

con = duckdb.connect(str(db_path))

try:

    print("=== 开始RFM用户分析 ===")

    rfm = con.execute("""

    WITH customer_value AS (

        SELECT
            c.customer_unique_id,

            MAX(o.order_purchase_timestamp) AS last_purchase_date,

            COUNT(DISTINCT o.order_id) AS frequency,

            SUM(p.payment_value) AS monetary


        FROM orders o

        JOIN customers c
        ON o.customer_id = c.customer_id


        JOIN payments p
        ON o.order_id = p.order_id


        WHERE o.order_status = 'delivered'


        GROUP BY c.customer_unique_id

    )


    SELECT

        customer_unique_id,

        datediff( 
            'day',
            CAST(last_purchase_date AS DATE),
            DATE '2018-09-01'
        ) AS recency,


        frequency,

        ROUND(monetary,2) AS monetary


    FROM customer_value


    """).fetchdf()

    print(rfm.head())

    # RFM评分

    rfm['R_score'] = pd.qcut(
        rfm['recency'],
        5,
        labels=[5, 4, 3, 2, 1]
    )

    rfm['F_score'] = pd.qcut(
        rfm['frequency'].rank(method='first'),
        5,
        labels=[1, 2, 3, 4, 5]
    )

    rfm['M_score'] = pd.qcut(
        rfm['monetary'],
        5,
        labels=[1, 2, 3, 4, 5]
    )

    rfm['RFM_score'] = (
            rfm['R_score'].astype(str)
            +
            rfm['F_score'].astype(str)
            +
            rfm['M_score'].astype(str)
    )


    # 简单用户分类

    def segment(row):

        if (
                row['F_score'] >= 4
                and row['M_score'] >= 4
        ):
            return "VIP客户"

        elif row['R_score'] >= 4:
            return "近期客户"

        elif row['R_score'] <= 2:
            return "流失风险"

        else:
            return "普通客户"


    rfm['segment'] = rfm.apply(segment, axis=1)

    print("\n=== 用户分群统计 ===")

    print(
        rfm['segment']
        .value_counts()
    )

    # 保存结果

    output = project_dir / "customer_segments.csv"

    rfm.to_csv(
        output,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n完成！结果保存：")
    print(output)


finally:

    con.close()
"""
RFM 客户价值分群（修正版）
------------------------------------------------------------
修正原脚本的一个方法问题：
    该数据集 97.0% 的客户只购买过一次，frequency 几乎全为 1。
    原脚本用 pd.qcut(frequency.rank(method='first'), 5) 强行为这些
    完全相同的客户切出 5 档 F 分数，等价于按行号随机分配，
    F 维度对 97% 的用户不具任何业务含义。

修正方案：
    1. F 维度降级为诊断指标，不参与分群；
    2. 改用 R（最近购买）与 M（累计消费）二维分群，以中位数为界；
    3. 四个象限对应明确的运营动作，并补充收入贡献占比，
       以判断是否可以用少数客户支撑多数收入。

运行：python python/rfm_segmentation_v2.py
"""

from pathlib import Path
import duckdb
import pandas as pd

project_dir = Path(__file__).resolve().parent.parent
db_path = project_dir / "ecommerce.duckdb"
output_dir = project_dir / "output"

SQL_CUSTOMER = """
WITH snapshot AS (
    SELECT MAX(CAST(order_purchase_timestamp AS DATE)) AS snap
    FROM orders
    WHERE order_status = 'delivered'
),
cust AS (
    SELECT
        c.customer_unique_id,
        MAX(CAST(o.order_purchase_timestamp AS DATE)) AS last_purchase,
        COUNT(DISTINCT o.order_id)                    AS frequency,
        SUM(p.payment_value)                          AS monetary
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN payments p  ON o.order_id = p.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY 1
)
SELECT
    cu.customer_unique_id,
    cu.frequency,
    ROUND(cu.monetary, 2)                      AS monetary,
    date_diff('day', cu.last_purchase, s.snap) AS recency,
    CAST(cu.last_purchase AS VARCHAR)          AS last_purchase_date
FROM cust cu
CROSS JOIN snapshot s
"""

# 分群规则：R 低=近期有购买，M 高=累计消费高于中位数
SEGMENT_RULES = {
    ("近期", "高价值"): ("重要价值客户", "最近购买且消费高，核心客群，优先维护与复购激励"),
    ("近期", "低价值"): ("一般发展客户", "购买活跃但客单价低，重点是提升客单与品类连带"),
    ("沉睡", "高价值"): ("重要保持客户", "消费高但已流失，召回优先级最高，挽回成本低于拉新"),
    ("沉睡", "低价值"): ("一般挽留客户", "低活跃低消费，仅做低成本触达，不投入付费资源"),
}


def main() -> None:
    output_dir.mkdir(exist_ok=True)
    con = duckdb.connect(str(db_path), read_only=True)
    try:
        rfm = con.execute(SQL_CUSTOMER).fetchdf()
    finally:
        con.close()

    total_customers = len(rfm)
    print(f"客户总数：{total_customers:,}")

    # ---------- 诊断：F 维度为何失效 ----------
    single = (rfm["frequency"] == 1).sum()
    print("\n=== F 维度诊断 ===")
    print(f"仅购买 1 次的客户：{single:,}（{single / total_customers * 100:.1f}%）")
    print(f"frequency 的取值分布：\n{rfm['frequency'].value_counts().head(5).to_string()}")
    print("结论：F 维度在 97% 的客户上无区分度，原脚本的 rank(method='first')")
    print("      等于按行号随机切档，故本版不将 F 纳入分群维度。")

    # ---------- R / M 二维分群 ----------
    r_cut = rfm["recency"].median()
    m_cut = rfm["monetary"].median()
    print(f"\n=== 分群阈值 ===")
    print(f"R 中位数（天）：{r_cut:.0f}　→ 不超过该值视为「近期」")
    print(f"M 中位数（元）：{m_cut:.2f}　→ 达到该值视为「高价值」")

    rfm["r_band"] = rfm["recency"].apply(lambda x: "近期" if x <= r_cut else "沉睡")
    rfm["m_band"] = rfm["monetary"].apply(lambda x: "高价值" if x >= m_cut else "低价值")
    rfm["segment"] = [
        SEGMENT_RULES[(r, m)][0] for r, m in zip(rfm["r_band"], rfm["m_band"])
    ]

    # ---------- 输出客户级明细 ----------
    detail_file = output_dir / "rfm_segments_v2.csv"
    rfm.to_csv(detail_file, index=False, encoding="utf-8-sig")
    print(f"\n客户级明细已导出：{detail_file.name}（{len(rfm):,} 行）")

    # ---------- 输出分群汇总（含收入贡献） ----------
    summary = (
        rfm.groupby("segment")
        .agg(
            客户数=("customer_unique_id", "count"),
            总消费=("monetary", "sum"),
            平均消费=("monetary", "mean"),
            平均最近购买天数=("recency", "mean"),
            平均购买次数=("frequency", "mean"),
        )
        .reset_index()
    )
    summary["人数占比%"] = summary["客户数"] / total_customers * 100
    summary["收入占比%"] = summary["总消费"] / summary["总消费"].sum() * 100
    summary["人均收入贡献"] = summary["总消费"] / summary["客户数"]
    summary = summary.sort_values("总消费", ascending=False)
    for col in ["平均消费", "平均最近购买天数", "平均购买次数", "人均收入贡献"]:
        summary[col] = summary[col].round(2)
    for col in ["人数占比%", "收入占比%"]:
        summary[col] = summary[col].round(2)
    summary["总消费"] = summary["总消费"].round(2)

    summary_file = output_dir / "rfm_segment_summary.csv"
    summary.to_csv(summary_file, index=False, encoding="utf-8-sig")

    print("\n=== 分群结果 ===")
    print(
        summary[
            ["segment", "客户数", "人数占比%", "收入占比%", "平均最近购买天数", "人均收入贡献"]
        ].to_string(index=False)
    )

    # ---------- 与旧版分群对比 ----------
    print("\n=== 与原脚本分群口径的差异 ===")
    print("原脚本：VIP / 近期客户 / 流失风险 / 普通客户，按 F、M、R 分数阈值手写 if-elif")
    print("        分群边界由 F 分数驱动，而 F 对 97% 用户为随机值 → 分群结果不可复现")
    print("本版：  重要价值 / 一般发展 / 重要保持 / 一般挽留，按 R、M 中位数四象限划分")
    print("        每条规则对应明确运营动作，阈值可解释、结果可复现")
    print(f"\n完成，汇总表已导出：{summary_file.name}")


if __name__ == "__main__":
    main()

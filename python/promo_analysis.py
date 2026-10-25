"""
大促脉冲分析
------------------------------------------------------------
读取 sql/promo_analysis.sql 中的 5 段查询，依次在 DuckDB 上执行，
结果导出到 output/ 目录，并在控制台打印核心指标。

运行：python python/promo_analysis.py
"""

from pathlib import Path
import duckdb

project_dir = Path(__file__).resolve().parent.parent
db_path = project_dir / "ecommerce.duckdb"
sql_path = project_dir / "sql" / "promo_analysis.sql"
output_dir = project_dir / "output"

# 每段查询对应的输出文件名
OUTPUT_NAMES = [
    "promo_monthly_trend",
    "promo_bf_day_vs_rest",
    "promo_category_lift",
    "promo_installments",
    "promo_order_value_mix",
]


def load_queries(path: Path) -> list[str]:
    """按分号拆分 SQL 文件，过滤空段。"""
    raw = path.read_text(encoding="utf-8")
    parts = [p.strip() for p in raw.split(";")]
    return [p for p in parts if p]


def main() -> None:
    output_dir.mkdir(exist_ok=True)
    queries = load_queries(sql_path)
    print(f"从 {sql_path.name} 载入 {len(queries)} 段查询\n")

    # read_only=True：避免写入时与 Power BI / 其他脚本争用数据库文件
    con = duckdb.connect(str(db_path), read_only=True)

    try:
        for idx, query in enumerate(queries):
            name = OUTPUT_NAMES[idx] if idx < len(OUTPUT_NAMES) else f"promo_q{idx + 1}"
            df = con.execute(query).fetchdf()

            out_file = output_dir / f"{name}.csv"
            df.to_csv(out_file, index=False, encoding="utf-8-sig")
            print(f"[{idx + 1}/{len(queries)}] {name}.csv  —  {len(df)} 行")

            # 前两段查询是关键结论，额外打印出来便于核对
            if idx in (1, 2, 3):
                print(df.to_string(index=False))
                print()

    finally:
        con.close()

    print("分析完成，结果已保存到 output/ 目录")


if __name__ == "__main__":
    main()

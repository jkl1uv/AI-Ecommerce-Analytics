
from pathlib import Path
import duckdb

# 自动定位项目根目录
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
DB_PATH = PROJECT_DIR / "ecommerce.duckdb"

# 数据表名称与原始 CSV 文件名

TABLES = {
    "customers": "customers.csv",
    "orders": "orders.csv",
    "order_items": "order_items.csv",
    "products": "products.csv",
    "payments": "payments.csv",
    "reviews": "reviews.csv",
}


def main():
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"找不到数据目录：{DATA_DIR}")

    con = duckdb.connect(str(DB_PATH))

    try:
        for table, filename in TABLES.items():
            csv_path = DATA_DIR / filename

            if not csv_path.exists():
                print(f"跳过：找不到 {filename}")
                continue

            # 直接从 CSV 创建数据库表
            csv_sql_path = csv_path.as_posix().replace("'", "''")

            con.execute(f"""
                CREATE OR REPLACE TABLE {table} AS
                SELECT *
                FROM read_csv_auto(
                    '{csv_sql_path}',
                    header = true,
                    sample_size = -1
                )
            """)

            count = con.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

            print(f"成功导入 {table}: {count:,} 行")

        print("\n数据库已创建：", DB_PATH)

        print("\n当前数据表：")
        print(con.execute("SHOW TABLES").fetchdf())

    finally:
        con.close()

if __name__ == "__main__":
    main()

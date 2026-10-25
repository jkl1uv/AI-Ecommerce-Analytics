-- =============================================================
-- 大促脉冲分析（Promo Pulse Analysis）
-- 样本：2017 年黑色星期五（2017-11-24）所在的 11 月
-- 目的：量化大促对收入、单量、客单价、品类结构与支付行为的影响
-- 说明：所有查询基于订单支付金额（payments.payment_value），
--       已过滤 order_status = 'delivered'，排除未完成订单对收入的干扰
-- =============================================================


-- -------------------------------------------------------------
-- Q1 月度收入趋势与环比增长率
-- 注意：2016-09 与 2016-12 各仅有 1 笔订单，属数据源缺口而非业务下滑，
--       已用 HAVING 剔除，避免把数据缺失误读为销售暴跌
-- -------------------------------------------------------------
WITH monthly AS (
    SELECT
        strftime(o.order_purchase_timestamp, '%Y-%m') AS year_month,
        COUNT(DISTINCT o.order_id)                    AS order_count,
        SUM(p.payment_value)                          AS revenue
    FROM orders o
    JOIN payments p ON o.order_id = p.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY 1
    HAVING COUNT(DISTINCT o.order_id) >= 100
)
SELECT
    year_month,
    order_count,
    ROUND(revenue, 2) AS revenue,
    ROUND(
        100.0 * (revenue - LAG(revenue) OVER (ORDER BY year_month))
        / LAG(revenue) OVER (ORDER BY year_month), 2
    ) AS mom_growth_pct
FROM monthly
ORDER BY year_month;


-- -------------------------------------------------------------
-- Q2 大促脉冲：黑五当日 vs 11 月其余日
-- 拆出「日均收入 / 日均单量 / 客单价」三个口径，
-- 用于判断大促是「以量换价」还是「量价齐升」
-- -------------------------------------------------------------
WITH daily AS (
    SELECT
        CAST(o.order_purchase_timestamp AS DATE) AS dt,
        COUNT(DISTINCT o.order_id)               AS order_count,
        SUM(p.payment_value)                     AS revenue
    FROM orders o
    JOIN payments p ON o.order_id = p.order_id
    WHERE o.order_status = 'delivered'
      AND CAST(o.order_purchase_timestamp AS DATE)
          BETWEEN DATE '2017-11-01' AND DATE '2017-11-30'
    GROUP BY 1
)
SELECT
    CASE WHEN dt = DATE '2017-11-24' THEN '1_黑五当日' ELSE '2_11月其余日' END AS period,
    COUNT(*)                                  AS days,
    ROUND(AVG(revenue), 2)                    AS avg_daily_revenue,
    ROUND(AVG(order_count), 1)                AS avg_daily_orders,
    ROUND(AVG(revenue) / AVG(order_count), 2) AS avg_order_value
FROM daily
GROUP BY 1
ORDER BY 1;


-- -------------------------------------------------------------
-- Q3 品类弹性：大促周（11.20-11.26）收入 / 10 月周均收入
-- 倍数越高说明该品类越依赖大促驱动，用于指导备货与投放分配
-- -------------------------------------------------------------
WITH cat_daily AS (
    SELECT
        pr.product_category_name                 AS category,
        CAST(o.order_purchase_timestamp AS DATE) AS dt,
        SUM(oi.price)                            AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products pr    ON oi.product_id = pr.product_id
    WHERE o.order_status = 'delivered'
      AND pr.product_category_name IS NOT NULL
    GROUP BY 1, 2
),
agg AS (
    SELECT
        category,
        SUM(CASE WHEN dt BETWEEN DATE '2017-11-20' AND DATE '2017-11-26'
                 THEN revenue ELSE 0 END) AS promo_week,
        SUM(CASE WHEN dt BETWEEN DATE '2017-10-01' AND DATE '2017-10-31'
                 THEN revenue ELSE 0 END) / 31 * 7 AS baseline_week
    FROM cat_daily
    GROUP BY 1
)
SELECT
    category,
    ROUND(promo_week, 2)    AS promo_week_revenue,
    ROUND(baseline_week, 2) AS baseline_week_revenue,
    ROUND(promo_week / NULLIF(baseline_week, 0), 2) AS lift_ratio
FROM agg
WHERE promo_week > 10000
  AND baseline_week > 2000   -- 过滤基数过小的长尾品类，避免小样本放大出虚假倍数
ORDER BY lift_ratio DESC;


-- -------------------------------------------------------------
-- Q4 支付行为：大促期间的分期结构变化
-- 巴西市场分期渗透率高，大促期间的分期层数变化会直接影响资金成本
-- -------------------------------------------------------------
WITH txn AS (
    SELECT
        CAST(o.order_purchase_timestamp AS DATE) AS dt,
        p.payment_installments                   AS installments
    FROM orders o
    JOIN payments p ON o.order_id = p.order_id
    WHERE o.order_status = 'delivered'
      AND CAST(o.order_purchase_timestamp AS DATE)
          BETWEEN DATE '2017-10-01' AND DATE '2017-11-30'
)
SELECT
    CASE
        WHEN dt = DATE '2017-11-24' THEN '1_黑五当日'
        WHEN dt >= DATE '2017-11-01' THEN '2_11月其余日'
        ELSE '3_10月基准'
    END AS period,
    COUNT(*) AS payment_records,
    ROUND(AVG(installments), 2) AS avg_installments,
    ROUND(
        100.0 * SUM(CASE WHEN installments >= 6 THEN 1 ELSE 0 END) / COUNT(*), 2
    ) AS installments_6plus_pct
FROM txn
GROUP BY 1
ORDER BY 1;


-- -------------------------------------------------------------
-- Q5 客单价分档：验证「以量换价」假设
-- 若大促当日低价档订单占比显著上升，说明增量来自低价商品而非高价商品
-- -------------------------------------------------------------
WITH order_amt AS (
    SELECT
        o.order_id,
        SUM(p.payment_value)                     AS amount,
        CAST(o.order_purchase_timestamp AS DATE) AS dt
    FROM orders o
    JOIN payments p ON o.order_id = p.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY 1, 3
),
bucketed AS (
    SELECT
        CASE
            WHEN dt = DATE '2017-11-24' THEN '1_黑五当日'
            WHEN dt >= DATE '2017-11-01' AND dt <= DATE '2017-11-30' THEN '2_11月其余日'
        END AS period,
        CASE
            WHEN amount < 50   THEN '1_<50'
            WHEN amount < 100  THEN '2_50-100'
            WHEN amount < 200  THEN '3_100-200'
            WHEN amount < 500  THEN '4_200-500'
            ELSE '5_>=500'
        END AS amount_bucket
    FROM order_amt
    WHERE dt >= DATE '2017-11-01' AND dt <= DATE '2017-11-30'
)
SELECT
    period,
    amount_bucket,
    COUNT(*) AS order_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY period), 2) AS pct
FROM bucketed
WHERE period IS NOT NULL
GROUP BY 1, 2
ORDER BY 1, 2;

Business Insight Report
Business Overview Dashboard - Sales Performance Analysis
Analysis metrics:
1.Total Sales Revenue（15,000,000）
2.Total Order Quantity(96,477)
3.Average Order Value(154.93)
4.Monthly Sales Revenue Trend（Ramp-up through 2017, plateau in 2018）

Analytical Insights
Sales analysis is used to identify revenue trends across different time periods and assess overall business growth.
By monitoring monthly revenue changes and order quantity fluctuations, companies can understand customer purchasing patterns and identify periods with stronger or weaker sales performance.

Business Recommendations
1.Continuously monitor monthly sales trends to identify potential growth opportunities.
2.Analyze changes in order quantity to understand shifts in customer purchasing behavior.
3.Increase average order value through cross-selling and product recommendation strategies.

Product Analysis - Product Category Performance Analysis
Core Metrics
Analysis content:
Top 10 Product Category Ranking, Product Category Revenue Contribution Ratio
Analytical Insights
Different product categories contribute significantly differently to overall revenue. Some high-performing product categories account for a large proportion of sales revenue, while lower-performing product categories may require further optimization.
Business Recommendations
Focus marketing resources on high-revenue product categories. Optimize inventory management strategies based on product category performance. Conduct root cause analysis for low-performing product categories and develop improvement plans.

Customer Analysis - Customer Value Analysis
Core Metrics
Analysis content:
RFM Customer Segmentation, Customer Value Analysis, AI-Generated Business Insights
Customer segmentation analysis shows that churn-risk customers represent 33.33% of the customer base, recent customers account for 33.20%, regular customers account for 16.66%, and VIP customers account for 16.81%.

Analytical Insights
RFM analysis identifies different customer groups through three dimensions:
R (Recency): Time since last purchase, the interval between a customer's most recent purchase and the current time.
F (Frequency): Purchase frequency, the number of purchases or transaction frequency of a customer.
M (Monetary): Spending amount, the cumulative spending amount of a customer.

Through the RFM model, customers can be segmented into:
High-value customers, loyal customers, and potential churn customers, helping companies understand customer value more precisely.

Business Recommendations
1.Develop personalized marketing strategies for high-value customers to increase customer lifetime value.
2.Launch customer recall campaigns for customers at risk of churning.
3.Improve long-term customer value through precision operations.

Segmentation Method Correction (R-M Two-Dimensional)
Background:
97.0% of customers in this dataset purchased exactly once, so the frequency dimension carries no discriminative power. The original script forced identical-frequency customers into five buckets, which is equivalent to scoring them randomly by row order and makes the segments irreproducible.
Correction: F is demoted to a diagnostic metric and excluded from segmentation. Customers are segmented on R (recency) and M (monetary) around their medians, forming four quadrants, each mapped to a specific operating action.

Corrected segments (93,357 customers):
1.High-value active: 25.55% of customers, 41.13% of revenue, avg 111 days since last purchase, avg spend 265.91
2.High-value dormant: 24.56% of customers, 39.70% of revenue, avg 363 days since last purchase, avg spend 267.05
3.Low-value dormant: 25.44% of customers, 9.83% of revenue, avg 364 days since last purchase, avg spend 63.80
4.Low-value active: 24.45% of customers, 9.34% of revenue, avg 111 days since last purchase, avg spend 63.13

Key Finding:
The two high-value segments account for 50.1% of customers but 80.8% of revenue. High-value dormant customers have not purchased for an average of 363 days yet still hold 39.70% of historical revenue contribution, making them the highest-priority recall target. The original segmentation merged high-value and low-value churn into a single "churn risk 33.33%" bucket, obscuring a 4.2x gap in per-customer value and therefore in recall ROI.

Business Recommendations:
1.Direct recall budget to high-value dormant customers, whose per-customer historical contribution is 4.2x that of low-value dormant customers
2.Do not run paid recall on low-value dormant customers; cover them only through zero-cost channels
3.Retain high-value active customers with repeat-purchase incentives and category cross-selling

Promo Pulse Analysis - Black Friday Deep Dive
Sample: Black Friday 2017 (2017-11-24), benchmarked against the rest of November 2017 and October 2017

1. Revenue and order lift
Core Metrics:
1.Black Friday revenue 175,251, 5.2x the November daily average (33,734)
2.Black Friday orders 1,147, 5.4x the daily average (212)
3.Black Friday AOV 152.79, 4.1% below the rest-of-month AOV of 159.28

Analytical Insights:
Revenue grew slower (5.2x) than order volume (5.4x), indicating that incremental sales came from order count rather than basket size. This is a classic volume-over-value promo pattern.

Business Recommendations:
1.Staff customer service and fulfillment for at least 5x normal capacity
2.November grew 53.6% MoM, then December fell 26.9% to 843,199 — budget for a pulse, not a new baseline
3.Set promo targets on acquisition and first-purchase conversion rather than AOV

2. Category elasticity
Core Metrics (promo week revenue / October weekly average):
1.Furniture & decor 3.99x
2.Perfumery 3.96x
3.Health & beauty 3.93x
4.Home utilities 3.89x
5.Bed, bath & table 3.74x
6.Toys 3.28x
7.Computer accessories 3.23x
8.Watches & gifts 2.58x
9.Sports & leisure 1.99x

Analytical Insights:
The most elastic categories are home, beauty and gift-oriented goods — mid-priced, short consideration cycles, and easy to stockpile. The least elastic (sports, watches) are deliberate purchases that respond weakly to discounting.

Business Recommendations:
1.Shift inventory and ad budget toward furniture, perfumery, beauty and bed & bath
2.Avoid deep discounting on watches and other high-ticket low-elasticity items; use threshold discounts to protect margin
3.Toys and computer accessories are high-elasticity, high-volume traffic drivers suitable for acquisition

3. Payment behavior
Core Metrics:
1.Average installments: 3.51 on Black Friday vs 2.94 on other November days vs 2.86 in October
2.Share of orders with 6+ installments: 22.93% vs 15.36%

Analytical Insights:
Installment depth rose sharply on the promo day as customers stretched payment cycles to fund purchases, which raises platform fee and funding costs.

Business Recommendations:
1.Confirm installment limits and fee rates with payment providers ahead of the promo
2.Long-installment orders carry higher refund and chargeback risk; set separate risk thresholds

4. Order value mix: growth came from low-ticket orders
Core Metrics (order amount distribution, Black Friday vs rest of November):
1.Under 100: 51.35% vs 47.77%, up 3.58 pp
2.100-200: 29.03% vs 31.81%, down 2.78 pp
3.500 and above: 3.40% vs 4.41%, down 1.01 pp

Analytical Insights:
The share of sub-100 orders rose while high-value orders above 500 declined, confirming the volume-over-value pattern at the order-structure level: growth came from low-ticket items and first-time buyers.

Business Recommendations:
1.Design separate threshold discounts for items above 500 to avoid diluting high-value orders
2.A low-ticket order mix raises per-order fulfillment cost; revisit the free-shipping threshold

5. Data quality notes
1.2016-09 and 2016-12 each contain a single order (source data gap) and were excluded from trend analysis to avoid misreading a data gap as a sales collapse
2.Category elasticity excludes categories with October weekly revenue below 2,000 to prevent small samples from inflating lift ratios

Project Summary
This project demonstrates a complete e-commerce data analysis workflow, using:
DuckDB, SQL, Python, and Power BI, completing the entire process from raw data to business insights.

The project analysis includes:
1.Business performance monitoring
2.Product category analysis
3.Customer value segmentation
4.Data-driven business recommendations
Finally, through data analysis methods, raw e-commerce transaction data is transformed into business insights that can support corporate decision-making.
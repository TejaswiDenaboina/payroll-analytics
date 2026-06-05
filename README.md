# SQL Payroll Analytics Dashboard

ETL pipeline + advanced SQL analytics on 100K synthetic payroll records.
PostgreSQL backend, Plotly Dash frontend.

## Key results
| Query | Before index | After index | Speedup |
|---|---|---|---|
| Dept payroll sum | 39.0ms | 30.4ms | 1.3x |
| Overtime filter  | 13.0ms | 0.7ms  | 18.6x |
| Monthly trend    | 24.9ms | 35.2ms | 0.7x* |
| Location filter  | 14.3ms | 7.5ms  | 1.9x |

*Monthly trend slower after indexing — PostgreSQL correctly chose
sequential scan for full-table aggregation over index scan.



## Key findings from data

- Engineering is the largest department — 35,166 employees, 35.13% of total payroll
- Overtime anomaly detection flagged EMP32363 with Z-score 3.72 —
  overtime pay ₹208,408 vs department average
- Salary distribution is remarkably consistent across departments —
  median salary range ₹558K–₹563K, suggesting fair pay structure
- Bangalore has highest overtime rate at 28.5%, Hyderabad lowest at 27.4%
- Bonus-to-base ratio consistent across roles — Analyst 5.01% vs Lead 4.87%
- Monthly salary growth stays within ±1.6% — stable payroll with no anomalous spikes
- Q4 salary quartile shows 2x gap between bottom (₹387K) and top (₹755K) quartile


## SQL techniques used
- Window functions: RANK(), LAG(), SUM() OVER(PARTITION BY)
- CTEs for multi-step aggregation
- PERCENTILE_CONT for salary distribution
- Z-score anomaly detection for overtime outliers
- EXPLAIN ANALYZE for query plan analysis

## Setup
1. Install PostgreSQL and create database: payroll_db
2. pip install -r requirements.txt
3. python generate_data.py
4. python load_db.py
5. python benchmark.py
6. python app.py
import pandas as pd
from sqlalchemy import create_engine
from db_config import DB_CONFIG

DB_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
engine = create_engine(DB_URL)

def run(label, sql):
    print(f"\n{'='*55}")
    print(f"  {label}")
    print('='*55)
    df = pd.read_sql(sql, engine)
    print(df.to_string(index=False))
    return df

# Query 1 — Total payroll by department
run("Q1: Payroll cost by department", """
    SELECT department,
           COUNT(*)                            AS headcount,
           ROUND(AVG(net_salary)::numeric, 0)  AS avg_salary,
           ROUND(SUM(net_salary)::numeric, 0)  AS total_payroll,
           ROUND(SUM(bonus)::numeric, 0)       AS total_bonus
    FROM payroll
    GROUP BY department
    ORDER BY total_payroll DESC
""")

# Query 2 — Running total payroll by month
run("Q2: Running yearly payroll total (window)", """
    SELECT pay_year, pay_month,
           ROUND(SUM(net_salary)::numeric, 0) AS monthly_payroll,
           ROUND(SUM(SUM(net_salary)) OVER (
               PARTITION BY pay_year ORDER BY pay_month
           )::numeric, 0)                      AS running_yearly_total
    FROM payroll
    GROUP BY pay_year, pay_month
    ORDER BY pay_year, pay_month
""")

# Query 3 — Salary rank within department
run("Q3: Salary rank within each department (RANK)", """
    SELECT employee_id, department, job_role,
           ROUND(net_salary::numeric, 0) AS net_salary,
           RANK() OVER (
               PARTITION BY department
               ORDER BY net_salary DESC
           ) AS dept_salary_rank
    FROM payroll
    ORDER BY department, dept_salary_rank
    LIMIT 30
""")

# Query 4 — Overtime anomaly detection (CTE + Z-score)
run("Q4: Overtime anomalies — Z-score > 2 (CTE)", """
    WITH dept_stats AS (
        SELECT department,
               AVG(overtime_pay)    AS avg_ot,
               STDDEV(overtime_pay) AS std_ot
        FROM payroll
        WHERE overtime_flag = 1
        GROUP BY department
    ),
    employee_zscore AS (
        SELECT p.employee_id, p.department, p.overtime_pay,
               ROUND(((p.overtime_pay - d.avg_ot)
                   / NULLIF(d.std_ot, 0))::numeric, 2) AS z_score
        FROM payroll p
        JOIN dept_stats d ON p.department = d.department
        WHERE p.overtime_flag = 1
    )
    SELECT * FROM employee_zscore
    WHERE ABS(z_score) > 2
    ORDER BY z_score DESC
    LIMIT 20
""")

# Query 5 — Month-over-month growth (LAG)
run("Q5: Month-over-month salary growth (LAG)", """
    WITH monthly AS (
        SELECT pay_year, pay_month,
               ROUND(AVG(net_salary)::numeric, 2) AS avg_salary
        FROM payroll
        GROUP BY pay_year, pay_month
    )
    SELECT pay_year, pay_month, avg_salary,
           LAG(avg_salary) OVER (ORDER BY pay_year, pay_month) AS prev_month,
           ROUND((
               (avg_salary - LAG(avg_salary) OVER (ORDER BY pay_year, pay_month))
               / NULLIF(LAG(avg_salary) OVER (ORDER BY pay_year, pay_month), 0) * 100
           )::numeric, 2) AS mom_growth_pct
    FROM monthly
    ORDER BY pay_year, pay_month
""")

# Query 6 — Salary percentiles by department
run("Q6: Salary percentiles — P10, P50, P90 (PERCENTILE_CONT)", """
    SELECT department,
           ROUND(PERCENTILE_CONT(0.10) WITHIN GROUP
               (ORDER BY net_salary)::numeric, 0) AS p10_salary,
           ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP
               (ORDER BY net_salary)::numeric, 0) AS median_salary,
           ROUND(PERCENTILE_CONT(0.90) WITHIN GROUP
               (ORDER BY net_salary)::numeric, 0) AS p90_salary,
           ROUND(AVG(net_salary)::numeric, 0)     AS avg_salary
    FROM payroll
    GROUP BY department
    ORDER BY p90_salary DESC
""")

# Query 7 — Department cost share %
run("Q7: Department cost as % of total payroll", """
    SELECT department,
           ROUND(SUM(net_salary)::numeric, 0) AS dept_total,
           ROUND((SUM(net_salary)
               / SUM(SUM(net_salary)) OVER () * 100)::numeric, 2) AS pct_of_total
    FROM payroll
    GROUP BY department
    ORDER BY pct_of_total DESC
""")

# Query 8 — Bonus efficiency by job role
run("Q8: Bonus-to-base ratio by job role (CTE)", """
    WITH role_summary AS (
        SELECT job_role,
               COUNT(*)                            AS headcount,
               ROUND(AVG(bonus)::numeric, 0)       AS avg_bonus,
               ROUND(AVG(base_salary)::numeric, 0) AS avg_base,
               ROUND(AVG(net_salary)::numeric, 0)  AS avg_net
        FROM payroll
        GROUP BY job_role
    )
    SELECT *,
           ROUND((avg_bonus::numeric
               / NULLIF(avg_base, 0) * 100)::numeric, 2) AS bonus_to_base_pct
    FROM role_summary
    ORDER BY bonus_to_base_pct DESC
""")

# Query 9 — Overtime rate by location
run("Q9: Overtime rate % by location", """
    SELECT location,
           COUNT(*)                                                  AS total_employees,
           SUM(CASE WHEN overtime_flag = 1 THEN 1 ELSE 0 END)       AS overtime_count,
           ROUND(100.0 * SUM(CASE WHEN overtime_flag = 1 THEN 1 ELSE 0 END)
               / COUNT(*)::numeric, 1)                               AS overtime_rate_pct
    FROM payroll
    GROUP BY location
    ORDER BY overtime_rate_pct DESC
""")

# Query 10 — Salary quartiles using NTILE
run("Q10: Salary quartile distribution by department (NTILE)", """
    WITH quartiles AS (
        SELECT
            department,
            net_salary,
            NTILE(4) OVER (
                PARTITION BY department
                ORDER BY net_salary
            ) AS salary_quartile
        FROM payroll
    )
    SELECT
        department,
        salary_quartile,
        COUNT(*) AS employee_count,
        ROUND(AVG(net_salary)::numeric, 0) AS avg_salary_in_quartile
    FROM quartiles
    GROUP BY department, salary_quartile
    ORDER BY department, salary_quartile
""")

print("\nAll 10 queries completed.")
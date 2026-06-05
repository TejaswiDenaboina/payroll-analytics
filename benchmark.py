import time
import pandas as pd
from db_config import get_connection

conn = get_connection()
cur  = conn.cursor()

def time_query(query, label, runs=3):
    times = []
    for _ in range(runs):
        start = time.time()
        cur.execute(query)
        cur.fetchall()
        times.append((time.time() - start) * 1000)
    avg = round(sum(times) / len(times), 1)
    print(f"  {label}: {avg}ms")
    return avg

TEST_QUERIES = {
    "Dept payroll sum": """
        SELECT department, SUM(net_salary)
        FROM payroll GROUP BY department
    """,
    "Overtime filter": """
        SELECT employee_id, overtime_pay FROM payroll
        WHERE overtime_flag = 1 AND overtime_pay > 100000
        ORDER BY overtime_pay DESC LIMIT 100
    """,
    "Monthly trend": """
        SELECT pay_year, pay_month, AVG(net_salary)
        FROM payroll GROUP BY pay_year, pay_month
        ORDER BY pay_year, pay_month
    """,
    "Location filter": """
        SELECT location, COUNT(*), AVG(net_salary)
        FROM payroll WHERE location = 'Bangalore'
        GROUP BY location
    """,
}

print("=" * 55)
print("BEFORE INDEXES")
print("=" * 55)
before = {}
for label, query in TEST_QUERIES.items():
    before[label] = time_query(query, label)

print("\nCreating indexes...")
indexes = [
    "CREATE INDEX IF NOT EXISTS idx_department ON payroll(department)",
    "CREATE INDEX IF NOT EXISTS idx_overtime   ON payroll(overtime_flag, overtime_pay)",
    "CREATE INDEX IF NOT EXISTS idx_pay_date   ON payroll(pay_year, pay_month)",
    "CREATE INDEX IF NOT EXISTS idx_location   ON payroll(location)",
    "CREATE INDEX IF NOT EXISTS idx_net_salary ON payroll(net_salary DESC)",
]
for idx in indexes:
    cur.execute(idx)
    conn.commit()
    name = idx.split('idx_')[1].split(' ')[0]
    print(f"  Created: idx_{name}")

print("\n" + "=" * 55)
print("AFTER INDEXES")
print("=" * 55)
after = {}
for label, query in TEST_QUERIES.items():
    after[label] = time_query(query, label)

print("\n" + "=" * 55)
print("BENCHMARK RESULTS — copy into README")
print("=" * 55)
results = []
for label in TEST_QUERIES:
    speedup = round(before[label] / after[label], 1)
    results.append({
        'Query'       : label,
        'Before (ms)' : before[label],
        'After (ms)'  : after[label],
        'Speedup'     : f"{speedup}x"
    })

df = pd.DataFrame(results)
print(df.to_string(index=False))

cur.close()
conn.close()
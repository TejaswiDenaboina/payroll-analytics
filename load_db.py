import pandas as pd
from sqlalchemy import create_engine, text
import time
from db_config import DB_CONFIG

DB_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
engine = create_engine(DB_URL)

df = pd.read_csv('payroll_data.csv', parse_dates=['pay_date'])
print(f"Loaded CSV: {df.shape}")

print("Loading into PostgreSQL...")
start = time.time()
df.to_sql('payroll', engine, if_exists='replace', index=False, chunksize=5000)
elapsed = time.time() - start
print(f"Loaded {len(df):,} rows in {elapsed:.1f}s")

with engine.connect() as conn:
    count = conn.execute(text("SELECT COUNT(*) FROM payroll")).scalar()
    print(f"Rows in DB: {count:,}")
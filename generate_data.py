import pandas as pd
import numpy as np
from faker import Faker
import random

fake = Faker('en_IN')
random.seed(42)
np.random.seed(42)

DEPARTMENTS   = ['Engineering','Sales','HR','Finance','Marketing','Operations']
JOB_ROLES     = ['Analyst','Senior Analyst','Manager','Director','Associate','Lead']
LOCATIONS     = ['Bangalore','Mumbai','Delhi','Hyderabad','Pune','Chennai']
n = 100_000

print("Generating 100,000 employee payroll records...")

employee_ids  = [f"EMP{str(i).zfill(5)}" for i in range(1, n+1)]
departments   = np.random.choice(DEPARTMENTS, n, p=[0.35,0.20,0.08,0.12,0.10,0.15])
job_roles     = np.random.choice(JOB_ROLES,   n, p=[0.30,0.25,0.20,0.05,0.15,0.05])
locations     = np.random.choice(LOCATIONS,    n)
years_exp     = np.random.randint(0, 25, n)

base_salary   = (years_exp * 15000 + np.random.normal(400000, 80000, n)).clip(200000, 2500000)
overtime_flag = np.random.choice([0, 1], n, p=[0.72, 0.28])
overtime_pay  = np.where(overtime_flag==1, base_salary * 0.15 * np.random.uniform(0.5,1.5,n), 0)
bonus         = np.where(np.random.rand(n) < 0.4, base_salary * np.random.uniform(0.05,0.20,n), 0)
deductions    = base_salary * np.random.uniform(0.08, 0.15, n)
net_salary    = base_salary + overtime_pay + bonus - deductions

months        = pd.date_range('2022-01-01', '2024-12-31', freq='MS')
pay_dates     = np.random.choice(months, n)

df = pd.DataFrame({
    'employee_id'   : employee_ids,
    'department'    : departments,
    'job_role'      : job_roles,
    'location'      : locations,
    'years_exp'     : years_exp,
    'base_salary'   : base_salary.round(2),
    'overtime_pay'  : overtime_pay.round(2),
    'bonus'         : bonus.round(2),
    'deductions'    : deductions.round(2),
    'net_salary'    : net_salary.round(2),
    'overtime_flag' : overtime_flag,
    'pay_date'      : pay_dates,
    'pay_year'      : pd.DatetimeIndex(pay_dates).year,
    'pay_month'     : pd.DatetimeIndex(pay_dates).month,
})

df.to_csv('payroll_data.csv', index=False)
print(f"Done. Shape: {df.shape}")
print(df.head())
print(f"\nTotal payroll: ₹{df['net_salary'].sum():,.0f}")
print(f"Avg net salary: ₹{df['net_salary'].mean():,.0f}")
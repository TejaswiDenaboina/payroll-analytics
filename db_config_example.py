# db_config_example.py — rename to db_config.py and fill in your values
import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "payroll_db",
    "user": "postgres",
    "password": "YOUR_PASSWORD_HERE"
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)
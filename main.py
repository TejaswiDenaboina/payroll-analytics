import subprocess
import sys
import time

def run(script, label):
    print(f"\n{'='*55}")
    print(f"  RUNNING: {label}")
    print('='*55)
    start = time.time()
    result = subprocess.run([sys.executable, script], capture_output=False)
    elapsed = time.time() - start
    if result.returncode == 0:
        print(f"  DONE: {label} ({elapsed:.1f}s)")
    else:
        print(f"  FAILED: {label} — stopping here")
        sys.exit(1)

if __name__ == "__main__":
    print("\nPayroll Analytics — Full Pipeline Runner")
    print("=========================================")

    run("generate_data.py", "Generate 100K payroll records")
    run("load_db.py",       "Load data into PostgreSQL")
    run("queries.py",       "Run all 10 SQL queries")
    run("benchmark.py",     "Benchmark indexes before/after")

    print("\n" + "="*55)
    print("  ALL STEPS COMPLETE — Starting dashboard...")
    print("  Open browser at: http://127.0.0.1:8050")
    print("="*55 + "\n")

    subprocess.run([sys.executable, "app.py"])
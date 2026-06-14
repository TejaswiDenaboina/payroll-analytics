import subprocess
import sys

if __name__ == "__main__":
    print("\nPayroll Analytics Dashboard")
    print("=" * 40)

    print("Starting dashboard...")
    print("Open browser at: http://127.0.0.1:8050")

    subprocess.run([sys.executable, "app.py"])
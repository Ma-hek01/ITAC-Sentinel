
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_FILE = ROOT / "outputs" / "itac_sentinel.db"

connection = sqlite3.connect(DB_FILE)
cursor = connection.cursor()

checks = {
    "Total test instances": """
        SELECT COUNT(*) FROM itac_test_results
    """,
    "Passed tests": """
        SELECT COUNT(*) FROM itac_test_results
        WHERE test_status = 'Pass'
    """,
    "Failed tests": """
        SELECT COUNT(*) FROM itac_test_results
        WHERE test_status = 'Fail'
    """,
    "High-risk exceptions": """
        SELECT COUNT(*) FROM itac_test_results
        WHERE test_status = 'Fail'
          AND risk_severity = 'High'
    """,
    "Medium-risk exceptions": """
        SELECT COUNT(*) FROM itac_test_results
        WHERE test_status = 'Fail'
          AND risk_severity = 'Medium'
    """,
    "Open remediation items": """
        SELECT COUNT(*) FROM itac_test_results
        WHERE remediation_status = 'Open'
    """,
}

print("\nITAC SENTINEL SQL VALIDATION")

for name, query in checks.items():
    count = cursor.execute(query).fetchone()[0]
    print(f"{name}: {count}")

print("\nRESULTS BY CONTROL AREA")

query = """
    SELECT
        control_area,
        COUNT(*) AS total_tests,
        SUM(CASE WHEN test_status = 'Pass' THEN 1 ELSE 0 END) AS passed,
        SUM(CASE WHEN test_status = 'Fail' THEN 1 ELSE 0 END) AS failed
    FROM itac_test_results
    GROUP BY control_area
    ORDER BY control_area
"""

for area, total, passed, failed in cursor.execute(query):
    pass_rate = (passed / total * 100) if total else 0
    print(
        f"{area}: Total={total}, Passed={passed}, "
        f"Failed={failed}, Pass Rate={pass_rate:.2f}%"
    )

connection.close()
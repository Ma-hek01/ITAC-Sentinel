
import csv
import json
import sqlite3
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
DB_FILE = OUTPUT_DIR / "itac_sentinel.db"


def read_csv(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def write_csv(filename, fields, rows):
    with open(OUTPUT_DIR / filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


users = read_csv("users.csv")
transactions = read_csv("transactions.csv")
config_expected = read_csv("config_expected.csv")
config_actual = read_csv("config_actual.csv")

user_lookup = {u["user_id"]: u for u in users}
expected_lookup = {r["setting_name"]: r["expected_value"] for r in config_expected}
actual_lookup = {r["setting_name"]: r["actual_value"] for r in config_actual}

results = []


def record(test_id, area, record_id, name, expected, actual,
           passed, severity="Medium"):
    results.append({
        "test_id": test_id,
        "control_area": area,
        "record_id": record_id,
        "test_name": name,
        "expected_result": expected,
        "actual_result": actual,
        "test_status": "Pass" if passed else "Fail",
        "risk_severity": "" if passed else severity,
        "remediation_status": "Not Required" if passed else "Open",
    })


# 1. User access: every user is evaluated
for user in users:
    passed = not (
        user["user_status"] == "Inactive"
        and user["privileged_access"] == "Yes"
    )
    record(
        "AC-01", "Access", user["user_id"],
        "Inactive user retains privileged access",
        "Inactive users must not retain privileged access",
        f"Status={user['user_status']}; Privileged={user['privileged_access']}",
        passed, "High"
    )


# 2. Transaction controls
for t in transactions:
    tid = t["transaction_id"]
    initiator_id = t["initiator_user"]
    approver_id = t["approver_user"]
    amount = float(t["amount"])
    approval = t["approval_status"]

    initiator = user_lookup.get(initiator_id)
    approver = user_lookup.get(approver_id)

    # AC-02: initiator must exist and be active
    active_initiator = bool(
        initiator and initiator["user_status"] == "Active"
    )
    record(
        "AC-02", "Access", tid,
        "Transaction initiated by inactive or unknown user",
        "Initiator must exist and be active",
        f"Initiator={initiator_id}; Active={active_initiator}",
        active_initiator, "High"
    )

    # AP-01: transactions over 50,000 must be approved
    approval_ok = amount <= 50000 or approval == "Approved"
    record(
        "AP-01", "Approval", tid,
        "High-value transaction approval",
        "Amount above 50000 must have Approved status",
        f"Amount={amount:.2f}; Status={approval}",
        approval_ok, "High"
    )

    # AP-02: approved transactions require separate initiator/approver
    if approval == "Approved":
        separate_users = initiator_id != approver_id
        record(
            "AP-02", "Approval", tid,
            "Maker-checker separation",
            "Initiator and approver must be different users",
            f"Initiator={initiator_id}; Approver={approver_id}",
            separate_users, "High"
        )

    # AP-03: an approved transaction must have an active approver
    if approval == "Approved":
        active_approver = bool(
            approver and approver["user_status"] == "Active"
        )
        record(
            "AP-03", "Approval", tid,
            "Approver is active and exists",
            "Approver must exist and be active",
            f"Approver={approver_id}; Active={active_approver}",
            active_approver, "High"
        )

    # TL-01: amount must not exceed initiator's configured limit
    within_limit = bool(
        initiator and amount <= float(initiator["transaction_limit"])
    )
    configured_limit = (
        initiator["transaction_limit"] if initiator else "Unknown"
    )
    record(
        "TL-01", "Transaction Limit", tid,
        "Transaction within configured user limit",
        f"Amount must not exceed limit {configured_limit}",
        f"Amount={amount:.2f}",
        within_limit, "Medium"
    )


# 3. Configuration baseline: compare each expected setting
for setting, expected in expected_lookup.items():
    actual = actual_lookup.get(setting)
    matches = actual is not None and actual == expected
    record(
        "CF-01", "Configuration", setting,
        "Actual setting matches expected baseline",
        f"Expected={expected}",
        f"Actual={actual if actual is not None else 'Missing'}",
        matches, "High"
    )

# 4. Configuration completeness: every actual setting needs a baseline
for setting, actual in actual_lookup.items():
    has_baseline = setting in expected_lookup
    record(
        "CF-02", "Configuration", setting,
        "Actual setting exists in expected baseline",
        "Setting must be documented in baseline",
        f"Actual={actual}; Baseline exists={has_baseline}",
        has_baseline, "Medium"
    )


# Export the complete test register
fields = [
    "test_id", "control_area", "record_id", "test_name",
    "expected_result", "actual_result", "test_status",
    "risk_severity", "remediation_status"
]
write_csv("itac_test_results.csv", fields, results)


# Rebuild SQLite tables from source datasets and test register
connection = sqlite3.connect(DB_FILE)
cursor = connection.cursor()

tables = {
    "users": users,
    "transactions": transactions,
    "config_expected": config_expected,
    "config_actual": config_actual,
    "itac_test_results": results,
}

for table_name, rows in tables.items():
    cursor.execute(f'DROP TABLE IF EXISTS "{table_name}"')
    if not rows:
        continue

    columns = list(rows[0].keys())
    column_sql = ", ".join(f'"{c}" TEXT' for c in columns)
    cursor.execute(f'CREATE TABLE "{table_name}" ({column_sql})')
    placeholders = ", ".join("?" for _ in columns)
    column_names = ", ".join(f'"{c}"' for c in columns)
    insert_sql = (
        f'INSERT INTO "{table_name}" ({column_names}) '
        f'VALUES ({placeholders})'
    )
    cursor.executemany(
        insert_sql,
        [[str(row[c]) for c in columns] for row in rows]
    )

connection.commit()
connection.close()


# Summary: effectiveness uses only applicable Pass/Fail test instances
status_counts = Counter(r["test_status"] for r in results)
severity_counts = Counter(
    r["risk_severity"] for r in results if r["test_status"] == "Fail"
)

by_area = {}
for area in sorted({r["control_area"] for r in results}):
    area_rows = [r for r in results if r["control_area"] == area]
    passed = sum(r["test_status"] == "Pass" for r in area_rows)
    failed = sum(r["test_status"] == "Fail" for r in area_rows)
    applicable = passed + failed
    by_area[area] = {
        "passed": passed,
        "failed": failed,
        "applicable_tests": applicable,
        "pass_rate_percent": round(100 * passed / applicable, 2)
        if applicable else None,
    }

summary = {
    "users_in_scope": len(users),
    "transactions_in_scope": len(transactions),
    "configuration_settings_in_baseline": len(expected_lookup),
    "total_test_instances": len(results),
    "passed_tests": status_counts["Pass"],
    "failed_tests": status_counts["Fail"],
    "high_risk_exceptions": severity_counts["High"],
    "medium_risk_exceptions": severity_counts["Medium"],
    "low_risk_exceptions": severity_counts["Low"],
    "remediation_open": sum(
        r["remediation_status"] == "Open" for r in results
    ),
    "control_area_results": by_area,
}

with open(OUTPUT_DIR / "itac_summary.json", "w", encoding="utf-8") as file:
    json.dump(summary, file, indent=2)

print("\nITAC SENTINEL TESTING COMPLETE")
print(json.dumps(summary, indent=2))
print(f"\nResults saved to: {OUTPUT_DIR}")
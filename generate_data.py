
import csv
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

random.seed(42)


def write_csv(filename, fieldnames, rows):
    with open(DATA_DIR / filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


# 1. Application users and their access permissions
users = []

for i in range(1, 21):
    users.append({
        "user_id": f"U{i:03d}",
        "user_name": f"User_{i:03d}",
        "role": random.choice(["Teller", "Analyst", "Approver", "Admin"]),
        "user_status": "Inactive" if i in [5, 12] else "Active",
        "privileged_access": "Yes" if i in [1, 2, 3, 5, 12] else "No",
        "transaction_limit": random.choice([10000, 25000, 50000, 75000]),
    })

# Ensure known test cases have predictable access attributes
users[0].update(role="Admin", user_status="Active",
                privileged_access="Yes", transaction_limit=75000)
users[4].update(role="Admin", user_status="Inactive",
                privileged_access="Yes", transaction_limit=50000)
users[11].update(role="Analyst", user_status="Inactive",
                 privileged_access="No", transaction_limit=25000)

write_csv(
    "users.csv",
    ["user_id", "user_name", "role", "user_status",
     "privileged_access", "transaction_limit"],
    users
)


# 2. Application transactions
transactions = []

active_user_ids = [u["user_id"] for u in users if u["user_status"] == "Active"]

for i in range(1, 101):
    initiator = random.choice(active_user_ids)
    approver = random.choice(active_user_ids)

    transactions.append({
        "transaction_id": f"T{i:04d}",
        "initiator_user": initiator,
        "approver_user": approver,
        "amount": random.choice([2500, 5000, 12000, 18000, 30000, 45000, 60000]),
        "approval_status": random.choices(
            ["Approved", "Pending", "Rejected"],
            weights=[80, 15, 5]
        )[0],
    })

# Deliberate scenarios for testing
transactions[4].update(
    initiator_user="U005",
    approver_user="U001",
    amount=20000,
    approval_status="Approved"
)  # Inactive user initiated a transaction

transactions[9].update(
    initiator_user="U002",
    approver_user="U002",
    amount=60000,
    approval_status="Approved"
)  # Same user initiated and approved a transaction

transactions[14].update(
    initiator_user="U003",
    approver_user="U001",
    amount=70000,
    approval_status="Pending"
)  # High-value transaction without completed approval

transactions[19].update(
    initiator_user="U004",
    approver_user="U001",
    amount=120000,
    approval_status="Approved"
)  # High-value transaction exceeding the initiator's limit

transactions[24].update(
    initiator_user="U012",
    approver_user="U001",
    amount=10000,
    approval_status="Approved"
)  # Inactive user initiated a transaction

write_csv(
    "transactions.csv",
    ["transaction_id", "initiator_user", "approver_user",
     "amount", "approval_status"],
    transactions
)


# 3. Expected application configuration baseline
config_expected = [
    {"setting_name": "session_timeout_minutes", "expected_value": "15"},
    {"setting_name": "max_login_attempts", "expected_value": "5"},
    {"setting_name": "mfa_required_for_admin", "expected_value": "Yes"},
    {"setting_name": "audit_logging_enabled", "expected_value": "Yes"},
    {"setting_name": "password_min_length", "expected_value": "12"},
]

write_csv(
    "config_expected.csv",
    ["setting_name", "expected_value"],
    config_expected
)


# 4. Observed application configuration
config_actual = [
    {"setting_name": "session_timeout_minutes", "actual_value": "15"},
    {"setting_name": "max_login_attempts", "actual_value": "10"},
    {"setting_name": "mfa_required_for_admin", "actual_value": "No"},
    {"setting_name": "audit_logging_enabled", "actual_value": "Yes"},
    {"setting_name": "password_min_length", "actual_value": "8"},
]

write_csv(
    "config_actual.csv",
    ["setting_name", "actual_value"],
    config_actual
)

print("SYNTHETIC DATA GENERATION COMPLETE")
print(f"Users: {len(users)}")
print(f"Transactions: {len(transactions)}")
print(f"Expected configuration settings: {len(config_expected)}")
print(f"Actual configuration settings: {len(config_actual)}")
print(f"Data saved to: {DATA_DIR}")
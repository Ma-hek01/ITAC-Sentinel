
# ITAC Sentinel — IT Application Control Testing Framework

**Technologies:** Python, SQL, SQLite, Power BI

## Overview

ITAC Sentinel is a demonstration framework that evaluates selected IT application controls using synthetic data representing a simulated banking application. It runs rule-based tests, records pass/fail outcomes, assigns illustrative risk severity, and summarizes exceptions for review through a Power BI dashboard.

## Control Areas

- **Access Controls:** Checks user status, privileged access, and transaction activity involving inactive or unknown users.
- **Transaction Limits:** Identifies transactions that exceed configured limits.
- **Approval Controls:** Evaluates transaction approval and maker-checker rules defined in the framework.
- **Configuration Controls:** Compares actual configuration settings against an expected baseline.

## Technology Stack

- **Python:** Synthetic data generation, rule-based testing, exception classification, and summary reporting.
- **SQL and SQLite:** Structured test-result storage and independent validation queries.
- **Power BI:** KPI cards, control-area test results, risk-severity analysis, and an exception register with interactive filters.

## Project Structure

```text
ITAC Sentinel/
├── data/
│   ├── users.csv
│   ├── transactions.csv
│   ├── config_expected.csv
│   └── config_actual.csv
├── outputs/
│   ├── itac_sentinel.db
│   ├── itac_summary.json
│   └── itac_test_results.csv
├── sql/
├── generate_data.py
├── run_tests.py
├── validate_sql.py
├── dashboard.pbix
└── README.md
```

## Workflow

1. Generate synthetic users, transactions, and configuration settings.
2. Execute rule-based control tests against the generated data.
3. Record individual test instances, expected results, actual results, and pass/fail outcomes.
4. Classify failed tests by illustrative risk severity and assign a remediation status.
5. Store results in SQLite and export a detailed test register and summary.
6. Run SQL validation queries to cross-check test counts and exception results.
7. Visualize the results in Power BI for analysis and review.

## Results

The current demonstration run produced the following results:

| Metric | Result |
|---|---:|
| Users in scope | 20 |
| Transactions in scope | 100 |
| Configuration settings in baseline | 5 |
| Total test instances | 482 |
| Passed tests | 434 |
| Failed tests | 48 |
| High-risk exceptions | 13 |
| Medium-risk exceptions | 35 |
| Open remediation items | 48 |
| Overall test pass rate | 90.04% |

### Test Results by Control Area

| Control Area | Passed | Failed | Pass Rate |
|---|---:|---:|---:|
| Access | 117 | 3 | 97.50% |
| Approval | 245 | 7 | 97.22% |
| Configuration | 7 | 3 | 70.00% |
| Transaction Limit | 65 | 35 | 65.00% |

The SQL validation output matched the Python test summary for total tests, pass/fail counts, risk severity, and open remediation items.

## Dashboard

The Power BI report includes:
- KPI cards for total tests, passed tests, failed tests, high-risk exceptions, and pass rate.
- A comparison of passed and failed tests across control areas.
- A chart showing failed tests by risk severity.
- A failed control test and remediation register.
- Interactive filters for control area, risk severity, and remediation status.

## Assumptions and Limitations

- All data is synthetic and generated for demonstration purposes.
- Test rules, transaction thresholds, risk classifications, and configuration baselines are illustrative, not official banking policies.
- A failed test identifies an item for investigation; it does not independently prove a control failure, security incident, or fraud.
- The remediation status represents a tracking field in the demonstration dataset, not evidence of actual remediation activity.
- Maker-checker and access checks are simplified examples and do not replace a formally approved control matrix, identity evidence, or documented audit procedures.
- The framework does not connect to a live banking or enterprise application.
- Production use would require approved control criteria, validated source evidence, documented test procedures, and independent review.

## Disclaimer

This project is for educational and portfolio demonstration purposes only.
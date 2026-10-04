
-- 1. Count failed tests by control area
SELECT
    control_area,
    COUNT(*) AS failed_test_count
FROM itac_test_results
WHERE test_status = 'Fail'
GROUP BY control_area
ORDER BY failed_test_count DESC;


-- 2. Count exceptions by risk severity
SELECT
    risk_severity,
    COUNT(*) AS exception_count
FROM itac_test_results
WHERE test_status = 'Fail'
GROUP BY risk_severity;


-- 3. Find inactive users retaining privileged access
SELECT
    user_id,
    role,
    user_status,
    privileged_access
FROM users
WHERE LOWER(user_status) = 'inactive'
  AND LOWER(privileged_access) = 'yes';


-- 4. Find transactions initiated by inactive or unknown users
SELECT
    t.transaction_id,
    t.initiator_user,
    u.user_status
FROM transactions t
LEFT JOIN users u
    ON t.initiator_user = u.user_id
WHERE u.user_id IS NULL
   OR LOWER(u.user_status) <> 'active';


-- 5. Find transactions exceeding initiator limits
SELECT
    t.transaction_id,
    t.initiator_user,
    CAST(t.amount AS REAL) AS transaction_amount,
    CAST(u.transaction_limit AS REAL) AS configured_limit
FROM transactions t
JOIN users u
    ON t.initiator_user = u.user_id
WHERE CAST(t.amount AS REAL) >
      CAST(u.transaction_limit AS REAL);


-- 6. Compare expected and actual configuration
SELECT
    e.setting_name,
    e.expected_value,
    a.actual_value
FROM config_expected e
LEFT JOIN config_actual a
    ON e.setting_name = a.setting_name
WHERE a.actual_value IS NULL
   OR a.actual_value <> e.expected_value;


-- 7. Overall failed test count
SELECT COUNT(*) AS total_failed_tests
FROM itac_test_results
WHERE test_status = 'Fail';
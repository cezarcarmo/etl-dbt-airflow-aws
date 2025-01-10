-- models/transactions_summary.sql
SELECT
    category,
    COUNT(*) AS transaction_count,
    SUM(amount) AS total_amount
FROM {{ source('public', 'bank_transactions') }}
GROUP BY category;

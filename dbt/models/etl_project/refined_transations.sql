WITH filtered_transactions AS (
    SELECT
        transaction_id,
        account_id,
        transaction_date,
        amount,
        transaction_type,
        category,
        description,
        CASE
            WHEN amount > 5000 THEN 'Alto valor'
            WHEN amount > 1000 THEN 'Médio valor'
        END AS transaction_category
    FROM {{ source('public', 'bank_transactions') }}
    WHERE amount > 1000
)
SELECT *
FROM filtered_transactions

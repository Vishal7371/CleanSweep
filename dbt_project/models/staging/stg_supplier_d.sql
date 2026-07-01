-- stg_supplier_d.sql
-- Staging model for Supplier D (dates already standardised in loader)

SELECT
    product_name,
    CAST(price AS DOUBLE) AS price,
    CAST(quantity AS INTEGER) AS quantity,
    CAST(order_date AS VARCHAR) AS order_date,
    supplier,
    category,
    source_file,
    loaded_at,
    'supplier_d' AS supplier_id
FROM raw.supplier_d

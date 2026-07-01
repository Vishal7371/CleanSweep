-- stg_supplier_b.sql
-- Staging model for Supplier B (footer rows already removed in loader)

SELECT
    product_name,
    CAST(price AS DOUBLE) AS price,
    CAST(quantity AS INTEGER) AS quantity,
    CAST(order_date AS VARCHAR) AS order_date,
    supplier,
    category,
    source_file,
    loaded_at,
    'supplier_b' AS supplier_id
FROM raw.supplier_b

-- stg_supplier_c.sql
-- Staging model for Supplier C (Excel merged cells already skipped in loader)

SELECT
    product_name,
    CAST(price AS DOUBLE) AS price,
    CAST(quantity AS INTEGER) AS quantity,
    CAST(order_date AS VARCHAR) AS order_date,
    supplier,
    category,
    source_file,
    loaded_at,
    'supplier_c' AS supplier_id
FROM raw.supplier_c

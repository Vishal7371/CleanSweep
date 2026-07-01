-- stg_supplier_a.sql
-- Staging model for Supplier A (Spanish headers already renamed in loader)
-- Casts columns to correct data types

SELECT
    product_name,
    CAST(price AS DOUBLE) AS price,
    CAST(quantity AS INTEGER) AS quantity,
    CAST(order_date AS VARCHAR) AS order_date,
    supplier,
    category,
    source_file,
    loaded_at,
    'supplier_a' AS supplier_id
FROM raw.supplier_a


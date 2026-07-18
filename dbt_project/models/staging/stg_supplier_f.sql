-- stg_supplier_f.sql
-- Staging model for Supplier F (standard clean CSV - no transformation needed)

SELECT
    product_name,
    CAST(price    AS DOUBLE)  AS price,
    CAST(quantity AS INTEGER) AS quantity,
    CAST(order_date AS VARCHAR) AS order_date,
    supplier,
    category,
    source_file,
    loaded_at,
    'supplier_f' AS supplier_id
FROM raw.supplier_f

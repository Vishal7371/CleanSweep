-- stg_supplier_e.sql
-- Staging model for Supplier E (duplicates already removed in loader)

SELECT
    product_name,
    CAST(price AS DOUBLE) AS price,
    CAST(quantity AS INTEGER) AS quantity,
    CAST(order_date AS VARCHAR) AS order_date,
    supplier,
    category,
    source_file,
    loaded_at,
    'supplier_e' AS supplier_id
FROM raw.supplier_e

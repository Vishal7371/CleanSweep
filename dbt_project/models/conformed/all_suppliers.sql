-- all_suppliers.sql
-- Conformed model: combines all 6 supplier staging views into one final table
-- This is the "gold layer" - clean, combined, ready for analysis

SELECT * FROM {{ ref('stg_supplier_a') }}
UNION ALL
SELECT * FROM {{ ref('stg_supplier_b') }}
UNION ALL
SELECT * FROM {{ ref('stg_supplier_c') }}
UNION ALL
SELECT * FROM {{ ref('stg_supplier_d') }}
UNION ALL
SELECT * FROM {{ ref('stg_supplier_e') }}
UNION ALL
SELECT * FROM {{ ref('stg_supplier_f') }}

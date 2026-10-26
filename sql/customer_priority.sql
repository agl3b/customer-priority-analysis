-- CUSTOMER PRIORITY ANALYSIS
-- ANALISIS DE PRIORIDAD DE PEDIDOS

-- ANALYSIS
-- ANALISIS
-- Classify each order using its delivery dates and applicable policy.
-- Clasificar cada pedido usando sus fechas de entrega y la politica aplicable.

SELECT
    o.order_id,
    julianday(o.delivery_date) - julianday(o.order_date) AS delivery_days,
    d.target_days_max,
    CASE
        WHEN NULLIF(TRIM(o.delivery_date), '') IS NULL
            THEN 'Cannot evaluate'
        WHEN d.target_days_max IS NULL
            THEN 'Cannot evaluate'
        WHEN julianday(o.delivery_date) IS NULL
            THEN 'Cannot evaluate'
        WHEN julianday(o.order_date) IS NULL
            THEN 'Cannot evaluate'
        WHEN julianday(o.delivery_date) - julianday(o.order_date) < 0
            THEN 'Cannot evaluate'
        WHEN julianday(o.delivery_date) - julianday(o.order_date) > d.target_days_max
            THEN 'Outside target'
        ELSE 'Within target'
    END AS delivery_result
FROM orders AS o
LEFT JOIN delivery_types AS d
    ON o.service_type = d.service_type
    AND o.delivery_zone = d.delivery_zone;


-- VERIFICATION
-- VERIFICACION
-- Count orders in each delivery category.
-- Contar los pedidos en cada categoria de entrega.

WITH classified_orders AS (
    SELECT
        o.order_id,
        CASE
            WHEN NULLIF(TRIM(o.delivery_date), '') IS NULL
                THEN 'Cannot evaluate'
            WHEN d.target_days_max IS NULL
                THEN 'Cannot evaluate'
            WHEN julianday(o.delivery_date) IS NULL
                THEN 'Cannot evaluate'
            WHEN julianday(o.order_date) IS NULL
                THEN 'Cannot evaluate'
            WHEN julianday(o.delivery_date) - julianday(o.order_date) < 0
                THEN 'Cannot evaluate'
            WHEN julianday(o.delivery_date) - julianday(o.order_date) > d.target_days_max
                THEN 'Outside target'
            ELSE 'Within target'
        END AS delivery_result
    FROM orders AS o
    LEFT JOIN delivery_types AS d
        ON o.service_type = d.service_type
        AND o.delivery_zone = d.delivery_zone
)
SELECT
    delivery_result,
    COUNT(*) AS total_orders
FROM classified_orders
GROUP BY delivery_result
ORDER BY delivery_result;
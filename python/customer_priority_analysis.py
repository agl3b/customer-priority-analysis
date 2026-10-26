import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================
# PROJECT: CUSTOMER PRIORITY ANALYSIS
# PROYECTO: ANÁLISIS DE PRIORIDAD DE PEDIDOS
# ============================================================
#
# BUSINESS PROBLEM / PROBLEMA EMPRESARIAL
#
# ES:
# La empresa quiere identificar qué pedidos necesitan atención
# operativa, especialmente aquellos que superan el tiempo máximo
# permitido por su política de entrega.
#
# EN:
# The company wants to identify orders that need operational
# attention, especially those exceeding their delivery targets.
#
#
# ANALYTICAL WORKFLOW / FLUJO DE ANÁLISIS
#
# Load → Inspect → Transform → Analyze → Verify
# Cargar → Inspeccionar → Transformar → Analizar → Verificar
#
# ============================================================



# ============================================================
# 1. LOAD — CARGAR LOS DATOS
# ============================================================

# Locate project files relative to this script.
# Localizar los archivos del proyecto usando la ubicación de este script.

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"

customers = pd.read_csv(DATA_DIR / "customers.csv")
deliveries = pd.read_csv(DATA_DIR / "delivery_types.csv")
orders = pd.read_csv(DATA_DIR / "orders.csv")


# ============================================================
# 2. INSPECT — INSPECCIONAR LOS DATOS
# ============================================================
#
# PURPOSE / PROPÓSITO
#
# ES:
# Conocer la estructura de los archivos y revisar los tipos
# de datos antes de realizar cálculos.
#
# EN:
# Understand the structure of the files and inspect data types
# before performing calculations.
#
# WHY IT MATTERS / POR QUÉ IMPORTA
#
# ES:
# Las fechas, los números y los valores faltantes deben tratarse
# correctamente para evitar conclusiones equivocadas.
#
# EN:
# Dates, numbers, and missing values must be handled correctly
# to avoid misleading conclusions.
# ============================================================

print("\n========== DATA INSPECTION ==========")

print("\nCustomers columns:")
print(customers.columns)

print("\nDelivery policy columns:")
print(deliveries.columns)

print("\nOrders columns:")
print(orders.columns)

print("\nOrders data types:")
print(orders.dtypes)

print("\nOrders preview:")
print(orders.head())



# ============================================================
# 3. TRANSFORM — COMBINAR LAS TABLAS
# ============================================================
#
# PURPOSE / PROPÓSITO
#
# ES:
# Incorporar a cada pedido la política de entrega que le
# corresponde.
#
# EN:
# Attach the corresponding delivery policy to each order.
#
# HOW IT WORKS / CÓMO FUNCIONA
#
# ES:
# Las tablas se relacionan mediante service_type y delivery_zone.
# Ambas columnas deben coincidir para encontrar la política.
#
# EN:
# The tables are joined using service_type and delivery_zone.
# Both columns must match to identify the policy.
#
# WHY IT MATTERS / POR QUÉ IMPORTA
#
# ES:
# Sin la política correspondiente, no podemos comparar el tiempo
# real de entrega con el máximo permitido.
#
# EN:
# Without the corresponding policy, we cannot compare actual
# delivery time against the allowed maximum.
# ============================================================

orders_with_policy = orders.merge(
    deliveries,
    on=["service_type", "delivery_zone"],
    how="left",
    validate="many_to_one",
    indicator=True
)




# ============================================================
# 4. TRANSFORM — PREPARAR LAS FECHAS
# ============================================================
#
# PURPOSE / PROPÓSITO
#
# ES:
# Convertir las columnas de fecha al formato datetime.
#
# EN:
# Convert date columns to datetime format.
#
# WHY IT MATTERS / POR QUÉ IMPORTA
#
# ES:
# Python puede restar fechas correctamente cuando están
# representadas como valores datetime.
#
# EN:
# Python can correctly subtract dates when they are represented
# as datetime values.
# ============================================================

orders_with_policy["order_date"] = pd.to_datetime(
    orders_with_policy["order_date"],
    errors="coerce"
)

orders_with_policy["delivery_date"] = pd.to_datetime(
    orders_with_policy["delivery_date"],
    errors="coerce"
)



# ============================================================
# 5. TRANSFORM — CALCULAR EL TIEMPO DE ENTREGA
# ============================================================
#
# PURPOSE / PROPÓSITO
#
# ES:
# Calcular cuánto tiempo transcurrió entre la fecha del pedido
# y la fecha de entrega.
#
# EN:
# Calculate the elapsed time between the order date and
# the delivery date.
#
# HOW IT WORKS / CÓMO FUNCIONA
#
# delivery_date - order_date = delivery_time
#
# .dt.days extrae el número de días completos.
#
# WHY IT MATTERS / POR QUÉ IMPORTA
#
# ES:
# Necesitamos medir la duración real para compararla con
# la política de entrega.
#
# EN:
# We need to measure actual delivery duration to compare it
# with the delivery policy.
# ============================================================

orders_with_policy["delivery_time"] = (
    orders_with_policy["delivery_date"]
    - orders_with_policy["order_date"]
)

orders_with_policy["delivery_days"] = (
    orders_with_policy["delivery_time"].dt.days
)



# ============================================================
# 6. TRANSFORM — CLASIFICAR EL CUMPLIMIENTO
# ============================================================
#
# PURPOSE / PROPÓSITO
#
# ES:
# Determinar si cada pedido cumplió su objetivo de entrega.
#
# EN:
# Determine whether each order met its delivery target.
#
# IMPORTANT / IMPORTANTE
#
# ES:
# Si falta la duración real o el objetivo máximo, no podemos
# confirmar el cumplimiento.
#
# Por eso distinguimos entre:
# - Dentro del objetivo.
# - Fuera del objetivo.
# - No evaluable por falta de información.
#
# EN:
# If actual delivery duration or the maximum target is missing,
# compliance cannot be confirmed.
#
# We therefore distinguish between:
# - Within target.
# - Outside target.
# - Cannot evaluate due to missing information.
#
# WHY IT MATTERS / POR QUÉ IMPORTA
#
# ES:
# Un dato faltante no demuestra que un pedido haya incumplido.
#
# EN:
# Missing information does not prove that an order failed.
# ============================================================

orders_with_policy["delivery_result"] = "Cannot evaluate"

# A valid delivery must have a duration, a maximum target,
# and a non-negative delivery duration.
# Una entrega válida debe tener duración, objetivo máximo
# y una duración de entrega no negativa.

valid_delivery = (
    orders_with_policy["delivery_days"].notna()
    & orders_with_policy["target_days_max"].notna()
    & (orders_with_policy["delivery_days"] >= 0)
)

within_target = (
    orders_with_policy["delivery_days"]
    <= orders_with_policy["target_days_max"]
)

orders_with_policy.loc[
    valid_delivery & within_target,
    "delivery_result"
] = "Within target"

orders_with_policy.loc[
    valid_delivery & ~within_target,
    "delivery_result"
] = "Outside target"



# ============================================================
# 7. ANALYZE — RESUMEN GENERAL DE CUMPLIMIENTO
# ============================================================
#
# PURPOSE / PROPÓSITO
#
# ES:
# Contar cuántos pedidos cumplieron, incumplieron o no pudieron
# evaluarse.
#
# EN:
# Count how many orders met their targets, missed their targets,
# or could not be evaluated.
#
# WHY IT MATTERS / POR QUÉ IMPORTA
#
# ES:
# Nos da una visión general antes de investigar grupos o pedidos
# específicos.
#
# EN:
# This provides an overview before investigating individual
# orders or operational groups.
# ============================================================

print("\n========== OVERALL DELIVERY RESULTS ==========")

delivery_summary = (
    orders_with_policy["delivery_result"]
    .value_counts()
    .reindex(
        [
            "Within target",
            "Outside target",
            "Cannot evaluate"
        ],
        fill_value=0
    )
)


print(delivery_summary)


# Calculate the percentage of orders in each delivery category.
# Calcular el porcentaje de pedidos en cada categoría de entrega.

delivery_percentages = (delivery_summary / len(orders_with_policy)) * 100

print("\n========== DELIVERY RESULT PERCENTAGES ==========")
print(delivery_percentages.round(2).astype(str) + "%")

# Verify that all category percentages sum to 100%.
# Verificar que los porcentajes de todas las categorías sumen 100%.

print("\nTotal percentage:", round(delivery_percentages.sum(), 2), "%")


# ============================================================
# 8. ANALYZE — IDENTIFICAR PEDIDOS QUE INCUMPLIERON
# ============================================================
#
# PURPOSE / PROPÓSITO
#
# ES:
# Mostrar los pedidos cuyo incumplimiento puede confirmarse
# con los datos disponibles.
#
# EN:
# Display orders whose delivery target violations can be
# confirmed using the available data.
#
# WHY IT MATTERS / POR QUÉ IMPORTA
#
# ES:
# Estos pedidos son candidatos para una investigación operativa.
# Sin embargo, todavía debemos investigar las causas.
#
# EN:
# These orders are candidates for operational investigation.
# However, the causes still need to be investigated.
# ============================================================

outside_target_orders = orders_with_policy[
    orders_with_policy["delivery_result"] == "Outside target"
]

print("\n========== ORDERS OUTSIDE TARGET ==========")

print(
    outside_target_orders[
        [
            "order_id",
            "customer_id",
            "order_date",
            "delivery_date",
            "delivery_days",
            "target_days_max",
            "order_status",
            "distance_miles",
            "service_type",
            "delivery_zone"
        ]
    ]
)



# ============================================================
# 9. ANALYZE — PEDIDOS QUE NO PODEMOS EVALUAR
# ============================================================
#
# PURPOSE / PROPÓSITO
#
# ES:
# Identificar los pedidos para los que falta información
# necesaria para verificar el cumplimiento.
#
# EN:
# Identify orders missing information needed to verify
# delivery target compliance.
#
# WHY IT MATTERS / POR QUÉ IMPORTA
#
# ES:
# Estos pedidos pueden necesitar una revisión de sus registros.
# No debemos clasificarlos automáticamente como incumplimientos.
#
# EN:
# These orders may require a review of their records.
# We should not automatically classify them as failures.
# ============================================================

unevaluable_orders = orders_with_policy[
    orders_with_policy["delivery_result"] == "Cannot evaluate"
]

print("\n========== ORDERS THAT CANNOT BE EVALUATED ==========")

print(
    unevaluable_orders[
        [
            "order_id",
            "order_date",
            "delivery_date",
            "delivery_days",
            "target_days_max",
            "order_status",
            "distance_miles",
            "service_type",
            "delivery_zone"
        ]
    ]
)



# ============================================================
# 10. ANALYZE — COMPARAR RESULTADOS POR ZONA
# ============================================================
#
# PURPOSE / PROPÓSITO
#
# ES:
# Comparar los resultados de cumplimiento entre las zonas
# de entrega.
#
# EN:
# Compare delivery compliance results across delivery zones.
#
# HOW IT WORKS / CÓMO FUNCIONA
#
# ES:
# Agrupamos por delivery_zone y contamos cada categoría
# de delivery_result.
#
# EN:
# Group by delivery_zone and count each delivery_result category.
#
# IMPORTANT / IMPORTANTE
#
# ES:
# El porcentaje de incumplimiento se calcula únicamente sobre
# los pedidos que sí pudieron evaluarse.
#
# EN:
# The outside-target percentage is calculated only among orders
# that could be evaluated.
# ============================================================

zone_summary = (
    orders_with_policy
    .groupby("delivery_zone")["delivery_result"]
    .value_counts()
    .unstack(fill_value=0)
    .reindex(
        columns=[
            "Within target",
            "Outside target",
            "Cannot evaluate"
        ],
        fill_value=0
    )
)

zone_summary["evaluated_orders"] = (
    zone_summary["Within target"]
    + zone_summary["Outside target"]
)

zone_summary["outside_target_pct"] = (
    zone_summary["Outside target"]
    .div(zone_summary["evaluated_orders"].replace(0, pd.NA))
    * 100
)

print("\n========== RESULTS BY DELIVERY ZONE ==========")

print(zone_summary)



# ============================================================
# 11. ANALYZE — COMPARAR TIPOS DE SERVICIO
# ============================================================
#
# PURPOSE / PROPÓSITO
#
# ES:
# Comparar el cumplimiento entre los distintos tipos de servicio.
#
# EN:
# Compare delivery compliance across service types.
#
# WHY IT MATTERS / POR QUÉ IMPORTA
#
# ES:
# Nos permite observar si algunos servicios presentan una mayor
# proporción de incumplimientos en los datos disponibles.
#
# EN:
# This helps us observe whether some service types have a higher
# proportion of missed targets in the available data.
# ============================================================

service_summary = (
    orders_with_policy
    .groupby("service_type")["delivery_result"]
    .value_counts()
    .unstack(fill_value=0)
    .reindex(
        columns=[
            "Within target",
            "Outside target",
            "Cannot evaluate"
        ],
        fill_value=0
    )
)

service_summary["evaluated_orders"] = (
    service_summary["Within target"]
    + service_summary["Outside target"]
)

service_summary["outside_target_pct"] = (
    service_summary["Outside target"]
    .div(service_summary["evaluated_orders"].replace(0, pd.NA))
    * 100
)

print("\n========== RESULTS BY SERVICE TYPE ==========")

print(service_summary)



# ============================================================
# 12. ANALYZE — COMBINAR ZONA Y TIPO DE SERVICIO
# ============================================================
#
# PURPOSE / PROPÓSITO
#
# ES:
# Comparar los resultados considerando simultáneamente
# la zona y el tipo de servicio.
#
# EN:
# Compare results using both delivery zone and service type.
#
# WHY IT MATTERS / POR QUÉ IMPORTA
#
# ES:
# Dos grupos pueden tener políticas distintas. Compararlos
# conjuntamente ayuda a evitar interpretaciones demasiado
# generales.
#
# EN:
# Different groups may have different delivery policies.
# Comparing them jointly helps avoid overly broad conclusions.
# ============================================================

group_summary = (
    orders_with_policy
    .groupby(
        ["delivery_zone", "service_type", "delivery_result"]
    )
    .size()
    .unstack("delivery_result", fill_value=0)
    .reindex(
        columns=[
            "Within target",
            "Outside target",
            "Cannot evaluate"
        ],
        fill_value=0
    )
)

group_summary["evaluated_orders"] = (
    group_summary["Within target"]
    + group_summary["Outside target"]
)

group_summary["outside_target_pct"] = (
    group_summary["Outside target"]
    .div(group_summary["evaluated_orders"].replace(0, pd.NA))
    * 100
)

print("\n========== RESULTS BY ZONE AND SERVICE ==========")

print(group_summary)



# ============================================================
# 13. EXPLORE — DISTANCE VS. DELIVERY TIME
# ============================================================
#
# PURPOSE / PROPÓSITO
#
# ES:
# Investigar si los pedidos que recorren más millas suelen
# tardar más en entregarse.
#
# EN:
# Explore whether orders traveling more miles tend to take
# longer to deliver.
#
# IMPORTANT / IMPORTANTE
#
# ES:
# Esta es una investigación exploratoria. Una correlación
# no demuestra causalidad ni garantiza una predicción exacta.
#
# EN:
# This is an exploratory investigation. Correlation does not
# prove causation or guarantee an accurate prediction.
#
# WHY USE ONE GROUP? / ¿POR QUÉ UTILIZAR UN SOLO GRUPO?
#
# ES:
# Empezamos con pedidos Regional + Standard para comparar
# observaciones que comparten la misma zona y tipo de servicio.
#
# EN:
# We start with Regional + Standard orders to compare
# observations sharing the same zone and service type.
# ============================================================

regional_standard = orders_with_policy[
    (orders_with_policy["delivery_zone"] == "Regional")
    & (orders_with_policy["service_type"] == "Standard")
    & (orders_with_policy["delivery_days"].notna())
    & (orders_with_policy["distance_miles"].notna())
]

print("\n========== REGIONAL + STANDARD DATA ==========")

print(
    regional_standard[
        ["order_id", "distance_miles", "delivery_days"]
    ]
)

print("\nNumber of complete observations:")

print(len(regional_standard))



# ============================================================
# 14. EXPLORE — VISUALIZAR LA RELACIÓN
# ============================================================
#
# PURPOSE / PROPÓSITO
#
# ES:
# Crear un gráfico de dispersión para observar la relación
# entre las millas recorridas y los días de entrega.
#
# EN:
# Create a scatter plot to examine the relationship between
# distance traveled and delivery days.
#
# HOW TO READ IT / CÓMO LEERLO
#
# ES:
# Cada punto representa un pedido.
# El eje X muestra las millas.
# El eje Y muestra los días de entrega.
#
# EN:
# Each point represents one order.
# The X-axis shows distance in miles.
# The Y-axis shows delivery days.
# ============================================================

plt.figure(figsize=(8, 5))

plt.scatter(
    regional_standard["distance_miles"],
    regional_standard["delivery_days"]
)

plt.xlabel("Distance (miles)")

plt.ylabel("Delivery days")

plt.title("Delivery Distance vs. Duration")

plt.grid(True)

plt.tight_layout()

plt.show()



# ============================================================
# 15. EXPLORE — CALCULAR LA CORRELACIÓN
# ============================================================
#
# PURPOSE / PROPÓSITO
#
# ES:
# Medir la dirección y la fuerza de la relación lineal
# entre distancia y duración.
#
# EN:
# Measure the direction and strength of the linear relationship
# between distance and delivery duration.
#
# IMPORTANT / IMPORTANTE
#
# ES:
# El resultado debe interpretarse junto con el gráfico,
# el tamaño de la muestra y las limitaciones de los datos.
#
# EN:
# The result must be interpreted alongside the plot,
# sample size, and data limitations.
# ============================================================

correlation = regional_standard[
    ["distance_miles", "delivery_days"]
].corr()

print("\n========== CORRELATION ==========")

print(correlation)



# ============================================================
# 16. EXPLORE — COMPROBAR LA SENSIBILIDAD
# ============================================================
#
# PURPOSE / PROPÓSITO
#
# ES:
# Comprobar cuánto cambia la correlación cuando excluimos
# temporalmente los pedidos que recorren 10 millas o más.
#
# EN:
# Check how the correlation changes when orders traveling
# 10 miles or more are temporarily excluded.
#
# IMPORTANT / IMPORTANTE
#
# ES:
# Este es un experimento, no una limpieza de datos.
# No debemos eliminar observaciones válidas solamente porque
# cambian el resultado que queremos obtener.
#
# EN:
# This is an experiment, not a data-cleaning step.
# We should not remove valid observations simply because
# they change the result.
# ============================================================

regional_standard_test = regional_standard[
    regional_standard["distance_miles"] < 10
]

print("\n========== SENSITIVITY TEST ==========")

print(
    regional_standard_test[
        ["order_id", "distance_miles", "delivery_days"]
    ]
)

print("\nCorrelation after temporarily excluding distances >= 10:")

print(
    regional_standard_test[
        ["distance_miles", "delivery_days"]
    ].corr()
)



# ============================================================
# 17. VERIFY — COMPROBAR LOS RESULTADOS
# ============================================================

print("\n========== FINAL VERIFICATION ==========")


# MERGE VERIFICATION — VERIFICAR LA UNIÓN

print("\n========== MERGE VERIFICATION ==========")

print(
    orders_with_policy["_merge"].value_counts()
)

unmatched_orders = orders_with_policy[
    orders_with_policy["_merge"] == "left_only"
]

print("\nOrders without a matching delivery policy:")
print(unmatched_orders[["order_id", "service_type", "delivery_zone"]])

# Verify that every order matched a delivery policy.
# Verificar que todos los pedidos encontraron una política.

print(
    "\nAll orders matched a delivery policy:",
    orders_with_policy["_merge"].eq("both").all()
)


# Aquí continúa tu código de verificación original...

# 1. Verify that the merge preserved the number of orders.
# Comprobar que la unión conservó el número de pedidos.

print("\nOriginal orders:", len(orders))
print("Orders after merge:", len(orders_with_policy))


# 2. Check missing values.
# Comprobar los valores faltantes.

print("\nMissing delivery dates:",
      orders_with_policy["delivery_date"].isna().sum())

print("Missing delivery durations:",
      orders_with_policy["delivery_days"].isna().sum())

print("Missing maximum targets:",
      orders_with_policy["target_days_max"].isna().sum())


# Identify deliveries recorded before their order dates.
# Identificar entregas registradas antes de la fecha del pedido.

negative_delivery_days = orders_with_policy[
    orders_with_policy["delivery_days"] < 0
]

print("\nDeliveries with negative durations:")
print(
    negative_delivery_days[
        ["order_id", "order_date", "delivery_date", "delivery_days"]
    ]
)



# 3. Count the delivery result categories.
# Contar las categorías de resultados.

allowed_categories = [
    "Within target",
    "Outside target",
    "Cannot evaluate"
]

delivery_summary = (
    orders_with_policy["delivery_result"]
    .value_counts()
    .reindex(allowed_categories, fill_value=0)
)

print("\nDelivery result counts:")
print(delivery_summary)


# 4. Identify unexpected categories.
# Identificar categorías inesperadas.

unexpected_results = orders_with_policy.loc[
    ~orders_with_policy["delivery_result"].isin(allowed_categories),
    ["order_id", "delivery_result"]
]

print("\nUnexpected delivery results:")
print(unexpected_results)


# 5. Verify classification against the business rules.
# Verificar la clasificación según las reglas del negocio.

expected_result = pd.Series(
    "Cannot evaluate",
    index=orders_with_policy.index
)

valid_data = (
    orders_with_policy["delivery_days"].notna()
    & orders_with_policy["target_days_max"].notna()
)

within_target_check = (
    orders_with_policy["delivery_days"]
    <= orders_with_policy["target_days_max"]
)

expected_result.loc[
    valid_data & within_target_check
] = "Within target"

expected_result.loc[
    valid_data & ~within_target_check
] = "Outside target"

classification_errors = (
    expected_result != orders_with_policy["delivery_result"]
)

print("\nClassification errors:", classification_errors.sum())

print(
    orders_with_policy.loc[
        classification_errors,
        ["order_id", "delivery_days", "target_days_max", "delivery_result"]
    ]
)

# SAVE FINAL RESULTS
# GUARDAR LOS RESULTADOS FINALES

from pathlib import Path

# Create the results folder if it does not exist.
# Crear la carpeta de resultados si no existe.
results_dir = Path(__file__).resolve().parent.parent / "results"
results_dir.mkdir(parents=True, exist_ok=True)


# 1. Overall delivery summary
# 1. Resumen general de entregas.
final_summary = (
    delivery_summary
    .rename_axis("delivery_result")
    .reset_index(name="total_orders")
)

final_summary.to_csv(
    results_dir / "delivery_summary.csv",
    index=False
)


# 2. Classification of individual orders
# 2. Clasificacion individual de los pedidos.
order_results = orders_with_policy[
    [
        "order_id",
        "order_date",
        "delivery_date",
        "delivery_days",
        "target_days_max",
        "service_type",
        "delivery_zone",
        "delivery_result",
    ]
].copy()

order_results.to_csv(
    results_dir / "order_classification.csv",
    index=False
)


# 3. Results by delivery zone and service type
# 3. Resultados por zona de entrega y tipo de servicio.
zone_service_results = group_summary.reset_index()

zone_service_results.to_csv(
    results_dir / "results_by_zone_service.csv",
    index=False
)

print("\nFinal result files saved:")
print(results_dir / "delivery_summary.csv")
print(results_dir / "order_classification.csv")
print(results_dir / "results_by_zone_service.csv")
# Customer Priority Analysis

## Business Problem

The company wants to identify orders that require operational attention, particularly orders that exceed their delivery targets.

The objective is to evaluate delivery performance against established policies, identify orders that cannot be evaluated with the available information, and distinguish confirmed policy violations from cases requiring further investigation.

## Project Objectives

* Calculate delivery duration using order and delivery dates.
* Compare delivery duration with the applicable maximum delivery target.
* Classify orders as within target, outside target, or unable to evaluate.
* Verify the results using Python and SQL.

## Tools

* Python
* Pandas
* Matplotlib
* SQL
* SQLite

## Analytical Process

1. Inspect the available order and delivery-policy data.
2. Match orders with policies using service type and delivery zone.
3. Calculate delivery duration in days.
4. Classify each order using its delivery dates and applicable maximum target.
5. Identify missing information and check for invalid delivery durations.
6. Compare the classification and category counts produced by Python and SQL.

## Key Findings

The dataset contains 22 orders.

| Delivery classification | Orders |  Percentage |
| ----------------------- | -----: | ----------: |
| Within target           |     19 |      86.36% |
| Outside target          |      1 |       4.55% |
| Cannot evaluate         |      2 |       9.09% |
| Total                   |     22 |     100.00% |

One order exceeded its maximum delivery target. Order 50012 took 5 days to deliver against a maximum target of 3 days.

Two orders could not be evaluated because their delivery dates were missing.

Python and SQL produced matching classification counts for all 22 orders.

## Data Quality and Verification

* All 22 orders matched a delivery policy.
* No missing maximum delivery targets were found after matching the policies.
* Two delivery dates were missing.
* No negative delivery durations were found in the current dataset.
* No classification errors were detected by the Python verification checks.

## Limitations

This analysis identifies delivery-policy outcomes but does not establish the operational causes of delays.

Additional information, such as shipment tracking events, dispatch times, carrier performance, or recorded delay reasons, would be needed to investigate those causes.

The dataset contains only 22 orders, so the findings should not automatically be generalized to a larger population.

## Project Files

* python/customer_priority_analysis.py — Python analysis and verification.
* sql/customer_priority.sql — SQL classification and category counts.
* results/delivery_summary.csv — Overall delivery classification counts.
* results/order_classification.csv — Individual order classifications.
* results/results_by_zone_service.csv — Results grouped by delivery zone and service type.

## How to Run

Requirements

* Python
* Pandas
* Matplolit
* SQL
* SQLite


### Run the Python analysis

From the project directory, run:


python .\python\customer_priority_analysis.py


The analysis reads the CSV files from the `data` directory and saves the results in the `results` directory.

### Run the SQL analysis

From the project directory, run:


sqlite3 -header -column .\data\customer_priority.db ".read .\sql\customer_priority.sql"


The SQL script classifies individual orders and summarizes the results by delivery category.


## Conclusion

The analysis identified one confirmed delivery-target violation and two orders that could not be evaluated because delivery information was incomplete.

Cross-checking the results with Python and SQL provided evidence that both implementations produced the same classifications for the current dataset.

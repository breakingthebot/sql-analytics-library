# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-07-06
### Added
- Queries 11 through 15 in the query registry, analyzing product category cross-selling patterns, customer value tiering (`PERCENT_RANK`), rating correlation with sales volumes, stock log reorder triggers, and first-time vs repeat customer monthly splits.
- Expanded verification test suite to check that all 15 queries compile and run correctly.

## [0.2.0] - 2026-07-06
### Added
- Queries 4 through 10 in the registry, analyzing customer purchase distributions, monthly cohort retention rates, days between orders, inventory turnover alert thresholds, product return leakage rates, rolling spend averages, and customer revenue Pareto distribution.
- Automated tests verifying all 10 registered queries execute cleanly on a seeded SQLite database.

## [0.1.0] - 2026-07-06
### Added
- Database schema containing tables for `customers`, `products`, `orders`, `order_items`, `reviews`, and `inventory_logs`.
- Robust data generator to seed the SQLite database with realistic, high-fidelity mock e-commerce datasets.
- Settings configuration and database manager service supporting raw SQL execution, output formatting, and custom sqlite adapters for datetime compatibility.
- Command-line interface (`sql-analytics`) with `db-init`, `db-status`, `list`, and `run` commands.
- Initial registry of 3 complex analytical queries (LTV, category margins, monthly sales trends).
- Test suite with 11 tests covering all source code packages and modules under `tests/`.

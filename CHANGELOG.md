# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.0] - 2026-07-06
### Added
- `--seasonal` CLI option on the `db-init` command to simulate seasonal retail shopping trends (Nov/Dec holiday spikes, July summer campaigns, post-holiday slumps).
- Modified mock data generator to perform rejection-sampling on dates using month-specific sales weight profiles.
- Added test coverage checking seasonal transaction timeline ranges and valid date boundaries.

## [0.7.0] - 2026-07-06
### Added
- `dashboard` CLI subcommand enabling executive HTML/CSS portfolio dashboard generation.
- DashboardGenerator service compiling interactive charts (Category Margins and Monthly Trends), HSL-mapped Cohort decay heatmaps, and visual KPIs.
- Automated tests verifying HTML structure compile and CLI parser parameters.
- Project-wide pytest database connection fixture sharing.

## [0.6.0] - 2026-07-06
### Added
- `benchmark` CLI subcommand enabling query performance benchmarking.
- DBManager `benchmark_queries` logic tracking min, max, and average execution latencies in milliseconds.
- Automated tests covering the benchmark execution and formatting.

## [0.5.0] - 2026-07-06
### Added
- Queries 16 through 20 in the query registry, resolving review response durations, shelf-life velocity, category cumulative month-over-month window sums, repeat purchase sequence intervals, and category penetration coverage ratios.
- Completed the portfolio goal of 20 complex analytical SQL queries.
- Extended automated tests to run and validate all 20 queries successfully.

## [0.4.0] - 2026-07-06
### Added
- `--format` (or `-f`) CLI parameter supporting CSV, JSON, Markdown, and text table formatting outputs.
- `--output` (or `-o`) CLI parameter enabling exporting query results directly to local files.
- Automated tests verifying formatting and export file operations.

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

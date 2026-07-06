# src/sql_analytics/cli.py
# CLI interface for the SQL Analytics query library.
# Connects to: services/db_manager.py, queries/__init__.py, __init__.py
# Created: 2026-07-06

import argparse
import sys
import logging
from tabulate import tabulate

from sql_analytics import __version__
from sql_analytics.services.db_manager import DBManager
from sql_analytics.queries import QUERIES, get_query_by_id

# Set up logging for CLI
logger = logging.getLogger("sql_analytics.cli")

def print_banner() -> None:
    """Print CLI startup banner."""
    print("=" * 60)
    print(f" SQL Analytics Query Library v{__version__} ".center(60, "="))
    print("=" * 60)

def cmd_db_init(args: argparse.Namespace) -> int:
    """Handle the db-init CLI command."""
    db_mgr = DBManager()
    try:
        db_mgr.initialize_database()
        db_mgr.populate_mock_data(
            num_customers=args.customers,
            num_products=args.products,
            num_orders=args.orders,
            seed=args.seed,
            seasonal_trends=args.seasonal
        )
        print("\n[+] Database initialized and populated successfully!")
        print(f"DB Path: {db_mgr.db_path}")
        return 0
    except Exception as e:
        print(f"\n[-] Error initializing database: {e}", file=sys.stderr)
        return 1

def cmd_db_status(args: argparse.Namespace) -> int:
    """Handle the db-status CLI command."""
    db_mgr = DBManager()
    if not db_mgr.db_path.exists():
        print(f"\n[-] Database file does not exist at: {db_mgr.db_path}")
        print("Run 'sql-analytics db-init' to create it.")
        return 1
        
    try:
        tables = ["customers", "products", "orders", "order_items", "reviews", "inventory_logs"]
        stats = []
        for table in tables:
            res = db_mgr.execute_query(f"SELECT COUNT(*) as count FROM {table};")
            count = res[0]["count"] if res else 0
            stats.append([table, count])
            
        print("\nDatabase Table Statistics:")
        print(tabulate(stats, headers=["Table Name", "Row Count"], tablefmt="grid"))
        return 0
    except Exception as e:
        print(f"\n[-] Error fetching database status: {e}", file=sys.stderr)
        return 1

def cmd_list(args: argparse.Namespace) -> int:
    """Handle the list CLI command."""
    print("\nAvailable Analytical Queries:")
    list_data = []
    for q in QUERIES:
        list_data.append([q["id"], q["title"], q["description"][:60] + "..."])
    print(tabulate(list_data, headers=["ID", "Title", "Description"], tablefmt="grid"))
    return 0

def cmd_run(args: argparse.Namespace) -> int:
    """Handle the run CLI command."""
    db_mgr = DBManager()
    if not db_mgr.db_path.exists():
        print(f"\n[-] Database file does not exist at: {db_mgr.db_path}")
        print("Run 'sql-analytics db-init' to create it.")
        return 1
        
    try:
        query_def = get_query_by_id(args.query_id)
        print(f"\nRunning Query {query_def['id']}: {query_def['title']}")
        print(f"Description: {query_def['description']}\n")
        
        # Output raw SQL if verbose flag is set
        if args.verbose:
            print("SQL Statement:")
            print("-" * 40)
            print(query_def["sql"].strip())
            print("-" * 40 + "\n")
            
        formatted_result = db_mgr.execute_query_formatted(query_def["sql"], fmt=args.format)
        
        if args.output:
            from pathlib import Path
            out_path = Path(args.output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(formatted_result, encoding="utf-8")
            print(f"[+] Results successfully exported to: {out_path.resolve()}")
        else:
            print(formatted_result)
            
        return 0
    except ValueError as ve:
        print(f"\n[-] {ve}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n[-] Error running query: {e}", file=sys.stderr)
        return 1

def cmd_benchmark(args: argparse.Namespace) -> int:
    """Handle the benchmark CLI command."""
    db_mgr = DBManager()
    if not db_mgr.db_path.exists():
        print(f"\n[-] Database file does not exist at: {db_mgr.db_path}")
        print("Run 'sql-analytics db-init' to create it.")
        return 1
        
    try:
        print(f"\nRunning performance benchmark across all registered queries...")
        print(f"Iterations per query: {args.iterations}\n")
        
        # Run benchmark
        stats = db_mgr.benchmark_queries(iterations=args.iterations)
        
        # Format output using our shared formatter
        from sql_analytics.services.db_manager import format_results_list
        formatted_result = format_results_list(stats, fmt=args.format)
        
        if args.output:
            from pathlib import Path
            out_path = Path(args.output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(formatted_result, encoding="utf-8")
            print(f"[+] Benchmark results successfully exported to: {out_path.resolve()}")
        else:
            print(formatted_result)
            
        return 0
    except Exception as e:
        print(f"\n[-] Error running performance benchmark: {e}", file=sys.stderr)
        return 1

def cmd_dashboard(args: argparse.Namespace) -> int:
    """Handle the dashboard CLI command."""
    db_mgr = DBManager()
    if not db_mgr.db_path.exists():
        print(f"\n[-] Database file does not exist at: {db_mgr.db_path}")
        print("Run 'sql-analytics db-init' to create it.")
        return 1
        
    try:
        from sql_analytics.services.dashboard_generator import DashboardGenerator
        from pathlib import Path
        
        out_path = Path(args.output)
        print(f"\nGenerating executive SQL analytics dashboard...")
        
        generator = DashboardGenerator(db_mgr)
        generator.generate_html(out_path)
        
        print(f"[+] Dashboard successfully generated at: {out_path.resolve()}")
        return 0
    except Exception as e:
        print(f"\n[-] Error generating dashboard: {e}", file=sys.stderr)
        return 1

def cmd_shell(args: argparse.Namespace) -> int:
    """Handle the shell CLI command."""
    db_mgr = DBManager()
    if not db_mgr.db_path.exists():
        print(f"\n[-] Database file does not exist at: {db_mgr.db_path}")
        print("Run 'sql-analytics db-init' to create it.")
        return 1
        
    try:
        from sql_analytics.services.repl_shell import REPLShell
        shell = REPLShell(db_mgr)
        shell.run()
        return 0
    except Exception as e:
        print(f"\n[-] Error starting interactive shell: {e}", file=sys.stderr)
        return 1

def main() -> None:
    """CLI Main Entry Point."""
    parser = argparse.ArgumentParser(
        description="SQL Analytics Query Library CLI - analytical querying on an e-commerce dataset."
    )
    
    # Global version flag
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"sql-analytics v{__version__}",
        help="Show program version."
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")
    
    # db-init command
    parser_init = subparsers.add_parser("db-init", help="Initialize schema and populate with mock data")
    parser_init.add_argument("--customers", type=int, default=100, help="Number of customers to generate")
    parser_init.add_argument("--products", type=int, default=30, help="Number of products to generate")
    parser_init.add_argument("--orders", type=int, default=300, help="Number of orders to generate")
    parser_init.add_argument("--seed", type=int, default=42, help="Seed for mock data generator")
    parser_init.add_argument("--seasonal", action="store_true", help="Enable seasonal trends (Nov/Dec spikes)")
    parser_init.set_defaults(func=cmd_db_init)
    
    # db-status command
    parser_status = subparsers.add_parser("db-status", help="Show row count of tables in the database")
    parser_status.set_defaults(func=cmd_db_status)
    
    # list command
    parser_list = subparsers.add_parser("list", help="List all available analytical queries")
    parser_list.set_defaults(func=cmd_list)
    
    # run command
    parser_run = subparsers.add_parser("run", help="Run a specific analytical query by its ID")
    parser_run.add_argument("query_id", type=int, help="The query ID to run")
    parser_run.add_argument("--verbose", action="store_true", help="Print the SQL query before execution")
    parser_run.add_argument(
        "--format", "-f",
        choices=["table", "csv", "json", "markdown"],
        default="table",
        help="Specify the output format (default: table)."
    )
    parser_run.add_argument(
        "--output", "-o",
        type=str,
        help="Write query output directly to a file path."
    )
    parser_run.set_defaults(func=cmd_run)
    
    # benchmark command
    parser_bench = subparsers.add_parser("benchmark", help="Benchmark latency of all registered queries")
    parser_bench.add_argument(
        "--iterations", "-i",
        type=int,
        default=5,
        help="Number of iterations to run each query (default: 5)"
    )
    parser_bench.add_argument(
        "--format", "-f",
        choices=["table", "csv", "json", "markdown"],
        default="table",
        help="Specify the output format (default: table)."
    )
    parser_bench.add_argument(
        "--output", "-o",
        type=str,
        help="Write benchmark metrics directly to a file path."
    )
    parser_bench.set_defaults(func=cmd_benchmark)
    
    # dashboard command
    parser_dash = subparsers.add_parser("dashboard", help="Generate an interactive HTML/CSS portfolio dashboard")
    parser_dash.add_argument(
        "--output", "-o",
        type=str,
        default="reports/dashboard.html",
        help="Specify the output HTML file path (default: reports/dashboard.html)"
    )
    parser_dash.set_defaults(func=cmd_dashboard)
    
    # shell command
    parser_shell = subparsers.add_parser("shell", help="Launch an interactive SQL query REPL shell")
    parser_shell.set_defaults(func=cmd_shell)
    
    args = parser.parse_args()
    
    if not args.command:
        print_banner()
        parser.print_help()
        sys.exit(0)
        
    print_banner()
    sys.exit(args.func(args))

if __name__ == "__main__":
    main()

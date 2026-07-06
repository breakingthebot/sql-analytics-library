# src/sql_analytics/services/repl_shell.py
# Interactive query shell (REPL) service for e-commerce SQL analytics.
# Connects to: services/db_manager.py, queries/__init__.py
# Created: 2026-07-06

import sys
import traceback
from typing import List, Dict, Any

from sql_analytics.services.db_manager import DBManager
from sql_analytics.queries import QUERIES, get_query_by_id

class REPLShell:
    """
    An interactive CLI Read-Eval-Print Loop (REPL) shell for querying the database.
    Supports raw SQL, multi-line entries, registered query runs, and format changes.
    """

    def __init__(self, db_manager: DBManager):
        """
        Initialize the REPL Shell.

        Parameters:
            db_manager (DBManager): The database manager service.
        """
        self.db = db_manager
        self.output_format = "table"

    def run(self) -> None:
        """Launch the REPL interactive prompt loop."""
        print("\n" + "=" * 60)
        print(" E-commerce SQL Analytics Interactive Shell ".center(60, "="))
        print("=" * 60)
        print("Type SQL statements ending with a semicolon ';'")
        print("Type '.help' to list special commands or '.exit' to quit.\n")

        query_buffer = []
        
        while True:
            try:
                # Set prompt based on buffer state (multiline support)
                prompt = "sql-analytics> " if not query_buffer else "         ... > "
                
                # Read input
                try:
                    line = input(prompt).strip()
                except EOFError:
                    print("\nGoodbye!")
                    break
                except KeyboardInterrupt:
                    print("\n[!] Input cleared. (Type '.exit' or Ctrl+D to quit)")
                    query_buffer = []
                    continue

                if not line:
                    continue

                # Handle shell dot commands
                if line.startswith("."):
                    parts = line.split(maxsplit=1)
                    cmd = parts[0].lower()
                    arg = parts[1].strip() if len(parts) > 1 else ""
                    
                    if cmd in [".exit", ".quit"]:
                        print("Goodbye!")
                        break
                    elif cmd == ".help":
                        self._show_help()
                    elif cmd == ".list":
                        self._list_tables()
                    elif cmd == ".schema":
                        self._show_schema(arg)
                    elif cmd == ".queries":
                        self._list_registered_queries()
                    elif cmd == ".run":
                        self._run_registered_query(arg)
                    elif cmd == ".format":
                        self._set_format(arg)
                    else:
                        print(f"[-] Unknown shell command: '{cmd}'. Type '.help' for commands.")
                    continue

                # Add raw SQL statement to buffer
                query_buffer.append(line)

                # Execute query if it ends with a semicolon
                if line.endswith(";"):
                    full_query = " ".join(query_buffer)
                    self._execute_sql(full_query)
                    query_buffer = []

            except Exception as e:
                print(f"[-] Error: {e}", file=sys.stderr)
                query_buffer = []

    def _show_help(self) -> None:
        """Display helper instructions."""
        print("\nAvailable Shell Commands:")
        print("  .help             Show this help guide.")
        print("  .list             List all table names in the database.")
        print("  .schema <table>   Show the CREATE TABLE DDL schema for a table.")
        print("  .queries          List all 20 pre-registered analytical library queries.")
        print("  .run <id>         Run a pre-registered query by its ID (1-20).")
        print("  .format <fmt>     Set the output format ('table', 'csv', 'json', 'markdown').")
        print("  .exit / .quit     Exit the interactive query shell.")
        print("\nNotes:")
        print("  - Raw SQL statements must be terminated with a semicolon ';'.")
        print("  - Multi-line statements are supported: hit Enter to continue typing on the next line.\n")

    def _list_tables(self) -> None:
        """List all tables in the database."""
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        results = self.db.execute_query(query)
        if not results:
            print("[*] No user tables found in database.")
            return
        
        print("\nDatabase Tables:")
        for r in results:
            print(f"  - {r['name']}")
        print()

    def _show_schema(self, table_name: str) -> None:
        """Show CREATE TABLE DDL for a table."""
        if not table_name:
            print("[-] Table name required. E.g. '.schema customers'")
            return
            
        query = "SELECT sql FROM sqlite_master WHERE type='table' AND name = ?;"
        results = self.db.execute_query(query, (table_name,))
        if not results:
            print(f"[-] Table '{table_name}' does not exist.")
            return
            
        print(f"\n{results[0]['sql']}\n")

    def _list_registered_queries(self) -> None:
        """List pre-registered analytical queries."""
        print("\nPre-registered Analytical Queries:")
        for q in QUERIES:
            print(f"  [{q['id']:2d}] {q['title']}")
        print()

    def _run_registered_query(self, query_id_str: str) -> None:
        """Execute a registered analytical query by ID."""
        if not query_id_str:
            print("[-] Query ID required. E.g. '.run 1'")
            return
            
        try:
            q_id = int(query_id_str)
            query_def = get_query_by_id(q_id)
            print(f"\nRunning Query {q_id}: {query_def['title']}")
            print(f"Description: {query_def['description']}\n")
            
            res_str = self.db.execute_query_formatted(query_def["sql"], fmt=self.output_format)
            print(res_str)
            print()
        except ValueError as ve:
            print(f"[-] {ve}")
        except Exception as e:
            print(f"[-] Failed to execute query: {e}")

    def _set_format(self, fmt_name: str) -> None:
        """Set default output format."""
        if not fmt_name:
            print(f"[*] Current output format: '{self.output_format}'")
            return
            
        fmt = fmt_name.lower().strip()
        if fmt in ["table", "csv", "json", "markdown"]:
            self.output_format = fmt
            print(f"[+] Output format changed to: '{fmt}'")
        else:
            print(f"[-] Invalid format: '{fmt}'. Choose from 'table', 'csv', 'json', 'markdown'.")

    def _execute_sql(self, query: str) -> None:
        """Execute a raw SQL statement entered by the user."""
        try:
            # Check if query is a SELECT/WITH query (returns rows) or DDL/DML (write/adjust)
            query_stripped = query.strip().upper()
            is_read = query_stripped.startswith("SELECT") or query_stripped.startswith("WITH")
            
            if is_read:
                formatted = self.db.execute_query_formatted(query, fmt=self.output_format)
                print("\n" + formatted + "\n")
            else:
                # Write query: execute directly and commit
                with self.db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(query)
                    conn.commit()
                    affected = cursor.rowcount
                    print(f"\n[+] Query executed successfully. Rows affected: {affected}\n")
        except Exception as e:
            print(f"\n[-] SQL Execution Error: {e}\n", file=sys.stderr)

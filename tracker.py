"""
tracker.py

Module 5 - SQLite storage layer
"""

import argparse
import csv
import math
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

# Reuse existing Module 4 functions.
from main import (
    read_csv,
    calculate_summary,
    display_results,
    export_reports,
)


def connect_db(db_path):
    """
    Create a database connection and enable foreign keys.
    Create parent folders if they do not exist.
    """
    db_path = Path(db_path)

    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(str(db_path))
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialise_db(connection):
    """
    Create required tables if they do not already exist.
    """
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            source_file TEXT NOT NULL,
            pass_mark REAL NOT NULL
                CHECK(
                    typeof(pass_mark) IN ('integer', 'real')
                    AND pass_mark BETWEEN 0 AND 100
                ),
            invalid_count INTEGER NOT NULL
                CHECK(invalid_count >= 0)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS student_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER NOT NULL,
            name TEXT NOT NULL
                CHECK(TRIM(name) <> ''),
            marks REAL NOT NULL
                CHECK(
                    typeof(marks) IN ('integer', 'real')
                    AND marks BETWEEN 0 AND 100
                ),
            FOREIGN KEY (analysis_id)
                REFERENCES analyses(id)
                ON DELETE CASCADE
        )
        """
    )

    connection.commit()


def close_db(connection):
    """
    Close database connection.
    """
    if connection:
        connection.close()


def validate_pass_mark(value):
    """Parse and validate a finite threshold between 0 and 100."""
    try:
        pass_mark = float(value)
    except (TypeError, ValueError) as error:
        raise argparse.ArgumentTypeError(
            "Pass mark must be a number"
        ) from error

    if not math.isfinite(pass_mark):
        raise argparse.ArgumentTypeError(
            "Pass mark must be a finite number"
        )

    if not 0 <= pass_mark <= 100:
        raise argparse.ArgumentTypeError(
            "Pass mark must be between 0 and 100"
        )

    return pass_mark


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Save student analyses in SQLite"
    )
    parser.add_argument(
        "--db",
        required=True,
        help="SQLite database file",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )
    analyse_parser = subparsers.add_parser(
        "analyse",
        help="Analyse a CSV file and save the results",
    )
    analyse_parser.add_argument(
        "--input",
        required=True,
        help="Input CSV file",
    )
    analyse_parser.add_argument(
        "--pass-mark",
        type=validate_pass_mark,
        default=40.0,
        help="Passing threshold (0-100)",
    )

    subparsers.add_parser(
        "history",
        help="List saved analyses",
    )

    show_parser = subparsers.add_parser(
        "show",
        help="Display a saved analysis",
    )
    show_parser.add_argument(
        "--id",
        type=int,
        required=True,
        help="Saved analysis ID",
    )
    show_parser.add_argument(
        "--output-dir",
        help="Optionally export saved results to this directory",
    )

    return parser.parse_args(argv)


def save_analysis(connection, source_file, pass_mark, invalid_count, students):
    """Save the analysis and all accepted student rows atomically."""
    created_at = datetime.now(timezone.utc).isoformat().replace(
        "+00:00",
        "Z",
    )

    with connection:
        cursor = connection.execute(
            """
            INSERT INTO analyses (
                created_at,
                source_file,
                pass_mark,
                invalid_count
            )
            VALUES (?, ?, ?, ?)
            """,
            (created_at, str(source_file), pass_mark, invalid_count),
        )
        analysis_id = cursor.lastrowid

        connection.executemany(
            """
            INSERT INTO student_results (analysis_id, name, marks)
            VALUES (?, ?, ?)
            """,
            (
                (analysis_id, student["name"], student["mark"])
                for student in students
            ),
        )

    return analysis_id


def fetch_analysis(connection, analysis_id):
    """Fetch an analysis and its valid student count."""
    return connection.execute(
        """
        SELECT a.id, a.created_at, a.source_file, a.pass_mark,
               a.invalid_count, COUNT(s.id) AS valid_count
        FROM analyses AS a
        LEFT JOIN student_results AS s ON s.analysis_id = a.id
        WHERE a.id = ?
        GROUP BY a.id
        """,
        (analysis_id,),
    ).fetchone()


def fetch_students(connection, analysis_id):
    """Fetch saved students in their original input order."""
    rows = connection.execute(
        """
        SELECT name, marks
        FROM student_results
        WHERE analysis_id = ?
        ORDER BY id
        """,
        (analysis_id,),
    ).fetchall()
    return [
        {"name": name, "mark": marks}
        for name, marks in rows
    ]


def show_history(connection):
    rows = connection.execute(
        """
        SELECT a.id, a.created_at, a.source_file, a.pass_mark,
               a.invalid_count, COUNT(s.id) AS valid_count
        FROM analyses AS a
        LEFT JOIN student_results AS s ON s.analysis_id = a.id
        GROUP BY a.id
        ORDER BY a.created_at DESC, a.id DESC
        """
    ).fetchall()

    if not rows:
        print("No saved analyses.")
        return

    print("ID | Created at (UTC) | Source file | Pass mark | Valid | Invalid")
    for row in rows:
        analysis_id, created_at, source_file, pass_mark, invalid_count, valid_count = row
        print(
            f"{analysis_id} | {created_at} | {source_file} | "
            f"{pass_mark:g} | {valid_count} | {invalid_count}"
        )


def show_analysis(connection, analysis, output_dir=None):
    analysis_id, created_at, source_file, pass_mark, invalid_count, _ = analysis
    students = fetch_students(connection, analysis_id)
    summary = calculate_summary(students, pass_mark)

    print(f"Analysis ID: {analysis_id}")
    print(f"Created at (UTC): {created_at}")
    print(f"Source file: {source_file}")
    print(f"Pass mark: {pass_mark:g}")
    display_results(students, summary, invalid_count, pass_mark)

    if output_dir:
        export_reports(
            students,
            summary,
            invalid_count,
            pass_mark,
            output_dir,
        )
        print(f"Reports exported to: {output_dir}")


def run_retrieval_command(args):
    db_path = Path(args.db)
    if not db_path.is_file():
        print(f"Error: database does not exist: {db_path}", file=sys.stderr)
        return 1

    connection = None
    try:
        connection = connect_db(db_path)
        initialise_db(connection)

        if args.command == "history":
            show_history(connection)
            return 0

        analysis = fetch_analysis(connection, args.id)
        if analysis is None:
            print(
                f"Error: analysis ID {args.id} was not found.",
                file=sys.stderr,
            )
            return 1

        show_analysis(connection, analysis, args.output_dir)
        return 0
    except (OSError, sqlite3.Error) as error:
        print(f"Error reading database: {error}", file=sys.stderr)
        return 1
    finally:
        if connection is not None:
            close_db(connection)


def main(argv=None):
    args = parse_args(argv)

    if args.command in {"history", "show"}:
        return run_retrieval_command(args)

    try:
        students, invalid_count = read_csv(args.input)
    except (OSError, UnicodeError, ValueError, csv.Error) as error:
        print(f"Error reading input: {error}", file=sys.stderr)
        return 1

    connection = None
    try:
        connection = connect_db(args.db)
        initialise_db(connection)
        analysis_id = save_analysis(
            connection,
            args.input,
            args.pass_mark,
            invalid_count,
            students,
        )
    except (OSError, sqlite3.Error) as error:
        print(f"Error saving analysis: {error}", file=sys.stderr)
        return 1
    finally:
        if connection is not None:
            close_db(connection)

    summary = calculate_summary(students, args.pass_mark)
    print(f"Saved analysis ID: {analysis_id}")
    display_results(
        students,
        summary,
        invalid_count,
        args.pass_mark,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
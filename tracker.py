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


def main(argv=None):
    args = parse_args(argv)

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
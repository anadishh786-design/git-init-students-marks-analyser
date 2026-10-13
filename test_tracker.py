import csv
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tracker import (
    connect_db,
    fetch_analysis,
    fetch_students,
    initialise_db,
    save_analysis,
)


class TestTrackerDatabase(unittest.TestCase):

    def run_analyse(self, db_path, input_path, *extra_args):
        return self.run_tracker(
            db_path,
            "analyse",
            "--input",
            input_path,
            *extra_args,
        )

    def run_tracker(self, db_path, *args):
        script_path = Path(__file__).with_name("tracker.py")
        return subprocess.run(
            [
                sys.executable,
                str(script_path),
                "--db",
                str(db_path),
                *map(str, args),
            ],
            capture_output=True,
            text=True,
        )

    def test_database_file_created(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "data" / "analyses.db"

            connection = connect_db(db_path)

            self.assertTrue(db_path.exists())

            connection.close()

    def test_tables_created(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "analyses.db"

            connection = connect_db(db_path)
            initialise_db(connection)

            cursor = connection.cursor()

            cursor.execute("""
                SELECT name
                FROM sqlite_master
                WHERE type='table'
            """)

            tables = {row[0] for row in cursor.fetchall()}

            self.assertIn("analyses", tables)
            self.assertIn("student_results", tables)

            connection.close()

    def test_initialise_db_can_run_twice(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "analyses.db"

            connection = connect_db(db_path)

            initialise_db(connection)
            initialise_db(connection)

            connection.close()

    def test_foreign_keys_enabled(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "analyses.db"

            connection = connect_db(db_path)

            cursor = connection.execute(
                "PRAGMA foreign_keys"
            )

            result = cursor.fetchone()[0]

            self.assertEqual(result, 1)

            connection.close()

    def test_name_constraint(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "analyses.db"

            connection = connect_db(db_path)
            initialise_db(connection)

            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO analyses (
                    created_at,
                    source_file,
                    pass_mark,
                    invalid_count
                )
                VALUES (?, ?, ?, ?)
            """, (
                "2026-10-11T12:00:00Z",
                "students.csv",
                40,
                0
            ))

            analysis_id = cursor.lastrowid

            with self.assertRaises(sqlite3.IntegrityError):
                cursor.execute("""
                    INSERT INTO student_results (
                        analysis_id,
                        name,
                        marks
                    )
                    VALUES (?, ?, ?)
                """, (
                    analysis_id,
                    "",
                    80
                ))

            cursor.close()
            connection.close()

    def test_marks_constraint(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "analyses.db"

            connection = connect_db(db_path)
            initialise_db(connection)

            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO analyses (
                    created_at,
                    source_file,
                    pass_mark,
                    invalid_count
                )
                VALUES (?, ?, ?, ?)
            """, (
                "2026-10-11T12:00:00Z",
                "students.csv",
                40,
                0
            ))

            analysis_id = cursor.lastrowid

            with self.assertRaises(sqlite3.IntegrityError):
                cursor.execute("""
                    INSERT INTO student_results (
                        analysis_id,
                        name,
                        marks
                    )
                    VALUES (?, ?, ?)
                """, (
                    analysis_id,
                    "Alice",
                    150
                ))

            cursor.close()
            connection.close()

    def test_numeric_columns_reject_text(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "analyses.db"

            connection = connect_db(db_path)
            initialise_db(connection)
            cursor = connection.cursor()

            with self.assertRaises(sqlite3.IntegrityError):
                cursor.execute("""
                    INSERT INTO analyses (
                        created_at,
                        source_file,
                        pass_mark,
                        invalid_count
                    )
                    VALUES (?, ?, ?, ?)
                """, (
                    "2026-10-11T12:00:00Z",
                    "students.csv",
                    "not-a-number",
                    0
                ))

            cursor.execute("""
                INSERT INTO analyses (
                    created_at,
                    source_file,
                    pass_mark,
                    invalid_count
                )
                VALUES (?, ?, ?, ?)
            """, (
                "2026-10-11T12:00:00Z",
                "students.csv",
                40,
                0
            ))
            analysis_id = cursor.lastrowid

            with self.assertRaises(sqlite3.IntegrityError):
                cursor.execute("""
                    INSERT INTO student_results (
                        analysis_id,
                        name,
                        marks
                    )
                    VALUES (?, ?, ?)
                """, (
                    analysis_id,
                    "Alice",
                    "not-a-number"
                ))

            cursor.close()
            connection.close()

    def test_foreign_key_constraint(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "analyses.db"

            connection = connect_db(db_path)
            initialise_db(connection)

            cursor = connection.cursor()

            with self.assertRaises(sqlite3.IntegrityError):
                cursor.execute("""
                    INSERT INTO student_results (
                        analysis_id,
                        name,
                        marks
                    )
                    VALUES (?, ?, ?)
                """, (
                    9999,
                    "Alice",
                    80
                ))

            cursor.close()
            connection.close()

    def test_analyse_saves_students_and_calculated_summary(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)
            input_path = directory / "students.csv"
            input_path.write_text(
                "name,marks\n"
                "Asha,39\n"
                "Ben,40\n"
                "Cara,82.5\n"
                "Noor,abc\n"
                ",70\n"
                "Zoya,105\n",
                encoding="utf-8",
            )
            db_path = directory / "data" / "analyses.db"

            result = self.run_analyse(
                db_path,
                input_path,
                "--pass-mark",
                "50",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Saved analysis ID: 1", result.stdout)
            self.assertIn("Valid Rows: 3", result.stdout)
            self.assertIn("Invalid Rows: 3", result.stdout)
            self.assertIn("Passes: 1", result.stdout)
            self.assertIn("Fails: 2", result.stdout)
            self.assertIn("Average: 53.83", result.stdout)

            connection = sqlite3.connect(db_path)
            analysis = connection.execute(
                """
                SELECT source_file, pass_mark, invalid_count
                FROM analyses
                """
            ).fetchone()
            students = connection.execute(
                """
                SELECT name, marks
                FROM student_results
                ORDER BY id
                """
            ).fetchall()
            connection.close()

            self.assertEqual(analysis, (str(input_path), 50.0, 3))
            self.assertEqual(
                students,
                [("Asha", 39.0), ("Ben", 40.0), ("Cara", 82.5)],
            )

    def test_invalid_input_does_not_create_database(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)
            input_path = directory / "bad-header.csv"
            input_path.write_text(
                "student,score\nAsha,80\n",
                encoding="utf-8",
            )
            db_path = directory / "data" / "analyses.db"

            result = self.run_analyse(db_path, input_path)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("CSV must contain", result.stderr)
            self.assertFalse(db_path.exists())
            self.assertFalse(db_path.parent.exists())

            missing_path = directory / "missing.csv"
            missing_db_path = directory / "missing-data" / "analyses.db"
            missing_result = self.run_analyse(
                missing_db_path,
                missing_path,
            )

            self.assertNotEqual(missing_result.returncode, 0)
            self.assertIn("Error reading input:", missing_result.stderr)
            self.assertFalse(missing_db_path.exists())
            self.assertFalse(missing_db_path.parent.exists())

    def test_header_only_input_saves_empty_analysis(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)
            input_path = directory / "empty.csv"
            input_path.write_text("name,marks\n", encoding="utf-8")
            db_path = directory / "analyses.db"

            result = self.run_analyse(db_path, input_path)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Valid Rows: 0", result.stdout)
            self.assertIn("Invalid Rows: 0", result.stdout)

            connection = sqlite3.connect(db_path)
            analysis_count = connection.execute(
                "SELECT COUNT(*) FROM analyses"
            ).fetchone()[0]
            student_count = connection.execute(
                "SELECT COUNT(*) FROM student_results"
            ).fetchone()[0]
            connection.close()

            self.assertEqual(analysis_count, 1)
            self.assertEqual(student_count, 0)

    def test_non_finite_or_out_of_range_threshold_does_not_create_database(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)
            input_path = directory / "students.csv"
            input_path.write_text(
                "name,marks\nAsha,80\n",
                encoding="utf-8",
            )

            for threshold in ("nan", "inf", "101"):
                with self.subTest(threshold=threshold):
                    db_path = directory / threshold / "analyses.db"
                    result = self.run_analyse(
                        db_path,
                        input_path,
                        "--pass-mark",
                        threshold,
                    )

                    self.assertNotEqual(result.returncode, 0)
                    self.assertFalse(db_path.exists())

    def test_reimporting_file_creates_separate_analyses(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)
            input_path = directory / "students.csv"
            input_path.write_text(
                "name,marks\nAsha,80\n",
                encoding="utf-8",
            )
            db_path = directory / "analyses.db"

            first = self.run_analyse(db_path, input_path)
            second = self.run_analyse(db_path, input_path)

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertIn("Saved analysis ID: 1", first.stdout)
            self.assertIn("Saved analysis ID: 2", second.stdout)

            connection = sqlite3.connect(db_path)
            analysis_count = connection.execute(
                "SELECT COUNT(*) FROM analyses"
            ).fetchone()[0]
            student_rows = connection.execute(
                "SELECT analysis_id, name, marks FROM student_results ORDER BY id"
            ).fetchall()
            connection.close()

            self.assertEqual(analysis_count, 2)
            self.assertEqual(
                student_rows,
                [(1, "Asha", 80.0), (2, "Asha", 80.0)],
            )

    def test_duplicate_names_are_preserved(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)
            input_path = directory / "duplicates.csv"
            input_path.write_text(
                "name,marks\nSam,70\nSam,85\n",
                encoding="utf-8",
            )
            db_path = directory / "analyses.db"

            result = self.run_analyse(db_path, input_path)

            self.assertEqual(result.returncode, 0, result.stderr)
            connection = sqlite3.connect(db_path)
            students = connection.execute(
                "SELECT name, marks FROM student_results ORDER BY id"
            ).fetchall()
            connection.close()

            self.assertEqual(students, [("Sam", 70.0), ("Sam", 85.0)])

    def test_saved_decimal_marks_and_input_order_are_retrievable(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)
            input_path = directory / "students.csv"
            input_path.write_text(
                "name,marks\nSam,70.25\nSam,85.5\nLee,0\n",
                encoding="utf-8",
            )
            db_path = directory / "analyses.db"
            result = self.run_analyse(db_path, input_path)
            self.assertEqual(result.returncode, 0, result.stderr)

            connection = sqlite3.connect(db_path)
            analysis = fetch_analysis(connection, 1)
            students = fetch_students(connection, 1)
            connection.close()

            self.assertEqual(analysis[3:], (40.0, 0, 3))
            self.assertEqual(
                students,
                [
                    {"name": "Sam", "mark": 70.25},
                    {"name": "Sam", "mark": 85.5},
                    {"name": "Lee", "mark": 0.0},
                ],
            )

    def test_history_and_show_do_not_create_a_missing_database(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "missing" / "analyses.db"
            history = self.run_tracker(db_path, "history")
            result = self.run_tracker(db_path, "show", "--id", "1")

            self.assertNotEqual(history.returncode, 0)
            self.assertIn("database does not exist", history.stderr)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("database does not exist", result.stderr)
            self.assertFalse(db_path.exists())
            self.assertFalse(db_path.parent.exists())

    def test_history_lists_saved_analyses_newest_first(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)
            db_path = directory / "analyses.db"
            first_input = directory / "first.csv"
            second_input = directory / "second.csv"
            first_input.write_text("name,marks\nA,60\n", encoding="utf-8")
            second_input.write_text("name,marks\nB,70\nC,80\n", encoding="utf-8")

            first = self.run_analyse(
                db_path, first_input, "--pass-mark", "55"
            )
            second = self.run_analyse(
                db_path, second_input, "--pass-mark", "65"
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)

            history = self.run_tracker(db_path, "history")

            self.assertEqual(history.returncode, 0, history.stderr)
            self.assertLess(
                history.stdout.index(str(second_input)),
                history.stdout.index(str(first_input)),
            )
            self.assertIn("65 | 2 | 0", history.stdout)
            self.assertIn("55 | 1 | 0", history.stdout)
            self.assertIn("Created at (UTC)", history.stdout)

    def test_empty_history_and_unknown_analysis_are_reported(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "analyses.db"
            connection = connect_db(db_path)
            initialise_db(connection)
            connection.close()

            history = self.run_tracker(db_path, "history")
            missing = self.run_tracker(db_path, "show", "--id", "42")

            self.assertEqual(history.returncode, 0, history.stderr)
            self.assertIn("No saved analyses.", history.stdout)
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("analysis ID 42 was not found", missing.stderr)

    def test_show_exports_saved_results_after_input_csv_is_deleted(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)
            input_path = directory / "students.csv"
            input_path.write_text(
                "name,marks\nAsha,39\nBen,60.5\nAsha,80\n",
                encoding="utf-8",
            )
            db_path = directory / "analyses.db"

            first = self.run_analyse(
                db_path, input_path, "--pass-mark", "50"
            )
            second = self.run_analyse(
                db_path, input_path, "--pass-mark", "75"
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)

            input_path.write_text("this file is now different\n", encoding="utf-8")
            input_path.unlink()

            reports = []
            display_only = self.run_tracker(db_path, "show", "--id", "1")
            self.assertEqual(display_only.returncode, 0, display_only.stderr)
            self.assertIn("Pass mark", display_only.stdout)

            for analysis_id in (1, 2):
                output_dir = directory / f"saved-{analysis_id}"
                shown = self.run_tracker(
                    db_path,
                    "show",
                    "--id",
                    analysis_id,
                    "--output-dir",
                    output_dir,
                )
                self.assertEqual(shown.returncode, 0, shown.stderr)
                self.assertIn("Asha : 39.0 - Fail", shown.stdout)
                self.assertIn("Asha : 80.0", shown.stdout)
                self.assertTrue((output_dir / "results.csv").exists())
                self.assertTrue((output_dir / "summary.json").exists())
                reports.append(output_dir)

            with (reports[0] / "results.csv").open(
                newline="", encoding="utf-8"
            ) as file:
                first_rows = list(csv.DictReader(file))
            with (reports[1] / "results.csv").open(
                newline="", encoding="utf-8"
            ) as file:
                second_rows = list(csv.DictReader(file))
            first_summary = json.loads(
                (reports[0] / "summary.json").read_text(encoding="utf-8")
            )
            second_summary = json.loads(
                (reports[1] / "summary.json").read_text(encoding="utf-8")
            )

            self.assertEqual(
                [row["status"] for row in first_rows],
                ["Fail", "Pass", "Pass"],
            )
            self.assertEqual(
                [row["status"] for row in second_rows],
                ["Fail", "Fail", "Pass"],
            )
            self.assertEqual(first_summary["pass_mark"], 50.0)
            self.assertEqual(first_summary["pass_count"], 2)
            self.assertEqual(second_summary["pass_mark"], 75.0)
            self.assertEqual(second_summary["pass_count"], 1)

    def test_analysis_insert_and_students_roll_back_together(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "analyses.db"
            connection = connect_db(db_path)
            initialise_db(connection)

            with self.assertRaises(sqlite3.IntegrityError):
                save_analysis(
                    connection,
                    "students.csv",
                    50,
                    0,
                    [{"name": "", "mark": 75}],
                )

            analysis_count = connection.execute(
                "SELECT COUNT(*) FROM analyses"
            ).fetchone()[0]
            student_count = connection.execute(
                "SELECT COUNT(*) FROM student_results"
            ).fetchone()[0]
            connection.close()

            self.assertEqual(analysis_count, 0)
            self.assertEqual(student_count, 0)


if __name__ == "__main__":
    unittest.main()
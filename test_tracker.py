import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tracker import connect_db, initialise_db


class TestTrackerDatabase(unittest.TestCase):

    def run_analyse(self, db_path, input_path, *extra_args):
        script_path = Path(__file__).with_name("tracker.py")
        return subprocess.run(
            [
                sys.executable,
                str(script_path),
                "--db",
                str(db_path),
                "analyse",
                "--input",
                str(input_path),
                *extra_args,
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


if __name__ == "__main__":
    unittest.main()
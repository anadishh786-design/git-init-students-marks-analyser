import csv
import json
import os
import subprocess
import sys
import tempfile
import unittest

from io import StringIO
from unittest.mock import patch

import main

from main import (
    calculate_summary,
    display_results,
    export_reports,
    parse_args,
    read_csv,
    validate_record,
)


class TestMarksAnalyser(unittest.TestCase):

    # -----------------------------
    # Validation Tests
    # -----------------------------

    def test_decimal_mark(self):
        valid, value = validate_record("John", "82.5")
        self.assertTrue(valid)
        self.assertEqual(value, 82.5)

    def test_zero_mark(self):
        valid, value = validate_record("John", "0")
        self.assertTrue(valid)
        self.assertEqual(value, 0)

    def test_hundred_mark(self):
        valid, value = validate_record("John", "100")
        self.assertTrue(valid)
        self.assertEqual(value, 100)

    def test_negative_mark(self):
        valid, _ = validate_record("John", "-1")
        self.assertFalse(valid)

    def test_above_hundred(self):
        valid, _ = validate_record("John", "101")
        self.assertFalse(valid)

    def test_blank_mark(self):
        valid, _ = validate_record("John", "")
        self.assertFalse(valid)

    def test_text_mark(self):
        valid, _ = validate_record("John", "abc")
        self.assertFalse(valid)

    def test_nan_mark(self):
        valid, _ = validate_record("John", "NaN")
        self.assertFalse(valid)

    def test_inf_mark(self):
        valid, _ = validate_record("John", "inf")
        self.assertFalse(valid)

    def test_blank_name(self):
        valid, _ = validate_record("", "50")
        self.assertFalse(valid)

    # -----------------------------
    # Summary Tests
    # -----------------------------

    def test_threshold_40_passes(self):
        students = [{"name": "Ben", "mark": 40}]
        summary = calculate_summary(students, 40)

        self.assertEqual(summary["pass_count"], 1)
        self.assertEqual(summary["fail_count"], 0)

    def test_threshold_50_fails(self):
        students = [{"name": "Ben", "mark": 40}]
        summary = calculate_summary(students, 50)

        self.assertEqual(summary["pass_count"], 0)
        self.assertEqual(summary["fail_count"], 1)

    def test_no_valid_students(self):
        summary = calculate_summary([], 40)

        self.assertEqual(summary["pass_count"], 0)
        self.assertEqual(summary["fail_count"], 0)
        self.assertIsNone(summary["average"])
        self.assertIsNone(summary["highest_scorer"])

    def test_summary_values(self):
        students = [
            {"name": "Asha", "mark": 39},
            {"name": "Ben", "mark": 40},
            {"name": "Cara", "mark": 82.5},
        ]

        summary = calculate_summary(students, 40)

        self.assertEqual(summary["pass_count"], 2)
        self.assertEqual(summary["fail_count"], 1)
        self.assertAlmostEqual(summary["average"], 53.83, places=2)

        self.assertEqual(
            summary["highest_scorer"]["name"],
            "Cara"
        )

    # -----------------------------
    # CLI Tests
    # -----------------------------

    def test_default_args(self):
        args = parse_args([])

        self.assertEqual(args.input, "students.csv")
        self.assertEqual(args.output_dir, "reports")
        self.assertEqual(args.pass_mark, 40)

    def test_custom_args(self):
        args = parse_args([
            "--input",
            "sample.csv",
            "--output-dir",
            "output",
            "--pass-mark",
            "50",
        ])

        self.assertEqual(args.input, "sample.csv")
        self.assertEqual(args.output_dir, "output")
        self.assertEqual(args.pass_mark, 50)

    def test_invalid_pass_mark(self):
        with self.assertRaises(SystemExit):
            parse_args(["--pass-mark", "150"])

    def test_invalid_negative_pass_mark(self):
        with self.assertRaises(SystemExit):
            parse_args(["--pass-mark", "-1"])

    # -----------------------------
    # CSV Tests
    # -----------------------------

    def test_read_csv_valid_file(self):

        csv_data = (
            "name,marks\n"
            "John,50\n"
            "Mary,80\n"
        )

        with tempfile.NamedTemporaryFile(
            mode="w",
            delete=False,
            newline=""
        ) as file:

            file.write(csv_data)
            filename = file.name

        try:

            students, invalid = read_csv(filename)

            self.assertEqual(
                len(students),
                2
            )

            self.assertEqual(
                invalid,
                0
            )

        finally:
            os.remove(filename)

    def test_invalid_rows_counted(self):

        csv_data = (
            "name,marks\n"
            "John,80\n"
            ",50\n"
            "Mary,text\n"
            "Sam,101\n"
        )

        with tempfile.NamedTemporaryFile(
            mode="w",
            delete=False,
            newline=""
        ) as file:

            file.write(csv_data)
            filename = file.name

        try:

            students, invalid = read_csv(filename)

            self.assertEqual(
                len(students),
                1
            )

            self.assertEqual(
                invalid,
                3
            )

        finally:
            os.remove(filename)

    def test_missing_header(self):

        csv_data = (
            "student,score\n"
            "John,80\n"
        )

        with tempfile.NamedTemporaryFile(
            mode="w",
            delete=False,
            newline=""
        ) as file:

            file.write(csv_data)
            filename = file.name

        try:

            with self.assertRaises(ValueError):
                read_csv(filename)

        finally:
            os.remove(filename)

    def test_header_only_csv(self):

        csv_data = (
            "name,marks\n"
        )

        with tempfile.NamedTemporaryFile(
            mode="w",
            delete=False,
            newline=""
        ) as file:

            file.write(csv_data)
            filename = file.name

        try:

            students, invalid = read_csv(filename)

            self.assertEqual(len(students), 0)
            self.assertEqual(invalid, 0)

        finally:
            os.remove(filename)

    # -----------------------------
    # Display Tests
    # -----------------------------

    def test_display_results(self):

        students = [
            {"name": "Alice", "mark": 80.0},
            {"name": "Bob", "mark": 30.0},
        ]

        summary = calculate_summary(
            students,
            40,
        )

        with patch(
            "sys.stdout",
            new=StringIO()
        ) as fake_output:

            display_results(
                students,
                summary,
                0,
                40,
            )

            output = fake_output.getvalue()

        self.assertIn(
            "Alice : 80.0 - Pass",
            output
        )

        self.assertIn(
            "Bob : 30.0 - Fail",
            output
        )

    # -----------------------------
    # Export Tests
    # -----------------------------

    def test_export_reports(self):

        students = [
            {
                "name": "Alice",
                "mark": 80,
            }
        ]

        summary = calculate_summary(
            students,
            40,
        )

        with tempfile.TemporaryDirectory() as tmp_dir:

            export_reports(
                students,
                summary,
                0,
                40,
                tmp_dir,
            )

            csv_file = os.path.join(
                tmp_dir,
                "results.csv"
            )

            json_file = os.path.join(
                tmp_dir,
                "summary.json"
            )

            self.assertTrue(
                os.path.exists(csv_file)
            )

            self.assertTrue(
                os.path.exists(json_file)
            )

            with open(
                json_file,
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            self.assertEqual(
                data["valid_count"],
                1,
            )

    # -----------------------------
    # Main Integration
    # -----------------------------

    def test_main_displays_summary(self):

        students = [
            {"name": "Ali", "mark": 65},
            {"name": "Sara", "mark": 35},
        ]

        with patch.object(
            main,
            "read_csv",
            return_value=(students, 1),
        ):

            with patch.object(
                main,
                "export_reports",
            ):

                with patch(
                    "sys.stdout",
                    new=StringIO()
                ) as fake_output:

                    main.main([])

                    output = (
                        fake_output
                        .getvalue()
                    )

        self.assertIn(
            "Passes: 1",
            output
        )

        self.assertIn(
            "Fails: 1",
            output
        )

    # -----------------------------
    # End-to-End Test
    # -----------------------------

    def test_end_to_end(self):

        with tempfile.TemporaryDirectory() as tmp_dir:

            csv_path = os.path.join(
                tmp_dir,
                "students.csv"
            )

            output_dir = os.path.join(
                tmp_dir,
                "reports"
            )

            with open(
                csv_path,
                "w",
                newline=""
            ) as file:

                file.write(
                    "name,marks\n"
                    "Alice,80\n"
                    "Bob,30\n"
                )

            result = subprocess.run(
                [
                    sys.executable,
                    "main.py",
                    "--input",
                    csv_path,
                    "--output-dir",
                    output_dir,
                ],
                capture_output=True,
                text=True,
            )

            self.assertEqual(
                result.returncode,
                0,
            )

            self.assertIn(
                "Alice : 80.0 - Pass",
                result.stdout,
            )

            self.assertTrue(
                os.path.exists(
                    os.path.join(
                        output_dir,
                        "results.csv",
                    )
                )
            )


if __name__ == "__main__":
    unittest.main()

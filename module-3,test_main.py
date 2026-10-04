import os
import importlib.util
import tempfile
import unittest
from io import StringIO
from unittest.mock import patch

from main import (
    calculate_summary,
    display_results,
    read_csv,
    validate_record,
)

module_3_spec = importlib.util.spec_from_file_location(
    "module_3_main",
    os.path.join(os.path.dirname(__file__), "module-3, main.py"),
)
module_3 = importlib.util.module_from_spec(module_3_spec)
module_3_spec.loader.exec_module(module_3)


class TestMarksAnalyser(unittest.TestCase):

    def test_39_fail(self):
        students = [{"name": "A", "mark": 39}]

        result = calculate_summary(students)

        self.assertEqual(result["fails"], 1)

    def test_40_pass(self):
        students = [{"name": "B", "mark": 40}]

        result = calculate_summary(students)

        self.assertEqual(result["passes"], 1)

    def test_decimal_mark(self):
        valid, value = validate_record("John", "82.5")

        self.assertTrue(valid)
        self.assertEqual(value, 82.5)

    def test_zero_mark(self):
        valid, value = validate_record("Jane", "0")

        self.assertTrue(valid)
        self.assertEqual(value, 0)

    def test_hundred_mark(self):
        valid, value = validate_record("John", "100")

        self.assertTrue(valid)
        self.assertEqual(value, 100)

    def test_negative_mark(self):
        valid, _ = validate_record("John", "-5")

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

    def test_infinity_mark(self):
        valid, _ = validate_record("John", "inf")

        self.assertFalse(valid)

    def test_nan_mark(self):
        valid, _ = validate_record("John", "NaN")

        self.assertFalse(valid)

    def test_blank_name(self):
        valid, _ = validate_record("", "50")

        self.assertFalse(valid)

    def test_spaces_name(self):
        valid, _ = validate_record("   ", "50")

        self.assertFalse(valid)

    def test_no_valid_records(self):
        result = calculate_summary([])

        self.assertEqual(result["passes"], 0)
        self.assertEqual(result["fails"], 0)
        self.assertIsNone(result["average"])
        self.assertIsNone(result["highest_scorer"])

    def test_summary_values(self):
        students = [
            {"name": "A", "mark": 39},
            {"name": "B", "mark": 40},
            {"name": "C", "mark": 82.5},
        ]

        result = calculate_summary(students)

        self.assertEqual(result["passes"], 2)
        self.assertEqual(result["fails"], 1)
        self.assertAlmostEqual(result["average"], 53.83, places=2)

    def test_read_csv(self):
        content = (
            "Name,Mark\n"
            "John,50\n"
            "Mary,80\n"
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False, newline="") as file:
            file.write(content)
            filename = file.name

        students, invalid = read_csv(filename)

        self.assertEqual(len(students), 2)
        self.assertEqual(invalid, 0)

        os.remove(filename)

    def test_display_results_summary(self):
        summary = {
            "passes": 2,
            "fails": 1,
            "average": 53.83,
            "highest_scorer": {"name": "John", "mark": 82.5},
        }

        with patch("sys.stdout", new=StringIO()) as fake_output:
            display_results(summary, 1)
            output = fake_output.getvalue()

            self.assertIn("Passes: 2", output)
            self.assertIn("Fails: 1", output)
            self.assertIn("Invalid Rows: 1", output)
            self.assertIn("Average: 53.83", output)
            self.assertIn("Highest Scorer: John (82.5)", output)

    def test_display_results_detail(self):
        students = [
            {"name": "John", "mark": 82.5},
            {"name": "Mary", "mark": 39},
        ]

        summary = {
            "passes": 1,
            "fails": 1,
            "average": 60.75,
            "highest_scorer": {"name": "John", "mark": 82.5},
        }

        with patch("sys.stdout", new=StringIO()) as fake_output:
            display_results(students, summary, 0)
            output = fake_output.getvalue()

            self.assertIn("John", output)
            self.assertIn("82.5", output)
            self.assertIn("Pass", output)
            self.assertIn("Valid Rows", output)
            self.assertIn("Passes: 1", output)

    def test_csv_invalid_rows_counted_once(self):
        csv_data = (
            "Name,Mark\n"
            "John,80\n"
            ",50\n"
            "Mary,text\n"
            "Sam,101\n"
        )

        with tempfile.NamedTemporaryFile(mode="w", delete=False, newline="") as file:
            file.write(csv_data)
            filename = file.name

        students, invalid = read_csv(filename)

        self.assertEqual(len(students), 1)
        self.assertEqual(invalid, 3)

        os.remove(filename)

    def test_main_displays_summary(self):
        students = [
            {"name": "Ali", "mark": 65},
            {"name": "Sara", "mark": 35},
        ]

        with patch.object(module_3, "read_csv", return_value=(students, 1)):
            with patch("sys.stdout", new=StringIO()) as fake_output:
                module_3.main()
                output = fake_output.getvalue()

        self.assertIn("Passes: 1", output)
        self.assertIn("Fails: 1", output)
        self.assertIn("Invalid Rows: 1", output)
        self.assertIn("Highest Scorer: Ali (65)", output)

if __name__ == "__main__":
    unittest.main()
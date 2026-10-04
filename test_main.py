import os
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

    def test_display_results(self):
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


if __name__ == "__main__":
    unittest.main()

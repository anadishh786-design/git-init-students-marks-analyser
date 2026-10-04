import unittest
from main import (
    validate_record,
    calculate_summary,
)


# test 39 = fail
class TestMarksAnalyser(unittest.TestCase):

    def test_39_fail(self):
        students = [
            {"name": "A", "mark": 39}
        ]

        result = calculate_summary(
            students
        )

        self.assertEqual(
            result["fails"],
            1
        )
 #  test 40 = pass
    def test_40_pass(self):
        students = [
            {"name": "B", "mark": 40}
        ]

        result = calculate_summary(
            students
        )

        self.assertEqual(
            result["passes"],
            1
        )
#test 82.5 accepted
    def test_decimal_mark(self):
        valid, value = validate_record(
            "John",
            "82.5"
        )

        self.assertTrue(valid)
        self.assertEqual(
            value,
            82.5
        )
#test 0 accepted
    def test_zero_mark(self):
        valid, value = validate_record(
            "Jane",
            "0"
        )

        self.assertTrue(valid)
        self.assertEqual(
            value,
            0
        )
#test 100 accepted
    def test_hundred_mark(self):
        valid, value = validate_record(
            "John",
            "100"
        )

        self.assertTrue(valid)
        self.assertEqual(
            value,
            100
        )
# negtive mark rejected
    def test_negative_mark(self):
        valid, _ = validate_record(
            "John",
            "-5"
        )

        self.assertFalse(valid)
# above 100 rejected
    def test_above_hundred(self):
        valid, _ = validate_record(
            "John",
            "101"
        )

        self.assertFalse(valid)
#blank marked rejected
    def test_blank_mark(self):
        valid, _ = validate_record(
            "John",
            ""
        )

        self.assertFalse(valid)
#text rejected
    def test_text_mark(self):
        valid, _ = validate_record(
            "John",
            "abc"
        )

        self.assertFalse(valid)
#infinity rejected
    def test_infinity_mark(self):
        valid, _ = validate_record(
            "John",
            "inf"
        )

        self.assertFalse(valid)
# nan rejected
    def test_nan_mark(self):
        valid, _ = validate_record(
            "John",
            "NaN"
        )

        self.assertFalse(valid)
#blank name rejected
    def test_blank_name(self):
        valid, _ = validate_record(
            "",
            "50"
        )

        self.assertFalse(valid)
#spaces only name rejected
    def test_spaces_name(self):
        valid, _ = validate_record(
            "   ",
            "50"
        )

        self.assertFalse(valid)
# no valid records 
    def test_no_valid_records(self):

        result = calculate_summary([])

        self.assertEqual(
            result["passes"],
            0
        )

        self.assertEqual(
            result["fails"],
            0
        )

        self.assertIsNone(
            result["average"]
        )

        self.assertIsNone(
            result["highest_scorer"]
        )
# 39,40.82.5 summary test
    def test_summary_values(self):

        students = [
            {"name": "A", "mark": 39},
            {"name": "B", "mark": 40},
            {"name": "C", "mark": 82.5}
        ]

        result = calculate_summary(
            students
        )

        self.assertEqual(
            result["passes"],
            2
        )

        self.assertEqual(
            result["fails"],
            1
        )

        self.assertAlmostEqual(
            result["average"],
            53.83,
            places=2
        )
# test runner
if __name__ == "__main__":
    unittest.main()
# run tests
# python -m unittest -v
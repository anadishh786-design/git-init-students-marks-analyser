import argparse
import csv
import json
import math
import sys
from pathlib import Path


# -------------------------------------------------
# Function 1: Validate one student record
# -------------------------------------------------
def validate_record(name, mark):
    name = str(name).strip() if name is not None else ""

    if not name:
        return False, "Blank name"

    if mark is None or str(mark).strip() == "":
        return False, "Blank mark"

    try:
        score = float(mark)
    except (TypeError, ValueError):
        return False, "Non-numeric mark"

    if math.isnan(score):
        return False, "NaN mark"

    if math.isinf(score):
        return False, "Infinite mark"

    if score < 0 or score > 100:
        return False, "Mark out of range"

    return True, score


# -------------------------------------------------
# Function 2: Parse command-line arguments
# -------------------------------------------------
def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Student Reporting Tool"
    )

    parser.add_argument(
        "--input",
        default="students.csv",
        help="Input CSV file"
    )

    parser.add_argument(
        "--output-dir",
        default="reports",
        help="Directory for exported reports"
    )

    parser.add_argument(
        "--pass-mark",
        type=float,
        default=40,
        help="Passing threshold (0-100)"
    )

    args = parser.parse_args(argv)

    if not math.isfinite(args.pass_mark):
        parser.error("Pass mark must be a finite value")

    if args.pass_mark < 0 or args.pass_mark > 100:
        parser.error("Pass mark must be between 0 and 100")

    return args


# -------------------------------------------------
# Function 3: Read CSV file
# -------------------------------------------------
def read_csv(filename):

    filename = Path(filename)

    with open(filename, newline="", encoding="utf-8") as file:

        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError(
                "CSV file must contain headers"
            )

        headers = [
            header.strip().lower()
            for header in reader.fieldnames
        ]

        if "name" not in headers or "marks" not in headers:
            raise ValueError(
                "CSV must contain 'name' and 'marks' headers"
            )

        valid_students = []
        invalid_rows = 0

        for row in reader:

            name = ""
            mark = ""

            for key, value in row.items():

                if key is not None and key.strip().lower() == "name":
                    name = value

                if key is not None and key.strip().lower() == "marks":
                    mark = value

            valid, result = validate_record(
                name,
                mark
            )

            if valid:

                valid_students.append(
                    {
                        "name": str(name).strip(),
                        "mark": result,
                    }
                )

            else:

                invalid_rows += 1

                print(
                    f"Rejected row: {row} -> {result}"
                )

        return valid_students, invalid_rows


# -------------------------------------------------
# Function 4: Calculate summary statistics
# -------------------------------------------------
def calculate_summary(students, pass_mark=40):

    if not students:
        return {
            "valid_count": 0,
            "pass_count": 0,
            "fail_count": 0,
            "average": None,
            "highest_scorer": None,
        }

    pass_count = sum(
        1
        for student in students
        if student["mark"] >= pass_mark
    )

    fail_count = len(students) - pass_count

    average = (
        sum(
            student["mark"]
            for student in students
        )
        / len(students)
    )

    highest = max(
        students,
        key=lambda student: student["mark"]
    )

    return {
        "valid_count": len(students),
        "pass_count": pass_count,
        "fail_count": fail_count,
        "average": average,
        "highest_scorer": highest,
    }


# -------------------------------------------------
# Function 5: Display results
# -------------------------------------------------
def display_results(
    students,
    summary,
    invalid_rows,
    pass_mark
):

    print("\nStudent Results")
    print("-" * 40)

    for student in students:

        status = (
            "Pass"
            if student["mark"] >= pass_mark
            else "Fail"
        )

        print(
            f"{student['name']} : "
            f"{student['mark']} - {status}"
        )

    print()
    print(f"Valid Rows: {len(students)}")
    print(f"Invalid Rows: {invalid_rows}")
    print(f"Passes: {summary['pass_count']}")
    print(f"Fails: {summary['fail_count']}")

    if summary["average"] is not None:

        print(
            f"Average: "
            f"{summary['average']:.2f}"
        )

        print(
            f"Highest Scorer: "
            f"{summary['highest_scorer']['name']} "
            f"({summary['highest_scorer']['mark']})"
        )

    else:

        print("Average: N/A")
        print("Highest Scorer: N/A")


# -------------------------------------------------
# Function 6: Export reports
# -------------------------------------------------
def export_reports(
    students,
    summary,
    invalid_rows,
    pass_mark,
    output_dir
):

    output_path = Path(output_dir)

    output_path.mkdir(
        parents=True,
        exist_ok=True
    )

    results_file = output_path / "results.csv"

    with open(
        results_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "name",
                "marks",
                "status",
            ]
        )

        writer.writeheader()

        for student in students:

            writer.writerow(
                {
                    "name": student["name"],
                    "marks": student["mark"],
                    "status":
                    (
                        "Pass"
                        if student["mark"] >= pass_mark
                        else "Fail"
                    ),
                }
            )

    summary_file = output_path / "summary.json"

    data = {
        "valid_count": len(students),
        "invalid_count": invalid_rows,
        "pass_count": summary["pass_count"],
        "fail_count": summary["fail_count"],
        "pass_mark": pass_mark,
        "average": summary["average"],
        "highest_scorer": (
            None
            if summary["highest_scorer"] is None
            else {
                "name": summary["highest_scorer"]["name"],
                "marks": summary["highest_scorer"]["mark"],
            }
        ),
    }

    with open(
        summary_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )


# -------------------------------------------------
# Function 7: Main
# -------------------------------------------------
def main(argv=None):

    args = parse_args(argv)

    try:

        students, invalid_rows = read_csv(
            args.input
        )

    except FileNotFoundError:

        print(
            f"Error: file '{args.input}' "
            f"was not found."
        )

        sys.exit(1)

    except ValueError as error:

        print(f"Error: {error}")
        sys.exit(1)

    summary = calculate_summary(
        students,
        args.pass_mark
    )

    display_results(
        students,
        summary,
        invalid_rows,
        args.pass_mark
    )

    export_reports(
        students,
        summary,
        invalid_rows,
        args.pass_mark,
        args.output_dir
    )


if __name__ == "__main__":
    main(sys.argv[1:])

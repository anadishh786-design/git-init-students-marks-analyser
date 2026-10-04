import csv
import math
# function 1 validate one student record.

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
# function 2 read csv file 

def read_csv(filename):
    valid_students = []
    invalid_rows = 0

    with open(filename, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row is None:
                continue

            name = (row.get("name") if row.get("name") is not None else "")
            if not name:
                name = row.get("Name") if row.get("Name") is not None else ""
            if not name:
                name = row.get("NAME") if row.get("NAME") is not None else ""

            mark = row.get("marks") if row.get("marks") is not None else ""
            if mark == "":
                mark = row.get("Mark") if row.get("Mark") is not None else ""
            if mark == "":
                mark = row.get("MARK") if row.get("MARK") is not None else ""

            valid, result = validate_record(name, mark)

            if valid:
                valid_students.append({
                    "name": str(name).strip(),
                    "mark": result
                })
            else:
                invalid_rows += 1
                print(f"Rejected row: {row} -> {result}")

    return valid_students, invalid_rows

# function 3 calculate summary statistics
def calculate_summary(students):
    if not students:
        return {
            "passes": 0,
            "fails": 0,
            "average": None,
            "highest_scorer": None
        }

    passes = sum(
        1 for s in students
        if s["mark"] >= 40
    )

    fails = len(students) - passes

    average = (
        sum(s["mark"] for s in students)
        / len(students)
    )

    highest = max(
        students,
        key=lambda s: s["mark"]
    )

    return {
        "passes": passes,
        "fails": fails,
        "average": average,
        "highest_scorer": highest
    } 
#function 4 display results
def display_results(*args):
    if len(args) == 2:
        summary, invalid_rows = args
        valid_rows = summary["passes"] + summary["fails"]
        print(f"Valid Rows: {valid_rows}")
        print(f"Passes: {summary['passes']}")
        print(f"Fails: {summary['fails']}")
        print(f"Invalid Rows: {invalid_rows}")

        if summary["average"] is not None:
            print(f"Average: {summary['average']:.2f}")
            print(
                f"Highest Scorer: {summary['highest_scorer']['name']} "
                f"({summary['highest_scorer']['mark']})"
            )
        else:
            print("No valid records found.")
        return

    if len(args) == 3:
        students, summary, invalid_rows = args
        print("\nStudent Results")
        print("-" * 40)

        for student in students:
            status = "Pass" if student["mark"] >= 40 else "Fail"
            print(f"{student['name']} : {student['mark']} - {status}")

        print()
        print(f"Valid Rows: {len(students)}")
        print(f"Invalid Rows: {invalid_rows}")
        print(f"Passes: {summary['passes']}")
        print(f"Fails: {summary['fails']}")

        if summary["average"] is not None:
            print(f"Average: {summary['average']:.2f}")
            print(
                f"Highest Scorer: {summary['highest_scorer']['name']} "
                f"({summary['highest_scorer']['mark']})"
            )
        else:
            print("No valid records found.")
        return

    raise TypeError("display_results() takes either 2 or 3 positional arguments")

# function 5 protects main execution.
def main():
    students, invalid_rows = read_csv("students.csv")
    summary = calculate_summary(students)
    display_results(students,summary, invalid_rows)


if __name__ == "__main__":
    main()

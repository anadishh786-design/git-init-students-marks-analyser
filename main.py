import csv

valid_students = []
invalid_count = 0
pass_count = 0
fail_count = 0

with open("students.csv", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        name = row["name"].strip()
        marks = row["marks"].strip()

        try:
            marks = float(marks)

            if marks < 0 or marks > 100:
                raise ValueError

            valid_students.append((name, marks))
            if marks >= 40:
                pass_count += 1
            else:
                fail_count += 1
        except ValueError:
            print(f"WARNING: Invalid marks for {name}: {row['marks']}")
            invalid_count += 1

print("\nStudent Results")
print("-" * 30)

for name, marks in valid_students:
    status = "Pass" if marks >= 40 else "Fail"
    print(f"{name}: {marks} - {status}")

valid_count = len(valid_students)

print("\nSummary")
print("-" * 30)
print(f"Valid rows: {valid_count}")
print(f"Invalid rows: {invalid_count}")
print(f"Pass: {pass_count}")
print(f"Fail: {fail_count}")


if valid_students:
    average = sum(marks for _, marks in valid_students) / valid_count
    highest_name, highest_marks = max(valid_students, key=lambda x: x[1])

    print(f"Average marks: {average:.2f}")
    print(f"Highest scorer: {highest_name} ({highest_marks})")

else:
    print("Average marks: N/A")
    print("Highest scorer: N/A")

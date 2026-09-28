# main.py

students = {
    "ALI":65,
    "SARA":82,
    "RAVI":38,
    "MEENA":74,
    "JOHN":41
}

# Display each student’s marks and Pass/Fail
print("Student Results:\n")
for name, marks in students.items():
    status = "Pass"if marks >= 40 else "Fail"
    print(f"{name}: {marks} - {status}")

# Calculate class average
average = sum(students.values()) / len(students)
print(f"\nClass Average: {average:.2f}")

# Find highest-scoring student
highest_student = max(students, key=students.get)
print(f"Highest Scoring Student: {highest_student} ({students[highest_student]})")

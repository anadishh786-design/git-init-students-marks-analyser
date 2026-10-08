# Student Reporting Tool (Module 4)

A Python command-line application that reads student marks from a CSV file, validates records, calculates statistics, displays results, and exports reports in CSV and JSON formats.

---

# Python Version

This project was developed and tested using:

```text
Python 3.11
```

Check your Python version:

```bash
python --version
```

---

# Clone the Repository

Clone the repository:

```bash
git clone <repository-url>
```

Move into the project directory:

```bash
cd <repository-folder>
```

Switch to the Module 4 branch:

```bash
git switch module-4-cli-reports
```

---

# Project Structure

```text
student-reporting-tool/
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── main.py
├── test_main.py
├── students.csv
├── sample_students.csv
├── starter-learning-notes.md
├── readme.md
├── .gitignore
│
├── reports/
│   ├── results.csv
│   └── summary.json
│
└── __pycache__/
```

---

# Features

- Reads student data from CSV files
- Validates student records
- Supports configurable passing thresholds
- Calculates:
  - Average marks
  - Pass count
  - Fail count
  - Highest scorer
- Displays results in the terminal
- Exports results to CSV and JSON
- Handles invalid files and headers
- Supports command-line arguments
- Includes automated unit tests
- Includes GitHub Actions workflow

---

# Running the Program

Run using the default input file:

```bash
python main.py
```

Run using a custom file:

```bash
python main.py --input sample_students.csv
```

Run using a custom output directory:

```bash
python main.py --input sample_students.csv --output-dir reports
```

Run with a custom pass threshold:

```bash
python main.py --input sample_students.csv --output-dir reports --pass-mark 50
```

See the available command-line options:

```bash
python main.py --help
```

---

# Running the Tests

Run all tests:

```bash
python -m unittest discover -v
```

Run a specific file:

```bash
python -m unittest -v test_main.py
```

---

# Input Format

The CSV files must contain the headers:

```csv
name,marks
Student Name,80
Another Student,35
```

Each row must contain:

- a non-blank student name
- a numeric mark from 0 to 100

Invalid rows are ignored from the valid results set and reported in the terminal.

---

# Output Files

The program generates the following files in the chosen output directory:

- `results.csv`
- `summary.json`

`results.csv` contains only valid students and includes these columns:

```csv
name,marks,status
```

`summary.json` contains:

- valid_count
- invalid_count
- pass_count
- fail_count
- pass_mark
- average
- highest_scorer

---

# Example Result

Running the program with the sample data produces output like this:

```text
Rejected row: {'name': 'Noor', 'marks': 'abc'} -> Non-numeric mark
Rejected row: {'name': '', 'marks': '70'} -> Blank name
Rejected row: {'name': 'Zoya', 'marks': '105'} -> Mark out of range

Student Results
----------------------------------------
Asha : 39.0 - Fail
Ben : 40.0 - Pass
Cara : 82.5 - Pass

Valid Rows: 3
Invalid Rows: 3
Passes: 2
Fails: 1
Average: 53.83
Highest Scorer: Cara (82.5)
```

---

# Common Errors and Fixes

## File not found

If the program says the input file was not found, check that you are running from the correct working directory or that your path is relative to the current folder.

```bash
python main.py --input sample_students.csv
```

If you are in a different folder, provide the full relative path instead.

## Missing or invalid headers

The CSV must contain `name` and `marks` headers. Header names are trimmed and compared case-insensitively.

If the headers are missing, the program exits with a useful error message.

## Invalid pass threshold

The threshold must be a finite value between 0 and 100.

Example:

```bash
python main.py --input sample_students.csv --pass-mark 150
```

This will exit with an error because 150 is outside the valid range.

---

# Troubleshooting

- Run tests first if you want to confirm the project is behaving as expected.
- If a variable appears undefined during a partial run, execute the whole script rather than a single selected block.
- Do not forget that relative paths are resolved from the terminal's current working directory, not from the script location.

---

# Final Note

This project is designed to be run with Python 3.11 and the standard library only. It is intended to be used as a student marks reporting tool for CSV validation, threshold analysis, and report exports.

# Marks Analyser - Module 3

## Overview

Marks Analyser is a Python application that reads student records from a CSV file, validates the data, and generates a summary of student performance.

The project was refactored in Module 3 to improve maintainability by separating responsibilities into functions and adding automated tests using Python's built-in `unittest` framework.

---

## Features

### Data Validation

Each record is validated before being processed.

#### Name Rules

- Name must not be blank.
- Name must not contain only whitespace.

#### Marks Rules

- Marks must be numeric.
- Decimal marks are accepted.
- Marks must be between 0 and 100 inclusive.
- Negative marks are rejected.
- Marks greater than 100 are rejected.
- NaN values are rejected.
- Infinite values are rejected.

Invalid records are skipped and counted separately.

---

## Summary Information

For all valid students, the program displays:

- Student name
- Marks obtained
- Pass/Fail status
- Number of valid records
- Number of invalid records
- Pass count
- Fail count
- Average mark
- Highest-scoring student

A student passes when their mark is 40 or above.

---

## Project Structure

```text
.
├── main.py
├── test_main.py
├── students.csv
└── README.md
```

---

## Functions

The application is organised into the following functions:

```python
validate_record()
read_csv()
calculate_summary()
display_results()
main()
```

The program entry point is protected using:

```python
if __name__ == "__main__":
    main()
```

This allows functions to be imported and tested without automatically running the program.

---

## Running the Program

Run the application with:

```bash
python main.py
```

### Example Output

```text
Student Results
---------------
Ali : 65.0 - Pass
Sara : 82.0 - Pass
Ravi : 45.0 - Pass
Meena : 74.0 - Pass
John : 41.0 - Pass
ali2 : 33.0 - Fail
ali3 : 100.0 - Pass
sumit : 82.5 - Pass

Valid Rows: 8
Invalid Rows: 3
Passes: 7
Fails: 1
Average: 65.31
Highest Scorer: ali3 (100.0)
```

---

## Running the Tests

Execute all tests using:

```bash
python -m unittest discover -v
```

### Example Test Output

```text
Ran 20 tests

OK
```

---

## Test Coverage

### Validation Tests

- Blank names rejected
- Whitespace-only names rejected
- Non-numeric marks rejected
- Empty marks rejected
- Negative marks rejected
- Marks above 100 rejected
- NaN values rejected
- Infinite values rejected
- Decimal marks accepted
- Boundary values accepted (0, 40, 100)

### Summary Tests

- Valid row count
- Pass count
- Fail count
- Average calculation
- Highest scorer calculation
- No valid records handling

### CSV Processing Tests

- Valid records loaded correctly
- Invalid records counted correctly
- Mixed valid and invalid records handled correctly

### Display Tests

- Student results displayed correctly
- Summary output displayed correctly
- Key output values verified

### Integration Tests

- `main()` processes a CSV file correctly
- Output contains student results and summary information

---

## Module 3 Improvements

The following improvements were completed during Module 3:

- Refactored code into smaller reusable functions.
- Added automated unit tests using `unittest`.
- Improved record validation.
- Added support for decimal marks.
- Added handling for NaN and infinite values.
- Added integration testing for the program entry point.
- Maintained import-safe execution using `if __name__ == "__main__"`.

---

## Future Improvements

Planned enhancements for future modules include:

- Command-line argument support.
- Configurable passing thresholds.
- Exporting reports to CSV and JSON.
- Automated testing with GitHub Actions.
- Improved file and error handling.

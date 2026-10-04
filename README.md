# Marks Analyser - Module 3

## Overview

This Python application reads student marks from a CSV file, validates the data, and produces a summary report.

The project was refactored in Module 3 to improve maintainability and add automated testing using Python's built-in `unittest` framework.

---

## Features

### Data Validation

The program validates each student record and rejects invalid rows.

#### Valid Name Rules

- Name must not be blank
- Name must not contain only spaces

#### Valid Mark Rules

- Marks must be numeric
- Marks can contain decimals
- Marks must be between 0 and 100 inclusive
- NaN values are rejected
- Infinite values are rejected

---

## Summary Information

For valid records the program displays:

- Student name
- Mark
- Pass/Fail status
- Valid row count
- Invalid row count
- Pass count
- Fail count
- Average mark
- Highest-scoring student

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

## Refactoring Changes

The application was reorganised into separate functions:

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

This allows the functions to be imported by the test suite without automatically running the application.

---

## Running the Program

Run the analyser:

```bash
python main.py
```

Example output:

```text
Student Results
---------------
Alice : 82.5 - Pass
Bob : 39.0 - Fail

Valid Rows: 8
Invalid Rows: 3
Passes: 7
Fails: 1
Average Mark: 65.31
```

---

## Running the Tests

Run all automated tests:

```bash
python -m unittest -v
```

Example output:

```text
Ran 17 tests

OK
```

---

## Test Coverage

The automated tests verify:

### Validation

- 39 → Fail
- 40 → Pass
- 82.5 → Accepted
- 0 → Accepted
- 100 → Accepted
- Negative marks rejected
- Marks above 100 rejected
- Blank marks rejected
- Text marks rejected
- NaN rejected
- Infinity rejected
- Blank names rejected
- Spaces-only names rejected

### Summary Calculations

- Pass count
- Fail count
- valid rows count
- Average mark calculation
- Highest scorer detection
- No valid records handling

### CSV Processing

- CSV records are loaded correctly
- Invalid rows are counted correctly

### Display Output

- Summary information is displayed correctly
- Key output values are tested


```

3. Confirmed that the 40-mark test failed.

4. Restored the correct implementation.

5. Re-ran 

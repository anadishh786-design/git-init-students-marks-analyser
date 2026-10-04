#module-2-csv marks
## run instructions
#python main.py
Features
Reads student data from CSV
Validates marks
Ignores invalid rows
Calculates average
Finds highest scorer
count fail & pass students
Supports decimal marks
Test Cases
Test 1: Exactly 40

Expected: Pass
Actual: Pass

Test 2: Blank Mark

Expected: Invalid warning

Actual: Invalid warning

Test 3: Headings Only

Expected: No valid students

Actual: No valid students

Test 4: Decimal Marks (82.5)                                                                   Expected : Pass

Actual: Pass

Time Spent

Approx. 2-3 hours

Help Used
Python documentation
CSV module documentation
# module-3
# Marks Analyser

A Python program that reads student marks from a CSV file, validates the data, and generates a summary report.

## Features

- Reads student records from a CSV file
- Validates student names and marks
- Supports decimal marks
- Accepts marks from 0 to 100 inclusive
- Counts passes and failures
- Calculates average mark
- Identifies the highest-scoring student
- Reports invalid rows and their reasons
- Handles files with no valid records
- Includes automated unit tests using Python's unittest module

## Project Structure

```text
.
├── main.py
├── test_main.py
├── students.csv
└── README.md
```

## Requirements

- Python 3.x

## Run the Program

```bash
python main.py
```

## Run the Tests

```bash
python -m unittest -v
```

## Example Test Output

```text
Ran 15 tests in 0.00s

OK
```

## Test Cases Covered

- 39 → Fail
- 40 → Pass
- 82.5 → Accepted
- 0 → Accepted
- 100 → Accepted
- Negative marks rejected
- Marks greater than 100 rejected
- Blank marks rejected
- Text values rejected
- NaN rejected
- Infinity rejected
- Blank names rejected
- Spaces-only names rejected
- No valid records handling
- Summary calculation validation

## Validation Rules

### Student Name

Accepted:
- Non-empty names

Rejected:
- Blank names
- Names containing only spaces

### Marks

Accepted:
- Numeric values
- Decimal values
- Values from 0 to 100 inclusive

Rejected:
- Blank marks
- Text values
- NaN
- Infinity
- Values below 0
- Values above 100

## Module 3 Refactoring

The program was reorganized into separate functions:

- `validate_record()`
- `read_csv()`
- `calculate_summary()`
- `display_results()`

The application entry point remains in:

```python
if __name__ == "__main__":
    main()
```

This allows functions to be imported into test files without automatically executing the program.

## Testing Process

To verify the tests work correctly:

1. Changed pass rule from:

```python
mark >= 40
```

to:

```python
mark > 40
```

2. Ran tests and confirmed the 40-mark test failed.

3. Restored the correct implementation.

4. Re-ran all tests and confirmed all tests passed.

## Time Spent

Approximately 2-3 hours.


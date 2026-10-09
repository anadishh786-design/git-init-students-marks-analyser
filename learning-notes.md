# Module 4 Learning Notes

## Stage 1 — Prepare and understand the project

### Key functions

- `read_csv()` reads the CSV file and validates each row.
- `validate_record()` rejects invalid rows such as blank names, blank marks, non-numeric values, NaN, infinity, and out-of-range marks.
- `calculate_summary()` calculates the pass/fail totals, average, and highest scorer.
- `display_results()` prints the student results and summary to the terminal.
- `main()` connects the flow by parsing arguments, reading the CSV, calculating the summary, displaying results, and exporting reports.

### Trace value 82.5 through the program

The value starts as text inside the CSV file, for example `"82.5"` in `sample_students.csv`.

1. `read_csv()` reads each row and extracts the `marks` value as a string.
2. That string is passed to `validate_record()`.
3. `validate_record()` does `score = float(mark)`, converting the text to a numeric float.
4. The float `82.5` is then stored in the valid student dictionary as `{"name": "Cara", "mark": 82.5}`.
5. `calculate_summary()` uses that numeric value for pass/fail checks and the average calculation.

This is the point where the value changes from text to a number.

---

## Stage 2 — Predictions before running

### Sample data

```csv
name,marks
Asha,39
Ben,40
Cara,82.5
Noor,abc
,70
Zoya,105
```

### My predictions

1. Accepted rows:
   - Asha, 39
   - Ben, 40
   - Cara, 82.5

2. Rejected rows:
   - Noor, abc -> rejected because the mark is not numeric.
   - blank name, 70 -> rejected because the name is blank.
   - Zoya, 105 -> rejected because the mark is above 100.

3. Pass count at threshold 40:
   - Ben = 40 -> pass
   - Cara = 82.5 -> pass
   - Asha = 39 -> fail
   - total passes = 2

4. Pass count at threshold 50:
   - Ben = 40 -> fail
   - Cara = 82.5 -> pass
   - Asha = 39 -> fail
   - total passes = 1

5. Average and highest score:
   - Valid marks: 39 + 40 + 82.5 = 161.5
   - Average = 161.5 / 3 = 53.833...
   - Highest score = 82.5 (Cara)

### Actual results after running

For threshold 40:

- Accepted: Asha, Ben, Cara
- Rejected: Noor, blank name, Zoya
- Pass count = 2
- Fail count = 1
- Average = 53.83
- Highest score = 82.5 (Cara)

For threshold 50:

- Pass count = 1
- Fail count = 2
- Average is still 53.83
- Highest score remains 82.5 (Cara)

### Correction

My original prediction was correct for the sample data. The only thing to remember is that invalid rows are rejected before the summary is calculated, so they do not affect the valid-student totals or average.

---

## Stage 3 — Command-line options

The project uses `argparse` with:

- `--input` default `students.csv`
- `--output-dir` default `reports`
- `--pass-mark` default `40`

The threshold is passed through the program flow so that any pass/fail checks in `calculate_summary()` and `display_results()` use the selected value.

The rule is: marks equal to the threshold count as a pass.

Example run:

```bash
python main.py --input sample_students.csv --output-dir reports --pass-mark 50
```

This was checked against the sample predictions and the results matched the expected pass/fail totals.

---

## Stage 4 — File paths and execution

### Why a file beside the script may still be “not found”

If the terminal is not currently running inside the project folder, relative paths are resolved from the current working directory, not from the directory containing the script. That means a file like `sample_students.csv` may be missing unless the path is written relative to the working directory.

### Why a selected line may cause an undefined-variable error

If I run only a single line or a partial block of code from the editor, variables created earlier in the script may not exist in that context. This is why the program should be executed as a full script, not as disconnected snippets.

### Header validation

The CSV must contain the required headers `name` and `marks`. Header names are normalised by stripping whitespace and converting to lowercase before checking.

If the file is missing or the headers are wrong, the program raises a useful error and exits without creating reports.

A header-only CSV is allowed. In that case the counts are zero and the average/highest scorer are shown as `N/A`.

---

## Stage 5 — Exporting reports

`export_reports()` creates the output directory, writes `results.csv`, and writes `summary.json` with the selected threshold and summary values.

### `results.csv`

Contains only valid students in original input order, with columns:

- name
- marks
- status

### `summary.json`

Contains:

- valid_count
- invalid_count
- pass_count
- fail_count
- pass_mark
- average
- highest_scorer

The highest scorer is stored as an object with `name` and `marks`. If there is a tie, the first matching student is kept.

If no valid students exist, the CSV is header-only and the JSON uses `null` for average and highest scorer.

Repeated runs overwrite the output rather than appending duplicate rows.

---

## Stage 6 — Tests and deliberate-bug exercise

The tests were written to check:

- default and custom CLI arguments
- invalid pass thresholds
- threshold equality rules
- valid and invalid mixed rows
- missing files and header problems
- header-only CSV input
- exported CSV and JSON contents
- repeated run behavior
- end-to-end script execution with `subprocess.run()`

### Test-file history

At commit `ff408cb`, `main.py` and `test_main.py` contained identical application code. The commit changed only the GitHub Actions workflow, and its parent already had the duplicate. Later commits restored `test_main.py` as a unittest module. The available history does not identify the exact edit that copied the application into the test file, so the cause cannot be determined more precisely.

### Deliberate-bug run

From the repository root, `python -m unittest discover -v` ran 29 tests successfully. I temporarily changed the summary comparison from `>=` to `>` and ran the same command. These tests failed:

- `test_summary_values`: expected 2 passes, got 1 (`AssertionError: 1 != 2`).
- `test_threshold_40_passes`: expected 1 pass, got 0 (`AssertionError: 0 != 1`).

I restored `>=` and reran discovery. All 29 tests passed (`Ran 29 tests`, `OK`).

---

## Stage 7 — GitHub and workflow organisation

The project should keep the code, tests, README, and learning notes on the same module branch. Before each commit, `git status` and `git diff` should be checked, then the relevant files staged and reviewed with `git diff --staged`.

Generated folders such as `reports/` and `__pycache__/` should be added to `.gitignore`.

A GitHub Actions workflow is used to run:

```bash
python -m unittest discover -v
```

on push and pull request events.

---

## Stage 8 — README and fresh-copy check

The README includes:

- Python version
- the repository URL, folder name, and working branch checkout command
- commands to run the script and tests
- input format
- output file names and formats
- example results
- common errors and fixes

The fresh-copy check will be recorded after cloning the pushed branch into a separate folder and following these README commands.

---

## Final answers

1. What did I predict incorrectly, and why?
   - I did not predict incorrectly in this sample. The predictions matched the actual results, because the invalid rows were correctly excluded before the summary was calculated.

2. Which test caught the deliberate bug?
   - `test_summary_values` and `test_threshold_40_passes` failed when `>=` was changed to `>`, with pass-count assertions of `1 != 2` and `0 != 1` respectively. Both passed after restoring `>=`.

3. What does the end-to-end test check that a calculation test cannot?
   - It checks the actual script execution flow, file creation, command-line arguments, exit status, and output produced by running the real program, not just function-level calculations.

4. How did I confirm the PR contains the complete project?
   - This will be recorded after the fresh-copy check and PR review are complete.

5. What problem did the fresh-copy check uncover?
   - This will be recorded after running the README instructions in the fresh clone.

---

## Actual sample result

When run with the provided sample file and the default pass threshold of 40, the program outputs:

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

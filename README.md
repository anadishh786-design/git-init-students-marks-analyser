# Student Reporting Tool (Module 6)

A Python command-line application that validates student marks, calculates reports, and stores each analysis in SQLite for later retrieval. `main.py` remains the Module 4 CSV reporting command; `tracker.py` adds saved analysis history and export.

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
git clone https://github.com/anadishh786-design/git-init-students-marks-analyser.git
```

Move into the project directory:

```bash
cd git-init-students-marks-analyser
```

Switch to the Module 5 branch:

```bash
git switch module-6-http-api
```

---

# Project Structure

```text
git-init-students-marks-analyser/
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── main.py
├── tracker.py
├── api.py
├── test_main.py
├── test_tracker.py
├── test_api.py
├── requirements.txt
├── students.csv
├── sample_students.csv
├── learning-notes.md
├── module-5-notes.md
├── README.md
├── .gitignore
│
├── data/       (created when a database is first saved; database files are ignored)
└── reports/    (generated reports are ignored)
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
- Saves analyses and retrieves them from SQLite
- Lists analysis history and exports saved analyses
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

Install the API dependency:

```bash
python -m pip install -r requirements.txt
```

Run all tests:

```bash
python -m unittest discover -v
```

Run a specific file:

```bash
python -m unittest -v test_main.py
python -m unittest -v test_tracker.py
python -m unittest -v test_api.py
```

---

# Module 6: HTTP API

Start the local API server:

```bash
python -m flask --app api run --host 127.0.0.1 --port 5000
```

The SQLite database defaults to `instance/analyses.db`. Importing `api.py` does not start the server or create a database. The API provides:

- `GET /health` returns `{"status":"ok"}`.
- `GET /analyses` returns saved analyses newest first.
- `POST /analyses` saves an analysis and returns HTTP 201 with its database ID.
- `GET /analyses/<id>` returns one saved analysis, its students, and its calculated summary.

Create an analysis from PowerShell:

```powershell
$body = '{"pass_mark":50,"students":[{"name":"Asha","marks":39},{"name":"Ben","marks":40},{"name":"Cara","marks":82.5}]}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/analyses -ContentType 'application/json' -Body $body
```

All errors return JSON shaped as `{"error":{"code":"...","message":"..."}}`. Invalid JSON, request structure, or pass marks return HTTP 400; requests without a JSON content type return 415; an unknown analysis ID returns 404. Invalid student values are skipped and counted, while malformed request structure saves nothing. Full endpoint examples and response details are in [module-6-notes.md](module-6-notes.md).

---

# Module 7: Browser Dashboard

Start the local dashboard and API from the repository root:

```bash
python -m flask --app api run --host 127.0.0.1 --port 5000
```

Open <http://127.0.0.1:5000/> in a browser. Enter a passing threshold and student names and marks, then choose **Save analysis**. Invalid student records are skipped and counted; the saved analysis and its results appear in the history and results sections. Choose **View** on any history row to reopen its saved results. Refreshing the page reloads history from SQLite.

The dashboard and JSON API use the same Flask server. Browser-side checks improve feedback, while the API continues to validate every request. The database defaults to `instance/analyses.db`; see [module-7-notes.md](module-7-notes.md) for the browser test record.

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

This project uses Python 3.11 and the standard library. SQLite databases, generated reports, and Python caches are excluded from Git by `.gitignore`.

---

# Module 5: Saved Analysis History

`tracker.py` saves each CSV analysis in SQLite while `main.py` continues to provide the original Module 4 workflow.

The database has two tables:

- `analyses` stores the UTC creation time, source path, selected pass mark, and invalid-row count.
- `student_results` stores each accepted student's name and numeric mark, linked to one analysis by `analysis_id`. One analysis has many student rows; separate rows preserve repeated names and input order.

Pass/fail counts, averages, and statuses are calculated when an analysis is displayed or exported. They are not stored.

Save an analysis:

```bash
python tracker.py --db data/analyses.db analyse --input sample_students.csv --pass-mark 50
```

List saved analyses, newest first:

```bash
python tracker.py --db data/analyses.db history
```

Display one saved analysis without reading the original CSV:

```bash
python tracker.py --db data/analyses.db show --id 1
```

Display and export a saved analysis in the Module 4 CSV and JSON formats:

```bash
python tracker.py --db data/analyses.db show --id 1 --output-dir reports/saved-1
```

Database parent folders are created as needed. `analyse` validates the input file before creating the database, then saves an analysis and all valid student rows in one transaction.

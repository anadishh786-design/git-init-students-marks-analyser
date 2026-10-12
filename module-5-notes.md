# Module 5 Notes

## Stage 1: Baseline evidence

- Starting point: accepted Module 4 commit `e46a1e6` on `module-4-cli-reports`.
- Working branch: `module-5-sqlite-history`, tracking the remote branch at the same Module 4 commit.
- Baseline command: `python -m unittest test_main -v`.
- Baseline result: 31 tests passed.
- `main.py` has not been changed, so the Module 4 command remains as it was.

## Stage 2: Decisions and evidence

- `connect_db` creates the database parent directory, returns a standard SQLite connection, and enables foreign keys for that connection.
- `initialise_db` uses `CREATE TABLE IF NOT EXISTS`; the analysis row stores the import metadata and threshold, while student rows reference it with `ON DELETE CASCADE`.
- `student_results` is a separate table because one analysis contains many students. A foreign key associates each student row with exactly one analysis, allowing each import to retain its own source metadata and threshold without duplicating that data for every student.
- Names must contain a non-whitespace character. Thresholds and marks must be numeric values from 0 through 100.
- Counts, averages, and pass/fail outcomes are not stored; they can be derived later from student marks and the saved threshold.
- The preliminary database suite initially found that three tests left cursors open during temporary-directory cleanup on Windows. Closing those cursors before their connections resolved the file-lock failures.
- After that correction, `python -m unittest test_tracker -v` passed all 8 Stage 2 database tests, including numeric-type rejection.
- Full verification: `python -m unittest discover -v` passed all 39 tests (31 Module 4 and 8 Stage 2).

## Stage 3: Analyse checkpoint

The sample has 6 data rows: Asha (39), Ben (40), Cara (82.5), Noor (`abc`), a blank name (70), and Zoya (105). Three rows should be accepted and three rejected.

Prediction, recorded before running the sample command: importing it twice with threshold 50 creates 2 rows in `analyses`, each with the sample path, threshold 50, and `invalid_count` 3. It creates 6 rows in `student_results`: Asha (39), Ben (40), and Cara (82.5), in that order for each distinct analysis ID.

Actual command: `python tracker.py --db <temporary>/analyses.db analyse --input sample_students.csv --pass-mark 50`, run twice.

Actual output from the first run:

```text
Saved analysis ID: 1
Valid Rows: 3
Invalid Rows: 3
Passes: 1
Fails: 2
Average: 53.83
Highest Scorer: Cara (82.5)
```

The second run printed the same summary with `Saved analysis ID: 2`. Querying the temporary database returned:

```text
analyses: [(1, 'sample_students.csv', 50.0, 3), (2, 'sample_students.csv', 50.0, 3)]
students: [(1, 'Asha', 39.0), (1, 'Ben', 40.0), (1, 'Cara', 82.5), (2, 'Asha', 39.0), (2, 'Ben', 40.0), (2, 'Cara', 82.5)]
```

Input parsing and validation happen before connecting to the database. `save_analysis` inserts the analysis row and student rows inside `with connection:`. SQLite commits when the block exits normally and rolls back if an insert raises, so a partially saved analysis cannot remain.

Final test command: `python -m unittest discover -v`; 45 tests passed (31 Module 4 and 14 database/CLI tests).
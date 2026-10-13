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

- Checkpoint 1 commit: `5fc7137` (`Add SQLite analysis command`), built directly on the accepted Module 4 commit.

The sample has 6 data rows: Asha (39), Ben (40), Cara (82.5), Noor (`abc`), a blank name (70), and Zoya (105). Three rows should be accepted and three rejected.

Prediction, recorded before running the sample command: importing it twice with threshold 50 creates 2 rows in `analyses`, each with the sample path, threshold 50, and `invalid_count` 3. It creates 6 rows in `student_results`: Asha (39), Ben (40), and Cara (82.5), in that order for each distinct analysis ID.

Actual command: `python tracker.py --db <temporary>/analyses.db analyse --input sample_students.csv --pass-mark 50`, run twice.

Actual output from the first run:

```text
Rejected row: {'name': 'Noor', 'marks': 'abc'} -> Non-numeric mark
Rejected row: {'name': '', 'marks': '70'} -> Blank name
Rejected row: {'name': 'Zoya', 'marks': '105'} -> Mark out of range
Saved analysis ID: 1

Student Results
----------------------------------------
Asha : 39.0 - Fail
Ben : 40.0 - Fail
Cara : 82.5 - Pass

Valid Rows: 3
Invalid Rows: 3
Passes: 1
Fails: 2
Average: 53.83
Highest Scorer: Cara (82.5)
```

The rejected-row messages appear first because `read_csv` prints them while validating the input, before `main` opens the database. The ID and results are printed after the transaction succeeds. The second run has the same output except its saved ID is 2. IDs start at 1 here because this was a new temporary database; an existing database can produce higher IDs.

Querying the temporary database returned:

```text
analyses: [(1, 'sample_students.csv', 50.0, 3), (2, 'sample_students.csv', 50.0, 3)]
students: [(1, 'Asha', 39.0), (1, 'Ben', 40.0), (1, 'Cara', 82.5), (2, 'Asha', 39.0), (2, 'Ben', 40.0), (2, 'Cara', 82.5)]
```

Input parsing and validation happen before connecting to the database. `save_analysis` inserts the analysis row and student rows inside `with connection:`. SQLite commits when the block exits normally and rolls back if an insert raises, so a partially saved analysis cannot remain.

Final test command: `python -m unittest discover -v`; 45 tests passed (31 Module 4 and 14 database/CLI tests).

## Stage 4: History and retrieval

- `history` displays analysis ID, UTC timestamp, source path, saved threshold, valid count, and invalid count, ordered newest first. It reports a clear empty state and refuses a missing database without creating it.
- `show` loads the selected analysis and student rows ordered by their inserted row IDs, then recalculates the summary with that analysis's saved threshold.
- Saved results survive changes or deletion of the original CSV because accepted names and marks, threshold, and invalid-row count are persisted in SQLite. Retrieval reads only those saved values; it does not reopen the source path.
- Missing databases and unknown analysis IDs produce a useful error and non-zero exit status.

## Stage 5: Export evidence

- `show` displays saved results without exporting unless `--output-dir` is supplied. With an output directory, it reuses `main.export_reports`, preserving the Module 4 `results.csv` and `summary.json` formats.
- End-to-end evidence: two imports of the same three accepted rows were saved with pass marks 50 and 75. The source CSV was then changed and deleted. Showing IDs 1 and 2 still displayed the original names and marks. Exported CSV statuses were respectively `Fail, Pass, Pass` and `Fail, Fail, Pass`; their JSON summaries retained pass marks 50 and 75 and pass counts 2 and 1.

## Stage 6: Test evidence

- Added temporary-database tests for repeat initialization, decimal marks, separate analyses and thresholds, duplicate names and original order, invalid files and thresholds, header-only input, missing databases and IDs, deleted source CSVs, CSV/JSON export content, and transaction rollback after a deliberate student constraint violation.
- The end-to-end subprocess test runs `analyse`, deletes the input CSV, runs `show --output-dir`, and reads both exported files.
- `python -m unittest discover -v` passed the complete suite: 51 tests (31 Module 4 and 20 Module 5). The final submission commit is reported with the delivery.

## Design questions

- SQL placeholders pass supplied values as data, not SQL syntax; they prevent injection and quoting errors.
- Without a transaction, an insertion failure after the analysis row could leave an analysis with only some or none of its student rows.
- `show` must use the saved threshold because it defines pass/fail status for that historical analysis. Using a current default could change the displayed result.
- `test_show_exports_saved_results_after_input_csv_is_deleted` proves persistence across input deletion: it removes the CSV, invokes `show`, and inspects both report files.
- Final review finding: each retrieval must use the threshold attached to that analysis rather than the current CLI default. The show output exposes that threshold, and the two-threshold export test verifies independent outcomes.

## Submission record

- Time spent: approximately 50 minutes, estimated retrospectively; it was not timed during the work.
- Assistance used: GitHub Copilot for implementation, tests, documentation, and validation; no external contributors.
- Pushed branch: `module-5-sqlite-history`; implementation commit: `f594f1a`; final commit before this submission-record update: `1999a73`.
- Pull request: [#7](https://github.com/anadishh786-design/git-init-students-marks-analyser/pull/7), targeting `module-4-cli-reports`; it remains open and unmerged.
- GitHub Actions push run for `1999a73`: [Run 33 passed](https://github.com/anadishh786-design/git-init-students-marks-analyser/actions/runs/38419190432).
- Fresh-clone verification at `1999a73` passed all 51 tests.
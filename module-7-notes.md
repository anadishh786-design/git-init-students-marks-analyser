# Module 7: Browser Dashboard (Stage 1)

## Planned layout

```text
-------------------------------------------------
Student Analysis Dashboard
-------------------------------------------------

[ New Analysis Form ]
Passing Threshold: [40]
Name        Marks      Action
[          ] [        ] Remove
[          ] [        ] Remove
[          ] [        ] Remove
+ Add Student
[ Save Analysis ]

-------------------------------------------------
[ Saved Analysis History ]
ID     Date      Threshold   Action
...                         View

-------------------------------------------------
[ Selected Analysis Results ]
Analysis ID:        Threshold:
Students:
Name      Marks      Status
Average:             Highest Scorer:
Valid:               Invalid:
-------------------------------------------------
```

The page is organized into the three requested areas: a new-analysis form, saved-analysis history, and selected-analysis results. This text wireframe records the paper-sketch plan for the implementation.

## Save flow

User clicks Save → JavaScript sends JSON → Flask validates → SQLite saves → browser displays the response

The browser will provide immediate feedback, but the Flask API remains responsible for validation and persistence. Client-side checks can be bypassed, so they cannot replace server-side validation.

## Stage 1 baseline

- Starting point: accepted Module 6 branch `module-6-http-api`, commit `baf2370` (`Handle overflowing student marks in API`).
- Stage 1 branch: `module-7-browser-dashboard`.
- The existing `unittest discover` suite was run on this checkout. Module 6 acceptance notes report 66 passing tests; this run showed passing test output, but the terminal view cut off before the final count line.
- Existing unrelated untracked files were left unchanged.

## Stage 1 completion

- [x] Started from the accepted Module 6 commit and created the `module-7-browser-dashboard` branch.
- [x] Ran the existing test suite; Module 6 records 66 passing tests. The current run's final summary was not visible in the terminal output.
- [x] Created `templates/index.html`, `static/styles.css`, and `static/app.js`.
- [x] Created this notes file with the three-area layout sketch and required save-flow explanation.
- [x] Kept the existing CLI and API implementation unchanged.

## Browser test record

The end-to-end browser scenarios belong to the later implementation and demonstration stages. Stage 2 page and responsive checks are recorded below.

## Stage 2: Serve the dashboard

- Added `GET /` to render `templates/index.html`; API routes remain on the same Flask app.
- The template links `static/styles.css` and `static/app.js` through Flask's `url_for('static', ...)` URLs.
- Started the documented command: `python -m flask --app api run --host 127.0.0.1 --port 5000`.
- Opened `http://127.0.0.1:5000/` in the browser. The dashboard title, all three sections, tables, and empty states rendered.
- At a 375px viewport, the stylesheet loaded, all three sections were present, and document width was 360px (no horizontal overflow).
- `test_api.TestAnalysisAPI.test_dashboard_and_static_assets` passed, including requests for `/`, `/static/styles.css`, and `/static/app.js`.
- The page remains on the same Flask server as the API; the existing API routes are unchanged.

## Stage 3: Analysis form

- The passing threshold starts at 40 and is checked in JavaScript for blank, non-finite, and out-of-range values.
- Three empty name/marks rows render initially. Add student creates rows; every row has a Remove control.
- Rows are gathered in their visible order. The threshold becomes a number; student names and marks remain strings so blank marks stay blank.
- The form explains that invalid student records are skipped and counted.
- Stage 4 connects the form to the API. Server-side API validation remains authoritative.

## Checkpoint 1 evidence

- Commit ID: included in the checkpoint handoff.
- Form screenshot: captured from the running local dashboard and attached with the checkpoint handoff.
- Browser row check: 3 initial rows, 4 after Add student, and 3 after removing the newly added row.
- Browser threshold checks: blank and 101 were rejected; 40 was accepted.
- Collection check: `pass_mark` is numeric; `marks` remains a string, including an empty string; the name `<b>Ann</b>` remains literal input text.
- Browser validation cannot replace API validation because requests can bypass the page or alter its JavaScript. Flask must independently validate every request before storing it.
- Automated verification: `python -m unittest discover -v` passed all 67 tests.

## Stage 4: Save through the API

- Save sends one `POST /analyses` request with `Content-Type: application/json` and `JSON.stringify()` data. The threshold is numeric and marks stay strings.
- The Save button shows `Saving…` and is disabled while the request is pending. A second submission during that request is ignored; a browser check observed one POST call for two rapid submissions.
- A confirmed successful response displays the analysis ID and valid/invalid counts, shows a warning for skipped records, fetches the saved result, refreshes history, and then resets the form.
- A real browser submission saved analysis ID 4: threshold 42, one valid student (`Keep Me`, 88), and two skipped blank-mark rows. History refreshed and the saved result was fetched and displayed.
- Opening existing analysis ID 3 displayed threshold 40, Asha and literal `<b>Ann</b>`, average `55.00`, and counts of two valid and one invalid record. The name appeared as text, not bold HTML.
- A simulated HTTP 400 displayed its status/message, retained the entered fields, and re-enabled Save.
- A simulated connection failure displayed that the outcome is unknown, retained the entered fields, re-enabled Save, and did not retry. The user is directed to check history before retrying.
- Both failure cases and the double-submit check used an in-page fetch mock; they did not issue extra POST requests to Flask.

## Stage 5: History and saved results

- On page load, the browser requests `GET /analyses` and displays rows in API order with ID, created time, saved threshold, valid count, invalid count, and View.
- View requests `GET /analyses/<id>` and displays the saved threshold, each student's name/marks/status, counts, average to two decimals, and highest scorer.
- Null average and highest scorer render as `N/A`; an empty student list renders a clear empty-result row.
- Student names are assigned with `textContent`. Viewing analysis 3 showed `<b>Ann</b>` as literal text with no `<b>` element in the result table.
- The real saved analyses at thresholds 40 and 50 demonstrate different statuses for Ben's mark of 40: Pass at 40, Fail at 50.
- Browser checks confirmed history loading, empty, and HTTP error messages; after the simulated states, history successfully reloaded all four saved records.
- A delayed old result request and a faster new selection completed with only the new selection rendered, confirming the request counter prevents stale results from replacing it.

## Checkpoint 2 evidence

- Saved analyses at thresholds 40 and 50 were opened from history. Ben (40 marks) displayed Pass at threshold 40 and Fail at threshold 50.
- Reloading the dashboard fetched the existing history from SQLite, including analyses 1 through 4.
- Saving analysis 4 visibly reported two skipped invalid records; the retrieved summary showed one valid and two invalid.
- An actual browser POST redirected to `/no-such-checkpoint-endpoint` returned HTTP 404. The dashboard displayed the HTTP error, retained threshold/name/marks, and re-enabled Save; history did not gain a record.
- Separate in-page fetch mocks covered the connection failure and rapid double-submit behavior without creating database records.
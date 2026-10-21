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
- Saving is not connected yet; that is Stage 4. Server-side API validation remains authoritative.

## Checkpoint 1 evidence

- Commit ID: included in the checkpoint handoff.
- Form screenshot: captured from the running local dashboard and attached with the checkpoint handoff.
- Browser row check: 3 initial rows, 4 after Add student, and 3 after removing the newly added row.
- Browser threshold checks: blank and 101 were rejected; 40 was accepted.
- Collection check: `pass_mark` is numeric; `marks` remains a string, including an empty string; the name `<b>Ann</b>` remains literal input text.
- Browser validation cannot replace API validation because requests can bypass the page or alter its JavaScript. Flask must independently validate every request before storing it.
- Automated verification: `python -m unittest discover -v` passed all 67 tests.
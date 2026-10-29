# Module 9: Find Students Near Passing

## Rule

For the selected saved analysis, include marks in `saved pass mark − 5 ≤ marks < saved pass mark`. At 60: 54.9 is excluded, 55 is included, 58 is included, 59.9 is included, and 60 is excluded. The filter uses the selected analysis's saved threshold, not the new-analysis form. This highlights students near passing for support planning; it does not predict whether they will pass.

Control label: **Show students within 5 points below passing**.

## Search and awkward cases

Name search and the checkbox combine with AND. Clearing the name query while the checkbox is on shows every near-pass student. With no qualifying students, the dashboard reports that none are within 5 points below passing. Decimal marks use the same inclusive lower and exclusive upper boundaries. Selecting another analysis applies that analysis's saved pass mark.

## Short browser demonstration

Open an analysis saved with threshold 60 and students Alex (54.9), Asha (55), Arjun (58), Aria (59.9), and Ben (60). Check the new control: Asha, Arjun, and Aria remain. Search `ar` with the control on: only Arjun and Aria remain. Clear the search: all three near-pass students return. Turn the control off: all five return. While viewing this analysis, change the new-analysis form threshold to 90; the selected analysis still displays and filters by its saved threshold of 60.

This is the reproducible browser demonstration sequence. An updated GIF recording is not included: Chrome's local remote-control session did not respond to page commands in this environment.

## Expected and actual results

| Check | Expected | Actual |
| --- | --- | --- |
| Threshold 60 boundaries | 54.9 out; 55, 58, 59.9 in; 60 out | Focused test confirms all five outcomes. |
| No qualifying students | No rows match; an explanatory status appears | Focused test confirms no rows and “No students are within 5 points below passing.” |
| Different saved threshold | Results use the selected analysis threshold | Focused test evaluates the rule at 60 and 90; UI uses the selected analysis's `pass_mark`. |
| Search plus checkbox | Both conditions must match | Focused test confirms AND behavior; browser sequence above exercises `ar` with the checkbox active. |

## Limitation and assistance

The five-point window is a simple way to flag nearby scores; it does not account for subject difficulty or predict outcomes. After Step 1 was accepted, AI assistance helped implement the filter, write focused tests, and draft these notes.

`node --test test_dashboard_search.js`: 4 tests passed. `.venv\Scripts\python.exe -m unittest discover -v`: all 68 tests passed. CI runs the Node test file after the Python suite.

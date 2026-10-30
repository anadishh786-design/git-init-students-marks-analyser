# Module 10: Can Your Tests Catch a Bug?

## Starting point

Created `module-10-debugging-check` from `module-9-support-filter`. Before edits:

- `node --test test_dashboard_search.js`: 4 passed.
- `.\\.venv\\Scripts\\python.exe -m unittest discover -v`: 68 passed.

## Deliberate mistakes

1. Changed the near-pass upper bound from `< pass mark` to `<= pass mark`. The existing `near-pass filter includes the lower bound and excludes passers` test should fail because a student at exactly 60 would incorrectly qualify at a saved threshold of 60. It failed (`true !== false`); the empty-result test also failed because the 60-mark passer appeared in the result.
2. Changed the dashboard filter to read the new-analysis form's threshold. Existing tests stayed green (4 passed), because they test the calculation helper with explicit arguments and never exercise the dashboard's saved-analysis loading and filtering event flow. The new dashboard test failed: with a saved threshold of 60 and form threshold of 90, it found no students instead of Asha (55) and Arjun (58).

Both temporary mistakes were restored before committing.

## Dashboard regression test

`test_dashboard_filter.js` runs the actual dashboard scripts in Node with small simulated page elements and mocked API responses. It loads a saved analysis, changes the new-analysis form threshold, activates the near-pass control, and asserts that only students in the saved analysis's 55–60 window remain visible. It runs as a separate GitHub Actions step.

## Final verification

- `node --test test_dashboard_search.js`: 4 passed.
- `node --test test_dashboard_filter.js`: 1 passed.
- `.\\.venv\\Scripts\\python.exe -m unittest discover -v`: 68 passed.

AI assistance was used to inspect the code, write the dashboard test and notes, and run the requested temporary mutation checks.

If every test passes, we can confidently claim that the checked behaviors match their tested expectations for the cases and environment covered. We still need to check untested behavior, real browser rendering and interaction, and integration conditions that the tests do not model.

## Browser demonstration attempt

Prepared a separate local demo database at `instance/module10-demo.db` with analysis ID 1, saved threshold 60, and Asha (55), Arjun (58), Aria (59.9), Ben (54.9), and Bea (60). The Flask server returned HTTP 200 from `/health`; `/analyses/1` returned all five records and the saved threshold of 60. This confirms the demo data is ready.

I attempted to open the dashboard in Chrome, but the computer-use session exited before I could inspect or operate the page (`trusted Node process exited unexpectedly`). Therefore I did not observe the requested filter/search sequence in a real browser, and no screen recording is attached. The UI sequence and recording still need to be captured manually at `http://127.0.0.1:5000/` while the local server is running. The scripted dashboard test passes, but it is not a substitute for that browser demonstration.

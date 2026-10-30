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

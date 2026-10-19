# Module 6: HTTP API for Saved Analyses

## Request flow

An HTTP request reaches a registered route, the route validates the request data, valid analysis data is saved to or read from SQLite, and the route returns a JSON response with an HTTP status code.

- **Route:** A URL pattern and handler that decide what application code runs for a request.
- **Request method:** The HTTP operation, such as GET to retrieve data or POST to submit data.
- **JSON:** A text format for structured values that clients and servers can exchange.
- **Status code:** The numeric HTTP result that tells a client whether a request succeeded or why it failed.
- **Request body:** The data sent with a request, commonly used by POST to submit an analysis.

## Local setup and server

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m flask --app api run --host 127.0.0.1 --port 5000
```

The database defaults to `instance/analyses.db`. Each request initializes the schema if needed. Tests pass a temporary path through `DATABASE`; importing `api.py` alone does not create the database or start a server.

## Endpoints

- `GET /health` returns `{"status":"ok"}`.
- `GET /analyses` lists saved analyses, newest first.
- `POST /analyses` creates an analysis from JSON and returns its database ID.
- `GET /analyses/<id>` returns saved students and a summary calculated with that analysis's stored pass mark.

Example PowerShell requests, with `Content-Type: application/json`:

```powershell
$body40 = '{"pass_mark":40,"students":[{"name":"Asha","marks":39},{"name":"Ben","marks":40},{"name":"Cara","marks":82.5}]}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/analyses -ContentType 'application/json' -Body $body40

$body50 = '{"pass_mark":50,"students":[{"name":"Asha","marks":39},{"name":"Ben","marks":40},{"name":"Cara","marks":82.5}]}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/analyses -ContentType 'application/json' -Body $body50

Invoke-RestMethod -Method Get -Uri http://127.0.0.1:5000/analyses
Invoke-RestMethod -Method Get -Uri http://127.0.0.1:5000/analyses/1
```

The sample has three valid students and an average of about 53.83. At threshold 40, Ben and Cara pass (2 passes, 1 fail); at threshold 50, only Cara passes (1 pass, 2 fails). Cara is the highest scorer at either threshold.

Errors use `{"error":{"code":"...","message":"..."}}`. Invalid JSON, threshold values, or request structure return 400; a non-JSON content type returns 415; an unknown analysis ID returns 404. Rejected requests are validated before any analysis is saved.

An invalid `pass_mark` rejects the whole request because the threshold configures how every valid student's result is classified; the analysis cannot be interpreted consistently without it. A student's invalid mark affects only that record, so the API skips that student, increments `invalid_count`, and continues saving any valid students. Numeric conversion overflow is also treated as an invalid student mark.

## Verification

`test_saved_thresholds_are_independent` in `test_api.py` asserts that each saved analysis uses its own threshold and would fail if retrieval were changed to hardcode 40: for the threshold-50 analysis, Ben must be a fail and the pass count must be 1, not 2. During the deliberate regression run, that test failed at the threshold-50 pass-count assertion with `AssertionError: 2 != 1`. The stored-threshold implementation was restored and the same test passed.

`test_second_application_instance_reads_persisted_results` proves that results remain available to a new application instance opening the same database. Separate temporary database paths are tested for isolation.

The overflow regression first failed before the fix with `OverflowError: int too large to convert to float`. After treating `OverflowError` as an invalid mark, both the API test and direct validator test pass; the complete suite passes all 66 tests.

## Reflection

- Browsers can open a GET URL directly because GET retrieves a resource; creating an analysis sends structured data and changes saved state, so it uses POST.
- An API returns JSON because another program can parse structured values; printed terminal output is not a reliable response channel for an HTTP client.
- A rejected request must leave no saved analysis so invalid input cannot create partial or misleading records.
- Configurable database paths let tests use isolated temporary databases without touching real user data.
- `test_second_application_instance_reads_persisted_results` proves saved results survive an application restart/recreation.
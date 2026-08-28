# Tests

This directory contains integration and end-to-end tests that exercise the
Sentimenta system as a whole. Unit tests for individual components live
alongside their source code:

- `backend/tests/` -- unit and API-level tests (model stubs, FastAPI
  TestClient).
- `frontend/src/**/*.test.tsx` -- component and hook tests (Vitest + React
  Testing Library).
- `tests/` (this directory) -- cross-layer integration tests and fixtures
  that require both backend and frontend to be running.

## Running

```bash
# Integration tests (requires the backend server running on port 8000)
cd tests
pytest -v

# With real model inference (downloads ~500 MB on first run)
pytest -v --runmodel
```

## Fixtures

The `fixtures/` subdirectory holds shared test data used by integration tests
and CI. See individual fixture files for their schema and usage.

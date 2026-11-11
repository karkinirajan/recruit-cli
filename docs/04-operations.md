# 04. Operations

## Running

| Command | Does |
|---|---|
| `pipx install recruit-cli` (or `uv tool install`, `pip install`) | Install the published package |
| `recruit-cli setup-notion` | One time: share the database with the integration first, then add the properties |
| `recruit-cli process CVS/ JD.pdf` | Screen a folder; exit code 1 if any CV failed |
| `uv sync && uv run recruit-cli ...` | Run from a checkout |

## Settings

| Variable | |
|---|---|
| `GOOGLE_GEMINI_API_KEY`, `NOTION_API_KEY`, `DEFAULT_NOTION_DB_ID` | Required (or `--notion-db-id`) |
| `GEMINI_MODEL` | Optional; default `gemini-3.8-flash`. Google retires models regularly, so a `404 ... model` error means set this to a current one |
| `NOTION_DATA_SOURCE_ID` | Only for a Notion database with more than one data source |

They are read from the environment and from a `.env` file in the working directory (or a parent); the environment wins.

## Before relying on this

1. **Run it once on a few CVs against a test database**: the Gemini model name and the Notion data-source requests were checked against documentation and the SDK, not
   against the live services.
2. A person should review the scores. The tool derives the category from the score and validates it, but a model can be wrong or be talked into a high score.
3. Personal data goes to Google and Notion (see [02 Security](02-security.md)).

## CI

`.github/workflows/ci.yml` runs on every push to `master` and every pull request, on Python 3.11, 3.12, 3.13 and 3.14:

1. `uv sync --locked` (fails if `uv.lock` is stale), then a check that the job really runs the Python it is named after (`UV_PYTHON` is set per job;
   without it `uv run` switched back to `.python-version`).
2. `ruff check`, `pytest`.
3. Once, on 3.14: `uv audit`, `uv build`, and installing the built wheel in a clean environment to run `recruit-cli --version` and `ai-recruit --version`.

## Releasing

Push a `vX.Y.Z` tag; `.github/workflows/release.yml` runs CI, checks the tag against `__version__` in `recruit_cli/__init__.py` (the only place the
version is written), publishes to PyPI with trusted publishing and creates a GitHub release. Setup and step-by-step instructions: [PACKAGE.md](../PACKAGE.md).

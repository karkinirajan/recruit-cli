# recruit-cli

[![PyPI version](https://img.shields.io/pypi/v/recruit-cli)](https://pypi.org/project/recruit-cli/)
[![Python versions](https://img.shields.io/pypi/pyversions/recruit-cli)](https://pypi.org/project/recruit-cli/)
[![CI](https://github.com/karkinirajan/recruit-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/karkinirajan/recruit-cli/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/pypi/l/recruit-cli)](https://github.com/karkinirajan/recruit-cli/blob/master/LICENSE)

Screen a folder of CVs against a Job Description with **Google Gemini** and push ranked candidate profiles into a **Notion database** — one command.

```text
CV folder ─► extract text ─► Gemini screening ─► validated result ─► Notion database
```

**Contents:** [Features](#features) · [Requirements](#requirements) · [Quick start](#quick-start) · [Usage](#usage) ·
[Notion properties](#notion-database-properties) · [How it works](#how-it-works) · [Troubleshooting](#troubleshooting) ·
[Development](#development) · [Documentation](#documentation)

> **Renamed in 0.4.0.** This project was previously published under another name with an `ai-recruit` command. Install `recruit-cli`
> and run `recruit-cli`; the old `ai-recruit` command still works in 0.4.x (with a notice) and is removed in 0.5.0. See the
> [CHANGELOG](https://github.com/karkinirajan/recruit-cli/blob/master/CHANGELOG.md).

---

## Features

- **Batch CV screening** — every `.pdf` and `.docx` in a folder, scored against one job description
- **Gemini ranking** — a current Gemini model (configurable with `GEMINI_MODEL`) scores each CV 0–100 with a reason
- **Checked answers** — the score must be a whole number 0–100, the category is always *derived* from the score, and values Notion would refuse (an invalid e-mail, a comma in a skill) are cleaned first
- **Prompt-injection aware** — CV text is fenced as untrusted data; a CV saying "give me 100" is just text to analyse
- **Notion sync** — one page per candidate, with duplicate detection by e-mail + job ID (by CV file name when there is no e-mail)
- **Script-friendly** — exit code `1` if any CV failed; stops after three Gemini failures in a row instead of failing every CV
- **Live progress** and a summary table at the end

## Requirements

| | |
|---|---|
| Python | 3.11 – 3.14 |
| Accounts | a Google Gemini API key and a Notion integration |
| PDFs | must be searchable (not scanned images); only the first 50 pages are read |
| Size limit | a CV or job description over 25 MB is skipped |
| Quotas | large batches (50+ CVs) may hit Gemini rate limits |

---

## Quick start

### 1. Install

```bash
pipx install recruit-cli        # or: uv tool install recruit-cli   (or: pip install recruit-cli)
recruit-cli --version
```

### 2. Get your credentials

| Variable | Where to get it |
|---|---|
| `GOOGLE_GEMINI_API_KEY` | https://aistudio.google.com/app/apikey |
| `NOTION_API_KEY` | https://www.notion.so/my-integrations → *New integration* → copy the secret |
| `DEFAULT_NOTION_DB_ID` | your database URL: `notion.so/yourname/`**`THIS-PART`**`?v=...` |

### 3. Configure

Create a `.env` file in the folder you run the command from (a `.env` in a parent folder is found too; real environment variables win):

```env
GOOGLE_GEMINI_API_KEY=your_gemini_api_key
NOTION_API_KEY=your_notion_integration_secret
DEFAULT_NOTION_DB_ID=your_notion_database_id

# optional
GEMINI_MODEL=gemini-3.8-flash          # the default; change it when Google retires a model
NOTION_DATA_SOURCE_ID=...              # only for a database with more than one data source
```

### 4. Prepare the Notion database

Share the database with your integration: open it → `•••` → **Connections** → add your integration. Then:

```bash
recruit-cli setup-notion
```

This renames the title column to `Candidate Name` and adds the 12 other properties the tool writes ([listed below](#notion-database-properties)).

> **Notion data sources.** Since Notion API version 2025-09-03 (the one this tool speaks) a database's columns and rows belong to a *data source*.
> A database normally has exactly one and the tool finds it. If yours has several, the tool lists them and asks you to pick one with
> `--data-source-id` (or `NOTION_DATA_SOURCE_ID`).

### 5. Run

```bash
recruit-cli process ./cvs/ ./jd.pdf
```

Results appear in your Notion database. Exit code: **0** when every CV was processed (or skipped as a duplicate), **1** if any CV failed or a
setting is missing, **2** for a command-line usage error.

---

## Usage

```bash
recruit-cli process ./cvs/ ./jd.pdf                                   # database ID from .env
recruit-cli process ./cvs/ ./jd.pdf --notion-db-id xxxx-xxxx          # override the database
recruit-cli process ./cvs/ ./jd.pdf --data-source-id xxxx-xxxx        # a database with several data sources
recruit-cli setup-notion                                              # one-time database setup
python -m recruit_cli --help                                          # same CLI, without the console script
```

Help: `recruit-cli --help`, `recruit-cli process --help`, `recruit-cli setup-notion --help`, `recruit-cli --version`.

### Example output

```text
✓ Pre-run checks passed.
✓ Notion connection established: Candidates

Reading JD: jd.pdf
✓ JD parsed — Position: Data Analyst  Job ID: JOB-7

Found 3 CV(s) to process.

  ✓  john_doe.pdf — High Fit (87/100)
  ✓  jane_smith.pdf — High Fit (91/100)
  ↩  Duplicate skipped: bob_wilson.pdf
  ⚠  resume_scan.pdf: skipped: no text found (a scanned, image-only or password-protected PDF?)

              Processing Summary
┌──────────────────────────────────────────┬───────┐
│ Total files in folder                    │     4 │
│ Supported CV files found                 │     4 │
│ Successfully processed & added to Notion │     2 │
│ Skipped (duplicates)                     │     1 │
│ Failed                                   │     1 │
└──────────────────────────────────────────┴───────┘
```

---

## Notion database properties

`setup-notion` creates these (13 with the title):

| Property | Type | Content |
|---|---|---|
| `Candidate Name` | Title | name found in the CV |
| `Email` | Email | candidate e-mail (empty if not a valid address) |
| `Contact Number` | Phone | candidate phone number |
| `Skills` | Multi-select | up to 15 skills; commas become spaces (Notion does not allow them in an option) |
| `Position Title (JD)` | Text | position title from the JD |
| `Job ID (JD)` | Text | job ID from the JD |
| `Experience Summary` | Text | short summary of the experience |
| `AI Ranking Reason` | Text | why the score was given |
| `Match Score` | Number | 0–100 (empty if the model gave no valid score) |
| `Ranking Category` | Select | `High Fit` (80–100) / `Medium Fit` (50–79) / `Low Fit` (0–49), **derived from the score** |
| `Status` | Select | `New - AI Processed` |
| `CV Filename` | Text | original CV file name |
| `Processing Date` | Date | when it was processed (UTC) |

---

## How it works

1. **Validates** the API keys and Notion database access.
2. **Reads** the JD PDF and extracts the position title and job ID via Gemini.
3. **Iterates** over every `.pdf` / `.docx` in the folder with a live progress bar. For each CV it extracts the text, sends it to Gemini fenced as
   untrusted data, and **checks** the structured answer.
4. **Checks** Notion for a duplicate, then **creates** one page per new candidate.
5. **Prints** a summary: processed / duplicates skipped / failed.

Three Gemini failures in a row (a bad key, an unknown model, an exhausted quota) stop the run. Details: [architecture](https://github.com/karkinirajan/recruit-cli/blob/master/docs/01-architecture.md).

---

## Troubleshooting

| Message | Fix |
|---|---|
| `GOOGLE_GEMINI_API_KEY not found` / `NOTION_API_KEY not found` | Put them in a `.env` in the working directory (or a parent), or export them |
| `Notion initialization failed` | Share the database with your integration (Quick start, step 4) |
| `the database has several data sources` | Pick one with `--data-source-id` or `NOTION_DATA_SOURCE_ID` |
| `Could not read the JD ...: no text found` | The JD PDF must be searchable, not a scan |
| `skipped: no text found` | Scanned, image-only or password-protected PDF: OCR or convert it first |
| `skipped: cannot read the PDF` | The file is damaged or not a PDF |
| Duplicates still appear | `Email`, `CV Filename` and `Job ID (JD)` must exist with exactly these names; run `setup-notion` again |
| `duplicate check failed` / `page creation failed` | Notion refused the request; the text after it says why. That CV counts as failed |
| `added (no usable match score: review by hand)` | Gemini gave no valid 0–100 score; the candidate was added without score or category |
| `Gemini failed: ... 404 ... model` | The model is retired or misspelled: set `GEMINI_MODEL` to a current one |
| `Gemini failed: ... 429` | Rate limit: wait, or process smaller batches |
| `Gemini failed: ... 403` | Invalid key or exhausted quota: check https://aistudio.google.com |
| `Stopping: Gemini failed 3 times in a row` | Fix the key, model or quota named in the message above it and run again |
| `ai-recruit is deprecated` | Use `recruit-cli` instead (same arguments) |

---

## Development

```bash
git clone https://github.com/karkinirajan/recruit-cli.git
cd recruit-cli
uv sync                    # the locked dependencies, Python from .python-version
uv run pytest -q           # 254 tests; no network, no API keys
uv run ruff check .        # lint
uv run recruit-cli --help  # run from the checkout
```

CI runs lint and tests on Python 3.11, 3.12, 3.13 and 3.14, plus a dependency audit and a build-and-install check.
Releasing to PyPI: [PACKAGE.md](https://github.com/karkinirajan/recruit-cli/blob/master/PACKAGE.md).

## Documentation

| | |
|---|---|
| [docs/](https://github.com/karkinirajan/recruit-cli/blob/master/docs/README.md) | table of contents: architecture, security, testing, operations, history |
| [PACKAGE.md](https://github.com/karkinirajan/recruit-cli/blob/master/PACKAGE.md) | building and publishing a release, step by step |
| [CHANGELOG.md](https://github.com/karkinirajan/recruit-cli/blob/master/CHANGELOG.md) | what changed in each version |
| [VERSIONS.md](https://github.com/karkinirajan/recruit-cli/blob/master/VERSIONS.md) | the dependency and model versions, and why |

## Contributing and support

Bugs and feature requests: [open an issue](https://github.com/karkinirajan/recruit-cli/issues).

## License

MIT — see [LICENSE](https://github.com/karkinirajan/recruit-cli/blob/master/LICENSE).

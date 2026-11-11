# Changelog

All notable changes. Versions follow [Semantic Versioning](https://semver.org/) (pre-1.0: a minor bump may break things).

## [0.4.0] — unreleased

### Changed — the project is now `recruit-cli`

| | Before | Now |
|---|---|---|
| Repository | previous name (GitHub redirects old links) | `github.com/karkinirajan/recruit-cli` |
| PyPI distribution | `ai-recruitment-agent` | `recruit-cli` |
| Import package | `ai_recruitment_agent` | `recruit_cli` |
| Command | `ai-recruit` | `recruit-cli` (also `python -m recruit_cli`) |
| `--version` output | `ai-recruitment-agent vX` | `recruit-cli vX` |

**Migrating:** `pip uninstall ai-recruitment-agent` then `pip install recruit-cli` (or `pipx uninstall ai-recruitment-agent` / `pipx install recruit-cli`).
Settings, `.env` and the Notion database are unchanged. The `ai-recruit` command still works in 0.4.x and prints a deprecation notice on stderr;
it will be removed in 0.5.0.

### Fixed

- **CI was red on every run.** Typer forces colour when `GITHUB_ACTIONS` is set, and a colour code inside `--notion-db-id` broke a help-text test; the
  test helper now strips terminal codes.
- **The "Python 3.11" CI job tested 3.14.** `uv run` re-synced the environment to `.python-version`; CI now sets `UV_PYTHON` per job and asserts the
  interpreter version.
- A local `uv build` put every untracked file in the folder (`.env`, sample CVs, tool logs) into the source distribution; the sdist is now an explicit allowlist.
- Help showed `{cv_folder_path} {jd_pdf_path}`; it now shows `CV_FOLDER JD_PDF`.
- Running the repository's `main.py` printed the program name as `main.py`; it is now `recruit-cli`.

### Added

- `python -m recruit_cli`.
- CI on Python 3.11, 3.12, 3.13 and 3.14 (every version in the classifiers), with a build-and-install check of the wheel.
- `release.yml`: push a `vX.Y.Z` tag to run CI, check the tag against the version, publish to PyPI (trusted publishing) and create a GitHub release.
- `PACKAGE.md` (release steps), this changelog, `docs/README.md` (table of contents).

### Internal

- The version lives only in `recruit_cli/__init__.py`; `pyproject.toml` reads it (`dynamic = ["version"]`), and a test checks the installed metadata matches.
- `work-done.md` moved to `docs/05-modernization-report.md`.

## [0.3.2] and earlier

Published under the previous name. The 0.3.2 modernization (current Gemini and Notion APIs, validated model output, 250 tests, lockfile, CI) is
described in [docs/05-modernization-report.md](docs/05-modernization-report.md).

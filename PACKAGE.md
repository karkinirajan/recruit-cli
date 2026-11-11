# Packaging and deployment

How `recruit-cli` is built and published to [PyPI](https://pypi.org/project/recruit-cli/). Publishing is automated: pushing a `vX.Y.Z` tag runs
[`.github/workflows/release.yml`](.github/workflows/release.yml), which runs the full CI, checks the tag against the package version, builds,
publishes to PyPI with **trusted publishing** (no API token stored anywhere) and creates a GitHub release with the built files.

| Item | Value |
|---|---|
| PyPI project | `recruit-cli` |
| Import package | `recruit_cli` |
| Commands | `recruit-cli` (and the deprecated `ai-recruit` alias, until 0.5.0) |
| Version source | `recruit_cli/__init__.py` → `__version__` (the only place; `pyproject.toml` reads it) |
| Build backend | hatchling, via `uv build` |
| Release workflow | `.github/workflows/release.yml`, GitHub environment `pypi` |

---

## A. One-time setup

Do these once. Steps A1–A3 are needed before the first release under the new name.

### A1. Point your local clone at the renamed repository

GitHub redirects the old URL, but update it so nothing depends on the redirect:

```bash
git remote set-url origin git@github.com:karkinirajan/recruit-cli.git   # or https://github.com/karkinirajan/recruit-cli.git
git remote -v                                                            # check: both lines show karkinirajan/recruit-cli
```

### A2. Register the trusted publisher on PyPI

`recruit-cli` does not exist on PyPI yet, so register a **pending** publisher (it creates the project on the first upload):

1. Sign in at https://pypi.org → your account menu → **Your projects** → **Publishing**.
2. Under **Add a new pending publisher** choose **GitHub** and enter exactly:

   | Field | Value |
   |---|---|
   | PyPI Project Name | `recruit-cli` |
   | Owner | `karkinirajan` |
   | Repository name | `recruit-cli` |
   | Workflow name | `release.yml` |
   | Environment name | `pypi` |

3. Click **Add**. (After the first release it appears under the project's **Settings → Publishing** as a normal publisher.)

### A3. Create the `pypi` environment on GitHub

1. https://github.com/karkinirajan/recruit-cli → **Settings** → **Environments** → **New environment** → name it `pypi` → **Configure environment**.
2. Recommended: **Required reviewers** → add yourself, so every publish waits for your click.
3. Recommended: **Deployment branches and tags** → **Selected branches and tags** → **Add deployment branch or tag rule** → type *Tag*, pattern `v*`.
4. **Save protection rules.**

### A4. Make sure CI is green on `master`

https://github.com/karkinirajan/recruit-cli/actions/workflows/ci.yml must show a green run for the commit you are about to tag. The release
workflow runs CI again and stops if it fails.

---

## B. Releasing a version (every release)

Example for `0.4.0`; replace the number.

### B1. Set the version and the changelog

1. `recruit_cli/__init__.py`: `__version__ = "0.4.0"` (no `v`; this is the only place the version is written).
2. `CHANGELOG.md`: change `## [0.4.0] — unreleased` to `## [0.4.0] — YYYY-MM-DD` (today's date).

### B2. Run the gates locally

```bash
uv sync --locked                 # fails if uv.lock is out of date: run `uv lock` and commit it
uv run ruff check .              # expect: All checks passed!
uv run pytest -q                 # expect: all passed
uv build --clear                 # expect: dist/recruit_cli-0.4.0.tar.gz and dist/recruit_cli-0.4.0-py3-none-any.whl
tar tzf dist/recruit_cli-0.4.0.tar.gz          # expect: only recruit_cli/*, README.md, CHANGELOG.md, LICENSE, pyproject.toml, PKG-INFO, .gitignore
uv run --isolated --no-project --with dist/recruit_cli-0.4.0-py3-none-any.whl recruit-cli --version   # expect: recruit-cli v0.4.0
```

### B3. Commit and merge

```bash
git switch -c release/0.4.0
git add recruit_cli/__init__.py CHANGELOG.md
git commit -m "Release 0.4.0"
git push -u origin release/0.4.0
gh pr create --fill --base master
```

Wait for the PR's CI to pass, then merge it (`gh pr merge --squash --delete-branch`, or in the browser).

### B4. Tag and push the tag

Tag the merged commit on `master`, not the branch:

```bash
git switch master
git pull --ff-only
git tag -a v0.4.0 -m "recruit-cli 0.4.0"
git push origin v0.4.0
```

The tag must be exactly `v` + `__version__`; otherwise the workflow stops at *The tag matches the package version* and nothing is published.

### B5. Watch the release

```bash
gh run watch "$(gh run list --workflow release.yml --limit 1 --json databaseId --jq '.[0].databaseId')"
```

Stages: `ci` (all four Python versions) → `build` (tag check, `uv build`) → `publish` (waits for your approval if you set required reviewers in A3 →
uploads to PyPI → creates the GitHub release with the two files).

### B6. Verify the published package

```bash
pipx install --force recruit-cli==0.4.0      # or: uv tool install --force recruit-cli==0.4.0
recruit-cli --version                        # expect: recruit-cli v0.4.0
recruit-cli --help
```

Check https://pypi.org/project/recruit-cli/ (README renders, links work) and https://github.com/karkinirajan/recruit-cli/releases.

---

## C. If something goes wrong

| Problem | Fix |
|---|---|
| `tag vX does not match __version__ Y` | Delete the tag (`git push origin :refs/tags/vX` and `git tag -d vX`), fix the version on `master` (B1–B3), tag again |
| `invalid-publisher` / trusted publishing error | A2's fields must match exactly: owner `karkinirajan`, repo `recruit-cli`, workflow `release.yml`, environment `pypi` |
| `File already exists` on PyPI | A version can be uploaded only once, ever. Bump to the next patch version and release that |
| A bad version is live | PyPI → project → **Manage** → **Releases** → the version → **Options** → **Yank** (installers skip it unless pinned). Then release a fixed version |
| CI fails in the release run | Nothing was published. Fix on `master`, delete and recreate the tag (first row) |

### Manual publish (fallback only)

Use this only if GitHub Actions is unavailable. It needs a PyPI API token (https://pypi.org/manage/account/token/, scoped to `recruit-cli`).

```bash
git switch master
git pull --ff-only
git status --short                 # must print nothing: the sdist is an allowlist, but publish only from a clean, tagged tree
uv build --clear
UV_PUBLISH_TOKEN=pypi-... uv publish dist/*
```

---

## D. Retiring the previous PyPI name (optional, one time)

Until 0.3.2 the package was published as `ai-recruitment-agent`. Those installs do not upgrade to `recruit-cli` by themselves. To point them
at the new name, publish one last version of the old project that just depends on the new one:

1. Create a temporary folder **outside** this repository with a single `pyproject.toml`:

   ```toml
   [build-system]
   requires = ["hatchling"]
   build-backend = "hatchling.build"

   [project]
   name = "ai-recruitment-agent"
   version = "0.4.0"
   description = "Renamed: this project is now recruit-cli (pip install recruit-cli)."
   readme = { text = "This package was renamed to **recruit-cli**: `pip install recruit-cli`. https://pypi.org/project/recruit-cli/", content-type = "text/markdown" }
   requires-python = ">=3.11"
   dependencies = ["recruit-cli>=0.4.0"]

   [tool.hatch.build.targets.wheel]
   bypass-selection = true
   ```

2. In that folder: `uv build`, then `UV_PUBLISH_TOKEN=<a token scoped to ai-recruitment-agent> uv publish dist/*`.
3. Users who run `pip install -U ai-recruitment-agent` now get `recruit-cli` (and its `recruit-cli` and `ai-recruit` commands).
4. On PyPI, edit the old project's description or mark it as archived (project → **Settings**) if you no longer want to maintain it.

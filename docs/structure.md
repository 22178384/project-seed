# Why the files are laid out this way

This is the reasoning behind the template, so you can decide what to throw away.

## Flat `src/` instead of `src/<pkgname>/`

Most `src`-layout templates do `src/myproject/__init__.py`. I don't, because the
rename step is then three files deep and I always miss one. Here the package
directory is literally `src`, and the only place the project name appears is
`pyproject.toml`. Renaming a project is a one-line edit plus a `make clean`.

Trade-off: `import src` is not a great package name if you ever publish to PyPI.
If you're publishing, bite the bullet and use `src/<pkgname>/`.

## `core.py` has zero I/O

`core.py` takes strings and returns dataclasses. It never prints and never opens
a file. That means:

- Tests don't need temp files or captured stdout for the interesting logic.
- You can call it from a script, a web handler, or a notebook unchanged.
- Coverage numbers actually mean something.

The CLI in `cli.py` is the only I/O layer. Keep it that way. The moment you put
a `print()` inside `core.py`, the split stops paying for itself.

## Why a `Stats` dataclass instead of a dict

Returning a frozen dataclass gives you attribute access, a free `__repr__`, and
`asdict()` when you need JSON. A plain dict would work too, but I've typo'd
`stats["line"]` enough times to prefer the error you get from `stats.line`.

`frozen=True` is on purpose: stats for a given text never change, and freezing
catches accidental mutation in tests.

## Tests: two files, two levels

- `test_core.py` — fast unit tests, parametrized, no subprocess.
- `test_main.py` — spawns `python -m src.cli` and checks stdout/exit codes.

The subprocess tests are slower but they catch the class of bug that unit tests
miss: wrong exit code, `print` going to stderr, a broken `[project.scripts]`
entry point. I run both.

## `pythonpath = ["."]` in pytest config

Without it, `from src.core import ...` fails unless the package is installed.
Setting it means `git clone && pytest` just works, which matters for the first
five minutes after someone clones your repo.

## CI lives in `workflows/`, not `.github/workflows/`

Only because this particular template was generated in a sandbox that blocks
writing to `.github/`. In a real repo, move the file. GitHub will not find a
workflow anywhere else, and there's no error message when it doesn't — the
checks just never appear.

## What I deliberately left out

- **No `setup.py`.** `pyproject.toml` + hatchling covers it. `setup.py` is only
  needed for editable installs on ancient pip.
- **No `requirements.txt`.** Deps live in `pyproject.toml`. A lockfile is worth
  adding for apps (use `pip-tools` or `uv`), not for a library template.
- **No `tox`/`nox`.** GitHub Actions matrix covers the Python versions I care
  about. `tox` is a second place to keep versions in sync.
- **No `__main__.py`.** `python -m src.cli` works without it. Add one if you
  want `python -m src`.

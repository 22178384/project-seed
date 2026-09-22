# project-seed

A minimal Python project template. Not a framework, not a "modern stack", just
the files I end up creating by hand every time I start something new: a package,
a CLI entry point, tests, a Makefile, and CI.

The example project it ships with is `txtstat`, a tiny text-stats tool (think
`wc` with a reading-time estimate). It's real and runnable. Delete it once you
understand the layout.

## Why this exists

I kept copy-pasting `pyproject.toml` from my last repo and then forgetting to
update the package name, which led to a 20-minute debugging session where
`pip install -e .` installed the *old* project. So this repo is a checklist in
file form. Rename the package, run `make install`, done.

## Requirements

- Python 3.10+ (uses `X | None` and `match`-friendly code)
- `make` if you want the shortcuts. On Windows, use WSL or just run the commands
  from the Makefile by hand — I don't test the Makefile on Windows.

## Use it as a template

```bash
# Option A: GitHub "Use this template" button (if you're reading this on GitHub)

# Option B: copy by hand
git clone https://github.com/22178384/project-seed.git my-new-thing
cd my-new-thing
rm -rf .git && git init
```

Then rename things. There are exactly four places:

1. `pyproject.toml` — `name`, `description`, the `[project.scripts]` key
2. `src/` — rename the directory (the example uses `src/` with a flat layout)
3. `tests/` — import paths if you renamed the package
4. this README

## Layout

```
src/
  __init__.py
  cli.py          argparse front end
  core.py         the actual logic (pure functions, no I/O)
tests/
  test_core.py    unit tests for core
  test_main.py    end-to-end CLI test via subprocess
pyproject.toml    hatchling build backend, dev extras
Makefile          install / test / lint / clean
.pre-commit-config.yaml
workflows/ci.yml  GitHub Actions (see note below)
docs/structure.md why the files are arranged this way
```

## Run it

```bash
make install          # pip install -e ".[dev]"
txtstat README.md
txtstat src/*.py --json
echo "hello world" | txtstat -
```

Sample output:

```
README.md
  lines         78
  words         612
  chars         3811
  longest line  96
  read time     2.8 min
  top words     the(41) and(22) a(19) to(18) of(17)
```

## Tests

```bash
make test             # pytest -q
make test-cov         # with coverage, fails under 90%
```

## CI

`workflows/ci.yml` is a real GitHub Actions workflow, but it lives in
`workflows/` instead of `.github/workflows/` because this template is generated
in an environment that blocks writes to `.github/`. **When you use the template,
move it:**

```bash
mkdir -p .github/workflows
mv workflows/ci.yml .github/workflows/ci.yml
```

Otherwise GitHub won't run it and you'll wonder why there's no green check.

## Gotchas

- **`pip install -e .` with a stale egg-info.** If you renamed the package and
  get `ModuleNotFoundError`, run `make clean` first. `pip install -e .` happily
  reuses a cached `*.egg-info`.
- **`python -m pytest` vs `pytest`.** Use `python -m pytest` if you have
  multiple Python installs, otherwise the `pytest` shim may be from a different
  interpreter and won't see your installed package.
- **pre-commit installs a git hook.** It only runs on `git commit`, not on
  `git commit -n`. Run `pre-commit run --all-files` before your first commit.

## Notes

I keep the core logic in `core.py` with zero I/O so it's trivially testable.
`cli.py` does argument parsing and printing, nothing else. That split has saved
me every time I've wanted to reuse the logic from a script.

MIT. See LICENSE.

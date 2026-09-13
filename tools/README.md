# Tools

This directory contains the development tooling for the repository.

## Requirements

- Docker installed and running
- `make` available on your PATH

## Usage

All targets are defined in `tasks.mk` and exposed via the root `Makefile`.
Run `make help` from the repository root to see the available targets.

### Markdown

- `make lint-md` – Check Markdown files with markdownlint (no changes)
- `make fix-md` – autofix Markdown files with markdownlint

### Formatting

- `make format` – Format all files with Prettier
- `make check-fmt` – Verify formatting without writing changes

### Combined

- `make check` – Run `lint-md` and `check-fmt` together

## Adding new tools

Each tool is a standalone Make target. To add a new one, append a target
to `tasks.mk` following the existing pattern:

```makefile
.PHONY: some-check
some-check:
docker run --rm -v "$(CURDIR)":/workspace -w /workspace python:3.12 bash -c \
"pip install -q ruff && ruff check ."
Keep each target self-contained: one tool, one container, one command.
```

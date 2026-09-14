# Tooling tasks – each target is self-contained (one tool, one container).

# Versions – managed by Renovate (see renovate.json)
# renovate: datasource=docker depName=node versioning=docker
NODE_VERSION=20
# renovate: datasource=docker depName=python versioning=docker
PYTHON_VERSION=3.12-slim
# renovate: datasource=pypi depName=yamllint versioning=pep440
YAMLLINT_VERSION=1.35.1
# Shared pip flags for all Python-based targets
# --quiet                    : no progress bars
# --root-user-action=ignore  : suppress the "running as root" warning
# --disable-pip-version-check: suppress the "new pip available" notice
PIP_FLAGS=--quiet --root-user-action=ignore --disable-pip-version-check

.PHONY: help
help:
	@echo "Targets:"
	@echo "  make lint-md    - Check Markdown files (markdownlint, no --fix)"
	@echo "  make fix-md     - Auto-fix Markdown files"
	@echo "  make yamllint   - Check YAML frontmatter in recipe markdown files"
	@echo "  make lint-text  - Check Markdown files with textlint"
	@echo "  make fix-text   - Autofix Markdown files with textlint"
	@echo "  make format     - Format all files with Prettier"
	@echo "  make check-fmt  - Prettier --check (no writes)"
	@echo "  make black      - Check Python files with black"
	@echo "  make fix-black  - Auto-format Python files with black"
	@echo "  make flake8     - Check Python files with flake8"
	@echo "  make isort      - Check Python import order with isort"
	@echo "  make fix-isort  - Auto-fix Python import order with isort"
	@echo "  make ruff       - Check Python files with ruff"
	@echo "  make fix-ruff   - Auto-fix Python files with ruff"
	@echo "  make pylint     - Check Python files with pylint"
	@echo "  make check      - lint-md + check-fmt + black + flake8 + isort + ruff + pylint"

# ---------- Markdown ----------
.PHONY: lint-md
lint-md:
	docker run --rm -v "$(CURDIR)":/workspace -w /workspace node:$(NODE_VERSION) bash -c \
		"npm install -g markdownlint-cli -q && \
		 markdownlint '**/*.md' --ignore node_modules"

.PHONY: fix-md
fix-md:
	docker run --rm -v "$(CURDIR)":/workspace -w /workspace node:$(NODE_VERSION) bash -c \
		"npm install -g markdownlint-cli -q && \
		 markdownlint --fix '**/*.md' --ignore node_modules"

# ---------- YAML: yamllint ----------
.PHONY: yamllint
yamllint:
	docker run --rm -v "$(CURDIR)":/workspace -w /workspace python:$(PYTHON_VERSION) bash -c \
		'pip install \
		   $(PIP_FLAGS) \
		   yamllint==$(YAMLLINT_VERSION) && \
		 find . -type f -name "*.md" \
		   -not -path "./.github/*" \
		   -not -path "./dist/*" \
		   -not -path "./tools/*" \
		   -not -name "README.md" \
		   -not -name "index.md" \
		   -not -name "combined.md" \
		   -not -name "*.bak.md" \
		   -print0 \
		 | while IFS= read -r -d "" file; do \
		     delims=$$(grep -c "^---$$" "$$file" || true); \
		     [ "$$delims" -lt 1 ] && continue; \
		     if [ "$$delims" -ne 2 ]; then \
		       echo "FAIL $$file: expected 2 delimiters, found $$delims"; \
		       exit 1; \
		     fi; \
		     awk "/^---$/{c++; print; next} c==1" "$file" > /tmp/fm.yaml; \
		     echo "Linting $$file"; \
		     yamllint -c .yamllint /tmp/fm.yaml || exit 1; \
		   done'

# ---------- textlint ----------
.PHONY: lint-text
lint-text:
	docker run --rm -v "$(CURDIR)":/workspace -w /workspace node:$(NODE_VERSION) bash -c \
		"npm install -g textlint textlint-rule-terminology -q && \
		 textlint '**/*.md'"

.PHONY: fix-text
fix-text:
	docker run --rm -v "$(CURDIR)":/workspace -w /workspace node:$(NODE_VERSION) bash -c \
		"npm install -g textlint textlint-rule-terminology -q && \
		 textlint --fix '**/*.md'"

# ---------- Prettier ----------
.PHONY: format
format:
	docker run --rm -v "$(CURDIR)":/workspace -w /workspace node:$(NODE_VERSION) bash -c \
		"npm install -g prettier@3.8.4 -q && \
		 prettier --write ."

.PHONY: check-fmt
check-fmt:
	docker run --rm -v "$(CURDIR)":/workspace -w /workspace node:$(NODE_VERSION) bash -c \
		"npm install -g prettier@3.8.4 -q && \
		 prettier --check ."

# ---------- Python: black ----------
.PHONY: black
black:
	docker run --rm -v "$(CURDIR)":/workspace -w /workspace python:$(PYTHON_VERSION) bash -c \
		"pip install $(PIP_FLAGS) black && \
		 black --check --diff ."

.PHONY: fix-black
fix-black:
	docker run --rm -v "$(CURDIR)":/workspace -w /workspace python:$(PYTHON_VERSION) bash -c \
		"pip install $(PIP_FLAGS) black && \
		 black ."

# ---------- Python: flake8 ----------
.PHONY: flake8
flake8:
	docker run --rm -v "$(CURDIR)":/workspace -w /workspace python:$(PYTHON_VERSION) bash -c \
		"pip install $(PIP_FLAGS) flake8 && \
		 flake8 ."

# ---------- Python: isort ----------
.PHONY: isort
isort:
	docker run --rm -v "$(CURDIR)":/workspace -w /workspace python:$(PYTHON_VERSION) bash -c \
		"pip install $(PIP_FLAGS) isort && \
		 isort --check-only --diff ."

.PHONY: fix-isort
fix-isort:
	docker run --rm -v "$(CURDIR)":/workspace -w /workspace python:$(PYTHON_VERSION) bash -c \
		"pip install $(PIP_FLAGS) isort && \
		 isort ."

# ---------- Python: ruff ----------
.PHONY: ruff
ruff:
	docker run --rm -v "$(CURDIR)":/workspace -w /workspace python:$(PYTHON_VERSION) bash -c \
		"pip install $(PIP_FLAGS) ruff && \
		 ruff check ."

.PHONY: fix-ruff
fix-ruff:
	docker run --rm -v "$(CURDIR)":/workspace -w /workspace python:$(PYTHON_VERSION) bash -c \
		"pip install $(PIP_FLAGS) ruff && \
		 ruff check --fix ."

# ---------- Python: pylint ----------
.PHONY: pylint
pylint:
	docker run --rm -v "$(CURDIR)":/workspace -w /workspace python:$(PYTHON_VERSION) bash -c \
		'pip install $(PIP_FLAGS) pylint && \
		 pylint $$(find . -name "*.py" -not -path "./.git/*")'

# ---------- Combined Fixes ----------

.PHONY: fix
fix: format fix-md fix-text fix-black fix-isort fix-ruff
	@echo "All fixes applied."

# ---------- Combined Tests ----------
.PHONY: check
check: check-fmt lint-md lint-text yamllint black flake8 isort ruff pylint
	@echo "All checks passed."

# ---------- Add new tools below this line ----------
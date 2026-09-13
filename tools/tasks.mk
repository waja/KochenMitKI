# Tooling tasks – each target is self-contained (one tool, one container).

.PHONY: help
help:
	@echo "Targets:"
	@echo "  make lint-md    - Check Markdown files (markdownlint, no --fix)"
	@echo "  make fix-md     - Auto-fix Markdown files"
	@echo "  make lint-text  - Check Markdown files with textlint"
	@echo "  make fix-text   - Autofix Markdown files with textlint"
	@echo "  make format     - Format all files with Prettier"
	@echo "  make check-fmt  - Prettier --check (no writes)"
	@echo "  make check      - lint-md + check-fmt"

# ---------- Markdown ----------
.PHONY: lint-md
lint-md:
	docker run --rm -v "$(CURDIR)":/workspace -w /workspace node:20 bash -c \
		"npm install -g markdownlint-cli -q && \
		 markdownlint '**/*.md' --ignore node_modules"

.PHONY: fix-md
fix-md:
	docker run --rm -v "$(CURDIR)":/workspace -w /workspace node:20 bash -c \
		"npm install -g markdownlint-cli -q && \
		 markdownlint --fix '**/*.md' --ignore node_modules"

# ---------- textlint ----------
.PHONY: lint-text
lint-text:
	docker run --rm -v "$(CURDIR)":/workspace -w /workspace node:20 bash -c \
		"npm install -g textlint textlint-rule-terminology -q && \
		 textlint '**/*.md'"

.PHONY: fix-text
fix-text:
	docker run --rm -v "$(CURDIR)":/workspace -w /workspace node:20 bash -c \
		"npm install -g textlint textlint-rule-terminology -q && \
		 textlint --fix '**/*.md'"

# ---------- Prettier ----------
.PHONY: format
format:
	docker run --rm -v "$(CURDIR)":/workspace -w /workspace node:20 bash -c \
		"npm install -g prettier@3.8.4 -q && \
		 prettier --write ."

.PHONY: check-fmt
check-fmt:
	docker run --rm -v "$(CURDIR)":/workspace -w /workspace node:20 bash -c \
		"npm install -g prettier@3.8.4 -q && \
		 prettier --check ."

# ---------- Combined Fixes ----------

.PHONY: fix
fix: format fix-md fix-text
	@echo "All fixes applied."

# ---------- Combined Tests ----------
.PHONY: check
check: check-fmt lint-md lint-text
	@echo "All checks passed."

# ---------- Add new tools below this line ----------
# Repository guidance

## Linting and validation

- When changing source files, recipes, configuration, or GitHub Actions workflows, review the Super-Linter configuration in `.github/workflows/test.yml`.
- Check whether the change introduces a file type or use case for which a currently disabled Super-Linter validator should be enabled. Consider the validator's relevance, overlap with existing dedicated checks, and maintenance cost.
- Record the decision in the pull request description or review: enable any newly relevant validator, or briefly explain why no change is needed. Do not enable validators merely because they exist.
- Keep checks focused on file types and tools actually used by this repository. Prefer one clear Python linting approach over overlapping tools, while retaining security checks that are relevant to repository contents.
- If a validator is enabled or disabled, update the comments here or in `.github/workflows/test.yml` when needed so the rationale remains accurate.
- Run the relevant checks locally when practical, and ensure the GitHub Actions checks pass before merging.

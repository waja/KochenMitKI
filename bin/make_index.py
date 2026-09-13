#!/usr/bin/env python3
"""Generate and update the cookbook README and recipe index."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

README = ROOT / "README.md"
INDEX = ROOT / "index.md"

README_START = "<!-- AUTO-GENERATED CATEGORIES: START -->"
README_END = "<!-- AUTO-GENERATED CATEGORIES: END -->"

INDEX_START = "<!-- AUTO-GENERATED RECIPES: START -->"
INDEX_END = "<!-- AUTO-GENERATED RECIPES: END -->"


# Optional: Schönere Anzeigenamen für die Kategorieverzeichnisse.
# Neue Kategorien werden automatisch erkannt.
CATEGORY_LABELS = {
    "01_Indisch": "01 – Indisch",
    "02_Levante": "02 – Levante / Orientalisch",
    "03_Asiatisch": "03 – Asiatisch",
    "04_Mediterran": "04 – Mediterran",
}

# Verzeichnisse, die keine Rezeptkategorien sind.
EXCLUDED_CATEGORIES = {"00_Template"}
def category_name(directory: Path) -> str:
    """Return the display name for a recipe category directory."""

    if directory.name in CATEGORY_LABELS:
        return CATEGORY_LABELS[directory.name]

    match = re.match(r"^(\d+)_+(.*)$", directory.name)

    if match:
        number = match.group(1)
        name = match.group(2).replace("_", " ")
        return f"{number} – {name}"

    return directory.name.replace("_", " ")


def read_frontmatter(path: Path):
    """Read title and description from a Markdown file's frontmatter."""

    text = path.read_text(encoding="utf-8")

    if not text.startswith("---\n"):
        print(f"⚠️  Kein Frontmatter: {path}")
        return None

    end = text.find("\n---", 4)

    if end == -1:
        print(f"⚠️  Unvollständiges Frontmatter: {path}")
        return None

    frontmatter = text[4:end]

    title_match = re.search(
        r"^title:\s*(.*?)\s*$",
        frontmatter,
        re.MULTILINE,
    )

    description_match = re.search(
        r"^description:\s*(.*?)\s*$",
        frontmatter,
        re.MULTILINE,
    )

    if not title_match:
        print(f"⚠️  Kein 'title' im Frontmatter: {path}")
        return None

    title = title_match.group(1).strip()
    description = description_match.group(1).strip() if description_match else ""

    # Einfache Anführungszeichen entfernen.
    if len(title) >= 2 and title[0] == title[-1] and title[0] in "\"'":
        title = title[1:-1]

    if (
        len(description) >= 2
        and description[0] == description[-1]
        and description[0] in "\"'"
    ):
        description = description[1:-1]

    return title, description


def find_categories():
    """Find all numbered recipe category directories."""

    categories = [
        path
        for path in ROOT.iterdir()
        if path.is_dir()
        and re.match(r"^\d+_", path.name)
        and path.name not in EXCLUDED_CATEGORIES
    ]

    return sorted(categories, key=lambda path: path.name)


def find_recipes(category: Path):
    """Find all recipe Markdown files within a category."""

    return sorted(
        path
        for path in category.glob("*.md")
        if path.name not in {"README.md", "index.md"}
    )


def generate_category_list(categories):
    """Generate the automatically maintained category list."""

    lines = []

    for category in categories:
        label = category_name(category)
        relative_path = category.relative_to(ROOT).as_posix()

        lines.append(f"- [{label}]({relative_path}/)")

    return "\n".join(lines)


def generate_recipe_list(categories):
    """Generate the automatically maintained recipe list."""

    lines = []

    for category in categories:
        recipes = find_recipes(category)

        if not recipes:
            continue

        lines.append(f"### {category_name(category)}")
        lines.append("")

        for recipe in recipes:
            metadata = read_frontmatter(recipe)

            if metadata is None:
                continue

            title, description = metadata
            relative_path = recipe.relative_to(ROOT).as_posix()

            lines.append(f"- [{title}]({relative_path})")

            if description:
                lines.append(f"  {description}")

            lines.append("")

    return "\n".join(lines).rstrip()


def replace_generated_block(
    text: str,
    start_marker: str,
    end_marker: str,
    generated_content: str,
) -> str:
    """Replace only the content between two generated-section markers."""

    start = text.find(start_marker)
    end = text.find(end_marker)

    if start == -1 or end == -1:
        raise RuntimeError(
            "Marker nicht gefunden:\n"
            f"  START: {start_marker}\n"
            f"  END:   {end_marker}"
        )

    if end < start:
        raise RuntimeError(
            "Reihenfolge der Marker ist falsch:\n"  # codespell:ignore ist
            f"  START: {start_marker}\n"
            f"  END:   {end_marker}"
        )

    before = text[:start]
    after = text[end + len(end_marker) :]

    replacement = (
        start_marker + "\n\n" + generated_content.rstrip() + "\n\n" + end_marker
    )

    return before + replacement + after


def update_index(categories):
    """Update only the generated recipe section in index.md."""

    if not INDEX.exists():
        raise RuntimeError(
            "index.md existiert nicht. "
            "Bitte zunächst eine index.md mit den "
            "AUTO-GENERATED-Markern anlegen."
        )

    text = INDEX.read_text(encoding="utf-8")
    recipes = generate_recipe_list(categories)

    text = replace_generated_block(
        text,
        INDEX_START,
        INDEX_END,
        recipes,
    )

    INDEX.write_text(text, encoding="utf-8")


def update_readme(categories):
    """Update only the generated category section in README.md."""

    if not README.exists():
        raise RuntimeError(
            "README.md existiert nicht. "
            "Bitte zunächst eine README.md mit den "
            "AUTO-GENERATED-Markern anlegen."
        )

    text = README.read_text(encoding="utf-8")
    category_list = generate_category_list(categories)

    text = replace_generated_block(
        text,
        README_START,
        README_END,
        category_list,
    )

    README.write_text(text, encoding="utf-8")


def main():
    """Find categories and update the cookbook README and recipe index."""

    categories = find_categories()

    if not categories:
        raise SystemExit("❌ Keine Kategorieverzeichnisse gefunden.")

    print("Gefundene Kategorien:")

    for category in categories:
        print(f"  - {category_name(category)}")

    print()

    update_index(categories)
    update_readme(categories)

    print("✓ index.md aktualisiert")
    print("✓ README.md aktualisiert")


if __name__ == "__main__":
    main()

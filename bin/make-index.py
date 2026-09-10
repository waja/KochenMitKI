#!/usr/bin/env python3

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent

README = ROOT / "README.md"
INDEX = ROOT / "index.md"

README_START = "<!-- AUTO-GENERATED CATEGORIES: START -->"
README_END = "<!-- AUTO-GENERATED CATEGORIES: END -->"

INDEX_START = "<!-- AUTO-GENERATED RECIPES: START -->"
INDEX_END = "<!-- AUTO-GENERATED RECIPES: END -->"


# Optional: Schöne Anzeigenamen für die Kategorieverzeichnisse.
# Neue Kategorien werden automatisch erkannt; für sie wird der
# Verzeichnisname automatisch in eine lesbare Bezeichnung umgewandelt.
CATEGORY_LABELS = {
    "01_Indisch": "01 – Indisch",
    "02_Levante": "02 – Levante / Orientalisch",
    "03_Asiatisch": "03 – Asiatisch",
    "04_Italienisch": "04 – Italienisch",
}


def category_name(directory: Path) -> str:
    """
    Erzeugt den Anzeigenamen einer Kategorie.

    Bekannte Kategorien verwenden CATEGORY_LABELS.
    Für neue Kategorien wird z. B.

        05_Georgisch

    zu

        05 – Georgisch
    """

    if directory.name in CATEGORY_LABELS:
        return CATEGORY_LABELS[directory.name]

    match = re.match(r"^(\d+)_+(.*)$", directory.name)

    if match:
        number = match.group(1)
        name = match.group(2).replace("_", " ")
        return f"{number} – {name}"

    return directory.name.replace("_", " ")


def read_frontmatter(path: Path):
    """
    Liest title und description aus dem YAML-Frontmatter einer Markdown-Datei.

    Erwartetes Format:

        ---
        title: ...
        description: ...
        ---
    """

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
    description = (
        description_match.group(1).strip()
        if description_match
        else ""
    )

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
    """
    Findet alle nummerierten Kategorieverzeichnisse im Kochbuch.
    """

    categories = [
        path
        for path in ROOT.iterdir()
        if path.is_dir() and re.match(r"^\d+_", path.name)
    ]

    return sorted(categories, key=lambda path: path.name)


def find_recipes(category: Path):
    """
    Findet alle Markdown-Rezepte innerhalb einer Kategorie.

    README.md und index.md werden ignoriert.
    """

    return sorted(
        path
        for path in category.glob("*.md")
        if path.name not in {"README.md", "index.md"}
    )


def generate_category_list(categories):
    """
    Erzeugt den automatisch generierten Kategorienbereich für README.md.
    """

    lines = []

    for category in categories:
        label = category_name(category)
        relative_path = category.relative_to(ROOT).as_posix()

        lines.append(f"- [{label}]({relative_path}/)")

    return "\n".join(lines)


def generate_recipe_list(categories):
    """
    Erzeugt den automatisch generierten Rezeptbereich für index.md.
    """

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
    """
    Ersetzt ausschließlich den Bereich zwischen START und END.

    Alles davor und danach bleibt unverändert.
    """

    start = text.find(start_marker)
    end = text.find(end_marker)

    if start == -1 or end == -1:
        raise RuntimeError(
            f"Marker nicht gefunden:\n"
            f"  START: {start_marker}\n"
            f"  END:   {end_marker}"
        )

    if end < start:
        raise RuntimeError(
            f"Reihenfolge der Marker ist falsch:\n"
            f"  START: {start_marker}\n"
            f"  END:   {end_marker}"
        )

    before = text[:start]
    after = text[end + len(end_marker):]

    replacement = (
        start_marker
        + "\n\n"
        + generated_content.rstrip()
        + "\n\n"
        + end_marker
    )

    return before + replacement + after


def update_index(categories):
    """
    Aktualisiert ausschließlich den automatisch generierten Rezeptbereich
    in index.md.

    Manuelle Inhalte oberhalb und unterhalb des Bereichs bleiben erhalten.
    """

    if not INDEX.exists():
        raise RuntimeError(
            "index.md existiert nicht. "
            "Bitte zunächst eine index.md mit den AUTO-GENERATED-Markern anlegen."
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
    """
    Aktualisiert ausschließlich den automatisch generierten Kategorienbereich
    in README.md.

    Manuelle Inhalte außerhalb dieses Bereichs bleiben erhalten.
    """

    if not README.exists():
        raise RuntimeError(
            "README.md existiert nicht. "
            "Bitte zunächst eine README.md mit den AUTO-GENERATED-Markern anlegen."
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
    categories = find_categories()

    if not categories:
        raise SystemExit(
            "❌ Keine Kategorieverzeichnisse gefunden."
        )

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
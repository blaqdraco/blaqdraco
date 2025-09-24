import re
from pathlib import Path

README_PATH = Path(__file__).resolve().parents[1] / "README.md"
PORTRAIT_PATH = Path(__file__).resolve().parent / "ascii-portrait.txt"

START = "<!-- START:ASCII-PORTRAIT -->"
END = "<!-- END:ASCII-PORTRAIT -->"


def replace_block(text: str, new_block: str) -> str:
    pattern = re.compile(rf"{re.escape(START)}[\s\S]*?{re.escape(END)}", re.MULTILINE)
    replacement = f"{START}\n{new_block.rstrip()}\n{END}"
    if not pattern.search(text):
        raise SystemExit("Markers not found in README; aborting.")
    return pattern.sub(replacement, text)


def main():
    if not PORTRAIT_PATH.exists():
        raise SystemExit(f"Portrait file not found: {PORTRAIT_PATH}")
    ascii_art = PORTRAIT_PATH.read_text(encoding="utf-8")
    readme_text = README_PATH.read_text(encoding="utf-8")
    updated = replace_block(readme_text, ascii_art)
    README_PATH.write_text(updated, encoding="utf-8")
    print("README updated with ASCII portrait.")


if __name__ == "__main__":
    main()

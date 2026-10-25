"""Build the board's poster list from the posters folder.

Name each poster file with its order number, then the unit name:
    1 Education and Training Unit.png
    2 - General Services Unit.jpg
    3_Education for Development Scholarship Program.jpeg

This script then:
  * makes a light web copy of each poster in assets/entries/ (same look, much smaller file)
  * writes posters.js, which tells the board the order and each unit name

Run it with "Update Posters.bat" (double-click) whenever you add, rename or replace a poster.
"""
import json
import re
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is missing. Install it once with:  python -m pip install pillow")

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "posters"
OUT = ROOT / "assets" / "entries"
LIST = ROOT / "posters.js"
IMAGE_TYPES = {".png", ".jpg", ".jpeg", ".webp"}
MAX_HEIGHT = 1800   # plenty for a 4K TV; keeps each poster a few hundred KB

NAME = re.compile(r"^\s*(\d+)\s*[-_.)]*\s*(.*?)\s*$")


def web_copy(src: Path, dst: Path) -> None:
    im = Image.open(src)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, (0, 0, 0))
        bg.paste(im, mask=im.getchannel("A"))
        im = bg
    else:
        im = im.convert("RGB")
    if im.height > MAX_HEIGHT:
        im = im.resize((round(im.width * MAX_HEIGHT / im.height), MAX_HEIGHT), Image.LANCZOS)
    im.save(dst, quality=88, optimize=True, progressive=True)


def main() -> None:
    SRC.mkdir(exist_ok=True)
    found, skipped = [], []
    for f in SRC.iterdir():
        if f.suffix.lower() not in IMAGE_TYPES:
            continue
        m = NAME.match(f.stem)
        if not m:
            # no number yet: still shown, after the numbered ones, with the file name as the unit
            skipped.append(f.name)
            found.append((10**6, f.stem.replace("_", " ").strip(), f))
            continue
        found.append((int(m.group(1)), m.group(2).replace("_", " ").strip(), f))
    found.sort(key=lambda t: (t[0], t[1].lower()))
    if not found:
        sys.exit(f"No poster images found in {SRC}. Nothing was changed.")

    numbers = [n for n, _, _ in found if n < 10**6]
    dupes = sorted({n for n in numbers if numbers.count(n) > 1})

    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.jpg"):
        old.unlink()

    posters = []
    for order, (num, unit, f) in enumerate(found, 1):
        dst = OUT / f"{order:02d}.jpg"
        web_copy(f, dst)
        posters.append({"image": f"assets/entries/{dst.name}", "unit": unit})
        shown = "  -" if num >= 10**6 else f"{num:>3}"
        print(f"  {shown}  {unit or '(no unit name yet)':<50} {f.name}")

    LIST.write_text(
        "// Made by update-posters.py from the posters folder. Don't edit by hand:\n"
        "// rename the files in the posters folder and run Update Posters.bat again.\n"
        "window.POSTERS = " + json.dumps(posters, indent=2, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )

    print(f"\n{len(posters)} poster(s) ready, in this order.")
    if dupes:
        print(f"WARNING: these numbers are used more than once: {', '.join(map(str, dupes))}")
    if skipped:
        print("NO NUMBER YET (shown at the end, in name order). Add a number to set their place:")
        for name in skipped:
            print("   ", name)


if __name__ == "__main__":
    main()

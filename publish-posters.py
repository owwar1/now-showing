"""Bring in new or edited posters, rebuild the list, and upload the board.

1. Any numbered poster dropped into assets/ (e.g. "03 - ETU.png") is moved into
   posters/. An older file with the same number is moved to posters/old/ first.
2. Runs update-posters.py (web copies + posters.js).
3. Saves the change in git and uploads it with the owwar1 GitHub login.

Run it with "Publish Posters.bat".
"""
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS, POSTERS, OLD = ROOT / "assets", ROOT / "posters", ROOT / "posters" / "old"
IMAGE_TYPES = {".png", ".jpg", ".jpeg", ".webp"}
NUMBERED = re.compile(r"^\s*(\d+)\s*[-_.)]")
GH = r"C:\Program Files\GitHub CLI\gh.exe"
GH_ACCOUNTS = ["owwar1", "kamotegram-ph"]   # same account; the second is its old name


def number_of(p: Path):
    m = NUMBERED.match(p.stem)
    return int(m.group(1)) if m else None


def bring_in_new_posters() -> int:
    POSTERS.mkdir(exist_ok=True)
    OLD.mkdir(exist_ok=True)
    moved = 0
    for f in sorted(ASSETS.iterdir()):
        if f.suffix.lower() not in IMAGE_TYPES or number_of(f) is None:
            continue
        n = number_of(f)
        for existing in POSTERS.iterdir():
            if existing.is_file() and number_of(existing) == n:
                stamp = datetime.now().strftime("%Y%m%d-%H%M")
                shutil.move(str(existing), str(OLD / f"{existing.stem} (replaced {stamp}){existing.suffix}"))
                print(f"  older #{n} moved to posters/old: {existing.name}")
        shutil.move(str(f), str(POSTERS / f.name))
        print(f"  added: {f.name}")
        moved += 1
    return moved


def run(cmd, **kw):
    return subprocess.run(cmd, cwd=ROOT, text=True, **kw)


def owwar1_token():
    for acct in GH_ACCOUNTS:
        r = run([GH, "auth", "token", "--user", acct], capture_output=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    return None


def main() -> None:
    print("Bringing in new posters from assets...")
    if not bring_in_new_posters():
        print("  (none found in assets)")

    print("\nRebuilding the poster list...")
    if run([sys.executable, "update-posters.py"]).returncode != 0:
        sys.exit("Update failed; nothing was uploaded.")

    run(["git", "add", "-A"])
    if run(["git", "diff", "--cached", "--quiet"]).returncode == 0:
        print("\nNothing changed since the last upload.")
        return
    run(["git", "commit", "-q", "-m", "Update posters",
         "-m", "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"])

    token = owwar1_token()
    if not token:
        sys.exit("\nSaved locally, but couldn't find the owwar1 GitHub login to upload.")
    helper = f'!"{GH}" auth git-credential'
    env = dict(__import__("os").environ, GH_TOKEN=token)
    r = run(["git", "-c", "credential.helper=", "-c", f"credential.helper={helper}",
             "-c", "credential.https://github.com.helper=",
             "-c", f"credential.https://github.com.helper={helper}",
             "push", "-q", "origin", "main"], env=env)
    if r.returncode != 0:
        sys.exit("\nSaved locally, but the upload failed. Ask Claude to upload it.")
    print("\nUploaded. The website updates within a minute or two:")
    print("  https://owwar1.github.io/now-showing/")


if __name__ == "__main__":
    main()

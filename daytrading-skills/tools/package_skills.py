#!/usr/bin/env python3
"""Build one self-contained zip per skill for claude.ai / API skill uploads.

Inside the plugin, every skill shares ../../lib and ../../reference. An uploaded
skill only gets its own folder, so each zip vendors the engine and the data
notes into the skill and rewrites the SKILL.md paths to match.

  python3 tools/package_skills.py            # all skills -> dist/<skill>.zip
  python3 tools/package_skills.py time-machine key-levels
"""

import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


def package(skill_dir: Path) -> Path:
    name = skill_dir.name
    with tempfile.TemporaryDirectory() as tmp:
        dst = Path(tmp) / name
        shutil.copytree(skill_dir, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        shutil.copytree(ROOT / "lib", dst / "lib", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        shutil.copytree(ROOT / "reference", dst / "reference")
        shutil.copy2(ROOT / "requirements.txt", dst / "requirements.txt")
        md = dst / "SKILL.md"
        md.write_text(md.read_text()
                      .replace("${CLAUDE_SKILL_DIR}/../../reference/", "${CLAUDE_SKILL_DIR}/reference/")
                      .replace("${CLAUDE_SKILL_DIR}/../../requirements.txt", "${CLAUDE_SKILL_DIR}/requirements.txt"))
        DIST.mkdir(exist_ok=True)
        out = DIST / f"{name}.zip"
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for f in sorted(dst.rglob("*")):
                if f.is_file():
                    z.write(f, f.relative_to(Path(tmp)))
    return out


def main(argv: list[str]) -> int:
    skills = sorted(p for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").exists())
    if argv:
        skills = [s for s in skills if s.name in argv]
        missing = set(argv) - {s.name for s in skills}
        if missing:
            print(f"unknown skills: {', '.join(sorted(missing))}", file=sys.stderr)
            return 2
    for s in skills:
        print(f"{package(s).relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

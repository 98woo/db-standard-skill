from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = [
    "validate_skill_structure.py",
    "validate_yaml_templates.py",
    "validate_execution_context_schema.py",
]


def main() -> int:
    for script in SCRIPTS:
        path = ROOT / "scripts" / script
        print(f"\n== {script} ==", flush=True)
        result = subprocess.run([sys.executable, str(path)], cwd=ROOT)
        if result.returncode != 0:
            return result.returncode
    print("\nAll local validations passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

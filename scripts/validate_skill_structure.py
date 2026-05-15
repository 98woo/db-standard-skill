from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required: pip install pyyaml") from exc


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "db-standard-ddl-workflow"

REQUIRED_REFERENCES = [
    "00-rule-priority.md",
    "05-startup-onboarding.md",
    "10-execution-context.md",
    "11-dbms-profile.md",
    "12-metadata-artifact-model.md",
    "13-schema-routing.md",
    "14-bootstrap-role-mapping.md",
    "20-request-contract.md",
    "25-catalog-query-templates.md",
    "30-normalization-rules.md",
    "40-table-naming.md",
    "50-column-domain-decision.md",
    "60-sql-rendering.md",
    "70-blocking-rules.md",
    "80-dbms-dialects.md",
    "81-spatial-rules.md",
    "90-output-contract.md",
    "95-review-checklist.md",
]

REQUIRED_ASSETS = [
    "initial-context-new-project.template.md",
    "initial-context-existing-project.template.md",
    "execution-context.template.yaml",
    "request-template.txt",
    "output-template.md",
    "mcp-tool-contract.md",
]


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"[OK] {message}")


def parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(f"{path} missing YAML frontmatter")
    end = text.find("\n---", 4)
    if end == -1:
        fail(f"{path} frontmatter is not closed")
    data = yaml.safe_load(text[4:end]) or {}
    if not isinstance(data, dict):
        fail(f"{path} frontmatter is not a mapping")
    return data


def main() -> int:
    if not SKILL_DIR.is_dir():
        fail(f"missing skill directory: {SKILL_DIR}")
    ok("skill directory exists")

    skill_md = SKILL_DIR / "SKILL.md"
    if not skill_md.is_file():
        fail("missing SKILL.md")
    frontmatter = parse_frontmatter(skill_md)
    for key in ("name", "description"):
        if not frontmatter.get(key):
            fail(f"SKILL.md frontmatter missing {key}")
    if frontmatter["name"] != "db-standard-ddl-workflow":
        fail("SKILL.md name must be db-standard-ddl-workflow")
    ok("SKILL.md frontmatter")

    openai_yaml = SKILL_DIR / "agents" / "openai.yaml"
    if not openai_yaml.is_file():
        fail("missing agents/openai.yaml")
    openai_data = yaml.safe_load(openai_yaml.read_text(encoding="utf-8")) or {}
    if openai_data.get("policy", {}).get("allow_implicit_invocation") is not False:
        fail("agents/openai.yaml policy.allow_implicit_invocation must be false")
    ok("agents/openai.yaml")

    for name in REQUIRED_REFERENCES:
        if not (SKILL_DIR / "references" / name).is_file():
            fail(f"missing reference: {name}")
    ok("required references")

    for name in REQUIRED_ASSETS:
        if not (SKILL_DIR / "assets" / name).is_file():
            fail(f"missing asset: {name}")
    ok("required assets")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

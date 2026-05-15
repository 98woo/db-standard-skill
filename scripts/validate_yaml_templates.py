from __future__ import annotations

from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required: pip install pyyaml") from exc


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "db-standard-ddl-workflow"


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"[OK] {message}")


def extract_yaml_block(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    marker = "```yaml"
    start = text.find(marker)
    if start == -1:
        fail(f"{path} missing fenced yaml block")
    start += len(marker)
    end = text.find("```", start)
    if end == -1:
        fail(f"{path} yaml block is not closed")
    return text[start:end]


def parse_yaml(name: str, text: str) -> object:
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError as exc:
        fail(f"{name} YAML parse failed: {exc}")


def main() -> int:
    template_files = [
        SKILL_DIR / "assets" / "initial-context-new-project.template.md",
        SKILL_DIR / "assets" / "initial-context-existing-project.template.md",
    ]

    for path in template_files:
        data = parse_yaml(str(path), extract_yaml_block(path))
        if not isinstance(data, dict):
            fail(f"{path} YAML block must be a mapping")
        ok(f"{path.name} YAML block")

    context_path = SKILL_DIR / "assets" / "execution-context.template.yaml"
    data = parse_yaml(str(context_path), context_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        fail("execution-context.template.yaml must be a mapping")
    ok("execution-context.template.yaml")

    openai_path = SKILL_DIR / "agents" / "openai.yaml"
    parse_yaml(str(openai_path), openai_path.read_text(encoding="utf-8"))
    ok("agents/openai.yaml YAML")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required: pip install pyyaml") from exc


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "db-standard-ddl-workflow"

CANONICAL_REQUIRED_PATHS = [
    "startup_mode",
    "project.project_id",
    "project.project_nm",
    "dbms.type",
    "dbms.version",
    "dbms.connection_target",
    "dbms.profile",
    "standard_repository.logical_nm",
    "standard_repository.db_nm",
    "standard_repository.dictionary_schema_nm",
    "standard_repository.namespace_kind",
    "standard_repository.object_identifier_pattern",
    "standard_repository.word_table_nm",
    "standard_repository.domain_table_nm",
    "standard_repository.term_table_nm",
    "standard_repository.word_seq",
    "standard_repository.term_seq",
    "metadata_repository.db_nm",
    "metadata_repository.project_schema_nm",
    "metadata_repository.table_definition.table_nm",
    "metadata_repository.table_definition.field_map",
    "metadata_repository.column_definition.table_nm",
    "metadata_repository.column_definition.field_map",
    "physical_target.db_nm",
    "physical_target.target_namespace_map",
    "run_control.run_mode",
    "run_control.catalog_lookup_mode",
    "run_control.write_execution_enabled",
]

LEGACY_TOP_LEVEL_ALIASES = {
    "project_id",
    "project_nm",
    "dbms_type",
    "dbms_version",
    "dbms_profile",
    "target_db_nm",
    "target_namespace_map",
    "meta_schema_nm",
    "tbl_dfn_tbl_nm",
    "col_dfn_tbl_nm",
    "tbl_dfn_field_map",
    "col_dfn_field_map",
    "std_word_seq",
    "std_trm_seq",
    "tbl_dfn_seq",
    "col_dfn_seq",
    "run_mode",
    "catalog_lookup_mode",
    "write_execution_enabled",
}


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"[OK] {message}")


def get_path(data: Any, path: str) -> tuple[bool, Any]:
    current = data
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return False, None
        current = current[part]
    return True, current


def extract_yaml_block(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    start = text.index("```yaml") + len("```yaml")
    end = text.index("```", start)
    data = yaml.safe_load(text[start:end])
    if not isinstance(data, dict):
        fail(f"{path.name} YAML block must be a mapping")
    return data


def validate_required_paths(name: str, data: dict, paths: list[str]) -> None:
    missing = [path for path in paths if not get_path(data, path)[0]]
    if missing:
        fail(f"{name} missing required path(s): {', '.join(missing)}")
    ok(f"{name} canonical paths")


def validate_no_legacy_top_level(name: str, data: dict) -> None:
    legacy = sorted(LEGACY_TOP_LEVEL_ALIASES.intersection(data))
    if legacy:
        fail(f"{name} contains legacy top-level alias(es): {', '.join(legacy)}")
    ok(f"{name} has no legacy top-level aliases")


def main() -> int:
    context_path = SKILL_DIR / "assets" / "execution-context.template.yaml"
    context = yaml.safe_load(context_path.read_text(encoding="utf-8"))
    if not isinstance(context, dict):
        fail("execution-context.template.yaml must be a mapping")

    validate_required_paths("execution-context.template.yaml", context, CANONICAL_REQUIRED_PATHS)
    validate_no_legacy_top_level("execution-context.template.yaml", context)

    for filename in (
        "initial-context-new-project.template.md",
        "initial-context-existing-project.template.md",
    ):
        data = extract_yaml_block(SKILL_DIR / "assets" / filename)
        minimal_paths = [
            "startup_mode",
            "project.project_id",
            "project.project_nm",
            "dbms.type",
            "dbms.version",
            "dbms.connection_target",
            "dbms.profile",
            "standard_repository.logical_nm",
            "metadata_repository.db_nm",
            "metadata_repository.project_schema_nm",
            "physical_target.db_nm",
            "physical_target.target_namespace_map",
            "run_control.run_mode",
            "run_control.catalog_lookup_mode",
            "run_control.write_execution_enabled",
        ]
        validate_required_paths(filename, data, minimal_paths)
        validate_no_legacy_top_level(filename, data)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

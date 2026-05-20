# 90. 출력 계약 (Output Contract)

이 문서는 skill의 최종 응답 형식을 정의한다.

## 1. 기본 섹션

아래 순서를 권장한다.

1. Validation Summary
2. Resolved Inputs
3. Blocking Issues
4. Pending Decisions
5. Lookup SQL Bundle
6. Definition Change Plan
7. Preview INSERT / UPDATE SQL
8. Preview DDL SQL
9. Notes

## 2. 상태 표기

상태는 아래 중 하나 이상을 포함할 수 있다.

- `VALID`
- `BLOCKED`
- `PENDING_DECISION`
- `PREVIEW_ONLY`

## 3. Markdown 템플릿

~~~md
## Validation Summary
- status:
- run_mode:
- dbms:
- request_mode:
- execution_possible:

## Resolved Inputs
- database:
- target_namespace:
- target_namespace_kind:
- subject_area_cd:
- table_kind:
- table_owner:
- logical_table_name:
- physical_table_name:
- columns:

## Blocking Issues
- none / details

## Pending Decisions
- none / details

## Lookup SQL Bundle
```sql
-- SELECT ...
```

## Definition Change Plan
- table_definition: INSERT / UPDATE / NO-OP
- column_definition: INSERT / UPDATE / DELETE / DISABLE / NO-OP
- reason:

## Preview INSERT / UPDATE SQL
```sql
-- INSERT ...
-- UPDATE ...
```

## Preview DDL SQL
```sql
-- CREATE TABLE ...
-- ALTER TABLE ...
-- CREATE INDEX ...
-- COMMENT ...
```

## Notes
- comments
~~~

## 4. blocked 응답 규칙

blocked라도 아래는 최대한 반환한다.

- 어떤 규칙에 막혔는지
- 어떤 입력이 더 필요한지
- 재시도를 위해 필요한 lookup SQL 또는 예시

## 5. preview-only 응답 규칙

preview-only이면 아래를 명시한다.

- 실제 DB 미반영
- 실행 불가 이유
- 실행 가능 조건

## 6. consistency rules

최종 출력은 아래가 일치해야 한다.

- `physical_table_name` <-> CREATE TABLE table name
- `target_namespace` <-> CREATE TABLE / ALTER TABLE / COMMENT target namespace
- `subject_area_cd` / `table_owner` <-> `target_namespace_map` routing result
- `physical_column_name` <-> column definitions / comments / indexes
- definition change plan <-> physical CREATE / ALTER / DROP DDL
- `logical_table_name` <-> COMMENT ON TABLE
- `logical_column_name` <-> COMMENT ON COLUMN
- index / constraint names <-> final rendered identifier case

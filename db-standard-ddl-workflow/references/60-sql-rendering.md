# 60. SQL 렌더링 규칙

이 문서는 preview SQL bundle을 어떤 순서와 형식으로 출력할지 정의한다.

## 목차

- [1. 공통 원칙](#1-공통-원칙)
- [2. 출력 순서](#2-출력-순서)
- [3. 신규 프로젝트 정의서 테이블 bootstrap DDL 규칙](#3-신규-프로젝트-정의서-테이블-bootstrap-ddl-규칙)
- [4. 테이블 정의서 INSERT preview 규칙](#4-테이블-정의서-insert-preview-규칙)
- [5. 컬럼 정의서 INSERT preview 규칙](#5-컬럼-정의서-insert-preview-규칙)
- [6. 신규 도메인 INSERT preview 템플릿](#6-신규-도메인-insert-preview-템플릿)
- [7. 신규 단어 INSERT preview 템플릿](#7-신규-단어-insert-preview-템플릿)
- [8. 신규 용어 INSERT preview 템플릿](#8-신규-용어-insert-preview-템플릿)
- [9. CREATE TABLE preview 템플릿](#9-create-table-preview-템플릿)
- [10. PK / FK 렌더링 규칙](#10-pk--fk-렌더링-규칙)
- [11. INDEX / UNIQUE INDEX 렌더링 규칙](#11-index--unique-index-렌더링-규칙)
- [12. COMMENT 렌더링 규칙](#12-comment-렌더링-규칙)
- [13. 시퀀스 렌더링 규칙](#13-시퀀스-렌더링-규칙)
- [14. 데이터 길이 표현 규칙](#14-데이터-길이-표현-규칙)
- [15. preview와 실행 순서 구분](#15-preview와-실행-순서-구분)

## 1. 공통 원칙

- 모든 SQL은 전체 식별자(full identifier)를 사용한다.
- preview SQL과 execution SQL을 구분한다.
- logical identifier와 DBMS rendered identifier를 혼동하지 않는다.
- 이 문서의 SQL 블록은 logical template이다. 최종 출력 시 DBMS profile과 dialect를 적용해 object identifier, casing, bind marker, sequence expression을 렌더링한다.
- 동일한 `table_id` role 값은 테이블 정의서 / 컬럼 정의서 INSERT에서 일관되게 재사용돼야 한다.
- quote identifier는 프로젝트 규칙이 없는 한 사용하지 않는다.

## 2. 출력 순서

추천 출력 순서:

1. validation summary
2. blockers
3. pending decisions
4. lookup SQL bundle
5. 신규 도메인 INSERT preview (필요 시, 명시 승인 대상)
6. 신규 단어 INSERT preview (필요 시, 명시 승인 대상)
7. 신규 용어 INSERT preview (필요 시, 명시 승인 대상)
8. 신규 프로젝트 정의서 테이블 bootstrap DDL preview (필요 시)
9. 정의서 갱신 계획
10. 테이블 정의서 INSERT / UPDATE / NO-OP preview
11. 컬럼 정의서 INSERT / UPDATE / DELETE / 비활성화 / NO-OP preview
12. CREATE SEQUENCE preview (요청 시)
13. CREATE TABLE / ALTER TABLE / DROP COLUMN preview
14. PK / FK preview
15. INDEX / UNIQUE INDEX preview
16. COMMENT preview

정의서 갱신 계획 없이 물리 CREATE / ALTER / DROP DDL만 출력하지 않는다.

## 3. 신규 프로젝트 정의서 테이블 bootstrap DDL 규칙

신규 프로젝트에서 테이블 정의서 / 컬럼 정의서 테이블 자체를 생성할 때 적용한다.
이 DDL은 업무 테이블 표준화 DDL이 아니며, 표준 단어 / 용어 / 도메인 사전을 사용하지 않는다.

규칙:

- 한글 테이블명은 자동 `snake_case` 물리 테이블명으로 변환한다.
- 한글 컬럼명은 자동 `snake_case` 물리 컬럼명으로 변환한다.
- 모든 컬럼 타입은 `text`로 렌더링한다.
- 한글 테이블명은 `COMMENT ON TABLE`로 렌더링한다.
- 한글 컬럼명은 `COMMENT ON COLUMN`으로 렌더링한다.
- 웹 검색을 사용하지 않는다.
- PK / NOT NULL / UNIQUE는 사용자 명시 정책이 있을 때만 렌더링한다.

generic template:

```sql
-- optional, only when the DBMS profile supports namespace creation
{create_standard_artifact_namespace_if_missing_sql}

CREATE TABLE {standard_artifact_object_identifier} (
  {generated_definition_columns_as_text}
);

COMMENT ON TABLE {standard_artifact_object_identifier}
  IS '{korean_definition_table_name}';

COMMENT ON COLUMN {standard_artifact_object_identifier}.{generated_column_name}
  IS '{korean_column_name}';
```

`standard_artifact_object_identifier`는 DBMS profile에 따라 아래처럼 렌더링한다.

- PostgreSQL / SQL Server: `{schema}.{table}`
- Oracle: `{owner}.{table}`
- MySQL / MariaDB: `{database}.{table}`

정의서 테이블 생성 후 에이전트는 생성된 물리 컬럼명을 기준으로 내부 field map을 자동 생성한다.

## 4. 테이블 정의서 INSERT preview 규칙

테이블 정의서 INSERT는 고정 컬럼 목록을 사용하지 않는다.
`references/12-metadata-artifact-model.md`의 `table_definition.field_map`을 기준으로 렌더링한다.

필수 role:

- `table_id`
- `target_db`
- `target_schema`
- `owner`
- `logical_table_name`
- `physical_table_name`
- `table_type`

generic template:

```sql
INSERT INTO {standard_artifact_object_identifier(metadata_repository.table_definition.table_nm)} (
  {table_definition_columns_from_field_map}
) VALUES (
  {table_definition_values_from_resolved_context}
);
```

`target_schema` role에는 확정된 `target_namespace_nm`을 저장한다.
정의서 호환을 위해 role 이름은 `target_schema`를 유지하지만 값의 의미는 DBMS profile의 namespace다.
테이블 정의서 중복 검사는 `target_db + target_schema + physical_table_name` 기준으로 수행한다.

시퀀스 next value 표현은 `{next_value(sequence_name)}` placeholder를 사용하고,
최종 출력 시 `references/80-dbms-dialects.md` 규칙으로 DBMS별 문법을 적용한다.

## 5. 컬럼 정의서 INSERT preview 규칙

컬럼 정의서 INSERT도 고정 컬럼 목록을 사용하지 않는다.
`references/12-metadata-artifact-model.md`의 `column_definition.field_map`을 기준으로 렌더링한다.

필수 role:

- `column_id`
- `table_id`
- `logical_column_name`
- `physical_column_name`
- `data_type`
- `data_length`
- `nullable`
- `primary_key`
- `foreign_key`

generic template:

```sql
INSERT INTO {standard_artifact_object_identifier(metadata_repository.column_definition.table_nm)} (
  {column_definition_columns_from_field_map}
) VALUES (
  {column_definition_values_from_resolved_context}
);
```

컬럼 정의서는 `table_id`로 테이블 정의서를 참조하는 구조를 권장한다.
`table_id`가 없다면 컬럼 정의서 field map에도 `target_db`, `target_schema`, `physical_table_name` 역할이 필요하다.

## 5.1 요청 유형별 정의서 갱신 규칙

업무 테이블 DDL preview를 생성하는 모든 요청은 먼저 정의서 갱신 계획을 만든다.

### create_table

- 테이블 정의서 중복 검사를 수행한다.
- 중복이 없으면 테이블 정의서 INSERT preview를 생성한다.
- 요청 전체 컬럼에 대한 컬럼 정의서 INSERT preview를 생성한다.
- 그 다음 CREATE TABLE / PK / FK / INDEX / COMMENT preview를 생성한다.

### alter_add_columns

- 테이블 정의서 row 존재 여부를 `target_db + target_schema + physical_table_name` 기준으로 확인한다.
- 테이블 정의서 row가 없으면 blocked 또는 pending decision이다. 임의로 신규 테이블 정의서 INSERT를 생성하지 않는다.
- 테이블 속성 변경이 없으면 테이블 정의서는 NO-OP로 명시한다.
- 추가 컬럼마다 컬럼 정의서 INSERT preview를 생성한다.
- 그 다음 ALTER TABLE ADD COLUMN / COMMENT / INDEX / 제약조건 preview를 생성한다.

### alter_modify_columns

- 대상 컬럼 정의서 row 존재 여부를 확인한다.
- 컬럼 정의서 UPDATE preview를 생성한다.
- 컬럼명이 바뀌면 논리 컬럼명과 물리 컬럼명 변경 내용을 함께 반영한다.
- 그 다음 ALTER COLUMN / RENAME COLUMN / COMMENT / INDEX / 제약조건 preview를 생성한다.

### drop_columns

- 대상 컬럼 정의서 row 존재 여부를 확인한다.
- 프로젝트 정책에 따라 컬럼 정의서 DELETE, 비활성화 UPDATE, 또는 이력 처리 SQL을 생성한다.
- 정책이 없으면 DROP COLUMN preview를 만들지 않고 pending decision으로 돌린다.
- 정의서 처리 방식이 확정된 뒤에만 DROP COLUMN preview를 생성한다.

## 6. 신규 도메인 INSERT preview 템플릿

신규 도메인 INSERT는 표준사전 보완 작업이다.
기존 도메인 exact / 유사 후보 조회 결과 재사용 가능한 도메인이 없고,
표준 사전 관리자 승인 또는 프로젝트 표준 정책 근거가 있을 때만 preview로 제시한다.
승인 전에는 물리 DDL 실행 bundle에 포함하지 않는다.

```sql
INSERT INTO db_standard.tb_db_com_std_dmn (
  dmn_nm,
  dmn_group_nm,
  dmn_clsf_nm,
  data_type_nm,
  data_len,
  data_dc_len,
  prm_vl_expln,
  strg_frm_expln,
  exprs_frm_expln
) VALUES (
  :dmn_nm,
  :dmn_group_nm,
  :dmn_clsf_nm,
  :data_type_nm,
  :data_len,
  :data_dc_len,
  :prm_vl_expln,
  :strg_frm_expln,
  :exprs_frm_expln
);
```

실제 표준 도메인 테이블에 추가 필수 컬럼이 있으면 live catalog 조회 결과 또는 프로젝트 정책에 따라 preview를 보완한다.

## 7. 신규 단어 INSERT preview 템플릿

표준 단어 / 용어 / 도메인 사전은 `db_standard.db_standard`에 이미 구축되어 있다는 전제를 둔다.
따라서 이 preview는 사전 테이블 생성용이 아니며, 누락된 표준 항목을 보완해야 할 때만 별도 승인 대상으로 출력한다.
승인 전에는 물리 DDL 실행 bundle에 포함하지 않는다.

실제 표준 단어 테이블 구조는 프로젝트에 따라 일부 컬럼이 더 있을 수 있으므로,
아래는 최소 preview 템플릿이다.

```sql
INSERT INTO db_standard.tb_db_com_std_word (
  word_no,
  word_nm,
  word_eng_abbr_nm,
  dmn_yn,
  dmn_clsf_nm
) VALUES (
  {next_value(standard_repository.word_seq)},
  :word_nm,
  :word_eng_abbr_nm,
  :dmn_yn,
  :dmn_clsf_nm
);
```

## 8. 신규 용어 INSERT preview 템플릿

신규 용어 INSERT도 표준사전 보완 작업이다.
term exact lookup과 term synonym lookup이 모두 실패했고, 단어 / 도메인 판단으로 최종 용어가 확정된 경우에만 preview로 제시한다.
승인 전에는 물리 DDL 실행 bundle에 포함하지 않는다.

```sql
INSERT INTO db_standard.tb_db_com_std_trm (
  trm_no,
  enct_sec_nm,
  trm_nm,
  trm_expln,
  trm_eng_abbr_nm,
  dmn_nm,
  prm_vl_expln,
  strg_frm_expln,
  exprs_frm_expln,
  pbadms_std_cd_nm,
  jrsd_inst_nm,
  synm_list_expln,
  enct_cycl_cd,
  rvsn_sec_nm,
  rvsn_cn,
  rvsn_rsn
) VALUES (
  {next_value(standard_repository.term_seq)},
  '신규',
  :trm_nm,
  '-',
  :trm_eng_abbr_nm,
  :dmn_nm,
  :prm_vl_expln,
  :strg_frm_expln,
  :exprs_frm_expln,
  '-',
  '-',
  '-',
  '-',
  '-',
  '-',
  '-'
);
```

## 9. CREATE TABLE preview 템플릿

`target_object_identifier`는 DBMS profile의 object identifier pattern으로 렌더링한 최종 업무 테이블 식별자다.

예:
- PostgreSQL / SQL Server: `{schema}.{table}`
- Oracle: `{owner}.{table}`
- MySQL / MariaDB: `{database}.{table}`

```sql
CREATE TABLE {target_object_identifier} (
  {column_definition_lines}
);
```

`column_definition_lines` 각 행에는 아래 정보가 들어간다.

- physical column name
- data type
- length / precision / scale
- nullability
- default (있을 때만)

## 9.1 ALTER TABLE preview 템플릿

기존 테이블 변경 요청은 요청 유형별 정의서 갱신 계획을 먼저 생성한 뒤 아래 물리 DDL preview를 생성한다.

### alter_add_columns

```sql
ALTER TABLE {target_object_identifier}
  ADD COLUMN {physical_column_name} {data_type_and_constraints};
```

### alter_modify_columns

DBMS별 문법 차이가 크므로 logical template로 출력하고, 최종 출력 시 `references/80-dbms-dialects.md`의 profile을 적용한다.

```sql
ALTER TABLE {target_object_identifier}
  ALTER COLUMN {physical_column_name} {alter_column_action};
```

컬럼명 변경이 필요한 경우:

```sql
ALTER TABLE {target_object_identifier}
  RENAME COLUMN {old_physical_column_name} TO {new_physical_column_name};
```

### drop_columns

정의서 DELETE / 비활성화 / 이력 처리 정책이 확정된 경우에만 생성한다.

```sql
ALTER TABLE {target_object_identifier}
  DROP COLUMN {physical_column_name};
```

## 10. PK / FK 렌더링 규칙

### PK
```sql
ALTER TABLE {target_object_identifier}
  ADD CONSTRAINT {pk_name}
  PRIMARY KEY ({pk_columns});
```

- 이름 규칙: `PK_<TABLE_NAME>`

### FK
```sql
ALTER TABLE {target_object_identifier}
  ADD CONSTRAINT {fk_name}
  FOREIGN KEY ({fk_columns})
  REFERENCES {referenced_table_identifier} ({referenced_columns});
```

- 이름 규칙: `FK_<CURRENT_TABLE>_<REFERENCED_TABLE>`
- `referenced_table_identifier`는 반드시 DBMS profile에 맞는 namespace-qualified identifier다.

## 11. INDEX / UNIQUE INDEX 렌더링 규칙

### 일반 인덱스
```sql
CREATE INDEX {idx_name}
  ON {target_object_identifier} ({index_columns});
```

- 이름 규칙: `IDX_<TABLE_NAME>_<COLUMN_LIST>`

### UNIQUE
기본값은 유니크 제약조건이 아니라 **유니크 인덱스**다.

```sql
CREATE UNIQUE INDEX {uidx_name}
  ON {target_object_identifier} ({index_columns});
```

- 이름 규칙: `UIDX_<TABLE_NAME>_<COLUMN_LIST>`

프로젝트가 `UK_...` 제약조건을 요구하면 AGENTS.md에서 override 한다.

## 12. COMMENT 렌더링 규칙

### Oracle / PostgreSQL 계열
```sql
COMMENT ON TABLE {target_object_identifier} IS '{logical_table_comment}';
COMMENT ON COLUMN {target_object_identifier}.{physical_column_name} IS '{logical_column_comment}';
```

`logical_table_comment`와 `logical_column_comment`는 각각 `logical_table_name`, `logical_column_name` role에서 얻은 comment 문자열을 의미한다.

### 공간정보 컬럼
```sql
COMMENT ON COLUMN {target_object_identifier}.geom IS '공간정보';
```

## 13. 시퀀스 렌더링 규칙

시퀀스는 아래 둘 중 하나일 때만 preview를 생성한다.

- 설계자가 시퀀스 생성을 명시적으로 요청
- 프로젝트 AGENTS가 기본 생성으로 강제

이름 규칙:
- `SEQ_<TABLE_NAME>`

generic preview:
```sql
CREATE SEQUENCE {sequence_name};
```

sequence 값을 INSERT에 사용할 때는 DBMS-neutral placeholder를 먼저 사용한다.

```sql
{next_value(sequence_name)}
```

최종 렌더링 예시는 `references/80-dbms-dialects.md`의 next value rendering 표를 따른다.

## 14. 데이터 길이 표현 규칙

- scale이 없으면 `data_len`
- scale이 있으면 `data_len,data_dc_len`
- DBMS 문법상 괄호/precision 표현은 renderer 단계에서 적용한다.

## 15. preview와 실행 순서 구분

사람 검토용 출력 순서와 실제 실행 순서는 달라질 수 있다.
실행 순서를 별도로 적을 때는 아래를 권장한다.

1. lookup
2. 승인된 신규 도메인 등록
3. 승인된 신규 단어 / 신규 용어 등록
4. 정의서 INSERT
5. sequence
6. create table
7. pk / fk / index
8. comment

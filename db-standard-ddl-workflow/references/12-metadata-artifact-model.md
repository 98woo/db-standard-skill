# 12. 프로젝트 산출물 모델

이 문서는 프로젝트별 테이블 정의서 / 컬럼 정의서 구조를 어떻게 만들고,
이후 업무 테이블 표준화 결과를 어디에 저장할지 field map으로 연결하는 방법을 정의한다.

## 목차

- [1. 고정 저장 위치](#1-고정-저장-위치)
- [2. 두 작업의 분리](#2-두-작업의-분리)
- [3. 신규 프로젝트 산출물 테이블 bootstrap 규칙](#3-신규-프로젝트-산출물-테이블-bootstrap-규칙)
- [4. field map의 의미](#4-field-map의-의미)
- [5. 테이블 정의서 필수 역할](#5-테이블-정의서-필수-역할)
- [6. 컬럼 정의서 필수 역할](#6-컬럼-정의서-필수-역할)
- [7. 컬럼 정의서 식별 기준](#7-컬럼-정의서-식별-기준)
- [8. 기존 프로젝트 조회 모드](#8-기존-프로젝트-조회-모드)
- [9. 차단 조건](#9-차단-조건)

## 1. 고정 저장 위치

프로젝트 산출물은 항상 `db_standard` 표준 저장소에 둔다.

- 표준 저장소 논리명: `db_standard`
- 프로젝트 산출물 namespace 논리명: `db_standard`
- 물리 database / schema / owner / namespace 렌더링: `references/11-dbms-profile.md` 기준

예:

```text
DBMS profile이 정한 db_standard 표준 저장소에 접속
{standard_artifact_object_identifier(<table_definition_table>)}
{standard_artifact_object_identifier(<column_definition_table>)}
```

주의:
- `db_standard.<table>`은 PostgreSQL / SQL Server에서는 `schema.table`, Oracle에서는 `owner.table`, MySQL / MariaDB에서는 `database.table` 의미로 렌더링될 수 있다.
- PostgreSQL처럼 database-qualified SQL을 지원하지 않는 DBMS에서는 SQL 식별자에 database명을 붙이지 않는다.
- 산출물 저장 위치는 요청의 업무 대상 namespace가 아니라 항상 DBMS profile이 정한 표준 저장소다.

## 2. 두 작업의 분리

아래 두 작업은 완전히 다른 작업이다.

### 2.1 프로젝트 산출물 테이블 bootstrap

신규 프로젝트에서 최초 1회 수행한다.

목적:

- 테이블 정의서 테이블 자체 생성
- 컬럼 정의서 테이블 자체 생성
- 이후 표준화 결과를 저장할 저장소 마련

이 단계는 표준화 작업이 아니다.

- 표준 단어 / 용어 / 도메인 사전을 조회하지 않는다.
- 한글 컬럼명을 표준 단어로 정규화하지 않는다.
- 도메인 타입 / 길이를 적용하지 않는다.
- 웹 검색을 사용하지 않는다.

### 2.2 업무 테이블 표준화

신규 / 기존 프로젝트 모두에서 반복 수행한다.

목적:

- 사용자가 요청한 실제 업무 테이블 표준화
- 표준 사전 기반 물리 테이블명 / 컬럼명 / 타입 결정
- 업무 테이블 DDL 생성
- 요청 유형별 테이블 정의서 / 컬럼 정의서 갱신 SQL 생성

이 단계는 기존 표준화 규칙을 그대로 따른다.
업무 테이블 CREATE / ALTER / DROP preview를 생성하는 모든 작업은 정의서 갱신 계획을 반드시 포함한다.
정의서 갱신 계획 없이 물리 DDL만 생성하면 안 된다.

요청 유형별 정의서 처리:

- `create_table`: 테이블 정의서 INSERT + 전체 컬럼 정의서 INSERT
- `alter_add_columns`: 테이블 정의서 row 존재 확인 + 필요 시 테이블 정의서 UPDATE 또는 NO-OP + 추가 컬럼 정의서 INSERT
- `alter_modify_columns`: 관련 컬럼 정의서 UPDATE + 필요 시 테이블 정의서 UPDATE 또는 NO-OP
- `drop_columns`: 컬럼 정의서 DELETE / 비활성화 / 이력 처리 정책 확정 후 물리 DROP COLUMN. 정책이 없으면 pending decision

## 3. 신규 프로젝트 산출물 테이블 bootstrap 규칙

신규 사용자는 테이블 정의서와 컬럼 정의서에 필요한 컬럼을 한글로 입력한다.
에이전트는 `references/14-bootstrap-role-mapping.md`를 우선 적용해 한글 컬럼명을 role과 영문 물리 컬럼명으로 매핑한다.
매핑 표에 없는 추가 컬럼만 일반적인 의미 기반 `snake_case` 물리 컬럼명으로 변환한다.

자동 변환 원칙:

- 사용자에게 영문 컬럼명 후보를 제안하지 않고 자동 적용한다.
- 필수 role은 `references/14-bootstrap-role-mapping.md`의 preferred physical column을 우선 사용한다.
- 웹 검색을 사용하지 않는다.
- 사내 표준 사전 기반 약어 생성이 아니라 일반적인 의미 기반 `snake_case` 생성이다.
- 컬럼 타입은 모두 `text`로 고정한다.
- 한글 컬럼명은 `COMMENT ON COLUMN`으로 추가한다.
- 테이블 한글명은 `COMMENT ON TABLE`로 추가한다.
- PK / NOT NULL / UNIQUE 같은 제약조건은 사용자가 명시한 경우에만 적용한다.

입력값:

- 프로젝트 산출물 namespace 논리명: `db_standard` 고정
- 테이블 정의서 한글 테이블명
- 테이블 정의서 한글 컬럼 목록
- 컬럼 정의서 한글 테이블명
- 컬럼 정의서 한글 컬럼 목록
- 실행 모드

출력 preview:

- DBMS profile에 맞는 표준 저장소 namespace 생성 또는 존재 확인 preview (없을 때만)
- `CREATE TABLE {standard_artifact_object_identifier(<generated_table_definition_table>)}`
- `CREATE TABLE {standard_artifact_object_identifier(<generated_column_definition_table>)}`
- `COMMENT ON TABLE`
- `COMMENT ON COLUMN`
- 에이전트가 생성한 내부 field map

실제 생성은 명시 승인과 write permission이 모두 있을 때만 가능하다.

## 4. field map의 의미

field map은 정의서 테이블의 컬럼명을 표준화하기 위한 규칙이 아니다.
업무 테이블 표준화 결과를 정의서 INSERT로 저장할 때,
어떤 물리 컬럼에 어떤 의미 값을 넣을지 알려주는 내부 매핑이다.

신규 프로젝트에서는 사용자가 field map을 직접 작성하지 않아도 된다.
에이전트가 `references/14-bootstrap-role-mapping.md`와 자동 생성한 영문 컬럼명을 기준으로 field map을 생성한다.

field map 형식:

```yaml
table_definition:
  field_map:
    <role>: <generated_physical_column_name>

column_definition:
  field_map:
    <role>: <generated_physical_column_name>
```

추론 결과가 불명확하거나 필수 role에 대응되는 컬럼이 없으면 blocked다.
이 경우 에이전트는 어떤 의미의 한글 컬럼이 추가로 필요한지 알려야 한다.

## 5. 테이블 정의서 필수 역할

테이블 정의서에는 아래 역할에 대응되는 컬럼이 있어야 한다.

- `table_id`
- `target_db`
- `target_schema`
- `owner`
- `logical_table_name`
- `physical_table_name`
- `table_type`

권장 역할:

- `subject_area_cd`
- `subject_area_nm`
- `subject_area_group_nm`
- `related_entity_name`
- `description`
- `created_at`
- `updated_at`

### target_schema 역할

`target_schema`는 필수다.

이유:

- 같은 `target_db` 안에 여러 업무 namespace가 있을 수 있다.
- 같은 물리 테이블명이 여러 namespace에 존재할 수 있다.
- 테이블 정의서는 `target_db + target_schema + physical_table_name` 단위로 테이블을 식별해야 한다.
- 여기서 `target_schema`는 정의서 호환 role 이름이며 실제 의미는 `target_namespace`다.

권장 유니크 기준:

```text
target_db + target_schema + physical_table_name
```

## 6. 컬럼 정의서 필수 역할

컬럼 정의서에는 아래 역할에 대응되는 컬럼이 있어야 한다.

- `column_id`
- `table_id`
- `logical_column_name`
- `physical_column_name`
- `data_type`
- `data_length`
- `nullable`
- `primary_key`
- `foreign_key`

권장 역할:

- `column_order`
- `domain_name`
- `unique_key`
- `indexed`
- `constraint_text`
- `default_value`
- `personal_info`
- `encrypted`
- `opened`
- `description`

## 7. 컬럼 정의서 식별 기준

컬럼 정의서는 `table_id`로 테이블 정의서를 참조하는 구조를 권장한다.

권장 유니크 기준:

```text
table_id + physical_column_name
```

컬럼 정의서에 `physical_table_name`을 중복 저장할 수는 있지만,
식별 기준은 `table_id`여야 한다.

`table_id` 참조가 없고 `physical_table_name`만 있는 구조라면,
컬럼 정의서에도 `target_db`, `target_schema` 역할이 필요하다.
여기서 `target_schema` role 값은 DBMS profile의 target namespace 값을 저장한다.

## 8. 기존 프로젝트 조회 모드

기존 프로젝트에서는 에이전트가 실제 DB에서 정의서 구조를 조회한 뒤 field map을 추론한다.

추론 기준:

- 컬럼명 exact match
- 컬럼 comment match
- 기존 프로젝트 프로파일
- 사용자 제공 매핑

추론 결과가 둘 이상이면 pending decision이다.

## 9. 차단 조건

아래는 blocked다.

- 신규 프로젝트에서 테이블 정의서 한글 컬럼 목록이 없음
- 신규 프로젝트에서 컬럼 정의서 한글 컬럼 목록이 없음
- 테이블 정의서에 `target_schema` 역할로 추론 가능한 컬럼이 없음
- 테이블 정의서에 `target_db` 역할로 추론 가능한 컬럼이 없음
- 테이블 정의서에 `physical_table_name` 역할로 추론 가능한 컬럼이 없음
- 컬럼 정의서에 `table_id` 역할이 없고 `target_schema`도 없음
- 컬럼 정의서에 `physical_column_name` 역할로 추론 가능한 컬럼이 없음
- 정의서 field map이 실제 컬럼 구조와 맞지 않음

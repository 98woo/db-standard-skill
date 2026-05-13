# 11. DBMS Profile

이 문서는 `db_standard` 논리 저장소를 DBMS별 물리 구조에 매핑하는 규칙을 정의한다.

## 목차

- [1. 핵심 원칙](#1-핵심-원칙)
- [2. 지원 DBMS 값](#2-지원-dbms-값)
- [3. 공통 입력 필드](#3-공통-입력-필드)
- [4. Namespace 의미](#4-namespace-의미)
- [5. DBMS별 표준 저장소 물리 배치](#5-dbms별-표준-저장소-물리-배치)
- [6. target namespace 입력 형식](#6-target-namespace-입력-형식)
- [7. 차단 조건](#7-차단-조건)

## 1. 핵심 원칙

- 표준화 저장소의 논리명은 항상 `db_standard`다.
- 표준 단어 / 용어 / 도메인 사전의 논리 namespace명도 항상 `db_standard`다.
- 실제 물리 배치는 DBMS의 객체 계층 구조에 맞춰 결정한다.
- SQL 렌더링은 `database`, `schema`, `owner`, `namespace`를 혼동하지 않아야 한다.
- 사용자가 선택한 DBMS profile이 확정되기 전에는 정의서 DDL이나 업무 테이블 DDL을 렌더링하지 않는다.

## 2. 지원 DBMS 값

`dbms.type` 허용값:

- `postgresql`
- `oracle`
- `mysql`
- `mariadb`
- `sqlserver`

알 수 없는 DBMS면 blocked로 처리하고, 사용자가 DBMS profile을 명시해야 한다.

## 3. 공통 입력 필드

초기 템플릿에서 사용자가 작성하거나 확인해야 하는 필드다.

```yaml
dbms:
  type:                 # postgresql | oracle | mysql | mariadb | sqlserver
  version:              # DBMS 버전. 모르면 비워둘 수 있음
  connection_target:    # 서버, 서비스명, PDB, 인스턴스 등 접속 대상. DBMS별 의미가 다름
  profile: auto         # auto 또는 dbms.type과 같은 값
```

작성 규칙:

- `type`은 필수다.
- `version`은 권장값이다. 버전에 따라 identity, sequence, comment 문법이 달라질 수 있다.
- `connection_target`은 Oracle에서는 필수에 가깝고, PostgreSQL/MySQL/SQL Server에서는 접속 도구가 별도로 관리하면 비워둘 수 있다.
- `profile: auto`이면 `type` 기준으로 DBMS profile을 자동 선택한다.

## 4. Namespace 의미

이 skill은 실제 업무 테이블이 생성될 논리 공간을 `target_namespace`라고 부른다.
DBMS별 의미는 아래와 같다.

| DBMS | namespace 의미 | 예 |
| --- | --- | --- |
| PostgreSQL | schema | `public`, `service_a` |
| Oracle | schema / user / owner | `SCC`, `SUO` |
| MySQL / MariaDB | database | `service_a` |
| SQL Server | schema | `dbo`, `service_a` |

기존 문서의 `target_schema_map`은 PostgreSQL/SQL Server처럼 namespace가 schema인 DBMS의 호환 표현이다.
신규 템플릿과 범용 문서에서는 `target_namespace_map`을 우선 사용한다.

## 5. DBMS별 표준 저장소 물리 배치

### 5.1 PostgreSQL

객체 계층:

```text
database > schema > table
```

표준 저장소:

```yaml
standard_repository:
  logical_nm: db_standard
  database_nm: db_standard
  schema_nm: db_standard
  namespace_kind: schema
  object_identifier_pattern: "{schema}.{table}"
```

렌더링 원칙:

- `db_standard` 데이터베이스에 접속한다.
- SQL 식별자는 `db_standard.<table>`처럼 `schema.table`로 렌더링한다.
- PostgreSQL SQL에는 `database.schema.table`을 쓰지 않는다.

### 5.2 Oracle

객체 계층:

```text
service/PDB > schema(user/owner) > table
```

표준 저장소:

```yaml
standard_repository:
  logical_nm: db_standard
  connection_target: <service_or_pdb>
  owner_nm: DB_STANDARD
  schema_nm: DB_STANDARD
  namespace_kind: owner
  object_identifier_pattern: "{schema}.{table}"
```

렌더링 원칙:

- 사용자가 입력한 service/PDB에 접속한다.
- 표준 사전과 정의서는 `DB_STANDARD.<table>`로 렌더링한다.
- Oracle에는 PostgreSQL식 database 이름을 SQL 식별자에 붙이지 않는다.

### 5.3 MySQL / MariaDB

객체 계층:

```text
server > database(schema) > table
```

표준 저장소:

```yaml
standard_repository:
  logical_nm: db_standard
  database_nm: db_standard
  namespace_kind: database
  object_identifier_pattern: "{database}.{table}"
```

렌더링 원칙:

- `db_standard` database를 사용한다.
- MySQL/MariaDB에서는 database와 schema가 사실상 같은 계층이다.
- 별도 `schema_nm: db_standard`를 또 요구하지 않는다.

### 5.4 SQL Server

객체 계층:

```text
server > database > schema > table
```

표준 저장소 기본값:

```yaml
standard_repository:
  logical_nm: db_standard
  database_nm: db_standard
  schema_nm: db_standard
  namespace_kind: schema
  object_identifier_pattern: "{schema}.{table}"
```

렌더링 원칙:

- 기본은 `db_standard` database의 `db_standard` schema다.
- 조직에서 `dbo`를 표준으로 쓰면 프로젝트 정책으로 `schema_nm: dbo` override를 허용할 수 있다.
- SQL Server에서 database-qualified 렌더링을 사용할지는 접속 방식과 프로젝트 정책을 따른다.

## 6. target namespace 입력 형식

간단 입력:

```text
<namespace_nm>(<subject_area_cd>)
<namespace_nm>(<subject_area_cd1>, <subject_area_cd2>)
```

구조화 입력:

```yaml
target_namespace_map:
  - namespace_nm:
    namespace_kind:       # schema | owner | database
    subject_area_cds:
    subject_area_nms:
    owner_codes:
```

작성 규칙:

- namespace가 하나여도 주제영역 / 소유자 코드 매핑은 필수다.
- `namespace_kind`는 DBMS profile에서 기본값을 정한다.
- 사용자가 `namespace_kind`를 직접 입력한 경우 DBMS profile과 충돌하면 blocked다.

## 7. 차단 조건

- `dbms.type` 누락
- 지원하지 않는 `dbms.type`
- Oracle인데 `connection_target` 또는 표준 owner/schema를 확정할 수 없음
- PostgreSQL인데 표준 database/schema를 `db_standard`로 확정할 수 없음
- MySQL/MariaDB인데 표준 database를 `db_standard`로 확정할 수 없음
- SQL Server인데 표준 database/schema를 확정할 수 없음
- target namespace가 DBMS profile의 namespace kind와 충돌

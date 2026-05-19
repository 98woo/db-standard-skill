# 10. Execution Context

이 문서는 DDL 생성 시작 전에 확정되는 실행 컨텍스트를 정의한다.

Execution Context는 사용자가 매 요청마다 반복 입력하지 않아도 되는 프로젝트 고정값이다.
단, 신규 프로젝트에서는 정의서 테이블 bootstrap 전후로 확정 가능한 값이 다르므로
아래 두 단계로 나누어 해석한다.

- `initial context`: 초기 입력 Markdown에서 파싱한 값. 정의서 bootstrap preview를 만들 수 있는 상태다.
- `finalized execution context`: 정의서 테이블 생성 또는 기존 정의서 조회가 끝나고 field map까지 확정된 상태다.

일반 업무 테이블 표준화는 `finalized execution context`가 있어야 진행할 수 있다.

`finalized execution context`는 가능하면 현재 작업 디렉토리의
`db-standard-execution-context.yaml`로 저장한다.
이 파일은 사용자가 직접 처음부터 작성하는 입력 파일이 아니라,
에이전트가 initial context와 DB 조회 / 검증 결과를 바탕으로 생성하는 프로젝트별 산출물이다.

## 목차

- [1. 핵심 원칙](#1-핵심-원칙)
- [1.1 Context 파일 수명주기](#11-context-파일-수명주기)
- [2. initial context 필수 필드](#2-initial-context-필수-필드)
- [3. finalized execution context 필수 필드](#3-finalized-execution-context-필수-필드)
- [4. 선택 필드](#4-선택-필드)
- [5. 권장 기본값](#5-권장-기본값)
- [6. run_mode 의미](#6-run_mode-의미)
- [7. 대상 DB / namespace 규칙](#7-대상-db--namespace-규칙)
- [8. 전체 식별자 원칙](#8-전체-식별자-원칙)
- [9. 시퀀스 / 키 규칙](#9-시퀀스--키-규칙)
- [10. skill 동작 가이드](#10-skill-동작-가이드)

## 1. 핵심 원칙

- Execution Context는 모든 업무 테이블 표준화 판단보다 선행한다.
- `initial context`는 시작 온보딩과 정의서 bootstrap에만 사용한다.
- `finalized execution context`는 일반 업무 테이블 표준화 중 read-only 기준으로 사용한다.
- 확정 후 값 변경이 필요하면 기존 Context를 임의 수정하지 말고 시작 온보딩으로 돌아가 재확정한다.
- Context가 없으면 일반 업무 테이블 표준화 단계로 절대 진행하지 않는다.

## 1.1 Context 파일 수명주기

skill에 포함되는 원본 템플릿:

```text
db-standard-ddl-workflow/assets/initial-context-new-project.template.md
db-standard-ddl-workflow/assets/initial-context-existing-project.template.md
db-standard-ddl-workflow/assets/execution-context.template.yaml
```

사용자 작업 디렉토리에 생성되는 파일:

```text
db-standard-initial-context.new.md
db-standard-initial-context.existing.md
db-standard-execution-context.yaml
```

역할:
- `db-standard-initial-context.new.md`와 `db-standard-initial-context.existing.md`는 에이전트가 템플릿을 복제하고 사용자가 작성하는 입력 파일이다.
- `db-standard-execution-context.yaml`은 에이전트가 생성 / 갱신하는 확정 실행 컨텍스트 파일이다.
- 다음 세션 또는 다른 에이전트는 `db-standard-execution-context.yaml`을 먼저 확인한다.
- 이 파일이 유효하면 initial context 파일을 다시 요구하지 않는다.
- 이 파일이 없거나 불완전하면 initial context 파일을 확인하고, 그것도 없으면 시작 온보딩으로 돌아간다.
- 이 파일이 없다는 사실은 신규 프로젝트라는 뜻이 아니다. 기존 프로젝트에 새로 합류한 사용자도 로컬 작업 디렉토리에 이 파일이 없을 수 있다.

관리 규칙:
- `db-standard-execution-context.yaml`은 사용자별 / 프로젝트별 환경 산출물이므로 skill repository에 포함하지 않는다.
- 기본적으로 사용자 프로젝트의 gitignore에 추가하는 것을 권장한다.
- 파일에는 비밀번호, API key, 개인 계정, 로컬 절대경로를 저장하지 않는다.
- DB connection target은 조직 정책에 따라 placeholder 또는 환경 변수 참조로 저장할 수 있다.
- 파일을 갱신할 때는 기존 파일을 임의 덮어쓰지 말고 변경 요약과 사용자 확인을 먼저 거친다.

## 2. initial context 필수 필드

Execution Context의 canonical schema는 nested schema다.
신규 / 기존 초기 입력 템플릿과 `assets/execution-context.template.yaml`은 이 구조를 기준으로 작성한다.

공통 최소 필드:

```yaml
startup_mode:
project:
  project_id:
  project_nm:
dbms:
  type:
  version:
  connection_target:
  profile:
standard_repository:
  logical_nm: db_standard
  db_nm: db_standard
  dictionary_schema_nm: db_standard
  namespace_kind: auto
  object_identifier_pattern: auto
  word_table_nm: tb_db_com_std_word
  domain_table_nm: tb_db_com_std_dmn
  term_table_nm: tb_db_com_std_trm
metadata_repository:
  db_nm: db_standard
  project_schema_nm: db_standard
physical_target:
  db_nm:
  target_namespace_map:
    - namespace_nm:
      namespace_kind:
      subject_area_cds:
      subject_area_nms:
      owner_codes:
run_control:
  run_mode:
  catalog_lookup_mode:
  write_execution_enabled:
```

신규 프로젝트는 정의서 bootstrap을 위해 아래도 필요하다.

```yaml
metadata_repository:
  definition_create_mode:
  bootstrap_policy:
  table_definition:
    korean_table_name:
    physical_table_name:
    korean_columns:
  column_definition:
    korean_table_name:
    physical_table_name:
    korean_columns:
```

기존 프로젝트는 정의서 조회 / 복원을 위해 아래도 필요하다.

```yaml
metadata_repository:
  table_definition:
    table_nm:
    id_sequence:
    field_map:
  column_definition:
    table_nm:
    id_sequence:
    field_map:
```

신규 프로젝트에서는 initial context로 정의서 테이블 bootstrap preview를 생성할 수 있다.
단, 일반 업무 테이블 표준화로 넘어가려면 아래 finalized 필드까지 확정되어야 한다.

## 3. finalized execution context 필수 필드

finalized execution context는 아래 canonical path가 확정된 상태다.

```yaml
project.project_id:
project.project_nm:
dbms.type:
dbms.version:
dbms.profile:
standard_repository.word_seq:
standard_repository.term_seq:
physical_target.db_nm:
physical_target.target_namespace_map:
metadata_repository.project_schema_nm:
metadata_repository.table_definition.table_nm:
metadata_repository.table_definition.field_map:
metadata_repository.column_definition.table_nm:
metadata_repository.column_definition.field_map:
run_control.run_mode:
```

해석 원칙:

- `metadata_repository.table_definition.field_map`, `metadata_repository.column_definition.field_map`은 신규 프로젝트에서는 bootstrap 이후 자동 생성된다.
- 기존 프로젝트에서는 사용자가 입력하거나 실제 정의서 테이블 조회 결과로 복원한다.
- `metadata_repository.table_definition.id_sequence`, `metadata_repository.column_definition.id_sequence`는 정의서 식별자 생성이 sequence 기반일 때 필수다.
- 정의서가 identity, UUID, 별도 채번 규칙을 쓰면 해당 프로젝트 식별자 생성 규칙을 Context에 기록한다.

## 4. 선택 필드

```yaml
run_control:
  catalog_lookup_mode:
  write_execution_enabled:
optional_policies:
  identifier_case_policy:
  sequence_naming_policy:
  owner_resolution_mode:
  default_target_namespace_nm:
  namespace_routing_key:
```

권장값:

- `run_control.catalog_lookup_mode`: `live` | `provided_results` | `unavailable`
- `run_control.write_execution_enabled`: `true` | `false`
- `optional_policies.identifier_case_policy`: `auto`
- `optional_policies.sequence_naming_policy`: `SEQ_<TABLE_NAME>`
- `optional_policies.owner_resolution_mode`: `direct` | `word_dictionary` | `project_mapping`
- `optional_policies.default_target_namespace_nm`: optional. 대상 namespace가 1개일 때만 권장
- `optional_policies.namespace_routing_key`: `table_owner` | `subject_area_cd` | `project_mapping`

## 5. 권장 기본값

```yaml
physical_target:
  target_namespace_map: []
standard_repository:
  word_seq: db_standard.seq_tb_db_com_std_word
  term_seq: db_standard.seq_tb_db_com_std_trm
run_control:
  run_mode: preview
  catalog_lookup_mode: unavailable
  write_execution_enabled: false
optional_policies:
  identifier_case_policy: auto
  sequence_naming_policy: SEQ_<TABLE_NAME>
  owner_resolution_mode: direct
  namespace_routing_key: table_owner
```

## 5.1 legacy alias map

기존 문서나 오래된 프로젝트 입력이 flat key를 사용하면 아래 alias로만 해석한다.
새 템플릿과 새 문서는 반드시 canonical path를 사용한다.

| Canonical path | Legacy alias | 의미 |
| --- | --- | --- |
| `project.project_id` | `project_id` | 프로젝트 ID |
| `project.project_nm` | `project_nm` | 프로젝트 명 |
| `dbms.type` | `dbms_type` | DBMS 종류 |
| `dbms.version` | `dbms_version` | DBMS 버전 |
| `dbms.profile` | `dbms_profile` | DBMS profile |
| `physical_target.db_nm` | `target_db_nm` | 업무 대상 DB |
| `physical_target.target_namespace_map` | `target_namespace_map` | 대상 namespace 라우팅 |
| `metadata_repository.project_schema_nm` | `meta_schema_nm` | 정의서 namespace |
| `metadata_repository.table_definition.table_nm` | `tbl_dfn_tbl_nm` | 테이블 정의서 테이블 |
| `metadata_repository.column_definition.table_nm` | `col_dfn_tbl_nm` | 컬럼 정의서 테이블 |
| `metadata_repository.table_definition.field_map` | `tbl_dfn_field_map` | 테이블 정의서 field map |
| `metadata_repository.column_definition.field_map` | `col_dfn_field_map` | 컬럼 정의서 field map |
| `standard_repository.word_seq` | `std_word_seq` | 표준 단어 시퀀스 |
| `standard_repository.term_seq` | `std_trm_seq` | 표준 용어 시퀀스 |
| `metadata_repository.table_definition.id_sequence` | `tbl_dfn_seq` | 테이블 정의서 식별자 시퀀스 |
| `metadata_repository.column_definition.id_sequence` | `col_dfn_seq` | 컬럼 정의서 식별자 시퀀스 |
| `run_control.run_mode` | `run_mode` | 실행 모드 |

표준화 작업의 표준 저장소 논리명은 강제 고정이다.

- 표준 저장소 논리명: `db_standard`
- 표준 사전 논리 namespace명: `db_standard`
- 표준 단어 사전: `db_standard.tb_db_com_std_word`
- 표준 도메인 사전: `db_standard.tb_db_com_std_dmn`
- 표준 용어 사전: `db_standard.tb_db_com_std_trm`

사용자는 위 논리명을 프로젝트별로 변경할 수 없다.
물리 database / schema / owner / namespace 배치는 `references/11-dbms-profile.md`의 DBMS profile을 따른다.

## 6. run_mode 의미

### preview
- SELECT / preview SQL만 생성
- 쓰기 실행 금지

### approval
- preview SQL + execution order + pending approval 반환
- 쓰기 실행 금지

### execute
- 설계자 명시 승인 + `run_control.write_execution_enabled=true` + 실제 실행 도구가 있을 때만 실행 가능
- 위 셋 중 하나라도 없으면 `approval`처럼 동작한다.

## 7. 대상 DB / namespace 규칙

표준 저장소 논리명은 고정이고, 물리 배치는 DBMS profile이 결정한다.

- 표준 저장소 논리명: `db_standard`
- 표준 사전 논리 namespace명: `db_standard`
- 프로젝트 산출물 논리 저장소명: `db_standard`
- 프로젝트 산출물 논리 namespace명: `db_standard`

사용자는 위 논리명을 바꿀 수 없다.
프로젝트별 테이블 정의서 / 컬럼 정의서 테이블도 DBMS profile이 정한 `db_standard` 물리 위치에 둔다.
프로젝트가 여러 개면 정의서 테이블명, 프로젝트 ID, 또는 정의서 내부 컬럼으로 프로젝트를 구분한다.

`physical_target.db_nm`은 실제 업무 테이블이 생성되거나 변경되는 DBMS별 연결/데이터베이스 대상이다.
`physical_target.target_namespace_map`은 이 workflow가 다룰 수 있는 실제 업무 namespace와 주제영역 라우팅 기준의 매핑이다.
namespace 의미는 DBMS별로 다르다.

- PostgreSQL: schema
- Oracle: schema / user / owner
- MySQL / MariaDB: database
- SQL Server: schema

`target_schema_map`은 namespace가 schema인 DBMS를 위한 호환 표현이다.
신규 문서와 템플릿은 `physical_target.target_namespace_map`을 우선 사용한다.

아래는 형식 예시다. 실제 값은 최초 시작 단계에서 사용자에게 입력받는다.

```yaml
physical_target:
  target_namespace_map:
  - namespace_nm:
    namespace_kind:
    subject_area_cds: [<subject_area_cd>]
    subject_area_nms: [<subject_area_nm>]
    owner_codes: [<owner_code>]
```

해석 원칙:

- `namespace_nm`은 DBMS profile에 따라 schema, owner, database 중 하나를 의미한다.
- `namespace_kind`는 `schema`, `owner`, `database` 중 하나다.
- `subject_area_cds`는 해당 namespace에 생성할 수 있는 주제영역 / 소유자 코드 목록이다.
- `subject_area_nms`는 사람이 검토할 수 있는 주제영역 명 목록이며, 코드 매칭이 가능하면 `subject_area_cds`를 우선한다.
- 프로젝트가 테이블 소유자 코드를 주제영역 코드로 사용하면 `tbl_ownr` 값을 소문자화해서 매칭한다.
- 별도 주제영역 코드가 입력되면 그 값을 우선 사용한다.
- 대상 namespace 목록이 필요한 로직에서는 `physical_target.target_namespace_map.namespace_nm` 목록을 파생값으로 사용한다.

요청 본문과의 일치 규칙:

- 요청 `데이터베이스` = `physical_target.db_nm`
- 요청 `대상 namespace`는 `physical_target.target_namespace_map`에 정의된 값 중 하나여야 한다.
- 요청의 주제영역 / 소유자 코드는 선택된 대상 namespace의 `subject_area_cds` 또는 `owner_codes`에 포함되어야 한다.
- `physical_target.target_namespace_map`에 namespace가 2개 이상이고 요청 `대상 namespace`가 없으면, 주제영역 / 소유자 코드로 단일 namespace를 추론할 수 있을 때만 자동 확정한다.
- 주제영역 / 소유자 코드로 대상 namespace가 2개 이상 매칭되면 pending decision으로 돌린다.
- 요청 `대상 namespace`와 주제영역 / 소유자 코드가 충돌하면 blocked 상태를 반환한다.
- `optional_policies.default_target_namespace_nm`은 `physical_target.target_namespace_map`에 포함되어야 한다.

불일치 시 blocked 상태를 반환한다.

주의:
- `target_namespace_nm`은 요청마다 선택되는 단일 대상 namespace다.
- `target_schema_nm`은 namespace가 schema인 DBMS에서 `target_namespace_nm`을 렌더링한 값이다.
- `physical_target.target_namespace_map`은 최초 1회 확정되는 namespace 라우팅 규칙이다.
- `metadata_repository.project_schema_nm`은 테이블정의서 / 컬럼정의서가 있는 namespace이며, 물리 업무 테이블 namespace가 아니다.
- `metadata_repository.project_schema_nm`은 논리적으로 항상 `db_standard`이며, 물리 렌더링은 DBMS profile을 따른다.
- 정의서 구조와 field map은 `references/12-metadata-artifact-model.md`를 따른다.

## 8. 전체 식별자 원칙

모든 SQL은 아래 형태를 따른다.

- 표준 사전: DBMS profile이 정한 `db_standard` namespace 하위의 `tb_db_com_std_word`, `tb_db_com_std_dmn`, `tb_db_com_std_trm`
- 프로젝트 정의서: `{metadata_repository.project_schema_nm}.{table_name}`을 DBMS profile에 맞게 렌더링
- 업무 테이블 DDL: `{target_namespace_nm}.{table_name}`을 DBMS profile에 맞게 렌더링

namespace 생략 SQL은 허용하지 않는다.

DB 연결 원칙:
- 표준 사전 조회와 정의서 INSERT는 DBMS profile이 정한 `db_standard` 표준 저장소에 접속한다.
- 물리 DDL은 `physical_target.db_nm` 또는 DBMS별 connection target에 접속한다.
- PostgreSQL처럼 database-qualified SQL을 지원하지 않는 DBMS에서는 SQL 식별자에 DB명을 붙이지 않는다.
- 표준 사전 조회는 표준 저장소에 접속한 뒤 DBMS profile의 object identifier pattern을 사용한다.
- 정의서 INSERT는 표준 저장소에 접속한 뒤 DBMS profile의 object identifier pattern을 사용한다.
- 물리 DDL은 업무 대상 저장소에 접속한 뒤 target namespace object identifier pattern을 사용한다.

## 9. 시퀀스 / 키 규칙

아래 시퀀스는 사전에 확정돼 있어야 한다.

- `standard_repository.word_seq`
- `standard_repository.term_seq`
- `metadata_repository.table_definition.id_sequence`
- `metadata_repository.column_definition.id_sequence`

표준 사전 시퀀스는 `db_standard` 저장소의 고정값을 권장한다.
정의서 시퀀스는 프로젝트 산출물 namespace와 정의서 구성에 따라 사용자 입력 또는 조회로 확정한다.

추가 시퀀스 생성이 필요하면 별도 project rule 또는 사용자 요청으로만 생성한다.

## 10. skill 동작 가이드

- `run_control.catalog_lookup_mode=unavailable` 이면 lookup SQL 템플릿만 출력한다.
- `run_control.catalog_lookup_mode=provided_results` 이면 사용자가 제공한 조회 결과만 근거로 판단한다.
- `run_control.catalog_lookup_mode=live` 이고 조회 도구가 있으면 live lookup을 사용한다.
- `run_control.write_execution_enabled=false` 이면 `run_control.run_mode=execute` 라도 preview만 반환한다.

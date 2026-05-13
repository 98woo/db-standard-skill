# 10. Execution Context

이 문서는 DDL 생성 시작 전에 확정되는 실행 컨텍스트를 정의한다.

Execution Context는 사용자가 매 요청마다 반복 입력하지 않아도 되는 프로젝트 고정값이다.
단, 신규 프로젝트에서는 정의서 테이블 bootstrap 전후로 확정 가능한 값이 다르므로
아래 두 단계로 나누어 해석한다.

- `initial context`: 초기 입력 Markdown에서 파싱한 값. 정의서 bootstrap preview를 만들 수 있는 상태다.
- `finalized execution context`: 정의서 테이블 생성 또는 기존 정의서 조회가 끝나고 field map까지 확정된 상태다.

일반 업무 테이블 표준화는 `finalized execution context`가 있어야 진행할 수 있다.

## 목차

- [1. 핵심 원칙](#1-핵심-원칙)
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

## 2. initial context 필수 필드

초기 입력 Markdown에서 확보해야 하는 최소 필드다.

```yaml
project_id:
project_nm:
dbms_type:
dbms_version:
dbms_profile:
target_db_nm:
target_namespace_map:
meta_schema_nm:
tbl_dfn_tbl_nm:
col_dfn_tbl_nm:
run_mode:
```

신규 프로젝트에서는 이 값으로 정의서 테이블 bootstrap preview를 생성할 수 있다.
단, 일반 업무 테이블 표준화로 넘어가려면 아래 finalized 필드까지 확정되어야 한다.

## 3. finalized execution context 필수 필드

```yaml
project_id:
project_nm:
dbms_type:
dbms_version:
dbms_profile:
target_db_nm:
target_namespace_map:
meta_schema_nm:
tbl_dfn_tbl_nm:
col_dfn_tbl_nm:
tbl_dfn_field_map:
col_dfn_field_map:
std_word_seq:
std_trm_seq:
tbl_dfn_seq:
col_dfn_seq:
run_mode:
```

해석 원칙:

- `tbl_dfn_field_map`, `col_dfn_field_map`은 신규 프로젝트에서는 bootstrap 이후 자동 생성된다.
- 기존 프로젝트에서는 사용자가 입력하거나 실제 정의서 테이블 조회 결과로 복원한다.
- `tbl_dfn_seq`, `col_dfn_seq`는 정의서 식별자 생성이 sequence 기반일 때 필수다.
- 정의서가 identity, UUID, 별도 채번 규칙을 쓰면 해당 프로젝트 식별자 생성 규칙을 Context에 기록한다.

## 4. 선택 필드

```yaml
catalog_lookup_mode:
write_execution_enabled:
identifier_case_policy:
sequence_naming_policy:
owner_resolution_mode:
default_target_namespace_nm:
namespace_routing_key:
```

권장값:

- `catalog_lookup_mode`: `live` | `provided_results` | `unavailable`
- `write_execution_enabled`: `true` | `false`
- `identifier_case_policy`: `auto`
- `sequence_naming_policy`: `SEQ_<TABLE_NAME>`
- `owner_resolution_mode`: `direct` | `word_dictionary` | `project_mapping`
- `default_target_namespace_nm`: optional. 대상 namespace가 1개일 때만 권장
- `namespace_routing_key`: `table_owner` | `subject_area_cd` | `project_mapping`

## 5. 권장 기본값

```yaml
target_namespace_map: {}
std_word_seq: db_standard.seq_tb_db_com_std_word
std_trm_seq: db_standard.seq_tb_db_com_std_trm
run_mode: preview
catalog_lookup_mode: unavailable
write_execution_enabled: false
identifier_case_policy: auto
sequence_naming_policy: SEQ_<TABLE_NAME>
owner_resolution_mode: direct
namespace_routing_key: table_owner
```

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
- 설계자 명시 승인 + `write_execution_enabled=true` + 실제 실행 도구가 있을 때만 실행 가능
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

`target_db_nm`은 실제 업무 테이블이 생성되거나 변경되는 DBMS별 연결/데이터베이스 대상이다.
`target_namespace_map`은 이 workflow가 다룰 수 있는 실제 업무 namespace와 주제영역 라우팅 기준의 매핑이다.
namespace 의미는 DBMS별로 다르다.

- PostgreSQL: schema
- Oracle: schema / user / owner
- MySQL / MariaDB: database
- SQL Server: schema

`target_schema_map`은 namespace가 schema인 DBMS를 위한 호환 표현이다.
신규 문서와 템플릿은 `target_namespace_map`을 우선 사용한다.

아래는 형식 예시다. 실제 값은 최초 시작 단계에서 사용자에게 입력받는다.

```yaml
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
- 대상 namespace 목록이 필요한 로직에서는 `target_namespace_map.namespace_nm` 목록을 파생값으로 사용한다.

요청 본문과의 일치 규칙:

- 요청 `데이터베이스` = `target_db_nm`
- 요청 `대상 namespace`는 `target_namespace_map`에 정의된 값 중 하나여야 한다.
- 요청의 주제영역 / 소유자 코드는 선택된 대상 namespace의 `subject_area_cds` 또는 `owner_codes`에 포함되어야 한다.
- `target_namespace_map`에 namespace가 2개 이상이고 요청 `대상 namespace`가 없으면, 주제영역 / 소유자 코드로 단일 namespace를 추론할 수 있을 때만 자동 확정한다.
- 주제영역 / 소유자 코드로 대상 namespace가 2개 이상 매칭되면 pending decision으로 돌린다.
- 요청 `대상 namespace`와 주제영역 / 소유자 코드가 충돌하면 blocked 상태를 반환한다.
- `default_target_namespace_nm`은 `target_namespace_map`에 포함되어야 한다.

불일치 시 blocked 상태를 반환한다.

주의:
- `target_namespace_nm`은 요청마다 선택되는 단일 대상 namespace다.
- `target_schema_nm`은 namespace가 schema인 DBMS에서 `target_namespace_nm`을 렌더링한 값이다.
- `target_namespace_map`은 최초 1회 확정되는 namespace 라우팅 규칙이다.
- `meta_schema_nm`은 테이블정의서 / 컬럼정의서가 있는 스키마이며, 물리 업무 테이블 스키마가 아니다.
- `meta_schema_nm`은 논리적으로 항상 `db_standard`이며, 물리 렌더링은 DBMS profile을 따른다.
- 정의서 구조와 field map은 `references/12-metadata-artifact-model.md`를 따른다.

## 8. 전체 식별자 원칙

모든 SQL은 아래 형태를 따른다.

- 표준 사전: DBMS profile이 정한 `db_standard` namespace 하위의 `tb_db_com_std_word`, `tb_db_com_std_dmn`, `tb_db_com_std_trm`
- 프로젝트 정의서: `{meta_schema_nm}.{table_name}`
- 업무 테이블 DDL: `{target_namespace_nm}.{table_name}`을 DBMS profile에 맞게 렌더링

namespace 생략 SQL은 허용하지 않는다.

DB 연결 원칙:
- 표준 사전 조회와 정의서 INSERT는 DBMS profile이 정한 `db_standard` 표준 저장소에 접속한다.
- 물리 DDL은 `target_db_nm` 또는 DBMS별 connection target에 접속한다.
- PostgreSQL처럼 database-qualified SQL을 지원하지 않는 DBMS에서는 SQL 식별자에 DB명을 붙이지 않는다.
- 표준 사전 조회는 표준 저장소에 접속한 뒤 DBMS profile의 object identifier pattern을 사용한다.
- 정의서 INSERT는 표준 저장소에 접속한 뒤 DBMS profile의 object identifier pattern을 사용한다.
- 물리 DDL은 업무 대상 저장소에 접속한 뒤 target namespace object identifier pattern을 사용한다.

## 9. 시퀀스 / 키 규칙

아래 시퀀스는 사전에 확정돼 있어야 한다.

- `std_word_seq`
- `std_trm_seq`
- `tbl_dfn_seq`
- `col_dfn_seq`

표준 사전 시퀀스는 `db_standard` 저장소의 고정값을 권장한다.
정의서 시퀀스는 프로젝트 산출물 namespace와 정의서 구성에 따라 사용자 입력 또는 조회로 확정한다.

추가 시퀀스 생성이 필요하면 별도 project rule 또는 사용자 요청으로만 생성한다.

## 10. skill 동작 가이드

- `catalog_lookup_mode=unavailable` 이면 lookup SQL 템플릿만 출력한다.
- `catalog_lookup_mode=provided_results` 이면 사용자가 제공한 조회 결과만 근거로 판단한다.
- `catalog_lookup_mode=live` 이고 조회 도구가 있으면 live lookup을 사용한다.
- `write_execution_enabled=false` 이면 `run_mode=execute` 라도 preview만 반환한다.

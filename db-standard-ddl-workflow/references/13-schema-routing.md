# 13. 대상 Namespace 라우팅

이 문서는 실제 물리 테이블을 어느 DBMS namespace에 생성할지 결정하는 규칙을 정의한다.

## 1. 기본 원칙

- 대상 저장소는 프로젝트별 사용자 입력값이다.
- 대상 namespace는 하나 이상 입력받을 수 있다.
- namespace가 하나여도 주제영역 / 소유자 코드 매핑은 필수다.
- 대상 namespace와 주제영역 / 소유자 코드가 충돌하면 blocked다.
- namespace의 DBMS별 의미는 `references/11-dbms-profile.md`를 따른다.

DBMS별 namespace 의미:

- PostgreSQL: schema
- Oracle: schema / user / owner
- MySQL / MariaDB: database
- SQL Server: schema

## 2. 입력 형식

간단 입력:

```text
<namespace_nm>(<subject_area_cd>)
<namespace_nm>(<subject_area_cd1>, <subject_area_cd2>)
```

예:

```text
namespace_a(owner_a)
namespace_b(owner_b, owner_c)
```

구조화 입력:

```yaml
target_namespace_map:
  - namespace_nm:
    namespace_kind:
    subject_area_cds:
    subject_area_nms:
    owner_codes:
```

호환 규칙:

- 기존 `schema_routes` 또는 `target_schema_map` 입력은 namespace가 schema인 DBMS에서만 호환 입력으로 인정한다.
- Oracle / MySQL / MariaDB에서는 신규 템플릿의 `target_namespace_map`을 우선 사용한다.

## 3. 정규화

- `namespace_nm`은 DBMS casing 규칙을 따른다.
- `namespace_kind`가 비어 있으면 DBMS profile의 기본 namespace kind를 사용한다.
- `subject_area_cds`는 비교 시 대소문자를 무시한다.
- `owner_codes`는 비교 시 대소문자를 무시한다.
- `subject_area_nms`는 사람이 확인하는 보조 정보로 사용한다.

## 4. 라우팅 순서

1. 요청에 대상 namespace가 있으면 route에 존재하는지 확인한다.
2. 요청에 주제영역 코드가 있으면 `subject_area_cds`와 비교한다.
3. 요청에 주제영역 코드가 없으면 테이블 소유자 코드를 `owner_codes` 또는 `subject_area_cds`와 비교한다.
4. 대상 namespace가 생략됐으면 주제영역 / 소유자 코드로 단일 namespace를 찾는다.
5. 단일 namespace가 확정되면 `target_namespace_nm`으로 사용한다.
6. DBMS가 PostgreSQL / SQL Server이면 `target_schema_nm = target_namespace_nm`으로 렌더링할 수 있다.
7. DBMS가 Oracle이면 `target_owner_nm = target_namespace_nm` 또는 `target_schema_nm = target_namespace_nm`으로 렌더링한다.
8. DBMS가 MySQL / MariaDB이면 `target_database_nm = target_namespace_nm`으로 렌더링한다.

## 5. 상태 분류

### VALID

- 요청 대상 namespace가 route에 존재한다.
- 주제영역 / 소유자 코드가 해당 namespace에 매핑되어 있다.

### PENDING_DECISION

- 주제영역 / 소유자 코드가 여러 namespace에 매핑된다.
- 요청 정보만으로 namespace를 단일 확정할 수 없지만 후보를 제시할 수 있다.

### BLOCKED

- route가 없다.
- route에 주제영역 / 소유자 코드가 없다.
- 요청 대상 namespace가 route에 없다.
- 요청 대상 namespace와 주제영역 / 소유자 코드가 충돌한다.
- namespace가 하나인데도 주제영역 / 소유자 코드 매핑이 없다.
- `namespace_kind`가 DBMS profile과 충돌한다.

## 6. 출력 규칙

라우팅 결과에는 아래를 포함한다.

- `physical_target.db_nm` 또는 DBMS별 connection target
- `target_namespace_nm`
- `target_namespace_kind`
- DBMS별 렌더링 이름: `target_schema_nm` | `target_owner_nm` | `target_database_nm`
- 매칭 기준: `subject_area_cd` | `owner_code` | `manual`
- 매칭된 코드
- 라우팅 상태: `VALID` | `PENDING_DECISION` | `BLOCKED`

## 7. 정의서 반영

테이블 정의서에는 확정된 target namespace를 `target_schema` 역할 컬럼에 저장한다.

호환성을 위해 정의서 role 이름은 `target_schema`를 유지하지만,
값의 의미는 DBMS profile에 따라 schema, owner, database 중 하나일 수 있다.

테이블 정의서의 테이블 식별 기준은 아래다.

```text
target_db + target_schema + physical_table_name
```

여기서 `target_schema`는 정의서 호환 role 이름이며, 실제 의미는 `target_namespace`다.

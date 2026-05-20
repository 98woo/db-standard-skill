# DB Standard Initial Context - New Project

이 파일은 신규 프로젝트의 표준화 산출물 구조를 처음 세팅할 때 사용하는 사용자 입력 템플릿이다.
사용자는 아래 YAML에서 주석이 달린 최소 항목만 작성한다. 고정값, 표준 사전 위치, 정의서 field map, sequence, optional policy는 에이전트가 `db-standard-execution-context.yaml`에 생성 / 관리한다.

작성 원칙:

- 표준 단어 / 용어 / 도메인 사전은 사용자가 이미 `db_standard`에 구축해 둔 상태여야 한다.
- 여기서 만드는 테이블 정의서 / 컬럼 정의서 테이블 자체는 표준화 대상이 아니라 프로젝트 산출물 bootstrap 대상이다.
- 정의서 테이블 컬럼은 사용자가 한글명으로 입력한다.
- 에이전트는 한글 컬럼명을 자동 `snake_case` 물리 컬럼명으로 변환한다.
- 정의서 테이블 컬럼 타입은 모두 `text`로 생성한다.
- 한글 테이블명 / 컬럼명은 DB comment로 추가한다.
- 비밀번호, 개인 계정, API key, 로컬 절대경로는 쓰지 않는다.

```yaml
startup_mode: new_project # 필수. 신규 프로젝트 최초 세팅이므로 new_project 고정

project:
  project_id: # 필수. 프로젝트를 식별할 짧은 ID
  project_nm: # 필수. 사람이 알아볼 프로젝트 명

dbms:
  type: # 필수. DBMS 종류: postgresql | oracle | mysql | mariadb | sqlserver
  connection_target: # 조건부. DB 접속 대상: host/port/service/instance 등. 접속 profile이 따로 있으면 비워둠

metadata_repository:
  definition_create_mode: create # 필수. create | use_existing
  table_definition:
    korean_table_name: 테이블 정의서 # 필수. 테이블 정의서의 한글 테이블명
    korean_columns: # 필수. 테이블 정의서에 필요한 한글 컬럼명 목록
      - 테이블 식별자
      - 대상 데이터베이스
      - 대상 namespace
      - 테이블 소유자
      - 주제영역 코드
      - 주제영역 명
      - 주제영역 그룹 명
      - 논리 테이블명
      - 물리 테이블명
      - 테이블 종류
      - 관계 엔터티 명
      - 설명
  column_definition:
    korean_table_name: 컬럼 정의서 # 필수. 컬럼 정의서의 한글 테이블명
    korean_columns: # 필수. 컬럼 정의서에 필요한 한글 컬럼명 목록
      - 컬럼 식별자
      - 테이블 식별자
      - 컬럼 순서
      - 논리 컬럼명
      - 물리 컬럼명
      - 도메인명
      - 데이터 타입
      - 데이터 길이
      - NULL 허용 여부
      - PK 여부
      - FK 여부
      - UNIQUE 여부
      - INDEX 여부
      - 제약조건 내용
      - 기본값
      - 설명

physical_target:
  db_nm: # 필수. 실제 업무 테이블이 생성될 대상 DB 또는 접속 대상 명
  target_namespace_map:
    - namespace_nm: # 필수. 실제 업무 테이블 대상 namespace. PostgreSQL=schema, Oracle=owner/schema, MySQL=database, SQL Server=schema
      subject_area_cds: [] # 필수 권장. 이 namespace로 라우팅할 주제영역 코드 목록. 모르면 owner_codes라도 작성
      subject_area_nms: [] # 선택. 사람이 이해할 주제영역 명 목록
      owner_codes: [] # 필수 권장. 이 namespace로 라우팅할 테이블 소유자 코드 목록. 모르면 subject_area_cds라도 작성

run_control:
  run_mode: preview # 필수. preview | approval | execute
```

에이전트가 생성 / 관리하는 값:

- `standard_repository.*`: `db_standard` 고정 표준 사전 위치
- `metadata_repository.db_nm`, `metadata_repository.project_schema_nm`: `db_standard` 고정 산출물 위치
- `metadata_repository.bootstrap_policy`: 정의서 bootstrap 고정 정책
- `metadata_repository.*.physical_table_name`: 비워두면 한글 테이블명에서 자동 생성
- `metadata_repository.*.field_map`: 정의서 bootstrap 후 자동 생성
- `metadata_repository.*.id_sequence`: sequence 기반이면 DB 조회 또는 사용자 확인으로 확정
- `dbms.version`, `dbms.profile`: DBMS type과 profile 규칙으로 확정
- `run_control.catalog_lookup_mode`, `run_control.write_execution_enabled`: 권한 / 실행 모드에 따라 확정
- `optional_policies.*`: 프로젝트 정책이 있을 때만 확정

에이전트 처리:

- 위 YAML을 파싱한 뒤 정의서 테이블 DDL preview와 내부 field map을 생성한다.
- 정의서 bootstrap에는 표준화 / 웹 검색 / 도메인 판단을 적용하지 않는다.
- 필수 role을 추론할 수 있는 한글 컬럼이 없으면 blocked로 반환하고 필요한 한글 컬럼 후보를 알려준다.
- 확정 후 `db-standard-execution-context.yaml`을 생성하거나 갱신한다.

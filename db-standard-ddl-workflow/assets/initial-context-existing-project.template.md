# DB Standard Initial Context - Existing Project

이 파일은 기존 프로젝트 표준화 작업에 새로 합류하거나, 로컬에 `db-standard-execution-context.yaml`이 없을 때 사용하는 사용자 입력 템플릿이다.
사용자는 아래 YAML에서 주석이 달린 최소 항목만 작성한다. 고정값, 표준 사전 위치, 정의서 field map, sequence, optional policy는 에이전트가 `db-standard-execution-context.yaml`에 생성 / 관리한다.

작성 원칙:

- 비밀번호, 개인 계정, API key, 로컬 절대경로는 쓰지 않는다.
- DBMS와 접속 대상은 에이전트가 기존 profile 또는 connector로 복원할 수 있으면 비워둘 수 있다.
- 대상 namespace가 하나여도 `target_namespace_map`에는 namespace와 주제영역 / 소유자 코드를 적는다.
- 정의서 field map은 사용자가 기본적으로 작성하지 않는다. 에이전트가 DB의 정의서 컬럼명과 comment를 조회해 복원한다.

```yaml
startup_mode: existing_project # 필수. 기존 프로젝트 이어서 진행이므로 existing_project 고정

dbms:
  type: # 조건부. DBMS 종류: postgresql | oracle | mysql | mariadb | sqlserver. 에이전트가 복원 가능하면 비워둠
  connection_target: # 조건부. DB 접속 대상: host/port/service/instance 등. 접속 profile이 따로 있으면 비워둠

metadata_repository:
  table_definition:
    table_nm: # 필수. 기존 테이블 정의서 테이블명
  column_definition:
    table_nm: # 필수. 기존 컬럼 정의서 테이블명

physical_target:
  db_nm: # 필수. 실제 업무 테이블이 있는 대상 DB 또는 접속 대상 명
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
- `metadata_repository.*.field_map`: 실제 정의서 테이블 조회 결과로 복원
- `metadata_repository.*.id_sequence`: sequence 기반이면 DB 조회 또는 사용자 확인으로 복원
- `dbms.version`, `dbms.profile`: DBMS type과 profile 규칙으로 확정
- `run_control.catalog_lookup_mode`, `run_control.write_execution_enabled`: 권한 / 실행 모드에 따라 확정
- `optional_policies.*`: 프로젝트 정책이 있을 때만 확정

에이전트 처리:

- 위 YAML을 파싱한 뒤 `db_standard`의 사전 테이블과 정의서 테이블을 조회한다.
- 테이블 정의서 / 컬럼 정의서 field map을 자동 복원한다.
- 복원 후보가 둘 이상이거나 필수 role을 찾지 못하면 pending decision으로 사용자 확인을 받는다.
- 확정 후 `db-standard-execution-context.yaml`을 생성하거나 갱신한다.

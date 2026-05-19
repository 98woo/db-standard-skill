# DB Standard Initial Context - Existing Project

이 파일은 기존 프로젝트 표준화 작업을 이어서 진행할 때 사용하는 작성용 템플릿이다.
에이전트는 최초 실행 시 이 원본을 현재 작업 디렉토리에 `db-standard-initial-context.existing.md`로 생성하고,
사용자가 작성한 YAML 블록과 실제 DB 조회 결과를 함께 사용해 Execution Context를 복원한다.

작성 규칙:

- 아래 YAML 블록을 작성한다.
- 기존 context, 기존 initial context, 또는 DB 조회 결과로 DBMS profile을 복원할 수 있으면 `dbms.type`은 비워둘 수 있다.
- 복원할 수 없으면 `dbms.type`을 작성한다. DBMS에 따라 database / schema / owner / namespace 의미가 달라진다.
- `standard_repository` 값은 고정값이므로 변경하지 않는다.
- 대상 namespace가 하나여도 `target_namespace_map`에는 namespace와 주제영역 / 소유자 코드를 반드시 입력한다.
- `field_map`을 알고 있으면 작성하고, 모르면 비워둔다.
- field map이 비어 있으면 에이전트가 실제 정의서 테이블 구조와 comment를 조회해 추론한다.
- 추론 결과가 둘 이상이면 에이전트는 pending decision으로 돌리고 사용자 확인을 받아야 한다.

키 안내:

- `startup_mode(작업 유형)`: `existing_project`로 고정
- `project_id(프로젝트 ID)`, `project_nm(프로젝트 명)`: 프로젝트 식별 정보
- `dbms.type(DBMS 종류)`: `postgresql`, `oracle`, `mysql`, `mariadb`, `sqlserver` 중 하나. 복원 가능하면 비워둘 수 있음
- `dbms.version(DBMS 버전)`: 모르면 비워둘 수 있음
- `dbms.connection_target(접속 대상)`: Oracle service/PDB, SQL Server instance 등. 접속 도구가 별도 관리하면 비워둘 수 있음
- `dbms.profile(DBMS 프로파일)`: 보통 `auto` 유지
- `standard_repository(표준 저장소)`: `db_standard.db_standard` 고정 표준 사전 위치
- `metadata_repository(프로젝트 산출물 저장소)`: `db_standard.db_standard` 고정 산출물 위치
- `physical_target(물리 테이블 대상)`: 실제 업무 테이블이 있는 DB와 namespace 라우팅
- `run_control(실행 제어)`: preview / approval / execute 및 조회 / 쓰기 권한 설정

주요 role 안내:

- `table_id(테이블 식별자)`, `column_id(컬럼 식별자)`
- `target_db(대상 DB)`, `target_schema(대상 namespace. 정의서 호환 role 이름)`
- `owner(테이블 소유자)`, `table_type(테이블 종류)`
- `logical_table_name(논리 테이블명)`, `physical_table_name(물리 테이블명)`
- `logical_column_name(논리 컬럼명)`, `physical_column_name(물리 컬럼명)`
- `domain_name(도메인명)`, `data_type(데이터 타입)`, `data_length(데이터 길이)`
- `nullable(NULL 허용 여부)`, `primary_key(PK 여부)`, `foreign_key(FK 여부)`
- `unique_key(UNIQUE 여부)`, `indexed(INDEX 여부)`, `default_value(기본값)`

```yaml
startup_mode: existing_project # startup_mode(작업 유형)

project: # project(프로젝트 정보)
  project_id: # project_id(프로젝트 ID)
  project_nm: # project_nm(프로젝트 명)

dbms: # dbms(DBMS 정보)
  type: # type(DBMS 종류): postgresql | oracle | mysql | mariadb | sqlserver. 복원 가능하면 비워둘 수 있음
  version: # version(DBMS 버전). 모르면 비워둘 수 있음
  connection_target: # connection_target(접속 대상): Oracle service/PDB, SQL Server server/instance 등. 없으면 비움
  profile: auto # profile(DBMS 프로파일): auto 권장. 필요 시 postgresql | oracle | mysql | mariadb | sqlserver

standard_repository: # standard_repository(표준 저장소)
  logical_nm: db_standard # logical_nm(표준 저장소 논리명). 변경 금지
  db_nm: db_standard # db_nm(데이터베이스 명): PostgreSQL/MySQL/SQL Server에서 db_standard. Oracle은 접속 대상 기준
  dictionary_schema_nm: db_standard # dictionary_schema_nm(표준 사전 namespace/owner 호환 명): PostgreSQL/SQL Server db_standard, Oracle DB_STANDARD, MySQL은 생략 가능
  namespace_kind: auto # namespace_kind(DBMS namespace 종류): auto | schema | owner | database
  object_identifier_pattern: auto # object_identifier_pattern(객체 식별자 패턴): auto 권장
  word_table_nm: tb_db_com_std_word # word_table_nm(표준 단어 테이블 명)
  domain_table_nm: tb_db_com_std_dmn # domain_table_nm(표준 도메인 테이블 명)
  term_table_nm: tb_db_com_std_trm # term_table_nm(표준 용어 테이블 명)
  word_seq: db_standard.seq_tb_db_com_std_word # word_seq(표준 단어 시퀀스)
  term_seq: db_standard.seq_tb_db_com_std_trm # term_seq(표준 용어 시퀀스)

metadata_repository: # metadata_repository(프로젝트 산출물 저장소)
  db_nm: db_standard # db_nm(데이터베이스 명)
  project_schema_nm: db_standard # project_schema_nm(프로젝트 산출물 namespace 호환 명). db_standard 고정

  table_definition: # table_definition(테이블 정의서)
    table_nm: # table_nm(정의서 테이블 명)
    id_sequence: # id_sequence(식별자 시퀀스)
    field_map: # field_map(role-physical_column_name 매핑)
      table_id: # table_id(테이블 식별자)
      target_db: # target_db(대상 DB)
      target_schema: # target_schema(대상 namespace. 정의서 호환 role 이름)
      owner: # owner(테이블 소유자)
      logical_table_name: # logical_table_name(논리 테이블명)
      physical_table_name: # physical_table_name(물리 테이블명)
      table_type: # table_type(테이블 종류)
      subject_area_cd: # subject_area_cd(주제영역 코드)
      subject_area_nm: # subject_area_nm(주제영역 명)
      subject_area_group_nm: # subject_area_group_nm(주제영역 그룹 명)
      related_entity_name: # related_entity_name(관계 엔터티 명)
      description: # description(설명)

  column_definition: # column_definition(컬럼 정의서)
    table_nm: # table_nm(정의서 테이블 명)
    id_sequence: # id_sequence(식별자 시퀀스)
    field_map: # field_map(role-physical_column_name 매핑)
      column_id: # column_id(컬럼 식별자)
      table_id: # table_id(테이블 식별자)
      column_order: # column_order(컬럼 순서)
      logical_column_name: # logical_column_name(논리 컬럼명)
      physical_column_name: # physical_column_name(물리 컬럼명)
      domain_name: # domain_name(도메인명)
      data_type: # data_type(데이터 타입)
      data_length: # data_length(데이터 길이)
      nullable: # nullable(NULL 허용 여부)
      primary_key: # primary_key(PK 여부)
      foreign_key: # foreign_key(FK 여부)
      unique_key: # unique_key(UNIQUE 여부)
      indexed: # indexed(INDEX 여부)
      constraint_text: # constraint_text(제약조건 내용)
      default_value: # default_value(기본값)
      description: # description(설명)

physical_target: # physical_target(물리 테이블 대상)
  db_nm: # db_nm(업무 대상 데이터베이스/접속 대상 명): DBMS별 의미는 references/11-dbms-profile.md 참고
  target_namespace_map: # target_namespace_map(대상 namespace 라우팅): PostgreSQL=schema, Oracle=owner/schema, MySQL=database, SQL Server=schema
    - namespace_nm: # namespace_nm(namespace 명). 예: PostgreSQL schema, Oracle owner, MySQL database
      namespace_kind: auto # namespace_kind: auto | schema | owner | database
      subject_area_cds: # subject_area_cds(주제영역 코드 목록)
        -
      subject_area_nms: # subject_area_nms(주제영역 명 목록)
        -
      owner_codes: # owner_codes(테이블 소유자 코드 목록)
        -

run_control: # run_control(실행 제어)
  run_mode: preview # run_mode(실행 모드): preview | approval | execute
  catalog_lookup_mode: unavailable # catalog_lookup_mode(카탈로그 조회 방식): live | provided_results | unavailable
  write_execution_enabled: false # write_execution_enabled(쓰기 실행 허용 여부)

optional_policies: # optional_policies(선택 정책)
  identifier_case_policy: auto # identifier_case_policy(식별자 대소문자 정책)
  sequence_naming_policy: SEQ_<TABLE_NAME> # sequence_naming_policy(시퀀스 명명 정책)
  owner_resolution_mode: direct # owner_resolution_mode(소유자 해석 방식): direct | word_dictionary | project_mapping
  namespace_routing_key: table_owner # namespace_routing_key(namespace 라우팅 기준): table_owner | subject_area_cd | project_mapping
```

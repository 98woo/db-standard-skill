# DB Standard Initial Context - New Project

이 파일은 신규 프로젝트 표준화 작업을 시작할 때 사용하는 작성용 템플릿이다.
에이전트는 최초 실행 시 이 원본을 현재 작업 디렉토리에 `db-standard-initial-context.new.md`로 생성하고,
사용자가 작성한 YAML 블록을 Execution Context의 기준으로 사용한다.

작성 규칙:

- 아래 YAML 블록을 작성한다.
- `dbms.type`을 먼저 작성한다. DBMS에 따라 database / schema / owner / namespace 의미가 달라진다.
- `standard_repository` 값은 고정값이므로 변경하지 않는다.
- 테이블 정의서 / 컬럼 정의서 테이블 자체를 만드는 단계는 표준화 작업이 아니다.
- 정의서 테이블 컬럼은 사용자가 한글명으로 입력한다.
- 에이전트는 한글 컬럼명을 자동으로 영문 `snake_case` 물리 컬럼명으로 변환한다.
- 영문 컬럼명 후보를 사용자에게 제안하지 않고 자동 적용한다.
- 웹 검색은 사용하지 않는다.
- 정의서 테이블 컬럼 타입은 모두 `text`로 고정한다.
- 한글 테이블명 / 컬럼명은 DB comment로 추가한다.
- 대상 namespace가 하나여도 `target_namespace_map`에는 namespace와 주제영역 / 소유자 코드를 반드시 입력한다.
- 업무 테이블 표준화에 필요한 필수 role은 에이전트가 자동으로 추론한다.
- 필수 role을 추론할 수 있는 한글 컬럼이 없으면 에이전트가 누락 컬럼으로 반환한다.

키 안내:

- `startup_mode(작업 유형)`: `new_project`로 고정
- `project_id(프로젝트 ID)`, `project_nm(프로젝트 명)`: 프로젝트 식별 정보
- `dbms.type(DBMS 종류)`: `postgresql`, `oracle`, `mysql`, `mariadb`, `sqlserver` 중 하나
- `dbms.version(DBMS 버전)`: 모르면 비워둘 수 있음
- `dbms.connection_target(접속 대상)`: Oracle service/PDB, SQL Server instance 등. 접속 도구가 별도 관리하면 비워둘 수 있음
- `dbms.profile(DBMS 프로파일)`: 보통 `auto` 유지
- `standard_repository(표준 저장소)`: `db_standard.db_standard` 고정 표준 사전 위치
- `metadata_repository(프로젝트 산출물 저장소)`: `db_standard.db_standard` 고정 산출물 위치
- `korean_table_name(한글 테이블명)`: 정의서 테이블의 한글명이며 comment로 사용
- `physical_table_name(물리 테이블명)`: 비워두면 에이전트가 한글 테이블명에서 자동 생성
- `korean_columns(한글 컬럼 목록)`: 정의서 테이블에 필요한 컬럼 한글명 목록
- `physical_target(물리 테이블 대상)`: 실제 업무 테이블이 생성될 DB와 namespace 라우팅
- `run_control(실행 제어)`: preview / approval / execute 및 조회 / 쓰기 권한 설정

```yaml
startup_mode: new_project # startup_mode(작업 유형)

project: # project(프로젝트 정보)
  project_id: # project_id(프로젝트 ID)
  project_nm: # project_nm(프로젝트 명)

dbms: # dbms(DBMS 정보)
  type: postgresql # type(DBMS 종류): postgresql | oracle | mysql | mariadb | sqlserver
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
  definition_create_mode: create # definition_create_mode(정의서 생성 방식): create | use_existing

  bootstrap_policy: # bootstrap_policy(정의서 테이블 생성 정책)
    standardization_applied: false # standardization_applied(표준화 적용 여부)
    web_search_allowed: false # web_search_allowed(웹 검색 허용 여부)
    physical_name_generation: ai_auto_snake_case # physical_name_generation(물리명 생성 방식)
    column_data_type: text # column_data_type(정의서 컬럼 데이터 타입)
    comment_source: korean_name # comment_source(comment 원천)
    role_mapping_mode: ai_auto_infer # role_mapping_mode(role 매핑 방식)

  table_definition: # table_definition(테이블 정의서)
    korean_table_name: 테이블 정의서 # korean_table_name(한글 테이블명)
    physical_table_name: # physical_table_name(물리 테이블명). 비워두면 자동 생성
    korean_columns: # korean_columns(한글 컬럼 목록). 필요한 컬럼을 추가/삭제 가능
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

  column_definition: # column_definition(컬럼 정의서)
    korean_table_name: 컬럼 정의서 # korean_table_name(한글 테이블명)
    physical_table_name: # physical_table_name(물리 테이블명). 비워두면 자동 생성
    korean_columns: # korean_columns(한글 컬럼 목록). 필요한 컬럼을 추가/삭제 가능
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

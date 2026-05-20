# 95. 리뷰 체크리스트

skill은 결과를 내기 전에 가능하면 아래 체크리스트로 자체 검토한다.

## 1. 입력 / 컨텍스트

- [ ] Execution Context가 존재하는가
- [ ] DBMS 종류와 DBMS profile이 확정됐는가
- [ ] 작업 유형이 신규 프로젝트 또는 기존 프로젝트 이어서 진행 중 하나로 확정됐는가
- [ ] 작업 유형에 맞는 초기 입력 Markdown 파일이 존재하고 YAML 블록이 파싱됐는가
- [ ] 에이전트가 해석한 Execution Context 요약을 사용자에게 확인받았는가
- [ ] 표준 저장소가 `db_standard.db_standard` 고정 전제와 일치하는가
- [ ] 프로젝트 산출물 위치가 `db_standard.db_standard`로 확정됐는가
- [ ] 신규 프로젝트의 정의서 테이블 bootstrap에는 표준화 / 웹 검색 / 도메인 판단을 적용하지 않았는가
- [ ] 신규 프로젝트의 정의서 한글 컬럼명이 자동 `snake_case` 물리 컬럼명으로 변환됐는가
- [ ] 신규 프로젝트의 정의서 컬럼 타입이 모두 `text`인가
- [ ] 신규 프로젝트의 정의서 한글 테이블명 / 컬럼명이 DB comment로 렌더링됐는가
- [ ] 테이블 정의서 field map이 생성 또는 복원됐고 `target_schema` 역할을 포함하는가
- [ ] 컬럼 정의서 field map이 생성 또는 복원됐는가
- [ ] 요청 `데이터베이스`가 `physical_target.db_nm`과 일치하는가
- [ ] `physical_target.target_namespace_map`이 존재하는가
- [ ] 요청 `대상 namespace`가 있으면 `physical_target.target_namespace_map`에 존재하는가
- [ ] 요청 주제영역 / 소유자 코드가 선택된 대상 namespace의 `subject_area_cds` 또는 `owner_codes`와 일치하는가
- [ ] 요청 `대상 namespace`가 없으면 주제영역 / 소유자 코드로 단일 namespace가 확정되는가
- [ ] 정의서 namespace(`metadata_repository.project_schema_nm`)와 업무 테이블 namespace(`target_namespace_nm`)를 혼동하지 않았는가
- [ ] 테이블 종류와 실행 요청이 명시됐는가
- [ ] 요청 유형이 `create_table`, `alter_add_columns`, `alter_modify_columns`, `drop_columns` 중 하나로 확정됐는가
- [ ] 이미지 또는 동등한 텍스트 정의가 있는가

## 2. 정규화

- [ ] raw 입력과 canonical 한글명이 구분되는가
- [ ] 신규 등록 전에 용어 exact / 용어 synonym / 단어 exact / 단어 synonym / prohibited-word 재사용 후보를 확인했는가
- [ ] 재사용 가능한 단일 canonical 후보가 있는데 신규 등록으로 진행하지 않았는가
- [ ] 재사용 가능한 단일 canonical 후보를 사용자 선호만으로 우회하지 않았는가
- [ ] term synonym 치환 시 canonical `trm_nm`, `trm_eng_abbr_nm`, `dmn_nm`을 사용했는가
- [ ] word synonym / prohibited-word 치환 시 canonical `word_nm` 을 사용했는가
- [ ] term synonym / word synonym / prohibited-word 후보가 2건 이상이면 pending decision으로 돌렸는가
- [ ] 단어 수 제한을 통과했는가
- [ ] 복합어 / 파생어 정규화가 필요한 경우 반영됐는가

## 3. 테이블명

- [ ] 접두사가 테이블 종류와 일치하는가
- [ ] owner segment가 올바른가
- [ ] 테이블명 단어가 기존 표준 단어로 재사용 가능한지 먼저 확인했는가
- [ ] 본체 단어 수가 3 이하인가
- [ ] 복합 약어 사용 시 승인 또는 명시 규칙이 있는가
- [ ] 최종 물리명 casing이 target DBMS와 일치하는가

## 4. 컬럼 / 도메인

- [ ] term exact hit 시 단어 분해를 건너뛰었는가
- [ ] term exact miss 시 term synonym을 조회했는가
- [ ] term synonym 단일 hit 시 단어 분해를 건너뛰었는가
- [ ] term exact / synonym hit 시 신규 용어 등록을 하지 않았는가
- [ ] 단어 exact / synonym / prohibited-word 재사용 후보가 있으면 신규 단어 등록을 하지 않았는가
- [ ] 마지막 단어만 도메인 판단 대상으로 썼는가
- [ ] 기존 단어에 도메인 신규 지정을 하지 않았는가
- [ ] 비종결 단어를 차단했는가
- [ ] 코드 계열 기본값 적용 시 `코드C2` 후보 존재를 확인했는가
- [ ] 신규 도메인 등록 전 기존 도메인 exact / 유사 후보를 확인했는가
- [ ] 신규 도메인 등록에 표준 사전 관리자 승인 또는 프로젝트 표준 정책 근거가 있는가

## 5. 정의서 INSERT

- [ ] 테이블 정의서 INSERT의 `logical_table_name`, `physical_table_name` role 값이 최종 결과와 일치하는가
- [ ] 컬럼 정의서 INSERT의 `logical_column_name`, `physical_column_name` role 값이 최종 결과와 일치하는가
- [ ] 공간정보 컬럼은 `geom / 공간정보` 예외를 지켰는가
- [ ] `table_id` role bind가 일관적인가
- [ ] `alter_add_columns` 요청에서 기존 테이블 정의서 row 존재 확인과 테이블 정의서 UPDATE/NO-OP 판단을 명시했는가
- [ ] `alter_add_columns` 요청에서 추가 컬럼 정의서 INSERT를 누락하지 않았는가
- [ ] `alter_modify_columns` 요청에서 컬럼 정의서 UPDATE를 누락하지 않았는가
- [ ] `drop_columns` 요청에서 컬럼 정의서 DELETE/비활성화/이력 처리 정책을 확정했는가
- [ ] 물리 DDL만 있고 정의서 갱신 계획이 없는 결과를 출력하지 않았는가

## 6. DDL

- [ ] CREATE TABLE 컬럼 정의와 도메인 타입/길이가 일치하는가
- [ ] CREATE TABLE / ALTER / COMMENT / INDEX가 DBMS profile에 맞는 `target_object_identifier`로 namespace-qualified 되었는가
- [ ] PK 이름이 `PK_<TABLE>` 규칙을 따르는가
- [ ] FK 이름이 `FK_<CURRENT>_<REFERENCED>` 규칙을 따르는가
- [ ] INDEX / UNIQUE INDEX 이름 규칙이 맞는가
- [ ] COMMENT 대상과 이름이 일치하는가

## 7. 실행 통제

- [ ] 승인 없는 write execution이 배제됐는가
- [ ] preview-only / blocked / pending 상태가 명확한가
- [ ] live lookup 부재 시 추측을 하지 않았는가

## 8. 최종 출력

- [ ] output contract 순서를 따랐는가
- [ ] blocker와 pending decision을 분리했는가
- [ ] 실행 가능 조건을 명확히 썼는가

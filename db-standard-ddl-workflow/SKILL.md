---
name: db-standard-ddl-workflow
description: Generate standardized DDL, metadata INSERT previews, and naming decisions for Korean business-definition requests that must follow standard word, term, and domain dictionaries. Do not use for generic SQL tuning, ORM modeling, or ad-hoc schema design.
---

## 목적

이 skill은 **표준 단어 / 표준 용어 / 표준 도메인 사전**을 기준으로
테이블명, 컬럼명, 정의서 INSERT SQL, DDL preview를 일관된 절차로 생성한다.

이 skill은 **생성 워크플로 전용**이다.
일반 SQL 튜닝, JPA 엔티티 설계, MyBatis 매퍼 리뷰, 임의 스키마 설계에는 사용하지 않는다.

## 이 skill을 호출해야 하는 경우

- 사용자가 표준 단어/용어/도메인 사전을 기준으로 DDL을 만들고 싶어 할 때
- 테이블명과 컬럼명을 한글 업무정의 기준으로 표준화해야 할 때
- 테이블 정의서 / 컬럼 정의서 INSERT SQL과 CREATE TABLE / 제약조건 / 인덱스 / 주석 SQL이 함께 필요할 때
- 이미지 기반 업무정의서 또는 구조화된 텍스트 요청을 표준 규칙으로 해석해야 할 때

## 이 skill을 호출하지 말아야 하는 경우

- 일반적인 SQL 성능 분석, 실행계획 리뷰, 인덱스 튜닝
- ORM 엔티티 모델링 또는 API DTO 설계
- 표준 사전과 무관한 자유 스키마 설계
- 승인 없이 실제 DB 변경을 수행해야 하는 작업
- 이미 완성된 SQL의 사소한 문법 수정만 필요한 경우

## 필수 입력

### 1. 시작 온보딩 / Execution Context
먼저 `references/05-startup-onboarding.md`와 `references/11-dbms-profile.md`를 읽고 작업 유형, DBMS, Execution Context를 확정한다.

작업 시작 시 현재 작업 디렉토리의 `db-standard-execution-context.yaml`을 먼저 확인한다.
이 파일이 있으면 우선 로드하고, 요약을 사용자에게 확인받은 뒤 일반 업무 테이블 표준화를 진행한다.
파일이 없거나 불완전하면 시작 온보딩으로 돌아간다.
단, 이 파일이 없다는 사실은 신규 프로젝트라는 뜻이 아니다.
기존 프로젝트에 새로 합류한 사용자도 로컬 작업 디렉토리에 이 파일이 없을 수 있으므로,
항상 작업 유형을 먼저 확인한다.

Execution Context가 없거나 재사용할 수 없으면 반드시 아래를 먼저 확인한다.

1. 신규 프로젝트 표준화 작업 시작 또는 기존 프로젝트 표준화 작업 이어서 진행
2. DBMS 종류와 버전. 단, 기존 프로젝트에서 기존 context나 초기 입력 파일로 복원 가능하면 재입력받지 않는다.

작업 유형이 확정되면 현재 작업 디렉토리에 작성용 초기 입력 파일을 생성한다.

- 신규 프로젝트: `assets/initial-context-new-project.template.md` -> `db-standard-initial-context.new.md`
- 기존 프로젝트: `assets/initial-context-existing-project.template.md` -> `db-standard-initial-context.existing.md`
- 확정 실행 컨텍스트: `assets/execution-context.template.yaml` -> `db-standard-execution-context.yaml`

같은 이름의 작성용 파일이 이미 있으면 덮어쓰지 않는다.
작성용 Markdown의 YAML 블록을 파싱하고, 해석한 Execution Context 요약을 사용자에게 먼저 확인받는다.
`db-standard-execution-context.yaml`은 사용자가 직접 작성하는 입력 파일이 아니라,
에이전트가 initial context와 DB 조회 / 검증 결과를 바탕으로 생성 또는 갱신하는 산출물이다.

그 다음 `references/10-execution-context.md`에 따라 아래 값을 확보한다.

- `project.project_id`, `project.project_nm`
- `dbms.type`, `dbms.version`, `dbms.profile`
- `physical_target.db_nm`, `physical_target.target_namespace_map`
- `metadata_repository.project_schema_nm`, 정의서 테이블명
- 신규 프로젝트: 테이블 정의서 / 컬럼 정의서 한글 컬럼 목록
- 기존 프로젝트: `metadata_repository.*.field_map`
- `standard_repository.word_seq`, `standard_repository.term_seq`, 정의서 식별자 생성 규칙
- `run_control.run_mode`
- (선택) `run_control.catalog_lookup_mode`, `run_control.write_execution_enabled`

Execution Context가 없으면 **절대 진행하지 않는다**.

### 2. 요청 본문
`references/20-request-contract.md`에 따라 아래를 검증한다.

- 데이터베이스
- 대상 namespace
- 요청 유형: `create_table`, `alter_add_columns`, `alter_modify_columns`, `drop_columns`
- 테이블 종류
- 실행 요청
- 업무정의 이미지 또는 동등한 텍스트 정의
- 추가 제약(FK, UNIQUE, INDEX, DEFAULT, 기타)

### 3. 실행 가능 상태
- 실제 카탈로그 조회가 가능한지 확인한다.
- 실제 DB 쓰기가 가능한지 확인한다.
- 가능하지 않으면 **추측하지 말고** lookup SQL + pending decisions + preview SQL만 반환한다.

## 항상 먼저 읽을 파일

1. `references/00-rule-priority.md`
2. `references/05-startup-onboarding.md`
3. `references/10-execution-context.md`
4. `references/11-dbms-profile.md`
5. `references/20-request-contract.md`

## 단계별 참조 파일

### 입력 정규화 단계
- `references/30-normalization-rules.md`

### 테이블 처리 단계
- `references/40-table-naming.md`
- `references/13-schema-routing.md`
- `references/11-dbms-profile.md`

### 컬럼 / 도메인 처리 단계
- `references/50-column-domain-decision.md`
- `references/81-spatial-rules.md` (공간정보 테이블일 때만)
- `references/14-bootstrap-role-mapping.md` (신규 프로젝트 정의서 bootstrap일 때)

### SQL 렌더링 단계
- `references/25-catalog-query-templates.md`
- `references/12-metadata-artifact-model.md`
- `references/60-sql-rendering.md`
- `references/80-dbms-dialects.md`

### 종료 전 검증 단계
- `references/70-blocking-rules.md`
- `references/90-output-contract.md`
- `references/95-review-checklist.md`

## 작업 절차

0. **시작 온보딩**
   - 현재 작업 디렉토리의 `db-standard-execution-context.yaml`을 먼저 확인
   - 기존 파일이 있으면 요약과 정합성 검증 결과를 사용자에게 확인받고 재사용
   - 신규 프로젝트인지 기존 프로젝트 이어서 진행인지 확인
   - `db-standard-execution-context.yaml` 부재만으로 신규 프로젝트라고 판단하지 않음
   - 신규 프로젝트이면 사용할 DBMS 종류와 버전을 입력받고 profile을 확정
   - 기존 프로젝트이면 기존 execution context, 초기 입력 파일, DB 조회 결과에서 DBMS profile 복원을 먼저 시도하고, 복원할 수 없을 때만 DBMS 종류와 버전을 입력받음
   - DBMS profile을 확정하고 `db_standard` 논리 저장소의 물리 배치를 결정
   - 작업 유형에 맞는 초기 입력 템플릿을 현재 작업 디렉토리에 작성용 Markdown으로 생성
   - 작성용 파일이 이미 있으면 덮어쓰지 않고 사용 여부를 확인
   - 작성된 Markdown의 YAML 블록을 파싱하고 Execution Context 후보를 구성
   - 신규 프로젝트면 프로젝트 산출물 namespace와 정의서 한글 컬럼 목록을 작성용 파일에서 입력받음
   - 신규 프로젝트의 정의서 테이블 bootstrap에는 표준 사전 조회 / 웹 검색 / 도메인 판단을 적용하지 않음
   - 신규 프로젝트의 정의서 테이블 컬럼은 한글 컬럼명을 자동 `snake_case`로 변환하고 타입은 모두 `text`로 생성
   - 신규 프로젝트의 정의서 한글 테이블명 / 컬럼명은 DB comment로 추가
   - 신규 프로젝트의 내부 field map은 `references/14-bootstrap-role-mapping.md`를 우선 적용한 뒤 생성된 정의서 컬럼명에서 추론
   - 신규 프로젝트는 initial context로 bootstrap preview를 만들고, field map 생성 후 finalized execution context로 일반 업무 테이블 표준화를 진행
   - 기존 프로젝트면 작성용 파일의 위치 정보를 기준으로 실제 DB 조회 후 프로파일을 복원
   - 해석한 Execution Context 요약과 누락 / 충돌 검증 결과를 사용자에게 확인받음
   - 확정된 값은 현재 작업 디렉토리의 `db-standard-execution-context.yaml`에 에이전트가 생성 또는 갱신
   - 테이블 정의서에 `target_schema` 역할이 없으면 중단

1. **Execution Context 검증**
   - 필수 값 누락 여부 확인
   - `dbms.type`과 DBMS profile이 확정됐는지 확인
   - 요청의 `데이터베이스`가 `physical_target.db_nm`과 일치하는지 확인
   - 요청의 대상 namespace가 `physical_target.target_namespace_map`에 정의된 값인지 확인
   - 요청의 주제영역 / 소유자 코드가 대상 namespace 라우팅 규칙과 일치하는지 확인
   - 대상 namespace가 생략되면 주제영역 / 소유자 코드로 단일 `target_namespace_nm`을 확정
   - `run_control.run_mode`와 사용자 `실행 요청`이 일치하는지 확인

2. **요청 계약 검증**
   - 이미지 기반 요청인지, 텍스트 기반 요청인지 판별
   - 필수 입력 누락 시 즉시 중단
   - 이미지에 엔터티가 2개 이상 섞인 경우 즉시 중단

3. **테이블 입력 정규화**
   - 한글 테이블명을 정규화한다.
   - 파생어/복합어 규칙을 적용한다.
   - 테이블 종류에 맞는 접두어를 결정한다.
   - 테이블소유자를 canonical owner segment로 확정한다.

4. **테이블명 생성**
   - 표준 단어 사전에서 각 테이블 단어를 조회한다.
   - exact / synonym / prohibited-word 순서로 기존 표준 단어 재사용을 우선한다.
   - 재사용 가능한 canonical 단어가 있으면 신규 단어 등록으로 진행하지 않는다.
   - 세 단어 제한을 검증한다.
   - 초과 시 조합안을 제안하고, 승인된 조합만 사용한다.
   - 물리 테이블명은 **논리 세그먼트 조립 후 DBMS 방언 단계에서 최종 casing 적용**한다.
   - 요청 유형에 따라 테이블 정의서 INSERT / UPDATE / NO-OP preview를 만든다.

5. **컬럼 목록 순회**
   각 컬럼에 대해 아래 순서를 강제한다.

   1) 용어 DB(trm) exact 선조회  
   2) 용어 exact miss 시 용어 synonym 조회  
   3) 용어 exact / synonym 모두 miss 시 단어 분해  
   4) 각 단어 정규화 및 표준 단어 조회  
   5) 마지막 단어 도메인 판단  
   6) term exact / term synonym / word exact / word synonym / prohibited-word 결과에서 재사용 가능한 후보가 있으면 신규 등록보다 재사용  
   7) 필요 시 신규 도메인 / 신규 단어 / 신규 용어 INSERT preview 생성. 단, 명시 승인 전 실행 bundle에는 포함하지 않음  
   8) 요청 유형에 따라 컬럼 정의서 INSERT / UPDATE / DELETE / 비활성화 / NO-OP preview 생성
   9) 물리 컬럼명 / 데이터 타입 / 길이 / 제약조건 확정

6. **마지막 단어 도메인 판단**
   - 마지막 단어만 도메인 판단 대상이다.
   - 기존 단어에 도메인을 신규 지정하지 않는다.
   - 신규 도메인 등록은 가능하지만 기존 도메인 exact / 유사 후보 재사용을 먼저 검토한다.
   - 신규 도메인은 재사용 가능한 후보가 없고 표준 사전 관리자 승인 또는 프로젝트 표준 정책 근거가 있을 때만 preview를 생성한다.
   - 컬럼 단어 수가 4 초과면 즉시 차단한다.
   - 비종결 단어 차단 규칙을 적용한다.
   - 공간정보 컬럼은 `geom / 공간정보` 예외 규칙을 적용한다.

7. **SQL preview bundle 생성**
   아래 순서로 묶는다.

   - 검증 요약
   - lookup SQL
   - pending decisions
   - 표준사전 보완 INSERT preview (필요 시, 명시 승인 대상)
   - 정의서 갱신 계획: 테이블 정의서 INSERT/UPDATE/NO-OP, 컬럼 정의서 INSERT/UPDATE/DELETE/비활성화/NO-OP
   - 테이블 정의서 INSERT preview
   - 컬럼 정의서 INSERT preview
   - CREATE SEQUENCE preview (요청 시)
   - CREATE TABLE 또는 ALTER TABLE preview
   - PK / FK / INDEX / UNIQUE INDEX preview
   - COMMENT preview

   업무 테이블 CREATE/ALTER/DROP preview를 생성하는 모든 작업은 테이블 정의서와 컬럼 정의서의 갱신 계획을 반드시 포함한다.
   정의서 갱신 계획 없이 물리 DDL만 출력하지 않는다.

8. **DBMS 방언 적용**
   - Oracle: `UPPER_SNAKE_CASE`
   - PostgreSQL / MySQL: `lower_snake_case`
- DBMS profile에 맞는 namespace-qualified identifier를 사용한다.
   - quote identifier는 프로젝트 규칙이 없는 한 사용하지 않는다.

9. **실행 통제**
   - `run_control.run_mode != execute` 이면 절대 쓰기 SQL을 실행하지 않는다.
   - `run_control.run_mode == execute` 이어도 설계자의 명시적 승인과 쓰기 가능 환경이 모두 있어야 실행 가능하다.
   - 둘 중 하나라도 없으면 preview만 반환한다.
   - 물리 DDL은 확정된 `target_namespace_nm`을 DBMS profile에 맞게 렌더링한 대상에만 실행한다.

## 강제 동작

- 표준 사전 조회가 불가능한데도 약어명이나 도메인을 **추측하지 않는다**.
- 신규 도메인 등록 전에 기존 도메인 exact / 유사 후보를 조회하고 재사용 가능성을 먼저 판단한다.
- 신규 단어 / 신규 용어 등록은 term exact / term synonym / word exact / word synonym / prohibited-word 재사용 후보가 없을 때만 진행한다.
- 단일 재사용 후보가 있는데 사용자 선호만으로 신규 등록하거나 canonical 후보를 우회하지 않는다.
- 재사용 후보 거부는 표준 사전 관리자 승인 또는 프로젝트 표준 정책 근거가 있을 때만 재검토한다.
- term synonym / word synonym / prohibited-word 매칭 결과가 둘 이상이면 **단일 결과로 임의 확정하지 않는다**.
- 최종 한글 테이블명 / 컬럼명은 canonical `trm_nm` 또는 canonical `word_nm` 기준으로 확정한다.
- 모든 SQL은 DBMS profile에 맞는 namespace 포함 전체 식별자를 사용한다.
- 실제 DB 실행 대신 preview를 반환할 때는, 실행 불가 이유를 명시한다.
- `references/90-output-contract.md` 형식을 따른다.

## 종료 조건

아래가 모두 충족되면 완료다.

- validation status가 명시되었다.
- blocker / pending decision이 분리되어 제시되었다.
- 테이블명 / 컬럼명 / 정의서 INSERT / DDL 사이의 식별자가 일관된다.
- 코멘트는 정의서 한글명과 일치한다.
- `run_control.run_mode`에 맞게 preview 또는 execution plan이 구분되었다.
- `references/95-review-checklist.md` 기준 점검이 끝났다.

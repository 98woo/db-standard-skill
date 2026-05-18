# 00. 규칙 우선순위와 해석 원칙

이 문서는 skill이 가장 먼저 읽어야 하는 기준 문서다.

## 1. 실행 기준 원칙

이 runtime skill은 `SKILL.md`와 `references/*.md`의 canonical 규칙만 실행 기준으로 사용한다.

과거 원문 문서는 설계 이력 보존용이며 runtime skill 안에서 직접 참조하지 않는다.
원문과 canonical 규칙이 다르면 canonical 규칙을 따른다.

## 2. 우선순위

충돌 시 아래 순서로 판단한다.

1. 시작 온보딩 / Execution Context / 실행 통제 / 권한 규칙
2. 표준 단어 / 용어 / 도메인 사전 재사용 규칙
3. 테이블명 / 컬럼명 / 도메인 판단 규칙
4. SQL rendering / output contract 규칙
5. 설계자 입력  
   단, 위 1~4를 위반하는 입력은 허용하지 않는다.

## 3. 보완 규칙

아래는 skill 안정성을 위해 추가한 실행 규칙이다.

### 3.1 표준 저장소와 프로젝트 값 분리
- 표준 저장소 DB는 항상 `db_standard`다.
- 표준 사전 namespace는 항상 `db_standard`다.
- 표준 단어 / 용어 / 도메인 사전은 사용자가 사전에 구축한다.
- 프로젝트 산출물은 항상 `db_standard` 표준 저장소의 `db_standard` namespace에 둔다.
- 실제 database / schema / owner / namespace 렌더링은 DBMS profile을 따른다.
- 최초 실행 시 작업 유형에 맞는 초기 입력 Markdown 템플릿을 현재 작업 디렉토리에 작성용 파일로 생성하고,
  그 YAML 블록을 Execution Context의 기준으로 사용한다.
- 신규 프로젝트의 테이블 정의서 / 컬럼 정의서 테이블 bootstrap은 표준화 작업이 아니므로,
  표준 사전 조회 / 도메인 판단 / 웹 검색을 적용하지 않는다.
- 신규 프로젝트 정의서 테이블 컬럼은 한글 입력을 자동 `snake_case` 물리명으로 변환하고,
  타입은 모두 `text`로 생성하며, 한글명은 comment로 남긴다.
- 업무 대상 namespace는 `physical_target.target_namespace_map`으로 관리하고,
  주제영역 / 소유자 코드에 따라 요청마다 하나의 `target_namespace_nm`을 확정한다.
- `physical_target.target_namespace_map`은 최초 1회 입력받으며, namespace가 하나여도 `namespace(subject)` 형식을 사용한다.
- 정의서 namespace(`metadata_repository.project_schema_nm`)와 업무 대상 namespace(`target_namespace_nm`)를 혼동하지 않는다.
- 테이블 정의서에는 `target_schema` 역할 컬럼이 필수다.

### 3.2 논리 식별자 생성 후 DBMS별 렌더링
- 먼저 canonical logical segments를 만든다.
- 마지막 단계에서 DBMS casing을 적용한다.

### 3.3 exact match 우선
- word / term exact match를 가장 먼저 시도한다.
- 컬럼명은 term exact miss 시 term synonym을 먼저 확인한 뒤 단어 분해로 내려간다.
- 단어 분해 후에는 word exact miss 단어에 대해서만 word synonym / prohibited-word 검색을 한다.
- term synonym / word synonym / prohibited-word 결과가 2건 이상이면 임의 확정 금지

### 3.4 표준 사전 재사용 우선
- 신규 단어 / 신규 용어 등록은 최후 수단이다.
- 신규 등록 전에 기존 용어 exact, 기존 용어 synonym, 기존 단어 exact, 기존 단어 synonym, prohibited-word를 반드시 확인한다.
- 기존 사전에 재사용 가능한 canonical 값이 있으면 신규 등록보다 재사용을 우선한다.
- 재사용 후보가 2건 이상이면 임의 선택하지 않고 pending decision으로 돌린다.
- 단일 재사용 후보가 있는데 사용자가 이를 거부하면 신규 등록으로 우회하지 않고 pending decision으로 돌린다.
- 이 경우 표준 사전 관리자 승인 또는 프로젝트 표준 정책 근거가 확보되어야 신규 등록 검토를 재개할 수 있다.
- 신규 등록은 재사용 가능한 후보가 없고 필수 도메인 / 약어 판단이 완료된 경우에만 검토한다.
- 신규 도메인 등록도 가능하지만, 기존 도메인 exact / 유사 후보 재사용 검토 후 최후 수단으로만 진행한다.
- 신규 도메인 등록은 표준 사전 관리자 승인 또는 프로젝트 표준 정책 근거가 있어야 preview를 생성한다.

### 3.5 lookup 불가 시 추측 금지
- live catalog lookup이 없으면 약어명과 도메인명을 추측하지 않는다.
- 필요한 SELECT SQL과 pending decisions만 반환한다.

### 3.6 UNIQUE 기본 전략
- 별도 프로젝트 규칙이 없으면 UNIQUE는 `UNIQUE INDEX` 로 렌더링한다.
- `UK_...` 제약조건 규칙이 있으면 프로젝트 AGENTS에서 override 한다.

### 3.7 공간정보 안전 규칙
- `geom / 공간정보` 규칙만 자동 확정한다.
- geometry subtype, SRID, spatial index는 명시 입력 없으면 추측 금지

## 4. 모든 단계 공통 불변식

- 모든 SQL은 DBMS profile에 맞는 namespace-qualified identifier를 사용한다.
- 승인 없는 DB write는 실행하지 않는다.
- 최종 한글명은 canonical `word_nm` 기준으로 확정한다.
- 코드 계열 기본값은 `코드C2` 이지만, 후보가 불명확하면 추측하지 않는다.
- blocker / pending decision / preview-only 상태를 분리해서 출력한다.

## 5. Canonical 파일 역할

| canonical file | 역할 |
| --- | --- |
| 05-startup-onboarding.md | 최초 사용자 / 기존 사용자 온보딩 |
| 10-execution-context.md | 프로젝트 고정 실행 컨텍스트 |
| 11-dbms-profile.md | DBMS별 표준 저장소 / target namespace 렌더링 |
| 12-metadata-artifact-model.md | 테이블 정의서 / 컬럼 정의서 산출물 모델 |
| 13-schema-routing.md | 대상 namespace 라우팅 |
| 20-request-contract.md | 사용자 업무 테이블 요청 계약 |
| 30-normalization-rules.md | 한글 입력 정규화 |
| 40-table-naming.md | 테이블명 표준화 |
| 50-column-domain-decision.md | 컬럼명 / 도메인 판단 |
| 60-sql-rendering.md | SQL preview / execution rendering |
| 70-blocking-rules.md | blocked / pending / preview-only 판정 |
| 80-dbms-dialects.md | DBMS 방언별 렌더링 차이 |
| 81-spatial-rules.md | 공간정보 예외 규칙 |

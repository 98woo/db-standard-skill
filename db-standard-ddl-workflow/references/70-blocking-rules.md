# 70. 차단 규칙 (Blocking Rules)

이 문서는 skill이 더 진행하면 안 되는 상황을 정의한다.

## 1. 상태 분류

### BLOCKED
규칙 위반 또는 필수 정보 부족으로 진행 불가

### PENDING_DECISION
추가 선택 또는 입력이 필요하지만, 일부 preview는 가능

### PREVIEW_ONLY
실행 권한은 없지만 preview 생성은 가능

## 2. 즉시 BLOCKED 조건

### 2.1 Execution Context 없음
- DBMS 종류 미선택
- DBMS profile 미확정
- 작업 유형 미선택: 신규 프로젝트 표준화 작업 시작 / 기존 프로젝트 표준화 작업 이어서 진행
- 작업 유형에 맞는 초기 입력 Markdown 파일 미작성
- 초기 입력 Markdown의 YAML 블록 파싱 실패
- 해석한 Execution Context 요약에 대한 사용자 확인 없음
- 필수 context 값 누락
- namespace명 / 시퀀스명 / 테이블명 불명확
- `target_namespace_map` 누락
- 신규 프로젝트에서 정의서 한글 컬럼 목록 누락
- 신규 프로젝트에서 한글 컬럼명 자동 `snake_case` 변환 불가
- 테이블 정의서 / 컬럼 정의서 field map 자동 추론 실패
- 테이블 정의서에 `target_schema` 역할로 추론 가능한 컬럼 없음

### 2.2 요청 계약 위반
- 데이터베이스 누락
- 테이블 종류 누락
- 실행 요청 누락
- 이미지 요청인데 핵심 필드 누락
- 이미지에 엔터티가 2개 이상 포함됨

### 2.3 명명 규칙 위반
- 테이블 종류가 허용값 외
- 컬럼명 5단어 이상
- owner 정규화 실패
- 기존 단어에 도메인 신규 지정 시도

### 2.4 도메인 의미 완결 위반
마지막 단어가 아래 목록이면 blocked:

- 분류
- 구분
- 유형
- 상태
- 종류
- 단계

### 2.5 live lookup 없이 추측 필요
- 표준 사전 조회 없이 약어를 추측해야 하는 상황
- 표준 사전 조회 없이 도메인을 추측해야 하는 상황
- 표준 사전 조회 없이 재사용 후보 유무를 판단해야 하는 상황
- 기존 도메인 exact / 유사 후보 조회 없이 신규 도메인 등록을 진행하려는 상황
- 재사용 후보 확인 없이 신규 단어 / 신규 용어 등록을 진행하려는 상황

### 2.6 요청 / context 불일치
- 요청 `데이터베이스` != context `target_db_nm`
- 요청 `대상 namespace`가 context `target_namespace_map`에 없음
- 요청 `대상 namespace`와 주제영역 / 소유자 코드가 context `target_namespace_map` 기준으로 충돌
- 요청 `대상 namespace`가 없고 주제영역 / 소유자 코드로 단일 namespace를 확정할 수 없음
- context `default_target_namespace_nm`이 `target_namespace_map`에 없음
  단, AGENTS override가 있으면 예외

## 3. PENDING_DECISION 조건

- synonym / prohibited-word 다중 매칭
- 단일 재사용 후보를 사용자가 거부했지만 표준 사전 관리자 승인 또는 프로젝트 표준 정책 근거가 없음
- 신규 도메인 등록이 필요하지만 표준 사전 관리자 승인 또는 프로젝트 표준 정책 근거가 없음
- 테이블명 4단어 이상으로 조합 승인 필요
- 마지막 단어 분해 필요
- 도메인 후보가 2건 이상
- 주제영역 / 소유자 코드가 여러 대상 namespace에 매칭됨
- geometry subtype / SRID / spatial index 미입력
- 참조 테이블 / 참조 컬럼 정보가 없어 FK 확정 불가

## 4. PREVIEW_ONLY 조건

아래 중 하나라도 해당하면 write execution은 하지 않는다.

- `run_mode != execute`
- `write_execution_enabled = false`
- 설계자의 명시 승인 없음
- 실제 실행 도구 부재

## 5. 차단 시 응답 방식

blocked 응답에는 아래를 반드시 포함한다.

- 상태: `BLOCKED`
- 차단 이유
- 위반 규칙 파일
- 진행을 재개하려면 필요한 입력
- 가능한 경우 lookup SQL 또는 수정 예시

## 6. pending 응답 방식

pending 응답에는 아래를 포함한다.

- 상태: `PENDING_DECISION`
- 필요한 선택 또는 보완 입력
- 현재까지 확정된 결과
- 현재 단계에서 생성 가능한 preview SQL

## 7. preview-only 응답 방식

preview-only 응답에는 아래를 포함한다.

- 상태: `PREVIEW_ONLY`
- 실제 실행이 되지 않는 이유
- 생성된 preview SQL
- 실행 가능해지기 위한 조건

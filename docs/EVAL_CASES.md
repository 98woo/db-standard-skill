# EVAL CASES

아래 케이스는 skill 품질 검증용이다.
각 케이스마다 **skill이 호출돼야 하는지**, **preview만 반환해야 하는지**, **차단해야 하는지**를 함께 검사한다.

## 1. 정상 생성

### 케이스
- 일반 테이블
- 테이블명 2단어
- 컬럼 6개
- 용어 DB hit 3개, 단어 분해 3개
- run_mode = preview

### 기대 결과
- skill 호출
- validation pass
- lookup SQL / preview INSERT / preview DDL 반환
- 실제 DB execution 없음

## 2. 테이블명 4단어 입력

### 기대 결과
- 차단이 아니라 조합안 제시
- 승인된 조합 없으면 pending decision
- 임의 조합 금지

## 3. 컬럼명 5단어 입력

### 기대 결과
- 즉시 blocked
- “컬럼 명은 네 단어를 초과할 수 없습니다.” 성격의 오류 반환
- 다음 단계 진행 금지

## 4. 용어 DB 즉시 hit

### 기대 결과
- 단어 분해 수행 금지
- trm_eng_abbr_nm, dmn_nm 기준으로 바로 확정
- domain detail lookup 수행

## 5. 마지막 단어 존재 + 도메인 미존재

### 기대 결과
- 기존 단어에 도메인 신규 지정 금지
- 도메인 선택 UI 제공 금지
- blocked 상태 반환

## 6. 마지막 단어 미존재 + 컬럼 단어 수 = 4

### 기대 결과
- 신규 단어 등록 + 도메인 선택 절차 진입
- 도메인 그룹 / 분류 / 타입 선택 흐름 제시
- 비종결 단어면 차단

## 7. 마지막 단어 미존재 + 컬럼 단어 수 <= 3

### 기대 결과
- 마지막 단어를 도메인 대상 단어로 간주
- 도메인 선택 후 “앞 단어 + 도메인” 분해 요청
- 앞 단어가 없으면 신규 단어 INSERT preview

## 8. synonym / prohibited word 다중 매칭

### 기대 결과
- 임의 확정 금지
- ambiguous match로 pending decision

## 8-1. 재사용 후보 우선

### 케이스
- 용어 exact miss
- 단어 exact miss
- synonym 또는 prohibited-word에서 단일 canonical 단어 매칭

### 기대 결과
- 신규 단어 등록 금지
- canonical `word_nm`, `word_eng_abbr_nm` 재사용
- 최종 논리명과 comment는 canonical 기준 사용

## 8-2. 기존 용어 재사용

### 케이스
- 공백 제거 컬럼명이 용어 사전에 exact hit

### 기대 결과
- 단어 분해 금지
- 신규 용어 등록 금지
- `trm_eng_abbr_nm`, `dmn_nm` 재사용

## 8-3. 단일 재사용 후보 거부

### 케이스
- synonym 또는 prohibited-word에서 단일 canonical 단어 매칭
- 사용자가 canonical 단어 대신 원 입력 단어를 신규 등록하자고 요청

### 기대 결과
- 사용자 선호만으로 신규 등록 금지
- 표준 사전 관리자 승인 또는 프로젝트 표준 정책 근거가 없으면 pending decision
- 승인 / 근거 확보 전까지 canonical 후보 우회 금지

## 9. 코드 계열 기본값

### 기대 결과
- 명시 지시가 없으면 `코드C2` 우선
- 단, 후보에 `코드C2`가 없으면 추측 금지

## 9-1. 신규 도메인 필요

### 케이스
- 요청 컬럼의 최종 도메인 후보가 기존 도메인 exact lookup에 없음
- 동일 또는 유사 `data_type_nm`, `data_len`, `data_dc_len` 후보 조회 필요

### 기대 결과
- 기존 도메인 exact / 유사 후보 조회 먼저 수행
- 재사용 가능한 후보가 있으면 신규 도메인 등록 금지
- 재사용 후보가 없고 표준 사전 관리자 승인 또는 프로젝트 표준 정책 근거가 있을 때만 신규 도메인 INSERT preview 생성
- 승인 전에는 신규 도메인 INSERT를 실행 bundle에 포함하지 않음

## 10. 공간정보 테이블

### 기대 결과
- 접두어 `GM`
- 공간정보 컬럼은 `geom / 공간정보`
- geometry subtype / SRID / spatial index 정보 없으면 pending decision

## 11. should not trigger

### 입력
- “이 SQL 왜 느려?”
- “JPA 엔티티 설계 봐줘”
- “MyBatis 쿼리 튜닝해줘”

### 기대 결과
- 이 skill을 호출하지 않음

## 12. execute 요청이지만 승인 없음

### 기대 결과
- preview만 반환
- write execution 미수행
- 실행 불가 이유 명시

## 13. 대상 namespace가 여러 개인 프로젝트

### 케이스
- Execution Context의 `target_namespace_map`이 `namespace_a(owner_a), namespace_b(owner_b)`로 설정됨
- 요청에 대상 namespace가 없음
- 요청의 테이블 소유자가 `OWNER_B`

### 기대 결과
- `namespace_b`를 대상 namespace로 자동 확정
- 정의서 namespace와 업무 대상 namespace를 혼동하지 않음

## 14. 대상 namespace와 주제영역 충돌

### 케이스
- Execution Context의 `target_namespace_map`이 `namespace_a(owner_a), namespace_b(owner_b)`로 설정됨
- 요청 대상 namespace가 `namespace_a`
- 요청의 테이블 소유자 또는 주제영역 코드가 `owner_b`

### 기대 결과
- 즉시 blocked
- 대상 namespace `namespace_a`는 `owner_a` 주제영역 / 소유자 코드에만 허용된다는 메시지 반환

## 15. 최초 실행 - 신규 프로젝트

### 케이스
- Execution Context 없음
- 사용자가 `신규 프로젝트 표준화 작업 시작` 선택

### 기대 결과
- 현재 작업 디렉토리에 `db-standard-initial-context.new.md` 작성용 파일 생성
- 원본 템플릿은 `assets/initial-context-new-project.template.md` 사용
- 같은 이름의 파일이 이미 있으면 덮어쓰기 금지
- 사용자가 작성한 YAML 블록 파싱 전 일반 DDL 작업 진행 금지
- 테이블 정의서 / 컬럼 정의서 한글 컬럼명은 자동 `snake_case` 물리 컬럼명으로 변환
- 정의서 테이블 컬럼 타입은 모두 `text`
- 한글 테이블명 / 컬럼명은 comment로 렌더링
- 표준 사전 조회 / 도메인 판단 / 웹 검색 미수행
- 생성된 정의서 컬럼명으로 내부 field map 자동 추론

## 16. 최초 실행 - 기존 프로젝트 이어서 진행

### 케이스
- Execution Context 없음
- 사용자가 `기존 프로젝트 표준화 작업 이어서 진행` 선택

### 기대 결과
- 현재 작업 디렉토리에 `db-standard-initial-context.existing.md` 작성용 파일 생성
- 원본 템플릿은 `assets/initial-context-existing-project.template.md` 사용
- field map이 비어 있으면 실제 정의서 테이블 조회로 추론
- 추론이 모호하면 pending decision

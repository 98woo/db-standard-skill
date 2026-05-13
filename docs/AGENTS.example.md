# Project AGENTS example for DB standardization workflow

이 파일은 예시다.
프로젝트 루트에 복사한 뒤 `AGENTS.md`로 사용한다.

## 기본 작업 원칙

- DB 표준화 관련 요청에는 `db-standard-ddl-workflow` skill을 명시적으로 호출한다.
- 기본 실행 모드는 `preview` 이다.
- 승인 없는 DB write는 절대 수행하지 않는다.
- 모든 SQL은 DBMS profile에 맞는 namespace-qualified identifier를 사용한다.
- 표준 사전 lookup 결과가 없으면 약어나 도메인을 추측하지 않는다.

## 프로젝트 기본값 예시

- 기본 DBMS: PostgreSQL
- 기본 identifier style: lower_snake_case
- 표준 namespace 기본값: db_standard
- 프로젝트 산출물 위치: `db_standard` 표준 저장소의 `db_standard` namespace
- 업무 대상 namespace 라우팅: Execution Context의 `target_namespace_map`
- UNIQUE 기본 전략: UNIQUE INDEX (`UIDX_...`)
- sequence 생성은 명시 요청이 있을 때만 수행

## skill 호출 전 준비

아래가 모두 있어야 한다.

- execution context
- 요청 템플릿
- 대상 namespace 또는 주제영역 / 소유자 코드. `target_namespace_map`으로 단일 namespace가 확정돼야 함
- 이미지 또는 텍스트 업무정의
- 실행 요청 (`SQL만 작성` / `SQL 작성 후 승인 대기` / `실제 DB 실행`)

## 출력 정책

항상 아래 순서를 따른다.

1. validation summary
2. resolved names
3. blockers
4. pending decisions
5. lookup SQL
6. insert preview SQL
7. ddl preview SQL
8. final notes

## override 예시

### UNIQUE를 constraint로 써야 하는 프로젝트
아래 규칙이 있으면 skill 기본값을 덮어쓴다.

- UNIQUE 제약조건 이름: `UK_<TABLE_NAME>_<COLUMN_NAME>`

### owner mapping이 별도 테이블에 있는 프로젝트
아래 규칙이 있으면 표준 단어 테이블 대신 owner mapping을 우선 사용한다.

- owner mapping table: `meta.tb_owner_map`

### 공간정보 프로젝트
아래 규칙이 있으면 `references/81-spatial-rules.md`보다 우선한다.

- 기본 geometry type
- 기본 SRID
- spatial index 생성 여부 및 명명 규칙

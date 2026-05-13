# 40. 테이블 명명 규칙

## 목차

- [1. 입력](#1-입력)
- [2. 공통 규칙](#2-공통-규칙)
- [3. 테이블 접두어](#3-테이블-접두어)
- [4. 테이블 소유자](#4-테이블-소유자)
- [5. 테이블명 생성 절차](#5-테이블명-생성-절차)
- [6. 단어 수 초과 처리](#6-단어-수-초과-처리)
- [7. 테이블 정의서 INSERT 규칙](#7-테이블-정의서-insert-규칙)
- [8. 중복 확인](#8-중복-확인)
- [9. blocked / pending 구분](#9-blocked--pending-구분)

## 1. 입력

필수 입력:
- 한글 테이블명
- 테이블 종류
- 테이블소유자

권장 입력:
- 주제 영역 명
- 주제 영역 코드
- 주제 영역 그룹 명
- 데이터베이스 (`target_db_nm`)
- 대상 namespace (`target_namespace_nm`)

## 2. 공통 규칙

- 테이블명은 원칙적으로 표준 단어 약어를 사용한다.
- 접두사와 테이블소유자를 제외한 본체 단어 수는 3개를 초과할 수 없다.
- 테이블소유자는 접두사 바로 뒤에 둔다.
- 단어는 `_` 로 구분한다.
- 복합 약어는 각 원 단어 약어의 앞글자를 순서대로 사용한다.
- 복합 약어는 사용자 승인 후에만 사용한다.

## 3. 테이블 종류별 접두사

| 테이블 종류 | 접두사 |
| --- | --- |
| 일반 테이블 | TB |
| 공간정보 테이블 | GM |
| 전자정부 프레임워크 | TC |
| 연계 테이블 | TR |

## 4. 테이블소유자 처리

### 4.1 owner가 이미 canonical abbreviation인 경우
아래와 같으면 그대로 사용 가능하다.

- 프로젝트가 인정한 영문 약어
- 대문자/소문자 라틴 문자 기반 owner code

### 4.2 owner가 한글 또는 비정규 값인 경우
아래 순서로 정규화한다.

1. 프로젝트 owner mapping
2. 표준 단어 사전 조회
3. 둘 다 없으면 blocked

## 5. 테이블명 처리 순서

1. raw 한글 테이블명 확보
2. 정규화 규칙 적용
3. 단어 분해
4. 각 단어 exact 조회
5. miss 시 synonym / prohibited-word 조회
6. canonical `word_nm`, `word_eng_abbr_nm` 확보
7. 본체 단어 수 검증
8. 접두사 + owner + 본체 약어 조합
9. DBMS별 casing 적용

대상 namespace 확정:
- 요청에 대상 namespace가 있으면 `target_namespace_map`에 존재하는지 확인한다.
- 요청의 주제영역 코드 또는 테이블소유자 코드가 대상 namespace의 `subject_area_cds` 또는 `owner_codes`에 포함되는지 확인한다.
- 요청에 대상 namespace가 없으면 주제영역 코드 또는 테이블소유자 코드로 `target_namespace_map`에서 단일 namespace를 찾아 확정한다.
- namespace와 주제영역 / 소유자 코드가 충돌하면 blocked 상태다.
- 여러 namespace가 매칭되면 pending decision 상태다.

## 5.1 테이블명 재사용 우선

테이블명 본체 단어는 신규 단어 등록보다 기존 표준 단어 재사용을 우선한다.

적용 순서:

1. 각 단어 exact 조회
2. exact miss인 단어만 synonym / prohibited-word 조회
3. 단일 canonical 후보가 있으면 해당 `word_nm`, `word_eng_abbr_nm` 재사용
4. 후보가 2건 이상이면 pending decision
5. 재사용 후보가 없을 때만 신규 단어 등록 검토

주의:

- synonym / prohibited-word 매칭 시 원 입력 단어가 아니라 canonical `word_nm`을 최종 논리명과 comment 기준으로 사용한다.
- 단일 canonical 후보를 사용자 선호만으로 거부하면 신규 단어 등록으로 우회하지 않고 pending decision으로 돌린다.
- 테이블 단어 신규 등록은 도메인 귀속 대상이 아니므로 `dmn_yn='N'`을 사용한다.
- live lookup 없이 신규 단어 약어를 추측하지 않는다.

## 6. 단어 수 제한

### 6.1 3단어 이하
- 그대로 진행한다.

### 6.2 4단어 이상
- 임의 축약 금지
- 복합 약어 조합안을 제안한다.
- 승인된 조합만 사용한다.
- 승인 전에는 pending decision 상태다.

## 7. 논리 식별자 조립

물리명 렌더링 전 canonical logical segments 예시:

```text
[PREFIX, OWNER, WORD1_ABBR, WORD2_ABBR, WORD3_ABBR]
```

예시:
- 일반 테이블 / owner OWN / 사용자 정보
  - logical: `TB_OWN_USER_INFO`
- 공간정보 테이블 / owner GEO / 격자 정보
  - logical: `GM_GEO_GRID_INFO`

## 8. 테이블 정의서 INSERT 규칙

테이블 정의서 INSERT preview는 고정 컬럼명을 가정하지 않는다.
`references/12-metadata-artifact-model.md`의 table definition field map을 기준으로 렌더링한다.

필수 role:

- `table_id`
- `target_db`
- `target_schema`
- `owner`
- `logical_table_name`
- `physical_table_name`
- `table_type`

role 값:

- `table_id` = `{tbl_dfn_seq}` next value 또는 프로젝트 정의서의 식별자 생성 규칙
- `target_db` = 요청 데이터베이스 (`target_db_nm`)
- `target_schema` = 확정된 대상 namespace (`target_namespace_nm`). 정의서 호환 role 이름은 유지한다.
- `owner` = 정규화된 테이블소유자
- `logical_table_name` = canonical 한글 테이블명
- `physical_table_name` = 최종 영문 테이블명
- `table_type` = 정규화된 테이블 종류

관계 엔터티, 설명, 생성일시 같은 추가 role은 프로젝트 정의서 field map에 있을 때만 반영한다.
생성되는 COMMENT ON TABLE은 `logical_table_name` 값을 사용한다.

주의:
- 테이블 정의서에는 `target_schema` role이 필수다.
- 정의서 등록과 중복 검사는 `target_db + target_schema + physical_table_name` 기준으로 수행한다.
- `target_schema` role이 없으면 대상 namespace를 생략한 식별 기준으로 대체하지 말고 blocked 처리한다.

## 9. 신규 단어 등록

테이블 본체 단어 중 표준 단어 사전에 없는 경우,
프로젝트 정책상 허용된다면 신규 단어 INSERT preview를 생성할 수 있다.

기본 규칙:
- exact / synonym / prohibited-word 조회에서 재사용 후보가 없어야 한다.
- 테이블 단어는 도메인 귀속 대상이 아니므로 `dmn_yn='N'`
- 실제 INSERT 실행은 승인 후에만 가능

## 10. blocked 조건

- 테이블 종류가 허용값 밖
- owner 정규화 실패
- 4단어 이상인데 승인된 조합 없음
- live lookup 부재 상태에서 약어를 추측하려는 경우

# 50. 컬럼 명 처리와 마지막 단어 도메인 판단

이 문서는 전체 skill의 핵심 분기 엔진이다.

## 목차

- [1. 컬럼 입력 공통 규칙](#1-컬럼-입력-공통-규칙)
- [2. 처리 순서](#2-처리-순서)
- [3. 용어 DB(trm) exact / synonym 선조회](#3-용어-dbtrm-exact--synonym-선조회)
- [4. 용어 miss 시 단어 분해](#4-용어-miss-시-단어-분해)
- [5. 마지막 단어 도메인 판단 규칙](#5-마지막-단어-도메인-판단-규칙)
- [6. 도메인 선택 절차](#6-도메인-선택-절차)
- [7. 비종결 단어 차단 규칙](#7-비종결-단어-차단-규칙)
- [8. 영문 컬럼명 생성 규칙](#8-영문-컬럼명-생성-규칙)
- [9. 컬럼 정의서 INSERT 규칙](#9-컬럼-정의서-insert-규칙)
- [10. 신규 도메인 등록 규칙](#10-신규-도메인-등록-규칙)
- [11. 신규 용어 등록 규칙](#11-신규-용어-등록-규칙)
- [12. 신규 단어 등록 규칙](#12-신규-단어-등록-규칙)
- [13. blocked / pending 구분](#13-blocked--pending-구분)

## 1. 컬럼 입력 공통 규칙

- 컬럼은 다중 입력으로 처리한다.
- 각 컬럼은 한글 컬럼명을 기준으로 시작한다.
- 부가 입력으로 PK, FK, NULL 여부, DEFAULT, INDEX, UNIQUE 등을 받을 수 있다.
- 컬럼 단어 수는 4를 초과할 수 없다.
- 마지막 단어만 도메인 판단 대상이다.
- 기존 단어에 도메인을 신규 지정하는 행위는 금지한다.

## 2. 처리 순서

1. raw 한글 컬럼명 확보
2. 공백 제거한 문자열로 **term exact lookup**
3. term exact hit면 즉시 확정하고 종료
4. term exact miss면 **term synonym lookup**
5. term synonym 단일 hit면 canonical term으로 확정하고 종료
6. term exact / synonym 모두 miss면 단어 분해
7. 각 단어 정규화 / canonicalization
8. 마지막 단어 도메인 판단
9. 영문 컬럼명 조합
10. 필요 시 신규 도메인 / 신규 단어 / 신규 용어 INSERT preview 생성
11. 컬럼 정의서 INSERT preview 생성

## 2.1 컬럼명 재사용 우선

컬럼명은 신규 단어 / 신규 용어 등록보다 기존 용어와 단어 재사용을 우선한다.

재사용 판단 순서:

1. 공백 제거한 컬럼명으로 용어 exact lookup
2. 용어 hit 시 `trm_eng_abbr_nm`, `dmn_nm`을 그대로 재사용하고 단어 분해를 중단
3. 용어 exact miss 시 용어 synonym lookup
4. 용어 synonym 단일 hit 시 canonical `trm_nm`, `trm_eng_abbr_nm`, `dmn_nm`을 재사용하고 단어 분해를 중단
5. 용어 exact / synonym 모두 miss 시 단어 분해
6. 각 단어 exact lookup
7. exact miss 단어에 대해서만 word synonym / prohibited-word lookup
8. 단일 canonical 후보가 있으면 canonical `word_nm`, `word_eng_abbr_nm` 재사용
9. 재사용 후보가 없을 때만 신규 단어 / 신규 용어 등록 검토

적용 원칙:

- 기존 용어가 있으면 신규 용어를 등록하지 않는다.
- 용어 synonym으로 재사용 가능한 canonical 용어가 있으면 신규 용어를 등록하지 않는다.
- existing word exact / synonym / prohibited-word로 재사용 가능한 단어가 있으면 신규 단어를 등록하지 않는다.
- term synonym 매칭은 원 입력을 유지하지 않고 canonical `trm_nm`으로 치환한다.
- word synonym / prohibited-word 매칭은 원 입력을 유지하지 않고 canonical `word_nm`으로 치환한다.
- 후보가 2건 이상이면 임의 확정하지 않고 pending decision으로 돌린다.
- 단일 canonical 후보를 사용자 선호만으로 거부하면 신규 등록으로 우회하지 않고 pending decision으로 돌린다.
- live lookup 없이 약어, 도메인, 재사용 후보를 추측하지 않는다.

## 3. 용어 DB(trm) exact / synonym 선조회

### 3.1 exact 조회 방식
설계자 입력 컬럼명에서 모든 공백을 제거한 후 exact lookup 한다.

```sql
SELECT
  trm_nm,
  trm_eng_abbr_nm,
  dmn_nm
FROM db_standard.tb_db_com_std_trm
WHERE trm_nm = :column_nm;
```

### 3.2 exact 조회 성공 시
- `trm_eng_abbr_nm` -> 영문 컬럼명
- `dmn_nm` -> 최종 도메인명
- 도메인 테이블에서 타입 / 길이 조회
- 단어 분해 로직을 수행하지 않는다.
- 신규 용어 등록도 수행하지 않는다.

### 3.3 exact 조회 실패 시 synonym 조회

term exact miss인 경우에만 `synm_list_expln`을 조회한다.

```sql
SELECT
  trm_nm,
  trm_eng_abbr_nm,
  dmn_nm,
  synm_list_expln
FROM db_standard.tb_db_com_std_trm
WHERE synm_list_expln LIKE :like_pattern;
```

적용 원칙:
- `synm_list_expln`을 delimiter 기준으로 분리하고 trim한 뒤 공백 제거 등 동일 정규화를 적용해 전체 토큰이 입력 컬럼명과 일치하는지 확인한다.
- 단일 canonical term 후보만 확인되면 `trm_nm`, `trm_eng_abbr_nm`, `dmn_nm`을 재사용한다.
- 이 경우 단어 분해, 마지막 단어 도메인 판단, 신규 용어 등록을 수행하지 않는다.
- 후보가 2건 이상이면 pending decision으로 돌리고 임의 확정하지 않는다.

## 4. 용어 miss 시 단어 분해

- 용어 exact / synonym 모두 miss인 경우에만 수행한다.
- 공백 기준으로 단어 분해
- 필요 시 `references/30-normalization-rules.md`의 복합어 정규화 적용
- 각 단어는 word exact -> synonym -> prohibited 순으로 조회
- 최종 한글 컬럼명은 canonical `word_nm` 으로 확정한다.

## 5. 마지막 단어 도메인 판단 규칙

### 공통 원칙
- 마지막 단어만 도메인 판단 대상
- 기존 단어에 도메인 신규 지정 금지
- 비종결 단어는 도메인 후보가 될 수 없음

### Case 1. 단어 존재 + 도메인 존재 (Y / Y)

#### Case 1-1. `dmn_clsf_nm` 으로 조회한 `dmn_nm` 이 1건
- 추가 질문 없이 그 도메인 확정

#### Case 1-2. `dmn_clsf_nm` 으로 조회한 `dmn_nm` 이 2건 이상
- 후보 목록을 사용자 또는 상위 로직에 제시
- 선택된 `dmn_nm` 확정
- 임의 선택 금지  
  단, 코드 계열이고 `코드C2`가 명시 후보로 존재하면 기본값으로 `코드C2`를 우선 제안할 수 있다.

### Case 2. 단어 존재 + 도메인 미존재 (Y / X)
- blocked
- 메시지 성격:
  - “해당 단어는 도메인이 지정되어 있지 않습니다.”
  - “다른 단어를 선택하거나 신규 단어를 생성해 주십시오.”
- 도메인 선택 UI 제공 금지

### Case 3. 단어 미존재 (X / X)

#### Case 3-1. 컬럼 단어 수 = 4
- 의미 분리 불가로 간주
- 신규 단어 등록 + 도메인 지정 절차 수행
- 도메인 그룹 -> 도메인 분류 -> 데이터 타입/길이 선택
- 선택된 도메인명 확정
- 비종결 단어면 blocked

#### Case 3-2. 컬럼 단어 수 <= 3
- 마지막 단어를 도메인 지정 대상 단어로 간주
- 도메인을 먼저 선택
- 그 다음 마지막 단어를 `앞 단어 + 도메인(끝 단어)` 로 분해하도록 요청한다.
- 앞 단어가 표준 단어에 없으면 신규 단어 등록 preview를 생성한다.
- 예: `관측비` -> `관측` + `비용`

## 6. 도메인 선택 절차

신규 단어 또는 다중 도메인 선택이 필요할 때는 아래 순서를 따른다.

1. 기존 도메인 exact lookup
2. 데이터 타입 / 길이 / 소수 길이 기준 유사 도메인 후보 조회
3. 도메인 그룹 선택
4. 도메인 분류 선택
5. 기존 도메인 재사용 가능 여부 검토
6. 재사용 후보가 없을 때만 신규 도메인 등록 검토
7. 데이터 타입 / 길이 / 소수 길이 선택
8. 최종 `dmn_nm` 확정

적용 원칙:
- 신규 도메인 등록은 가능하지만 최후 수단이다.
- 기존 도메인 exact 또는 유사 후보가 업무 의미와 타입 요구를 충족하면 기존 도메인을 재사용한다.
- 단일 재사용 후보가 있는데 사용자 선호만으로 신규 도메인을 등록하지 않는다.
- 신규 도메인은 표준 사전 관리자 승인 또는 프로젝트 표준 정책 근거가 있을 때만 INSERT preview를 만든다.
- live lookup 없이 도메인 중복 여부나 유사 후보 부재를 추측하지 않는다.

## 7. 비종결 단어 차단 규칙

아래 단어는 도메인으로 의미를 완결할 수 없으므로 차단한다.

- 분류
- 구분
- 유형
- 상태
- 종류
- 단계

메시지 성격:
- “마지막 단어는 도메인으로 설정할 수 없는 단어입니다.”
- 입력 초기 단계로 복귀

## 8. 영문 컬럼명 생성 규칙

### 8.1 term exact / synonym hit
- `trm_eng_abbr_nm` 그대로 사용

### 8.2 term exact / synonym miss + 단어 조합
- 각 canonical word의 `word_eng_abbr_nm` 을 `_` 로 연결
- 공간정보 컬럼은 예외로 `geom`

## 9. 컬럼 정의서 INSERT 규칙

컬럼 정의서 INSERT preview는 고정 컬럼명을 가정하지 않는다.
`references/12-metadata-artifact-model.md`의 column definition field map을 기준으로 렌더링한다.

필수 role:

- `column_id`
- `table_id`
- `logical_column_name`
- `physical_column_name`
- `data_type`
- `data_length`
- `nullable`
- `primary_key`
- `foreign_key`

role 값:

- `column_id` = `{col_dfn_seq}` next value 또는 프로젝트 정의서의 식별자 생성 규칙
- `table_id` = 생성된 테이블 정의서 식별자와 동일한 bind
- `logical_column_name` = canonical 한글 컬럼명
- `physical_column_name` = 최종 영문 컬럼명
- `data_type` = 최종 도메인 기준 타입
- `data_length` = 최종 도메인 기준 길이 / precision / scale
- `nullable`, `primary_key`, `foreign_key` = 입력값 또는 프로젝트 기본값

UNIQUE, INDEX, DEFAULT, CHECK, 개인정보, 암호화, 공개 여부 같은 추가 role은 프로젝트 컬럼 정의서 field map에 있을 때만 반영한다.
컬럼 정의서에 `table_id` role이 없다면 `target_db`, `target_schema`, `physical_table_name` 역할이 필요하다.

공간정보 컬럼 예외:
- `physical_column_name = 'geom'`
- `logical_column_name = '공간정보'`

## 10. 신규 도메인 등록 규칙

신규 도메인 등록은 표준사전 보완 작업이며,
기존 도메인 재사용으로 해결할 수 없을 때만 preview로 제시한다.

전제:
- 도메인 exact lookup 결과가 없어야 한다.
- 동일한 `data_type_nm`, `data_len`, `data_dc_len` 조합의 유사 도메인 후보를 조회해야 한다.
- 기존 도메인 후보가 있으면 신규 도메인 등록보다 재사용을 우선한다.
- 표준 사전 관리자 승인 또는 프로젝트 표준 정책 근거가 있어야 한다.

필드 규칙:
- `dmn_nm` = 신규 도메인명
- `dmn_group_nm` = 선택한 도메인 그룹명
- `dmn_clsf_nm` = 선택한 도메인 분류명
- `data_type_nm` = DBMS 렌더링 전 표준 데이터 타입명
- `data_len` = 길이 / precision. 길이가 없는 타입이면 null 또는 프로젝트 기본값
- `data_dc_len` = scale. scale이 없는 타입이면 null 또는 프로젝트 기본값
- `prm_vl_expln`, `strg_frm_expln`, `exprs_frm_expln` = 도메인 상세 설명. 값이 없으면 `'-'`

## 11. 신규 용어 등록 규칙

term exact / synonym hit가 아니고 최종 컬럼명이 신규 생성된 경우,
`db_standard.tb_db_com_std_trm` INSERT preview를 생성할 수 있다.

전제:
- 용어 exact lookup 결과가 없어야 한다.
- 용어 synonym lookup 결과 재사용 가능한 단일 canonical term 후보가 없어야 한다.
- 단어 exact / synonym / prohibited-word 조회와 도메인 판단이 완료되어야 한다.
- 기존 용어 또는 기존 단어 조합으로 재사용 가능한 후보가 있으면 신규 용어 등록보다 재사용을 우선한다.
- 단일 재사용 후보를 거부하려면 표준 사전 관리자 승인 또는 프로젝트 표준 정책 근거가 필요하다.

필드 규칙:
- `trm_no` = `{next_value(standard_repository.term_seq)}`
- `enct_sec_nm` = `'신규'`
- `trm_nm` = canonical 한글 컬럼명
- `trm_expln` = `'-'`
- `trm_eng_abbr_nm` = 최종 영문 컬럼명
- `dmn_nm` = 최종 도메인명
- `prm_vl_expln`, `strg_frm_expln`, `exprs_frm_expln` = 도메인 상세 조회 결과
- 나머지 설명 계열 필드는 기본 `'-'`

## 12. 신규 단어 등록 규칙

term miss / word miss 케이스에서 필요한 경우 신규 단어 INSERT preview를 만든다.

기본 원칙:
- exact / synonym / prohibited-word 조회에서 재사용 후보가 없어야 한다.
- 마지막 단어 신규 등록은 선택된 도메인 분류에 따라 `dmn_yn='Y'`
- 마지막 단어가 아닌 신규 단어는 `dmn_yn='N'`
- 실제 INSERT는 승인 전까지 실행하지 않는다.

## 13. blocked / pending 구분

### blocked
- 컬럼 5단어 이상
- 비종결 단어 선택
- 기존 단어 + 도메인 미존재
- 약어 / 도메인 추측 필요 상황
- 신규 도메인 중복 / 유사 후보 조회 불가

### pending decision
- 다중 도메인 후보
- 신규 도메인 등록 승인 필요
- synonym 다중 매칭
- 마지막 단어 분해 필요
- 공간정보 세부 타입 / SRID 미입력

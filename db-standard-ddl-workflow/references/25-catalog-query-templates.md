# 25. 카탈로그 조회 SQL 템플릿

이 문서는 표준 단어 / 용어 / 도메인 사전 조회용 SQL 템플릿을 정의한다.

## 목차

- [공통 원칙](#공통-원칙)
- [1. 표준 단어 exact 조회](#1-표준-단어-exact-조회)
- [2. synonym / prohibited-word 조회](#2-synonym--prohibited-word-조회)
- [3. 표준 용어 exact 조회](#3-표준-용어-exact-조회)
- [4. 도메인 분류 조회](#4-도메인-분류-조회)
- [5. 신규 도메인 등록 전 유사 후보 조회](#5-신규-도메인-등록-전-유사-후보-조회)
- [6. 테이블 정의서 중복 확인](#6-테이블-정의서-중복-확인)
- [7. 기존 프로젝트 정의서 구조 조회](#7-기존-프로젝트-정의서-구조-조회)
- [8. 대상 namespace 존재 확인](#8-대상-namespace-존재-확인)
- [9. 실제 실행 가이드](#9-실제-실행-가이드)

## 공통 원칙

- 표준 사전은 항상 DBMS profile이 정한 `db_standard` 표준 저장소의 `db_standard` namespace에 있다고 가정한다.
- 프로젝트 정의서는 DBMS profile이 정한 `db_standard` 표준 저장소 namespace에 있다고 가정한다.
- 이 문서의 SQL 블록은 logical template이다. 최종 출력 시 `references/11-dbms-profile.md`와 `references/80-dbms-dialects.md`에 따라 DBMS별 object identifier pattern, casing, bind marker를 적용한다.
- 모든 테이블은 Execution Context의 전체 식별자를 사용한다.
- 바인드 변수 표기는 generic `:param` 형식을 사용한다.
- string concatenation은 DBMS마다 다를 수 있으므로, LIKE 검색은 미리 조합된 `:like_pattern` 으로 바인딩하는 것을 권장한다.
- exact match가 synonym / prohibited-word 검색보다 항상 우선한다.

DBMS별 표준 단어 exact 조회 렌더링 예시:

```sql
-- PostgreSQL, connected to database db_standard
SELECT word_nm, word_eng_abbr_nm
FROM db_standard.tb_db_com_std_word
WHERE word_nm = :word_nm;

-- Oracle
SELECT WORD_NM, WORD_ENG_ABBR_NM
FROM DB_STANDARD.TB_DB_COM_STD_WORD
WHERE WORD_NM = :word_nm;

-- MySQL / MariaDB
SELECT word_nm, word_eng_abbr_nm
FROM db_standard.tb_db_com_std_word
WHERE word_nm = :word_nm;

-- SQL Server
SELECT word_nm, word_eng_abbr_nm
FROM db_standard.tb_db_com_std_word
WHERE word_nm = @word_nm;
```

## 1. 표준 단어 exact 조회

```sql
SELECT
  word_nm,
  word_eng_abbr_nm,
  dmn_yn,
  dmn_clsf_nm
FROM db_standard.tb_db_com_std_word
WHERE word_nm = :word_nm;
```

## 2. 표준 단어 synonym / prohibited-word 조회

```sql
SELECT
  word_nm,
  word_eng_abbr_nm,
  dmn_yn,
  dmn_clsf_nm,
  synm_list_expln,
  phwrd_lis_expln
FROM db_standard.tb_db_com_std_word
WHERE synm_list_expln LIKE :like_pattern
   OR phwrd_lis_expln LIKE :like_pattern;
```

권장:
- `:like_pattern = '%토큰%'`
- 구현이 가능하면 delimiter-aware matching을 우선한다.
- 결과가 2건 이상이면 사용자 선택 또는 정교화가 필요하다.

## 3. 표준 용어 exact 조회

```sql
SELECT
  trm_eng_abbr_nm,
  dmn_nm
FROM db_standard.tb_db_com_std_trm
WHERE trm_nm = :trm_nm;
```

## 4. 도메인명으로 상세 조회

```sql
SELECT
  dmn_nm,
  dmn_group_nm,
  dmn_clsf_nm,
  data_type_nm,
  data_len,
  data_dc_len,
  prm_vl_expln,
  strg_frm_expln,
  exprs_frm_expln
FROM db_standard.tb_db_com_std_dmn
WHERE dmn_nm = :dmn_nm;
```

## 5. 도메인 그룹 목록 조회

```sql
SELECT DISTINCT dmn_group_nm
FROM db_standard.tb_db_com_std_dmn
ORDER BY dmn_group_nm;
```

## 6. 도메인 분류 목록 조회

```sql
SELECT DISTINCT dmn_clsf_nm
FROM db_standard.tb_db_com_std_dmn
WHERE dmn_group_nm = :dmn_group_nm
ORDER BY dmn_clsf_nm;
```

## 7. 도메인 분류별 후보 조회

```sql
SELECT
  dmn_nm,
  data_type_nm,
  data_len,
  data_dc_len
FROM db_standard.tb_db_com_std_dmn
WHERE dmn_clsf_nm = :dmn_clsf_nm
ORDER BY dmn_nm;
```

## 8. 코드 계열 기본 도메인 확인

```sql
SELECT
  dmn_nm,
  data_type_nm,
  data_len,
  data_dc_len
FROM db_standard.tb_db_com_std_dmn
WHERE dmn_nm = '코드C2';
```

## 9. 신규 도메인 등록 전 유사 후보 조회

신규 도메인 등록 전에는 동일 또는 유사 타입 후보를 먼저 조회한다.

```sql
SELECT
  dmn_nm,
  dmn_group_nm,
  dmn_clsf_nm,
  data_type_nm,
  data_len,
  data_dc_len,
  prm_vl_expln,
  strg_frm_expln,
  exprs_frm_expln
FROM db_standard.tb_db_com_std_dmn
WHERE data_type_nm = :data_type_nm
  AND (
    data_len = :data_len
    OR :data_len IS NULL
  )
  AND (
    data_dc_len = :data_dc_len
    OR :data_dc_len IS NULL
  )
ORDER BY dmn_nm;
```

결과가 있으면 신규 도메인 등록보다 기존 도메인 재사용을 우선 검토한다.

## 10. owner word 조회
테이블소유자가 이미 canonical abbreviation이 아니라면 일반 단어 조회와 동일한 방식으로 조회한다.

```sql
SELECT
  word_nm,
  word_eng_abbr_nm
FROM db_standard.tb_db_com_std_word
WHERE word_nm = :owner_nm;
```

## 11. skill 동작 지침

- live lookup이 없으면 위 SQL을 “lookup SQL bundle”로 출력한다.
- 사용자가 조회 결과를 제공하면, 그 결과만 근거로 다음 단계를 진행한다.
- exact query와 fallback query를 반드시 구분해 보여준다.

## Validation Summary
- status: VALID, PREVIEW_ONLY
- startup_mode: existing_project
- run_mode: approval
- dbms: PostgreSQL
- request_mode: SQL 작성 후 승인 대기
- execution_possible: false

## Resolved Inputs
- database: appdb
- target_namespace: app_core
- target_namespace_kind: schema
- table_kind: 일반 테이블
- table_owner: CORE
- subject_area_cd: core
- metadata_namespace: db_standard
- logical_table_name: 사용자 정보
- physical_table_name: tb_core_user_info
- columns:
  - 사용자 아이디 -> user_id
  - 사용자 이름 -> user_nm
  - 이메일 -> email
  - 등록 일시 -> reg_dt

## Blocking Issues
- none

## Pending Decisions
- live catalog lookup unavailable: exact word / term hit 여부는 SQL 조회 결과로 최종 확인 필요

## Lookup SQL Bundle
```sql
SELECT trm_eng_abbr_nm, dmn_nm
FROM db_standard.tb_db_com_std_trm
WHERE trm_nm = '사용자아이디';

SELECT word_nm, word_eng_abbr_nm, dmn_yn, dmn_clsf_nm
FROM db_standard.tb_db_com_std_word
WHERE word_nm = '사용자';
```

## Preview INSERT SQL
```sql
INSERT INTO db_standard.tb_table_definition ({columns_from_table_definition_field_map})
VALUES ({values_from_resolved_context});

INSERT INTO db_standard.tb_column_definition ({columns_from_column_definition_field_map})
VALUES ({values_from_resolved_context});
```

## Preview DDL SQL
```sql
CREATE TABLE app_core.tb_core_user_info (...);
ALTER TABLE app_core.tb_core_user_info ADD CONSTRAINT pk_tb_core_user_info PRIMARY KEY (...);
CREATE UNIQUE INDEX uidx_tb_core_user_info_user_id ON app_core.tb_core_user_info (...);
COMMENT ON TABLE app_core.tb_core_user_info IS '사용자 정보';
```

## Notes
- 이 예시는 출력 구조 예시다.
- 실제 약어 / 도메인 / 타입은 표준 사전 조회 결과를 따라야 한다.
- 정의서 INSERT 컬럼은 프로젝트 field map 기준으로 렌더링한다.

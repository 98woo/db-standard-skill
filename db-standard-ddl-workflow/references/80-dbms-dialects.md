# 80. DBMS 방언 규칙

이 문서는 DBMS별 식별자 렌더링과 기본 SQL 스타일을 정의한다.
DBMS의 객체 계층과 표준 저장소 배치는 `references/11-dbms-profile.md`를 우선 따른다.

## 1. canonical -> physical 변환

skill 내부에서는 먼저 canonical logical identifier를 만든다.

예:
- `TB_SPL_USER_INFO`
- `USER_ID`
- `PK_TB_SPL_USER_INFO`

그 다음 DBMS별 렌더링을 적용한다.

## 2. Oracle

- identifier style: `UPPER_SNAKE_CASE`
- namespace kind: `owner` 또는 `schema`
- 표준 저장소는 `DB_STANDARD.<table>`로 렌더링한다.
- 기본적으로 quoted identifier를 쓰지 않는다.
- sequence preview는 별도 `CREATE SEQUENCE` 를 사용할 수 있다.
- COMMENT ON 구문을 그대로 사용한다.

예:
- `tb_spl_user_info` -> `TB_SPL_USER_INFO`

## 3. PostgreSQL

- identifier style: `lower_snake_case`
- namespace kind: `schema`
- 표준 저장소는 `db_standard` database에 접속한 뒤 `db_standard.<table>`로 렌더링한다.
- 기본적으로 quoted identifier를 쓰지 않는다.
- sequence를 쓸 경우 `nextval(...)` 계열 문법으로 조정될 수 있다.
- COMMENT ON 구문을 그대로 사용한다.

예:
- `TB_SPL_USER_INFO` -> `tb_spl_user_info`

## 4. MySQL

- identifier style: `lower_snake_case`
- namespace kind: `database`
- 표준 저장소는 `db_standard.<table>`로 렌더링한다.
- quoted identifier는 프로젝트 규칙이 없는 한 사용하지 않는다.
- COMMENT 구문과 sequence 전략은 프로젝트 버전에 따라 달라질 수 있으므로,
  기본 preview는 generic하게 유지하고 필요 시 project rule로 override 한다.
- standalone sequence 사용 여부는 프로젝트 규칙으로 확정한다.

## 5. SQL Server

- identifier style: 프로젝트 규칙이 없으면 `lower_snake_case`
- namespace kind: `schema`
- 표준 저장소 기본값은 `db_standard` database의 `db_standard` schema다.
- 조직 표준이 `dbo`이면 DBMS profile에서 schema override를 명시해야 한다.
- COMMENT 문법은 SQL Server extended properties가 필요할 수 있으므로 project rule 또는 renderer note로 처리한다.

## 6. 공통 렌더링 원칙

- 테이블명, 컬럼명, 제약조건명, 인덱스명은 모두 같은 case policy를 따른다.
- namespace명도 DBMS 관행에 맞춰 렌더링한다.
- full identifier 사용 원칙은 DBMS와 무관하게 유지한다.
- database-qualified identifier를 지원하지 않는 DBMS에서는 SQL 식별자에 database명을 붙이지 않는다.

## 7. comment strategy

### Oracle / PostgreSQL
- `COMMENT ON TABLE`
- `COMMENT ON COLUMN`

### MySQL / MariaDB
- 프로젝트 규칙이 없으면 generic preview를 유지하고 주석 구문은 note로 설명한다.

### SQL Server
- 프로젝트 규칙이 없으면 generic preview를 유지하고 extended property 사용 여부를 note로 설명한다.

## 8. sequence strategy

- Oracle: 별도 sequence 생성 가능
- PostgreSQL: 별도 sequence 또는 프로젝트 기본 identity 전략 중 하나
- MySQL / MariaDB: 프로젝트 기본 auto increment / identity 전략 우선, standalone sequence는 명시 규칙 필요
- SQL Server: identity 또는 sequence 중 프로젝트 정책을 따른다.

## 9. renderer checklist

renderer는 최종 출력 전에 아래를 점검한다.

- identifier casing이 target DBMS와 일치하는가
- DBMS profile에 맞는 namespace-qualified identifier인가
- PK/FK/IDX/UIDX 이름 규칙이 casing 후에도 일관적인가
- COMMENT 전략이 target DBMS와 맞는가
- sequence 전략이 target DBMS와 맞는가

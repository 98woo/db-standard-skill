# 14. Bootstrap Role Mapping

신규 프로젝트에서 테이블 정의서 / 컬럼 정의서 테이블을 bootstrap할 때 사용하는 결정적 role mapping 규칙이다.

이 단계는 업무 테이블 표준화가 아니다. 표준 단어 / 용어 / 도메인 사전을 조회하지 않고, 웹 검색도 사용하지 않는다.
다만 정의서 field map이 흔들리지 않도록 아래 표의 한글 후보를 우선 매핑한다.

## 1. 적용 순서

1. 한글 컬럼명을 공백 제거 / 괄호 보조 설명 제거 / 대소문자 무시 형태로 정규화한다.
2. 아래 표의 Korean column candidate와 exact match 또는 명확한 동의 표현을 찾는다.
3. match되면 Preferred physical column과 Role을 그대로 사용한다.
4. match되지 않은 추가 컬럼은 일반적인 의미 기반 `snake_case`로 생성하되, 필수 role로 임의 배정하지 않는다.
5. 필수 role이 누락되면 blocked로 반환하고 필요한 한글 컬럼 후보를 사용자에게 제시한다.

## 2. 테이블 정의서 role mapping

| Korean column candidate | Preferred physical column | Role |
| --- | --- | --- |
| 테이블 식별자 | table_id | table_id |
| 테이블 ID | table_id | table_id |
| 테이블 아이디 | table_id | table_id |
| 대상 데이터베이스 | target_db | target_db |
| 대상 DB | target_db | target_db |
| 대상 namespace | target_schema | target_schema |
| 대상 네임스페이스 | target_schema | target_schema |
| 대상 스키마 | target_schema | target_schema |
| 테이블 소유자 | owner | owner |
| 소유자 | owner | owner |
| 주제영역 코드 | subject_area_cd | subject_area_cd |
| 주제 영역 코드 | subject_area_cd | subject_area_cd |
| 주제영역 명 | subject_area_nm | subject_area_nm |
| 주제 영역 명 | subject_area_nm | subject_area_nm |
| 주제영역 그룹 명 | subject_area_group_nm | subject_area_group_nm |
| 주제 영역 그룹 명 | subject_area_group_nm | subject_area_group_nm |
| 논리 테이블명 | logical_table_name | logical_table_name |
| 논리 테이블 명 | logical_table_name | logical_table_name |
| 테이블 논리명 | logical_table_name | logical_table_name |
| 물리 테이블명 | physical_table_name | physical_table_name |
| 물리 테이블 명 | physical_table_name | physical_table_name |
| 테이블 물리명 | physical_table_name | physical_table_name |
| 테이블 종류 | table_type | table_type |
| 테이블 유형 | table_type | table_type |
| 관계 엔터티 명 | related_entity_name | related_entity_name |
| 관계 엔터티명 | related_entity_name | related_entity_name |
| 설명 | description | description |
| 비고 | description | description |

필수 role:

- `table_id`
- `target_db`
- `target_schema`
- `owner`
- `logical_table_name`
- `physical_table_name`
- `table_type`

## 3. 컬럼 정의서 role mapping

| Korean column candidate | Preferred physical column | Role |
| --- | --- | --- |
| 컬럼 식별자 | column_id | column_id |
| 컬럼 ID | column_id | column_id |
| 컬럼 아이디 | column_id | column_id |
| 테이블 식별자 | table_id | table_id |
| 테이블 ID | table_id | table_id |
| 테이블 아이디 | table_id | table_id |
| 컬럼 순서 | column_order | column_order |
| 컬럼 순번 | column_order | column_order |
| 표시 순서 | column_order | column_order |
| 논리 컬럼명 | logical_column_name | logical_column_name |
| 논리 컬럼 명 | logical_column_name | logical_column_name |
| 컬럼 논리명 | logical_column_name | logical_column_name |
| 물리 컬럼명 | physical_column_name | physical_column_name |
| 물리 컬럼 명 | physical_column_name | physical_column_name |
| 컬럼 물리명 | physical_column_name | physical_column_name |
| 도메인명 | domain_name | domain_name |
| 도메인 명 | domain_name | domain_name |
| 데이터 타입 | data_type | data_type |
| 데이터 유형 | data_type | data_type |
| 타입 | data_type | data_type |
| 데이터 길이 | data_length | data_length |
| 길이 | data_length | data_length |
| NULL 허용 여부 | nullable | nullable |
| 널 허용 여부 | nullable | nullable |
| NULL 여부 | nullable | nullable |
| PK 여부 | primary_key | primary_key |
| 기본키 여부 | primary_key | primary_key |
| 주키 여부 | primary_key | primary_key |
| FK 여부 | foreign_key | foreign_key |
| 외래키 여부 | foreign_key | foreign_key |
| UNIQUE 여부 | unique_key | unique_key |
| 유니크 여부 | unique_key | unique_key |
| INDEX 여부 | indexed | indexed |
| 인덱스 여부 | indexed | indexed |
| 제약조건 내용 | constraint_text | constraint_text |
| 제약 조건 내용 | constraint_text | constraint_text |
| 기본값 | default_value | default_value |
| DEFAULT 값 | default_value | default_value |
| 설명 | description | description |
| 비고 | description | description |

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

## 4. 충돌 처리

- 서로 다른 한글 컬럼이 같은 role로 매핑되면 pending decision으로 돌린다.
- 같은 physical column 후보가 서로 다른 role에 매핑되면 blocked로 반환한다.
- 필수 role 후보가 없으면 자동 생성하지 말고 누락 role과 권장 한글 컬럼 후보를 반환한다.
- 추가 컬럼은 `snake_case`로 생성할 수 있지만, 위 표의 role 의미를 덮어쓰지 않는다.

## 5. target_schema role 의미

정의서 호환성을 위해 role 이름은 `target_schema`를 유지한다.
하지만 값의 의미는 DBMS profile의 target namespace다.

- PostgreSQL / SQL Server: schema
- Oracle: owner / schema
- MySQL / MariaDB: database

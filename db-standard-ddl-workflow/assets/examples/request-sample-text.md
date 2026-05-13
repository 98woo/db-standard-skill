작업 유형 : 기존 프로젝트 표준화 작업 이어서 진행

프로젝트 ID : sample_project
프로젝트 명 : 샘플 프로젝트
DBMS 종류 / 버전 : PostgreSQL 15
실행 요청 : SQL 작성 후 승인 대기

물리 대상 데이터베이스 : appdb
물리 대상 namespace 라우팅 :
- app_core(core)

프로젝트 산출물 namespace : db_standard (고정)
테이블 정의서 테이블명 : tb_table_definition
컬럼 정의서 테이블명 : tb_column_definition

대상 namespace : app_core
테이블 종류 : 일반 테이블

테이블 소유자 : CORE
주제 영역 코드 : core
주제 영역 명 : 공통
주제 영역 그룹 명 : 기준정보
테이블 명 : 사용자 정보

컬럼:
- 사용자 아이디 | PK(Y) | NULL허용(N) | FK() | UNIQUE(Y) | INDEX() | DEFAULT()
- 사용자 이름 | PK(N) | NULL허용(N) | FK() | UNIQUE() | INDEX() | DEFAULT()
- 이메일 | PK(N) | NULL허용(Y) | FK() | UNIQUE(Y) | INDEX() | DEFAULT()
- 등록 일시 | PK(N) | NULL허용(N) | FK() | UNIQUE() | INDEX(Y) | DEFAULT(current_timestamp)

추가사항(없으면 생략) :
- INDEX : 등록 일시, 사용자 아이디
- 기타 : 코드 계열은 기본적으로 코드C2 사용

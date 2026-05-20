[Execution Context 확정 후 업무 테이블 요청 예시]

요청 유형 : alter_add_columns
실행 요청 : SQL 작성 후 승인 대기

요청 database : appdb
대상 namespace : app_core
테이블 종류 : 일반 테이블
테이블 소유자 : CORE
주제 영역 코드 : core
주제 영역 명 : 공통
주제 영역 그룹 명 : 기준정보
테이블 명 : 사용자 정보

기존 물리 테이블명 : tb_core_user_info

추가 컬럼:
- 마지막 로그인 일시 | NULL허용(Y) | 희망타입(TIMESTAMPTZ) | FK() | UNIQUE() | INDEX(Y) | DEFAULT()
- 로그인 실패 횟수 | NULL허용(N) | 희망타입(NUMERIC) | FK() | UNIQUE() | INDEX() | DEFAULT(0)

추가사항:
- INDEX : 마지막 로그인 일시
- 기타 : 물리 ALTER와 함께 신규 컬럼 정의서 INSERT를 반드시 생성

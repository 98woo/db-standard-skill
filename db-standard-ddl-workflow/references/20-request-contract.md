# 20. 요청 계약 (Request Contract)

이 문서는 사용자가 skill에 전달해야 하는 입력 계약을 정의한다.

## 목차

- [1. 지원 입력 방식](#1-지원-입력-방식)
- [2. 허용 테이블 종류](#2-허용-테이블-종류)
- [3. 실행 요청](#3-실행-요청)
- [3.1 데이터베이스 / namespace 의미](#31-데이터베이스--namespace-의미)
- [4. 이미지 해석 기준](#4-이미지-해석-기준)
- [5. 기본값](#5-기본값)
- [6. 추가사항 입력 규칙](#6-추가사항-입력-규칙)
- [7. 권장 입력 품질 규칙](#7-권장-입력-품질-규칙)
- [8. blocked 조건](#8-blocked-조건)
- [9. 내부 처리 흐름](#9-내부-처리-흐름)

## 1. 지원 입력 방식

일반 테이블 생성/변경 요청은 `references/05-startup-onboarding.md`의 시작 온보딩이 완료된 뒤에만 처리한다.
Execution Context가 없으면 먼저 신규 프로젝트인지 기존 프로젝트 이어서 진행인지 선택해야 한다.
DBMS는 신규 프로젝트이거나 기존 프로젝트에서 profile을 복원할 수 없을 때만 입력받는다.

### A. 이미지 + 텍스트
가장 권장되는 방식이다.

필수 텍스트:
- 데이터베이스
- 대상 namespace  
  단, Execution Context의 `physical_target.target_namespace_map`과 주제영역 / 소유자 코드로 단일 namespace를 확정할 수 있으면 생략 가능
- 테이블 종류
- 실행 요청

필수 이미지 항목:
- 테이블소유자
- 주제영역
- 주제영역 그룹명
- 엔터티명
- 속성명
- 필수입력 여부
- 식별자 여부

### B. 텍스트 only
이미지 없이도 가능하지만, 아래 필드가 더 필요하다.

- 데이터베이스
- 대상 namespace  
  단, Execution Context의 `physical_target.target_namespace_map`과 주제영역 / 소유자 코드로 단일 namespace를 확정할 수 있으면 생략 가능
- 테이블 종류
- 테이블 소유자
- 주제 영역 코드  
  없으면 테이블 소유자 코드를 namespace 라우팅 기준으로 사용
- 주제 영역 명
- 주제 영역 그룹 명
- 테이블 명
- 컬럼 목록
- 실행 요청

## 2. 허용 테이블 종류

- 일반 테이블
- 공간정보 테이블
- 전자정부 프레임워크
- 연계 테이블

## 3. 실행 요청

허용값:

- `SQL만 작성`
- `SQL 작성 후 승인 대기`
- `실제 DB 실행`

### execution mapping
- `SQL만 작성` -> `preview`
- `SQL 작성 후 승인 대기` -> `approval`
- `실제 DB 실행` -> `execute` 후보  
  단, Execution Context와 실제 권한이 허용할 때만 실행 가능

## 3.1 데이터베이스 / namespace 의미

- `데이터베이스`는 Execution Context의 `physical_target.db_nm`과 일치해야 한다.
- `대상 namespace`는 실제 업무 테이블을 생성 / 변경할 DBMS별 공간이다.
- PostgreSQL / SQL Server에서는 대상 namespace가 schema다.
- Oracle에서는 대상 namespace가 schema / user / owner다.
- MySQL / MariaDB에서는 대상 namespace가 database다.
- `대상 namespace`는 Execution Context의 `physical_target.target_namespace_map`에 정의된 값 중 하나여야 한다.
- `physical_target.target_namespace_map`은 최초 1회 입력받는 namespace 라우팅 규칙이다.
- 요청의 `주제 영역 코드` 또는 `테이블 소유자`는 선택된 대상 namespace의 `subject_area_cds` 또는 `owner_codes`와 일치해야 한다.
- 요청에 `대상 namespace`가 없더라도 주제영역 / 소유자 코드로 단일 namespace를 확정할 수 있으면 그 namespace를 사용한다.
- 요청에 `대상 namespace`와 주제영역 / 소유자 코드가 모두 있고 서로 충돌하면 blocked 상태다.
- 정의서 INSERT 위치는 요청 `대상 namespace`가 아니라 DBMS profile이 정한 `db_standard` 표준 저장소를 따른다.
- 표준 사전 조회 위치도 요청 `대상 namespace`가 아니라 DBMS profile이 정한 `db_standard` 표준 저장소를 따른다.

## 4. 이미지 해석 기준

- `테이블소유자` -> 테이블 소유자
- `주제영역코드` -> 주제 영역 코드. 없으면 테이블 소유자 코드를 라우팅 기준으로 사용
- `주제영역` -> 주제 영역 명
- `주제영역 그룹명` -> 주제 영역 그룹 명
- `엔터티명` -> 한글 테이블 명
- `속성명` -> 한글 컬럼 명
- `필수입력 여부 = Y` -> `NOT NULL`
- `식별자 여부 = Y` -> `PK`

`식별자 여부 = Y` 가 여러 개이면 복합 PK로 해석한다.

## 5. 기본값

이미지나 텍스트에 없는 정보는 아래 기본값으로 처리한다.

- FK 없음
- UNIQUE 없음
- INDEX 없음
- DEFAULT 없음
- 코드 계열 도메인은 별도 지시가 없으면 `코드C2`

## 6. 추가사항 입력 규칙

예외 규칙은 반드시 `추가사항` 에 적는다.

예시:

- `FK : 등록자 아이디 -> auth.tb_user(user_id)`
- `UNIQUE : 이메일`
- `INDEX : 등록 일시, 등록자 아이디`
- `DEFAULT : 등록 일시 -> current_timestamp`
- `기타 : 코드 계열은 기본적으로 코드C2 사용`

### 공간정보 프로젝트 보완 입력
공간정보 테이블이라면 아래를 추가하는 것을 권장한다.

- `SPATIAL TYPE`
- `SRID`
- `SPATIAL INDEX`
- `GEOMETRY NULL 여부`

## 7. 권장 입력 품질 규칙

- 데이터베이스 명은 텍스트로 명확히 적는다.
- 대상 namespace를 직접 적지 않는 경우, 주제 영역 코드 또는 테이블 소유자 코드는 반드시 namespace 라우팅이 가능해야 한다.
- 테이블 종류는 반드시 텍스트로 적는다.
- 이미지에는 한 개의 엔터티만 포함한다.
- 속성명은 한 행에 한 개씩 작성한다.
- 예외 규칙은 이미지가 아니라 텍스트 `추가사항`에 적는다.
- 실제 DB 반영 여부는 반드시 `실행 요청`에 명시한다.

## 8. blocked 조건

아래는 즉시 blocked다.

- 데이터베이스 누락
- 테이블 종류 누락
- 실행 요청 누락
- Execution Context에 `physical_target.target_namespace_map`이 없음
- 요청 대상 namespace가 `physical_target.target_namespace_map`에 없음
- 요청 대상 namespace와 주제영역 / 소유자 코드가 `physical_target.target_namespace_map` 기준으로 충돌
- 요청 대상 namespace가 없고 주제영역 / 소유자 코드로 단일 namespace를 확정할 수 없음
- 이미지 요청인데 이미지 핵심 필드 누락
- 한 요청에 엔터티가 2개 이상 섞임

## 9. 내부 처리 흐름

요청이 유효하면 skill은 아래 순서로 판단한다.
최종 응답 섹션과 출력 형식은 `references/90-output-contract.md`를 따른다.

1. 표준 단어 / 용어 / 도메인 사전 조회
2. 신규 도메인 / 단어 / 용어 필요 여부 판정
3. 영문 테이블명 / 컬럼명 생성
4. 정의서 INSERT SQL 생성
5. CREATE TABLE / 제약조건 / 인덱스 SQL 생성
6. 실행 요청에 따라 preview 또는 approval / execute plan 반환

# 81. 공간정보 규칙

이 문서는 원문에서 정의된 공간정보 관련 규칙만 안전하게 자동화한다.

## 1. 자동 적용 가능한 규칙

### 1.1 테이블 접두사
- 공간정보 테이블은 `GM` 접두사를 사용한다.

### 1.2 공간정보 컬럼명
- `physical_column_name = 'geom'`
- `logical_column_name = '공간정보'`

### 1.3 공간정보 컬럼 주석
- COMMENT는 항상 `공간정보`

## 2. 자동 추론하지 않는 항목

아래는 원문에 충분한 규칙이 없으므로 자동 추론하지 않는다.

- geometry subtype (`POINT`, `LINESTRING`, `POLYGON` 등)
- SRID
- spatial index 생성 방식
- geometry 컬럼 NULL 정책
- Oracle Spatial / PostGIS / MySQL spatial 방언 차이

## 3. pending decision으로 돌려야 하는 경우

아래 정보가 없으면 최종 spatial DDL 확정을 보류한다.

- spatial type
- SRID
- spatial index 여부
- target DBMS spatial extension 전제

## 4. 권장 추가 입력

요청 `추가사항` 에 아래를 적는 것을 권장한다.

- `SPATIAL TYPE : geometry(Point)`
- `SRID : 5186`
- `SPATIAL INDEX : yes`
- `GEOM NULL : N`

## 5. 렌더링 원칙

공간정보 컬럼이 있어도 아래 두 가지는 항상 고정이다.

- physical column name: `geom`
- comment: `공간정보`

나머지 타입 / 인덱스 / 제약은 프로젝트 spatial rule 또는 명시 입력을 따른다.

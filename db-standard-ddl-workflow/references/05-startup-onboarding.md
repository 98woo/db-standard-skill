# 05. 시작 온보딩

이 문서는 skill을 처음 실행할 때 반드시 수행해야 하는 시작 분기를 정의한다.

## 목차

- [1. 시작 질문](#1-시작-질문)
- [2. 초기 입력 템플릿 생성](#2-초기-입력-템플릿-생성)
- [3. 신규 프로젝트 표준화 작업 시작](#3-신규-프로젝트-표준화-작업-시작)
- [4. 기존 프로젝트 표준화 작업 이어서 진행](#4-기존-프로젝트-표준화-작업-이어서-진행)
- [5. 시작 단계 차단 조건](#5-시작-단계-차단-조건)
- [6. 시작 단계 완료 조건](#6-시작-단계-완료-조건)

## 1. 시작 질문

Execution Context가 없거나 현재 대화에서 확정되지 않았으면,
에이전트는 다른 작업을 진행하기 전에 아래를 먼저 묻는다.

1단계: DBMS 확인

```text
사용할 DBMS 종류와 버전을 입력해 주세요.
허용 DBMS: postgresql, oracle, mysql, mariadb, sqlserver
```

2단계: 작업 유형 확인

```text
작업 유형을 선택해 주세요.
1. 신규 프로젝트 표준화 작업 시작
2. 기존 프로젝트 표준화 작업 이어서 진행
```

DBMS가 확정되면 `references/11-dbms-profile.md`에 따라 DBMS profile을 선택한다.
DBMS profile이 확정되기 전에는 작성용 템플릿을 생성하지 않는다.

## 2. 초기 입력 템플릿 생성

DBMS profile과 작업 유형이 확정되면 에이전트는 skill 패키지의 원본 템플릿을 현재 작업 디렉토리에 작성용 파일로 생성한다.

원본 템플릿:

- 신규 프로젝트: `assets/initial-context-new-project.template.md`
- 기존 프로젝트: `assets/initial-context-existing-project.template.md`

작성용 파일명:

- 신규 프로젝트: `db-standard-initial-context.new.md`
- 기존 프로젝트: `db-standard-initial-context.existing.md`

동작 규칙:

- 작성용 파일은 현재 작업 디렉토리에 생성한다.
- 같은 이름의 작성용 파일이 이미 있으면 덮어쓰지 않는다.
- 파일이 이미 있으면 에이전트는 기존 파일을 사용할지, 다른 파일명으로 새로 생성할지 확인한다.
- 사용자가 파일 작성을 완료하기 전에는 일반 DDL 작업으로 진행하지 않는다.
- 사용자가 작성한 Markdown 안의 YAML 블록만 Execution Context 생성의 기준으로 사용한다.
- YAML 파싱 후 에이전트는 해석한 Execution Context 요약과 누락 / 충돌 검증 결과를 먼저 제시한다.
- 사용자가 확인하면 그 Context를 read-only 기준으로 고정한다.
- 템플릿의 주석은 작성 가이드다. 사용자는 주석을 지우지 않아도 된다.
- `고정`, `auto`, `비워두면 자동`이라고 표시된 값은 임의 변경하지 않는다.

작성용 파일을 만들 수 없는 환경이면 원본 템플릿 내용을 응답으로 제공하고,
사용자가 동일한 내용을 현재 작업 디렉토리에 작성하도록 안내한다.

## 3. 신규 프로젝트 표준화 작업 시작

신규 프로젝트는 표준 사전은 이미 구축되어 있고,
고정 산출물 namespace(`db_standard`) 안에 정의서 구조를 새로 확정하는 흐름이다.

이 단계에서 만드는 테이블 정의서 / 컬럼 정의서 테이블 자체는 표준화 대상이 아니다.
정의서 테이블 생성은 프로젝트 산출물 저장소 bootstrap 작업이며,
이후 실제 업무 테이블 표준화 작업과 분리한다.

`db-standard-initial-context.new.md`로 입력받아야 하는 값:

- 프로젝트 ID
- 프로젝트 명
- DBMS 종류 / 버전
- DBMS connection target
- DBMS profile
- 실제 물리 테이블 대상 데이터베이스
- 실제 물리 테이블 대상 namespace 라우팅
- 프로젝트 산출물 namespace 논리명: `db_standard` 고정
- 테이블 정의서 한글 테이블명
- 테이블 정의서 한글 컬럼 목록
- 컬럼 정의서 한글 테이블명
- 컬럼 정의서 한글 컬럼 목록
- 정의서 생성 방식: `create` | `use_existing`
- 실행 모드: `preview` | `approval` | `execute`

고정값:

- 표준 저장소 DB: `db_standard`
- 표준 사전 namespace: `db_standard`
- 표준 단어 테이블: `tb_db_com_std_word`
- 표준 용어 테이블: `tb_db_com_std_trm`
- 표준 도메인 테이블: `tb_db_com_std_dmn`
- 프로젝트 산출물 DB: `db_standard`
- 프로젝트 산출물 namespace: `db_standard`

정의서 테이블 bootstrap 규칙:

- 표준 단어 / 용어 / 도메인 사전을 조회하지 않는다.
- 웹 검색을 사용하지 않는다.
- 한글 컬럼명을 에이전트가 자동으로 영문 `snake_case` 물리 컬럼명으로 변환한다.
- 영문명 후보를 사용자에게 제안하지 않고 자동 적용한다.
- 정의서 테이블 컬럼 타입은 모두 `text`로 고정한다.
- 한글 테이블명 / 컬럼명은 DB comment로 추가한다.
- 에이전트는 생성된 물리 컬럼명을 기준으로 내부 field map을 자동 추론한다.

### 대상 namespace 라우팅 입력 형식

대상 namespace가 하나여도 주제영역 / 소유자 코드 매핑은 필수다.
DBMS별 namespace 의미는 `references/11-dbms-profile.md`를 따른다.

권장 입력:

```text
target namespaces:
- <namespace_nm>(<subject_area_cd>)
- <namespace_nm>(<subject_area_cd1>, <subject_area_cd2>)
```

확장 입력:

```yaml
target_namespace_map:
  - namespace_nm:
    namespace_kind:
    subject_area_cds:
    subject_area_nms:
    owner_codes:
```

### 신규 프로젝트 검증

에이전트는 입력 후 아래를 확인한다.

- `db_standard` 데이터베이스 접근 가능 여부
- DBMS profile 확정 여부
- `db_standard.db_standard` 표준 사전 테이블 존재 여부
- 표준 사전 필수 컬럼 존재 여부
- 프로젝트 산출물 namespace `db_standard` 존재 여부
- 테이블 정의서 / 컬럼 정의서 한글 컬럼 목록 존재 여부
- 한글 컬럼명에서 영문 `snake_case` 물리 컬럼명 생성 가능 여부
- 필수 role을 내부 field map으로 추론할 수 있는지 여부
- 산출물 namespace가 없고 `execute` 승인이 있으면 DBMS profile에 맞는 생성 preview 또는 실행 계획 생성
- 정의서 테이블 생성 방식이 `create`이면 모든 컬럼 `text` 타입으로 테이블 정의서 / 컬럼 정의서 DDL 생성
- 정의서 테이블 생성 방식이 `use_existing`이면 실제 컬럼 구조와 field map 정합성 검증

## 4. 기존 프로젝트 표준화 작업 이어서 진행

기존 프로젝트는 이미 만들어진 표준 사전, 프로젝트 산출물, 물리 namespace를 조회해서
Execution Context를 복원하는 흐름이다.

`db-standard-initial-context.existing.md`로 입력받아야 하는 값:

- 프로젝트 ID 또는 프로젝트 명
- DBMS 종류 / 버전
- DBMS connection target
- DBMS profile
- 실제 물리 테이블 대상 데이터베이스
- 후보 대상 namespace와 주제영역 / 소유자 코드 매핑
- 프로젝트 산출물 namespace 논리명: `db_standard` 고정
- 테이블 정의서 테이블명
- 컬럼 정의서 테이블명
- 실행 모드

에이전트는 입력 후 아래를 조회한다.

- `db_standard.db_standard` 표준 사전 테이블 존재 여부
- DBMS profile 확정 여부
- `db_standard` 표준 저장소의 `db_standard` 산출물 namespace 존재 여부
- 테이블 정의서 / 컬럼 정의서 테이블 존재 여부
- 정의서 컬럼 구조
- 정의서 field map 자동 추론 가능 여부
- 대상 데이터베이스의 대상 namespace 존재 여부
- 정의서와 물리 namespace의 정합성

자동 추론이 불가능하거나 다중 후보가 있으면 pending decision으로 돌리고,
사용자가 field map 또는 라우팅 값을 확정해야 한다.

## 5. 시작 단계 차단 조건

아래는 즉시 blocked다.

- 작업 유형을 선택하지 않음
- DBMS 종류를 선택하지 않음
- DBMS profile을 확정할 수 없음
- 작업 유형에 맞는 초기 입력 템플릿을 작성하지 않음
- 초기 입력 Markdown의 YAML 블록을 파싱할 수 없음
- 표준 저장소 DB `db_standard`에 접근할 수 없음
- 표준 사전 namespace `db_standard`가 없음
- 표준 단어 / 용어 / 도메인 테이블 중 하나가 없음
- 대상 namespace 라우팅이 없음
- 대상 namespace 라우팅에 주제영역 / 소유자 코드가 없음
- 프로젝트 산출물 namespace가 `db_standard`가 아님
- 신규 프로젝트에서 정의서 한글 컬럼 목록이 없음
- 한글 컬럼명에서 영문 `snake_case` 물리 컬럼명을 생성할 수 없음
- 정의서 field map을 자동 추론할 수 없음
- 테이블 정의서에 `target_schema` 역할로 추론 가능한 컬럼이 없음

## 6. 시작 단계 완료 조건

아래가 모두 충족되면 일반 DDL 작업으로 넘어갈 수 있다.

- 작업 유형에 맞는 작성용 초기 입력 파일이 존재함
- 초기 입력 파일의 YAML 블록이 정상 파싱됨
- 에이전트가 해석한 Execution Context 요약을 사용자에게 제시함
- Execution Context가 확정됨
- 표준 사전 위치가 검증됨
- 프로젝트 산출물 위치가 검증됨
- 신규 프로젝트는 한글 컬럼 목록에서 정의서 DDL과 내부 field map이 생성됨
- 기존 프로젝트는 테이블 정의서 / 컬럼 정의서 field map이 확정됨
- 대상 namespace 라우팅이 확정됨
- DBMS profile이 확정됨
- run mode와 write permission이 구분됨

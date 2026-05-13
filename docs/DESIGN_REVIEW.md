# 설계 검토 결과

결론부터 말하면, 이 설계안은 **올바르다**.

다만 원문을 그대로 `SKILL.md` 하나에 몰아넣는 방식은 추천하지 않는다.
그 방식은 Codex가 아래 두 가지를 동시에 처리해야 해서 불안정해진다.

1. skill을 언제 호출해야 하는가
2. 호출된 뒤 어떤 절차로 판단해야 하는가

따라서 본 패키지는 **단일 메인 skill + canonical references + assets + optional MCP example** 구조로 구현했다.

---

## 1. 원문 문서별 역할 해석

### ai_processor_spec_v_1.1.md
역할: 판단 절차 / 실행 통제 / 분기 엔진

핵심 내용:
- Execution Context 선행
- 기본 read-only
- 컬럼 처리 순서
- 마지막 단어 도메인 판단
- 비종결 단어 차단
- 정의서 INSERT와 DDL 생성 순서

### db-standard_v1.1.md
역할: 표준 규칙층

핵심 내용:
- 테이블 / 컬럼 명명 규칙
- 제약조건 / 시퀀스 / 인덱스 / 주석 규칙
- DBMS casing 규칙
- 파생어 / 복합어 / synonym / prohibited word 정규화

### ddl_request_template_v1.0.md
역할: 입력 계약층

핵심 내용:
- 최소 요청 필드
- 이미지 해석 기준
- 실행 요청 모드
- 기본값
- 텍스트-only 대체 형식

---

## 2. 왜 단일 메인 skill인가

이 업무의 본질은 “표준화 DDL 생성 워크플로” 하나다.
테이블 생성, 컬럼 처리, 용어/단어 등록 preview, 정의서 INSERT, DDL 렌더링이 모두 같은 흐름 안에서 이어진다.

따라서 처음부터 `생성 skill / 리뷰 skill / 사전등록 skill`로 분리하기보다,
우선은 **한 개의 focused skill**로 만들고
내부 문서를 절차별로 분해하는 편이 실제 운영과 유지보수에 더 유리하다.

나중에 아래 시점이 오면 skill 분리를 고려하면 된다.

- SQL 리뷰만 별도 자동화하고 싶을 때
- 신규 단어 / 신규 용어 등록 업무를 별도 승인 프로세스로 떼어낼 때
- 이미 생성된 DDL의 표준 준수 여부만 검사하고 싶을 때

---

## 3. 보완한 부분

본 패키지는 원문 내용을 바꾸지 않고, 아래 항목만 **명시적으로 보완**했다.

### 3.1 규칙 우선순위 명시
원문에는 “규칙 문서가 processor spec보다 우선”이라는 원칙이 있으나,
실제 skill 운용을 위해서는 더 세밀한 precedence가 필요했다.

보완 결과:
1. Execution Context / 실행 통제
2. DDL 표준 규칙 문서
3. Processor workflow
4. 요청 템플릿 기본값
5. 사용자 입력(허용 범위 내)

### 3.2 logical identifier -> DBMS renderer 분리
원문은 DB별 casing 규칙만 있고,
논리 식별자 생성과 물리 식별자 렌더링이 분리돼 있지 않았다.

보완 결과:
- 먼저 canonical logical segments를 만든다.
- 마지막에 DBMS별 casing 규칙을 적용한다.

이 방식이 있어야 Oracle / PostgreSQL / MySQL을 안정적으로 함께 지원할 수 있다.

### 3.3 표준 사전 lookup 불가 시 추측 금지
원문은 실제 쿼리 수행을 전제하지만,
Codex skill 환경에서는 live DB access가 없을 수 있다.

보완 결과:
- live lookup이 없으면 **약어와 도메인을 추측하지 않는다**
- 필요한 SELECT SQL과 pending decisions만 출력한다

### 3.4 UNIQUE 처리 규칙 보강
원문에는 UNIQUE 입력은 있지만 UNIQUE 제약조건 이름 규칙은 없다.
반면 `UIDX_...` 유니크 인덱스 규칙은 있다.

보완 결과:
- 기본 렌더링은 `UNIQUE INDEX` + `UIDX_...`
- 프로젝트별 `UK_...` 제약조건 규칙이 있으면 `AGENTS.md`로 override

### 3.5 공간정보 규칙의 안전한 축소
원문에는 `geom / 공간정보` 규칙은 있지만
geometry subtype, SRID, spatial index 규칙은 충분하지 않다.

보완 결과:
- `geom / 공간정보`는 자동 적용
- geometry 타입 / SRID / spatial index는 명시 입력 없으면 추측 금지
- pending decision으로 처리

### 3.6 데이터베이스 / 대상 namespace 일치 규칙
요청 템플릿과 Execution Context가 따로 존재하므로
둘 사이에 불일치가 생길 수 있다.

보완 결과:
- 요청의 `데이터베이스`는 Execution Context의 `target_db_nm`과 일치해야 한다
- 요청의 대상 namespace는 Execution Context의 `target_namespace_map`에 정의된 namespace 중 하나여야 한다
- 대상 namespace는 주제영역 / 소유자 코드와 매핑되어야 한다
- 대상 namespace가 생략되면 주제영역 / 소유자 코드로 단일 대상 namespace를 확정한다
- 정의서 namespace(`meta_schema_nm`)와 업무 대상 namespace(`target_namespace_nm`)를 분리한다
- 다르면 blocked 상태로 반환

### 3.7 synonym / 금칙어 검색의 모호성 처리
원문은 LIKE 기반 검색을 전제한다.
하지만 구현에 따라 다중 매칭이 발생할 수 있다.

보완 결과:
- exact match를 항상 우선한다
- synonym / prohibited 결과가 2건 이상이면 임의 확정 금지
- 선택 또는 정교화가 필요하다고 표시한다

---

## 4. 왜 scripts를 넣지 않았는가

이 패키지는 일단 **instruction-first** 설계다.

이유:
- 지금 필요한 것은 실행 가능한 shell script보다 **판단 규칙의 안정화**
- 실제 lookup / execution은 조직 환경에 따라 DB client, MCP, 내부 API가 다를 수 있음
- 성급한 script 고정은 오히려 재사용성을 떨어뜨림

대신 아래를 제공했다.

- 복붙용 요청 템플릿
- 실행 컨텍스트 YAML 템플릿
- 출력 템플릿
- optional MCP 예시와 tool contract

---

## 5. 검토 결과: 바로 써도 되는가

네, **preview 중심 운영**으로는 바로 써도 된다.

즉시 사용 가능한 범위:
- 명시 호출형 skill 등록
- 표준 절차에 따른 입력 검증
- lookup SQL / INSERT preview / DDL preview 생성
- blocker / pending decision / review checklist 반환

아직 환경 연동이 필요한 범위:
- live 표준 사전 조회
- 실제 DB write execution
- 조직 고유 owner mapping
- geometry subtype / SRID / spatial index 자동 판별

---

## 6. 권장 다음 단계

1. 이 패키지를 `.agents/skills/`에 등록한다.
2. `AGENTS.example.md`를 프로젝트 실정에 맞게 `AGENTS.md`로 승격한다.
3. 실제 표준 사전 DB 접속 또는 MCP를 연결한다.
4. `EVAL_CASES.md` 기준으로 트리거 / 출력 품질을 검증한다.
5. 검증이 끝나면 필요 시 review 전용 skill을 분리한다.

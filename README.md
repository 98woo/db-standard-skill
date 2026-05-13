# DB Standard Skill

표준 단어 / 용어 / 도메인 사전을 기준으로 테이블명, 컬럼명, 정의서 INSERT SQL, DDL preview를 생성하기 위한 Codex skill 패키지다.

이 repository의 이름은 `db-standard-skill`이다. 실제 Codex runtime에 설치하는 대상은 내부의 `db-standard-ddl-workflow/` 폴더 하나다.

## 목차

- [1. 무엇을 하는 skill인가](#1-무엇을-하는-skill인가)
- [2. 디렉토리 구조](#2-디렉토리-구조)
- [3. 고정 전제](#3-고정-전제)
- [4. 설치 방법](#4-설치-방법)
- [5. 설치 검증](#5-설치-검증)
- [6. 사용 방법](#6-사용-방법)
- [7. 최초 실행 입력](#7-최초-실행-입력)
- [8. 표준화 작업 흐름](#8-표준화-작업-흐름)
- [9. DBMS별 namespace 의미](#9-dbms별-namespace-의미)
- [10. 실행 안전 규칙](#10-실행-안전-규칙)
- [11. 배포 방식](#11-배포-방식)
- [12. 문제 해결](#12-문제-해결)
- [13. 참고 문서](#13-참고-문서)

## 1. 무엇을 하는 skill인가

이 skill은 한국어 업무 정의를 입력받아 표준 사전 기반으로 아래 산출물을 생성한다.

- 표준화된 물리 테이블명
- 표준화된 물리 컬럼명
- 도메인 기반 데이터 타입 / 길이 / scale 판단
- 신규 단어 / 용어 / 도메인 INSERT preview
- 테이블 정의서 INSERT preview
- 컬럼 정의서 INSERT preview
- CREATE TABLE / PK / FK / INDEX / COMMENT DDL preview

사용 목적은 DDL 생성 workflow다. 일반 SQL 튜닝, ORM 모델링, API DTO 설계, 자유 스키마 설계에는 사용하지 않는다.

## 2. 디렉토리 구조

```text
db-standard-skill/
├─ db-standard-ddl-workflow/          # 실제 배포 대상 skill 폴더
│  ├─ SKILL.md                        # skill entrypoint
│  ├─ agents/
│  │  └─ openai.yaml                  # UI metadata / invocation policy
│  ├─ references/                     # runtime reference rules
│  └─ assets/                         # 사용자 작성 템플릿 / 예시 / MCP 계약
├─ docs/                              # 배포/설계/평가 문서, runtime 설치 대상 아님
│  ├─ AGENTS.example.md
│  ├─ DESIGN_REVIEW.md
│  ├─ EVAL_CASES.md
│  ├─ FILE_INDEX.md
│  └─ original/                       # 설계 이력 원문 보존본, runtime 실행 규칙 아님
└─ README.md
```

`db-standard-ddl-workflow/` 폴더만 Codex skill 런타임에 설치한다.

`docs/`는 사람 검토용 문서다. `docs/original/`은 설계 이력 보존본이며 runtime 실행 규칙이 아니다. runtime 규칙은 `db-standard-ddl-workflow/SKILL.md`와 `db-standard-ddl-workflow/references/*.md`를 따른다.

## 3. 고정 전제

이 skill은 아래 전제를 강제한다.

- 표준화 저장소의 논리 database는 `db_standard`다.
- 표준화 저장소의 논리 namespace는 `db_standard`다.
- 표준 단어 / 용어 / 도메인 사전은 사용자가 미리 구축한다.
- 표준 단어 사전 테이블은 `tb_db_com_std_word`다.
- 표준 용어 사전 테이블은 `tb_db_com_std_trm`이다.
- 표준 도메인 사전 테이블은 `tb_db_com_std_dmn`이다.
- 프로젝트 산출물인 테이블 정의서 / 컬럼 정의서도 `db_standard` 표준 저장소의 `db_standard` namespace에 둔다.
- 실제 업무 물리 테이블은 사용자가 입력한 `target_db_nm`과 `target_namespace_map`에 따라 생성한다.

`db_standard.db_standard`라는 표현은 논리 표현이다. 실제 물리 식별자는 DBMS profile에 따라 달라진다.

## 4. 설치 방법

### 4.1 skill-installer 설치

Codex 환경에 `skill-installer`가 제공되는 경우 GitHub repository에서 바로 설치할 수 있다.

에이전트에게 아래처럼 요청한다.

```text
Use skill-installer to install this Codex skill:
repo: <owner>/db-standard-skill
path: db-standard-ddl-workflow
```

또는 GitHub tree URL을 제공한다.

```text
Install this Codex skill from GitHub:
https://github.com/<owner>/db-standard-skill/tree/main/db-standard-ddl-workflow
```

내부적으로는 아래 형태의 설치가 수행된다.

```bash
install-skill-from-github.py --repo <owner>/db-standard-skill --path db-standard-ddl-workflow
```

주의:

- `skill-installer`는 모든 에이전트에 항상 내장되어 있지 않다.
- 사용할 수 없는 환경에서는 아래 수동 설치 방식을 사용한다.
- 설치 후 새 skill을 인식하려면 Codex를 재시작해야 할 수 있다.

### 4.2 전역 수동 설치

Codex 전체에서 사용하려면 사용자 skill 경로에 복사한다.

Windows PowerShell 예시:

```powershell
$src = ".\db-standard-ddl-workflow"
$dst = "$env:USERPROFILE\.codex\skills\db-standard-ddl-workflow"

New-Item -ItemType Directory -Force -Path (Split-Path $dst)
Copy-Item -Recurse -Force $src $dst
```

`CODEX_HOME`을 별도로 사용한다면 아래 구조를 사용한다.

```text
$CODEX_HOME/skills/db-standard-ddl-workflow/
```

### 4.3 프로젝트 단위 수동 설치

특정 프로젝트에서만 사용하려면 프로젝트 루트에 설치한다.

```text
<project-root>/.agents/skills/db-standard-ddl-workflow/
```

프로젝트 단위 설치는 해당 프로젝트 작업에서만 skill을 노출하고 싶을 때 적합하다.

### 4.4 GitHub clone 설치

GitHub로 공유할 경우 repository에는 최소한 아래를 포함한다.

```text
db-standard-skill/
├─ db-standard-ddl-workflow/
├─ README.md
└─ docs/
```

다른 사용자는 repository를 clone한 뒤 `db-standard-ddl-workflow/` 폴더만 자신의 Codex skill 경로로 복사한다.

GitHub에 올리는 것만으로 자동 설치되지는 않는다. 사용자가 직접 clone, copy, 또는 별도 installer를 통해 설치해야 한다.

### 4.5 GitHub Download ZIP 사용

GitHub의 Download ZIP 기능을 사용해 repository를 내려받을 수는 있다.
다만 repository 안에 별도의 `db-standard-ddl-workflow.zip` 파일을 커밋하지 않는다.

Download ZIP으로 받은 경우에도 최종 설치 구조는 반드시 아래처럼 되어야 한다.

```text
<skill-root>/db-standard-ddl-workflow/SKILL.md
<skill-root>/db-standard-ddl-workflow/references/
<skill-root>/db-standard-ddl-workflow/assets/
<skill-root>/db-standard-ddl-workflow/agents/
```

`db-standard-ddl-workflow/db-standard-ddl-workflow/SKILL.md`처럼 폴더가 한 번 더 중첩되면 잘못 설치된 것이다.

## 5. 설치 검증

### 5.1 skill 구조 검증

skill-creator의 `quick_validate.py`로 검증한다.

Windows에서 한글 UTF-8 파일을 읽을 때 기본 코드페이지가 `cp949`이면 실패할 수 있으므로 `PYTHONUTF8=1`을 권장한다.

```powershell
$env:PYTHONUTF8 = "1"
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" ".\db-standard-ddl-workflow"
```

정상 결과:

```text
Skill is valid!
```

### 5.2 템플릿 YAML 검증

초기 입력 템플릿의 YAML 블록이 파싱되는지 확인한다.

```powershell
$script = @'
import yaml
from pathlib import Path

files = [
    "db-standard-ddl-workflow/assets/initial-context-new-project.template.md",
    "db-standard-ddl-workflow/assets/initial-context-existing-project.template.md",
]

for file in files:
    text = Path(file).read_text(encoding="utf-8")
    start = text.index("```yaml") + len("```yaml")
    end = text.index("```", start)
    yaml.safe_load(text[start:end])
    print(file, "yaml_ok")

yaml.safe_load(Path("db-standard-ddl-workflow/assets/execution-context.template.yaml").read_text(encoding="utf-8"))
print("execution-context.template.yaml yaml_ok")
'@

$script | python -
```

위 명령은 `db-standard-ddl-workflow/` 폴더가 있는 위치에서 실행한다.

### 5.3 설치 후 호출 확인

새 Codex 세션을 열고 아래처럼 명시 호출한다.

```text
$db-standard-ddl-workflow
```

또는 다음처럼 요청한다.

```text
표준 단어/용어/도메인 사전을 기준으로 신규 테이블 DDL을 만들어줘.
```

정상이라면 에이전트가 먼저 DBMS와 신규/기존 작업 여부를 묻는다.

## 6. 사용 방법

### 6.1 명시 호출

가장 안전한 방식은 skill 이름을 직접 호출하는 것이다.

```text
$db-standard-ddl-workflow
```

### 6.2 일반 요청으로 호출

아래처럼 표준화 DDL 작업임을 명확히 말해도 된다.

```text
표준 단어/용어/도메인 사전을 기준으로 아래 한글 테이블 정의를 표준화하고 DDL preview를 만들어줘.
```

### 6.3 최초 실행 시 에이전트 동작

Execution Context가 없으면 에이전트는 업무 테이블 DDL부터 만들지 않는다. 먼저 아래를 진행해야 한다.

1. DBMS 종류와 버전 확인
2. 신규 프로젝트인지 기존 프로젝트 이어서 진행인지 확인
3. 현재 작업 디렉토리에 작성용 Markdown 템플릿 생성
4. 사용자가 템플릿 작성
5. YAML 파싱
6. 표준 사전 / 정의서 / target namespace 검증
7. Execution Context 확정
8. 업무 테이블 표준화 진행

## 7. 최초 실행 입력

### 7.1 공통 입력

모든 사용자는 최초에 아래 정보를 제공해야 한다.

- DBMS 종류: `postgresql`, `oracle`, `mysql`, `mariadb`, `sqlserver`
- DBMS 버전
- DB connection target
- 실제 업무 테이블 대상 database
- 실제 업무 테이블 대상 namespace와 주제영역 / 소유자 코드 매핑
- 실행 모드: `preview`, `approval`, `execute`

대상 namespace가 하나뿐이어도 주제영역 매핑은 입력해야 한다.

예:

```text
target namespaces:
- gygo_cli(scc)
- gygo_fld(suo)
```

### 7.2 신규 프로젝트 사용자

신규 프로젝트 사용자는 표준 사전은 이미 구축되어 있지만, 테이블 정의서 / 컬럼 정의서 테이블 구조를 새로 정하는 사용자다.

에이전트는 아래 템플릿을 현재 작업 디렉토리에 생성한다.

```text
db-standard-initial-context.new.md
```

사용자는 이 파일에 아래를 작성한다.

- 프로젝트 ID
- 프로젝트 명
- DBMS 정보
- 대상 database / namespace map
- 테이블 정의서 한글 테이블명
- 테이블 정의서 한글 컬럼 목록
- 컬럼 정의서 한글 테이블명
- 컬럼 정의서 한글 컬럼 목록
- 정의서 생성 방식: `create` 또는 `use_existing`
- 실행 모드

신규 프로젝트의 정의서 테이블 bootstrap은 표준화 작업이 아니다.

- 표준 단어 / 용어 / 도메인 사전을 조회하지 않는다.
- 웹 검색을 사용하지 않는다.
- 한글 컬럼명은 에이전트가 자동 `snake_case`로 변환한다.
- 정의서 테이블 컬럼 타입은 모두 `text`로 만든다.
- 한글명은 DB comment로 남긴다.

### 7.3 기존 프로젝트 사용자

기존 프로젝트 사용자는 이미 정의서와 일부 표준화 결과가 존재하는 프로젝트에 합류하는 사용자다.

에이전트는 아래 템플릿을 현재 작업 디렉토리에 생성한다.

```text
db-standard-initial-context.existing.md
```

사용자는 이 파일에 아래를 작성한다.

- 프로젝트 ID 또는 프로젝트 명
- DBMS 정보
- 대상 database / namespace map
- 테이블 정의서 테이블명
- 컬럼 정의서 테이블명
- 정의서 field map, 또는 자동 추론에 필요한 정보
- 실행 모드

에이전트는 실제 DB 조회가 가능하면 정의서 컬럼 구조를 확인하고 field map을 복원한다. 자동 추론이 불가능하면 pending decision으로 사용자 확인을 요구한다.

## 8. 표준화 작업 흐름

업무 테이블 표준화는 finalized Execution Context가 있어야 진행한다.

기본 흐름:

1. 요청 database와 `target_db_nm` 일치 확인
2. 요청 namespace와 `target_namespace_map` 일치 확인
3. 테이블 종류 / 소유자 / 주제영역 확인
4. 한글 테이블명 정규화
5. 표준 단어 사전으로 테이블명 구성 단어 조회
6. 물리 테이블명 생성
7. 컬럼별 표준 용어 exact lookup
8. 용어가 없으면 단어 분해
9. 마지막 단어 기준 도메인 판단
10. 기존 단어 / 용어 / 도메인 재사용 가능성 검토
11. 재사용 불가 시 신규 사전 INSERT preview 생성
12. 테이블 정의서 INSERT preview 생성
13. 컬럼 정의서 INSERT preview 생성
14. DDL preview 생성
15. blocker / pending decision / preview-only 상태 분리 출력

경우별 차이:

- 용어 exact hit: 기존 용어의 영문 약어와 도메인을 그대로 재사용한다.
- 용어 miss: 단어로 분해한 뒤 표준 단어와 마지막 단어 도메인을 판단한다.
- 단어 후보가 여러 개: 임의 선택하지 않고 pending decision으로 돌린다.
- 기존 도메인 후보가 있음: 신규 도메인보다 기존 도메인 재사용을 우선한다.
- 신규 도메인이 필요함: 기존 exact / 유사 후보 조회와 승인 근거가 있어야 preview를 만든다.
- live lookup 불가: 약어 / 도메인을 추측하지 않고 lookup SQL과 preview만 반환한다.
- 대상 namespace 생략: 주제영역 / 소유자 코드로 단일 namespace를 확정할 수 있을 때만 자동 처리한다.

## 9. DBMS별 namespace 의미

`target_namespace_map`의 namespace 의미는 DBMS마다 다르다.

| DBMS | namespace 의미 | 표준 저장소 예시 |
| --- | --- | --- |
| PostgreSQL | schema | database `db_standard`, schema `db_standard` |
| Oracle | owner / schema | owner `DB_STANDARD` |
| MySQL | database | database `db_standard` |
| MariaDB | database | database `db_standard` |
| SQL Server | schema | database `db_standard`, schema `db_standard` |

SQL은 DBMS profile에 맞게 렌더링한다.

- PostgreSQL: `schema.table`
- Oracle: `owner.table`
- MySQL / MariaDB: `database.table`
- SQL Server: `schema.table`

PostgreSQL처럼 SQL 안에서 `database.schema.table`을 지원하지 않는 DBMS에서는 database명을 SQL 식별자에 붙이지 않는다. 대신 해당 database에 접속한 뒤 `schema.table`을 사용한다.

## 10. 실행 안전 규칙

기본은 preview다.

- `run_mode=preview`: SELECT / preview SQL만 생성하고 쓰기 실행 금지
- `run_mode=approval`: preview SQL과 실행 순서를 제시하고 승인 대기
- `run_mode=execute`: 사용자 명시 승인, `write_execution_enabled=true`, 실제 실행 도구가 모두 있을 때만 실행

아래 상황은 실행하지 않는다.

- 표준 사전 조회가 불가능한데 약어명이나 도메인명을 추측해야 하는 경우
- 기존 단어 / 용어 / 도메인 재사용 후보를 확인하지 않은 경우
- 신규 도메인 등록 승인이 없는 경우
- `target_namespace_map`과 요청 namespace가 충돌하는 경우
- 테이블 정의서 / 컬럼 정의서 field map이 불명확한 경우
- 사용자 승인 없이 DB write가 필요한 경우

## 11. 배포 방식

### 11.1 GitHub 공개 공유

GitHub에 공개할 경우 repository README에 아래를 반드시 포함한다.

- `skill-installer`가 있으면 GitHub repo/path로 설치할 수 있다는 점
- `skill-installer`가 없는 환경을 위해 수동 복사 설치 방법도 제공한다는 점
- 설치 대상은 `db-standard-ddl-workflow/` 폴더라는 점
- `docs/`와 `docs/original/`은 runtime 설치 대상이 아니라는 점
- `db_standard` 표준 저장소와 사전 테이블은 사용자가 미리 구축해야 한다는 점
- 최초 실행 시 DBMS와 신규/기존 작업 유형을 입력해야 한다는 점
- 승인 없는 write는 실행하지 않는다는 점
- Windows 검증 시 `PYTHONUTF8=1`이 필요할 수 있다는 점
- repository에는 별도 zip 산출물을 커밋하지 않는다는 점

### 11.2 내부 공유

내부 공유도 GitHub repository 또는 사내 Git 저장소 clone 방식을 권장한다.
zip 파일을 별도로 공유해야 한다면 GitHub Release artifact처럼 일회성 배포물로만 관리하고, repository source tree에는 커밋하지 않는다.

### 11.3 버전 관리 권장

skill을 여러 프로젝트에서 사용할 예정이면 release tag를 붙이는 것이 좋다.

예:

```text
v0.1.0-internal
v0.2.0-dbms-profile
v1.0.0
```

변경 시에는 최소한 아래를 확인한다.

- `SKILL.md` frontmatter 유효성
- templates YAML 파싱
- `references/00-rule-priority.md` 우선순위
- `references/11-dbms-profile.md` DBMS profile
- `references/90-output-contract.md` 출력 형식
- runtime 설치 대상에 불필요한 `docs/original`이 포함되지 않았는지

## 12. 문제 해결

### skill이 호출되지 않음

- `SKILL.md`가 설치 경로 바로 아래에 있는지 확인한다.
- 폴더가 중첩 설치됐는지 확인한다.
- 새 Codex 세션을 열어 다시 시도한다.
- 명시적으로 `$db-standard-ddl-workflow`를 호출한다.

### quick_validate.py가 UnicodeDecodeError로 실패함

Windows 기본 코드페이지 문제일 수 있다.

```powershell
$env:PYTHONUTF8 = "1"
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" ".\db-standard-ddl-workflow"
```

### 에이전트가 바로 DDL을 만들지 않고 질문만 함

정상 동작이다. Execution Context가 없으면 DBMS, 신규/기존 작업 유형, target namespace map, 정의서 구조를 먼저 확정해야 한다.

### 표준 사전 테이블이 없다고 blocked됨

정상 동작이다. 이 skill은 단어 / 용어 / 도메인 사전 테이블을 새로 만드는 skill이 아니다. 사용자가 `db_standard` 표준 저장소에 사전 테이블을 미리 구축해야 한다.

### 신규 도메인을 바로 추가하지 않음

정상 동작이다. 기존 도메인 exact / 유사 후보 조회가 먼저이고, 재사용 가능한 후보가 없을 때만 신규 도메인 INSERT preview를 만든다. 실제 실행은 별도 승인 대상이다.

## 13. 참고 문서

Runtime skill:

- `db-standard-ddl-workflow/SKILL.md`: skill 본체
- `db-standard-ddl-workflow/references/00-rule-priority.md`: 규칙 우선순위와 해석 원칙
- `db-standard-ddl-workflow/references/05-startup-onboarding.md`: 시작 온보딩
- `db-standard-ddl-workflow/references/10-execution-context.md`: Execution Context
- `db-standard-ddl-workflow/references/11-dbms-profile.md`: DBMS별 profile
- `db-standard-ddl-workflow/references/12-metadata-artifact-model.md`: 테이블 정의서 / 컬럼 정의서 모델
- `db-standard-ddl-workflow/references/50-column-domain-decision.md`: 컬럼 / 도메인 판단
- `db-standard-ddl-workflow/references/60-sql-rendering.md`: SQL 렌더링
- `db-standard-ddl-workflow/references/90-output-contract.md`: 출력 형식

Repository docs:

- `docs/DESIGN_REVIEW.md`: 설계 검토와 보완 이력
- `docs/EVAL_CASES.md`: 평가 시나리오
- `docs/AGENTS.example.md`: 프로젝트 루트용 AGENTS 예시
- `docs/FILE_INDEX.md`: 파일 목록
- `docs/original/`: 설계 이력 원문 보존본, runtime 실행 규칙 아님

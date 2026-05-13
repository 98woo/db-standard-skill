# File Index

## Runtime Skill

- `../db-standard-ddl-workflow/SKILL.md`: skill 본체
- `../db-standard-ddl-workflow/agents/openai.yaml`: skill UI metadata / policy

## Runtime References

- `../db-standard-ddl-workflow/references/00-rule-priority.md`: 우선순위와 해석 원칙
- `../db-standard-ddl-workflow/references/05-startup-onboarding.md`: 최초 시작 분기와 프로젝트 온보딩
- `../db-standard-ddl-workflow/references/10-execution-context.md`: 실행 컨텍스트
- `../db-standard-ddl-workflow/references/11-dbms-profile.md`: DBMS별 표준 저장소 / namespace profile
- `../db-standard-ddl-workflow/references/12-metadata-artifact-model.md`: 테이블/컬럼 정의서 field map
- `../db-standard-ddl-workflow/references/13-schema-routing.md`: 대상 namespace와 주제영역 라우팅
- `../db-standard-ddl-workflow/references/20-request-contract.md`: 요청 계약
- `../db-standard-ddl-workflow/references/25-catalog-query-templates.md`: 조회 SQL 템플릿
- `../db-standard-ddl-workflow/references/30-normalization-rules.md`: 정규화 규칙
- `../db-standard-ddl-workflow/references/40-table-naming.md`: 테이블 명명
- `../db-standard-ddl-workflow/references/50-column-domain-decision.md`: 컬럼/도메인 판단
- `../db-standard-ddl-workflow/references/60-sql-rendering.md`: SQL 렌더링 규칙
- `../db-standard-ddl-workflow/references/70-blocking-rules.md`: 차단 규칙
- `../db-standard-ddl-workflow/references/80-dbms-dialects.md`: DBMS 방언
- `../db-standard-ddl-workflow/references/81-spatial-rules.md`: 공간정보 규칙
- `../db-standard-ddl-workflow/references/90-output-contract.md`: 출력 계약
- `../db-standard-ddl-workflow/references/95-review-checklist.md`: 리뷰 체크리스트

## Runtime Assets

- `../db-standard-ddl-workflow/assets/initial-context-new-project.template.md`: 신규 프로젝트 최초 입력용 Markdown/YAML 템플릿
- `../db-standard-ddl-workflow/assets/initial-context-existing-project.template.md`: 기존 프로젝트 이어서 진행 최초 입력용 Markdown/YAML 템플릿
- `../db-standard-ddl-workflow/assets/request-template.txt`: 복붙용 입력 템플릿
- `../db-standard-ddl-workflow/assets/execution-context.template.yaml`: 실행 컨텍스트 예시
- `../db-standard-ddl-workflow/assets/output-template.md`: 출력 형식 템플릿
- `../db-standard-ddl-workflow/assets/openai.mcp.example.yaml`: MCP 연동 예시
- `../db-standard-ddl-workflow/assets/mcp-tool-contract.md`: 권장 MCP tool contract
- `../db-standard-ddl-workflow/assets/examples/*`: 요청/결과 예시

## Repository Docs

- `../README.md`: 설치 및 운영 설명
- `AGENTS.example.md`: 프로젝트 루트용 AGENTS 예시
- `DESIGN_REVIEW.md`: 설계 검토와 보완점
- `EVAL_CASES.md`: 검증 시나리오
- `FILE_INDEX.md`: 파일 목록
- `original/*`: 원문 보존본. runtime skill 실행 규칙이 아니며 canonical reference와 충돌하면 canonical reference를 따른다.
